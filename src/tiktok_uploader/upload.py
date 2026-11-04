"""
`tiktok_uploader` module for uploading videos to TikTok

Key Classes
-----------
TikTokUploader : Client for uploading videos to TikTok
"""

import datetime
import logging
import time
import weakref
from collections.abc import Callable
from os.path import abspath, exists
from typing import Any, Literal

import pytz
from playwright.sync_api import Dialog, Locator, Page
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError

from tiktok_uploader import config
from tiktok_uploader.auth import AuthBackend
from tiktok_uploader.browsers import get_browser
from tiktok_uploader.types import Cookie, ProxyDict, VideoDict

logger = logging.getLogger(__name__)

# VideoDict keys that are passed to complete_upload_form as keyword options;
# a video's own value overrides the same keyword given to upload_videos
PER_VIDEO_OPTIONS = (
    "comment",
    "stitch",
    "duet",
    "reuse_of_content",
    "sound_name",
    "sound_artist",
    "draft",
    "ai_label",
    "skip_restricted",
)

# where TikTok Studio sends the browser once a post has gone through
POSTED_URL_FRAGMENT = "tiktokstudio/content"

_pages_accepting_dialogs: "weakref.WeakSet[Page]" = weakref.WeakSet()


class TikTokUploader:
    def __init__(
        self,
        username: str = "",
        password: str = "",
        cookies: str = "",
        cookies_list: list[Cookie] = [],
        cookies_str: str | None = None,
        sessionid: str | None = None,
        proxy: ProxyDict | None = None,
        browser: Literal["chrome", "safari", "chromium", "edge", "firefox"] = "chrome",
        headless: bool = False,
        *args,
        **kwargs,
    ):
        """
        Initializes the TikTok Uploader client.

        The browser is not started until the first upload is attempted (lazy initialization).
        """
        self.auth = AuthBackend(
            username=username,
            password=password,
            cookies=cookies,
            cookies_list=cookies_list,
            cookies_str=cookies_str,
            sessionid=sessionid,
        )
        self.proxy = proxy
        self.browser_name = browser
        self.headless = headless
        self.browser_args = args
        self.browser_kwargs = kwargs

        self._page: Page | None = None
        self._browser_context: Any = (
            None  # Stored implicitly via page.context if needed
        )

    @property
    def page(self) -> Page:
        if self._page is None:
            logger.debug(
                "Create a %s browser instance %s",
                self.browser_name,
                "in headless mode" if self.headless else "",
            )
            self._page = get_browser(
                self.browser_name,
                headless=self.headless,
                proxy=self.proxy,
                *self.browser_args,
                **self.browser_kwargs,
            )  # type: ignore[misc]
            self._page = self.auth.authenticate_agent(self._page)
        return self._page

    def upload_video(
        self,
        filename: str,
        description: str = "",
        schedule: datetime.datetime | None = None,
        product_id: str | None = None,
        cover: str | None = None,
        visibility: Literal["everyone", "friends", "only_you"] = "everyone",
        num_retries: int = 1,
        skip_split_window: bool = False,
        *args,
        sound_name: str | None = None,
        sound_artist: str | None = None,
        draft: bool = False,
        ai_label: bool | None = None,
        skip_restricted: bool = False,
        **kwargs,
    ) -> bool:
        """
        Uploads a single TikTok video.

        - sound_name / sound_artist: background sound picked from TikTok's library
        - draft: save to the account's drafts instead of posting (not schedulable)
        - ai_label: turn TikTok's "AI-generated content" label on (True) or off
          (False); None leaves it as TikTok sets it
        - skip_restricted: do not post if TikTok's content check warns the video
          may be restricted

        Returns True if successful, False otherwise; the reason for a failure
        is logged on the "tiktok_uploader" logger.
        """
        video_dict = _video_dict(
            filename,
            description,
            schedule,
            product_id,
            cover,
            visibility,
            sound_name,
            sound_artist,
            draft,
            ai_label,
            skip_restricted,
        )

        failed_list = self.upload_videos(
            [video_dict], num_retries, skip_split_window, *args, **kwargs
        )

        return len(failed_list) == 0

    def upload_videos(
        self,
        videos: list[VideoDict],
        num_retries: int = 1,
        skip_split_window: bool = False,
        on_complete: Callable[[VideoDict], None] | None = None,
        *args,
        **kwargs,
    ) -> list[VideoDict]:
        """
        Uploads multiple videos to TikTok.
        Returns a list of failed videos.

        Each video's outcome is logged on the "tiktok_uploader" logger: INFO
        when it is posted, scheduled or saved as a draft, ERROR with the
        reason when it fails or is skipped.
        """
        videos = _convert_videos_dict(videos)  # type: ignore

        page = self.page  # Triggers lazy loading/authentication

        failed = []
        # uploads each video
        for video in videos:
            path = abspath(video.get("path", "."))
            try:
                description = video.get("description", "")
                schedule = video.get("schedule", None)
                product_id = video.get("product_id", None)
                cover_path = video.get("cover", None)
                if cover_path is not None:
                    cover_path = abspath(cover_path)

                visibility = video.get("visibility", "everyone")

                logger.debug(
                    "Posting %s%s",
                    video.get("path", ""),
                    (
                        f"\n{' ' * 15}with description: {description}"
                        if description
                        else ""
                    ),
                )

                # Video must be of supported type
                if not _check_valid_path(path):
                    logger.error("Skipped %s: not a supported video file", path)
                    failed.append(video)
                    continue

                # Video must have a valid datetime for tiktok's scheduler.
                # A naive datetime is UTC, as documented (astimezone() would
                # read it as host-local time); an aware one is converted, since
                # pytz's localize() raises on an already-aware datetime.
                if schedule:
                    if schedule.tzinfo is None:
                        schedule = pytz.UTC.localize(schedule)
                    schedule = schedule.astimezone(pytz.UTC)

                    valid_tiktok_minute_multiple = 5
                    schedule = _get_valid_schedule_minute(
                        schedule, valid_tiktok_minute_multiple
                    )
                    if not _check_valid_schedule(schedule):
                        logger.error(
                            "Skipped %s: the schedule %s UTC must be 20 minutes "
                            "to 10 days ahead",
                            path,
                            f"{schedule:%Y-%m-%d %H:%M}",
                        )
                        failed.append(video)
                        continue

                video_options: dict[str, Any] = {
                    k: v for k, v in video.items() if k in PER_VIDEO_OPTIONS
                }
                options = {**kwargs, **video_options}
                if schedule and options.get("draft"):
                    logger.error("Skipped %s: a draft cannot be scheduled", path)
                    failed.append(video)
                    continue

                complete_upload_form(
                    page,
                    path,
                    description,
                    schedule,
                    skip_split_window,
                    cover_path,
                    product_id,
                    visibility,
                    num_retries,
                    self.headless,
                    *args,
                    **options,
                )  # type: ignore[misc]

                if options.get("draft"):
                    logger.info("Saved %s as a draft", path)
                elif schedule:
                    logger.info(
                        "Scheduled %s for %s UTC", path, f"{schedule:%Y-%m-%d %H:%M}"
                    )
                else:
                    logger.info("Posted %s", path)
            except Exception as exception:
                logger.error("Failed to upload %s: %s", path, exception)
                logger.debug("Traceback for %s", path, exc_info=True)
                failed.append(video)

            if on_complete and callable(
                on_complete
            ):  # calls the user-specified on-complete function
                on_complete(video)

        if len(videos) > 1:
            done = len(videos) - len(failed)
            logger.info("Uploaded %d of %d videos", done, len(videos))

        return failed

    def close(self):
        """Closes the browser instance."""
        if self._page:
            try:
                self._page.context.browser.close()
            except Exception as e:
                logger.debug(f"Error closing browser: {e}")
            self._page = None

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()


# Wrapper functions for backward compatibility (optional but good for transition)
def upload_video(
    filename: str,
    description: str | None = None,
    cookies: str = "",
    schedule: datetime.datetime | None = None,
    username: str = "",
    password: str = "",
    sessionid: str | None = None,
    cookies_list: list[Cookie] = [],
    cookies_str: str | None = None,
    proxy: ProxyDict | None = None,
    product_id: str | None = None,
    cover: str | None = None,
    visibility: Literal["everyone", "friends", "only_you"] = "everyone",
    browser: Literal["chrome", "safari", "chromium", "edge", "firefox"] = "chrome",
    headless: bool = False,
    *args,
    sound_name: str | None = None,
    sound_artist: str | None = None,
    draft: bool = False,
    ai_label: bool | None = None,
    skip_restricted: bool = False,
    **kwargs,
) -> list[VideoDict]:
    """
    Uploads a single TikTok video using the TikTokUploader class.
    See TikTokUploader.upload_video for the options.

    Returns a list of failed videos (empty if successful).
    """
    uploader = TikTokUploader(
        username=username,
        password=password,
        cookies=cookies,
        cookies_list=cookies_list,
        cookies_str=cookies_str,
        sessionid=sessionid,
        proxy=proxy,
        browser=browser,
        headless=headless,
        *args,
        **kwargs,
    )  # type: ignore[misc]

    video_dict = _video_dict(
        filename,
        description,
        schedule,
        product_id,
        cover,
        visibility,
        sound_name,
        sound_artist,
        draft,
        ai_label,
        skip_restricted,
    )

    try:
        return uploader.upload_videos([video_dict], *args, **kwargs)
    finally:
        if config.quit_on_end:
            uploader.close()


def _video_dict(
    filename: str,
    description: str | None,
    schedule: datetime.datetime | None,
    product_id: str | None,
    cover: str | None,
    visibility: Literal["everyone", "friends", "only_you"],
    sound_name: str | None,
    sound_artist: str | None,
    draft: bool,
    ai_label: bool | None,
    skip_restricted: bool,
) -> VideoDict:
    """
    The VideoDict for upload_video's arguments, holding only the non-defaults
    """
    video_dict: VideoDict = {"path": filename}
    if description:
        video_dict["description"] = description
    if schedule:
        video_dict["schedule"] = schedule
    if product_id:
        video_dict["product_id"] = product_id
    if visibility != "everyone":
        video_dict["visibility"] = visibility
    if cover:
        video_dict["cover"] = cover
    if sound_name:
        video_dict["sound_name"] = sound_name
    if sound_artist:
        video_dict["sound_artist"] = sound_artist
    if draft:
        video_dict["draft"] = True
    if ai_label is not None:
        video_dict["ai_label"] = ai_label
    if skip_restricted:
        video_dict["skip_restricted"] = True
    return video_dict


def upload_videos(
    videos: list[VideoDict],
    username: str = "",
    password: str = "",
    cookies: str = "",
    cookies_list: list[Cookie] = [],
    cookies_str: str | None = None,
    sessionid: str | None = None,
    proxy: ProxyDict | None = None,
    browser: Literal["chrome", "safari", "chromium", "edge", "firefox"] = "chrome",
    browser_agent: Page
    | None = None,  # Not fully supported in new class-based approach as constructor
    headless: bool = False,
    *args,
    **kwargs,
) -> list[VideoDict]:
    """
    Uploads multiple videos to TikTok using the TikTokUploader class.
    """
    uploader = TikTokUploader(
        username=username,
        password=password,
        cookies=cookies,
        cookies_list=cookies_list,
        cookies_str=cookies_str,
        sessionid=sessionid,
        proxy=proxy,
        browser=browser,
        headless=headless,
        *args,
        **kwargs,
    )  # type: ignore[misc]

    if browser_agent:
        uploader._page = uploader.auth.authenticate_agent(browser_agent)

    try:
        return uploader.upload_videos(videos, *args, **kwargs)
    finally:
        if config.quit_on_end:
            uploader.close()


def complete_upload_form(
    page: Page,
    path: str,
    description: str,
    schedule: datetime.datetime | None,
    skip_split_window: bool,
    cover_path: str | None = None,
    product_id: str | None = None,
    visibility: Literal["everyone", "friends", "only_you"] = "everyone",
    num_retries: int = 1,
    headless: bool = False,
    *args,
    sound_name: str | None = None,
    sound_artist: str | None = None,
    draft: bool = False,
    ai_label: bool | None = None,
    skip_restricted: bool = False,
    **kwargs,
) -> None:
    """
    Actually uploads each video, or saves it as a draft if `draft` is set
    """
    # the react-joyride tour overlay is removed by get_browser's init script
    _go_to_upload(page)
    _remove_cookies_window(page)

    _set_video(page, path=path, num_retries=num_retries, **kwargs)
    _dismiss_blocking_modals(page)

    if cover_path:
        _set_cover(page, cover_path)
    if not skip_split_window:
        _remove_split_window(page)
    _dismiss_blocking_modals(page)
    _set_interactivity(page, **kwargs)
    _set_description(page, description)
    if sound_name:
        _set_sound(page, sound_name, sound_artist)
    if visibility != "everyone":
        _set_visibility(page, visibility)
    if ai_label is not None:
        _set_ai_label(page, ai_label)
    if schedule:
        _set_schedule_video(page, schedule)
    if product_id:
        _add_product_link(page, product_id)
    if draft:
        _save_draft(page)
    else:
        _post_video(page, skip_restricted=skip_restricted)


def _go_to_upload(page: Page) -> None:
    """
    Navigates to the upload page
    """
    logger.debug("Navigating to upload page")

    # A page left on the upload form (a failed upload) asks before it reloads;
    # unanswered, Playwright dismisses that dialog, which cancels the reload and
    # fails every later video in the batch. Registered once, before reloading.
    if page not in _pages_accepting_dialogs:
        page.on("dialog", _accept_dialog)
        _pages_accepting_dialogs.add(page)

    if page.url != config.paths.upload:
        page.goto(str(config.paths.upload))
    else:
        page.reload()

    # waits for the root to load
    page.wait_for_selector("#root", timeout=config.explicit_wait * 1000)


def _accept_dialog(dialog: Dialog) -> None:
    dialog.accept()


def _click_if_visible(locator: Locator, timeout: float) -> bool:
    """
    Clicks the element if it becomes visible within `timeout` seconds.

    Playwright's is_visible() ignores its timeout argument and answers at once,
    so it cannot wait for a modal that is still animating in.
    """
    try:
        locator.wait_for(state="visible", timeout=timeout * 1000)
    except PlaywrightTimeoutError:
        return False
    locator.click()
    return True


def _dismiss_blocking_modals(page: Page, max_modals: int = 3) -> None:
    """
    Dismisses the one-off TikTok Studio modals ("New editing features added",
    "Turn on automatic content checks?") whose overlays intercept every click
    on the upload form underneath
    """
    logger.debug("Dismissing blocking modals")

    # the modals can stack, each dismissed by its own button
    button = page.locator(f"xpath={config.selectors.upload.modal_dismiss}").first
    for _ in range(max_modals):
        try:
            if not _click_if_visible(button, timeout=3):
                break
        except Exception as e:
            logger.debug(f"Could not click a modal's dismiss button: {e}")
            break

    # a modal with no "Got it" (the content-checks prompt) declines on Escape;
    # whatever still has a backdrop open is then removed outright
    try:
        page.keyboard.press("Escape")
        page.evaluate(
            """overlayClass => document
                .querySelectorAll('[data-floating-ui-portal]')
                .forEach(portal => {
                    if (portal.querySelector('.' + overlayClass)) portal.remove();
                })""",
            config.selectors.upload.modal_overlay,
        )
    except Exception as e:
        logger.debug(f"Could not clear modal overlays: {e}")


def _set_description(page: Page, description: str) -> None:
    """
    Sets the description of the video
    """
    if description is None:
        return

    logger.debug("Setting description")

    # Remove any characters outside the BMP range (emojis, etc) & Fix accents
    description = description.encode("utf-8", "ignore").decode("utf-8")
    saved_description = description

    desc_locator = page.locator(f"xpath={config.selectors.upload.description}")
    try:
        desc_locator.wait_for(state="visible", timeout=config.implicit_wait * 1000)

        desc_locator.click()

        # Clear existing text (TikTok pre-fills the caption with the filename)
        _clear(desc_locator)

        desc_locator.click()
        time.sleep(1)

        words = description.split(" ")
        for word in words:
            if not word:  # consecutive spaces
                continue
            if word[0] == "#":
                desc_locator.press_sequentially(word, delay=50)
                time.sleep(0.5)

                mention_box = page.locator(
                    f"xpath={config.selectors.upload.mention_box}"
                )
                try:
                    mention_box.wait_for(
                        state="visible", timeout=config.add_hashtag_wait * 1000
                    )
                    # Enter inserts a line break rather than picking the
                    # suggestion, so click the hashtag that matches exactly
                    mention_box.get_by_text(word, exact=True).first.click(
                        timeout=config.add_hashtag_wait * 1000
                    )
                except Exception:
                    desc_locator.press_sequentially(" ")

            elif word[0] == "@":
                logger.debug("- Adding Mention: " + word)
                desc_locator.press_sequentially(word)
                time.sleep(1)

                mention_box_user_id = page.locator(
                    f"xpath={config.selectors.upload.mention_box_user_id}"
                )
                try:
                    mention_box_user_id.first.wait_for(state="visible", timeout=5000)

                    found = False
                    user_ids = mention_box_user_id.all()

                    target_username = word[1:].lower()

                    for i, user_el in enumerate(user_ids):
                        if user_el.is_visible():
                            text = user_el.inner_text().split(" ")[0]
                            if text.lower() == target_username:
                                found = True
                                logger.debug("Matched the mention %s", word)
                                for _ in range(i):
                                    desc_locator.press("ArrowDown")
                                desc_locator.press("Enter")
                                break

                    if not found:
                        desc_locator.press_sequentially(" ")

                except Exception:
                    desc_locator.press_sequentially(" ")

            else:
                desc_locator.press_sequentially(word + " ")

    except Exception as exception:
        logger.warning(
            "Could not type the description, pasting it as plain text: %s", exception
        )
        _clear(desc_locator)
        desc_locator.fill(saved_description)


def _clear(locator) -> None:
    """
    Clears the text of the element
    """
    locator.press("ControlOrMeta+A")
    locator.press("Backspace")


def _set_video(page: Page, path: str = "", num_retries: int = 3, **kwargs) -> None:
    """
    Sets the video to upload
    """
    logger.debug("Uploading video file")

    for attempt in range(1, num_retries + 1):
        try:
            upload_box = page.locator(f"xpath={config.selectors.upload.upload_video}")
            upload_box.set_input_files(path)

            # wait until a non-draggable image is found (process confirmation)
            process_confirmation = page.locator(
                f"xpath={config.selectors.upload.process_confirmation}"
            )
            process_confirmation.wait_for(
                state="attached", timeout=config.explicit_wait * 1000
            )
            return
        except PlaywrightTimeoutError:
            logger.warning(
                "%s was not processed within %ds (attempt %d of %d)",
                path,
                config.explicit_wait,
                attempt,
                num_retries,
            )
        except Exception as exception:
            raise FailedToUpload(exception)

    # posting still waits for processing to finish, so a slow video can succeed
    logger.warning("Continuing with %s before TikTok confirmed processing", path)


def _remove_cookies_window(page: Page) -> None:
    """
    Removes the cookies window if it is open
    """
    logger.debug("Removing cookies window")

    try:
        selector = f"{config.selectors.upload.cookies_banner.banner} >> {config.selectors.upload.cookies_banner.button} >> button"

        button = page.locator(selector).first
        _click_if_visible(button, timeout=5)

    except Exception:
        # a banner that never offers its button is removed instead; that
        # removal is best-effort too, since the banner may not exist at all
        try:
            page.evaluate(f"""
                const banner = document.querySelector("{config.selectors.upload.cookies_banner.banner}");
                if (banner) banner.remove();
            """)
        except Exception as e:
            logger.debug(f"Could not remove the cookies banner: {e}")


def _remove_split_window(page: Page) -> None:
    """
    Remove the split window if it is open
    """
    logger.debug("Removing split window")
    window_xpath = config.selectors.upload.split_window

    try:
        window = page.locator(f"xpath={window_xpath}")
        if not _click_if_visible(window, timeout=5):
            logger.debug("Split window not found")
    except PlaywrightTimeoutError:
        logger.debug("Split window not found or operation timed out")


def _expand_more_options(page: Page) -> None:
    """
    Opens the "Show more" section holding the interactivity and AI label options
    """
    show_more = page.locator(f"xpath={config.selectors.upload.show_more}").first
    if show_more.count() and show_more.is_visible():
        show_more.click(force=True)
        time.sleep(1)


def _set_interactivity(
    page: Page,
    comment: bool = True,
    stitch: bool = True,
    duet: bool = True,
    reuse_of_content: bool | None = None,
    *args,
    **kwargs,
) -> None:
    """
    Sets the interactivity settings of the video.

    TikTok Studio merged Duet and Stitch into a single "Reuse of content"
    checkbox, which follows `reuse_of_content`, else is allowed only when
    both `stitch` and `duet` are. The separate checkboxes are still set on
    the legacy form.
    """
    try:
        logger.debug("Setting interactivity settings")

        _expand_more_options(page)

        comment_box = page.locator(f"xpath={config.selectors.upload.comment}")
        reuse_box = page.locator(f"xpath={config.selectors.upload.reuse_of_content}")

        # force=True: a transient Studio toast over the checkbox would
        # otherwise make the click wait out its whole timeout
        if comment ^ comment_box.is_checked():
            comment_box.click(force=True)

        # checked with count(), which does not wait: is_checked() on a missing
        # checkbox waits out the whole default timeout first
        if reuse_box.count():
            allow_reuse = (
                reuse_of_content if reuse_of_content is not None else stitch and duet
            )
            if allow_reuse ^ reuse_box.is_checked():
                reuse_box.click(force=True)
        else:
            stitch_box = page.locator(f"xpath={config.selectors.upload.stitch}")
            duet_box = page.locator(f"xpath={config.selectors.upload.duet}")

            if stitch ^ stitch_box.is_checked():
                stitch_box.click(force=True)

            if duet ^ duet_box.is_checked():
                duet_box.click(force=True)

    except Exception as e:
        logger.warning("Could not set interactivity, posting with TikTok's: %s", e)


def _set_visibility(
    page: Page, visibility: Literal["everyone", "friends", "only_you"]
) -> None:
    """
    Sets the visibility/privacy of the video
    """
    try:
        logger.debug(f"Setting visibility to: {visibility}")

        dropdown_xpath = (
            "//div[@data-e2e='video_visibility_container']//button[@role='combobox']"
        )
        dropdown = page.locator(f"xpath={dropdown_xpath}")
        dropdown.click(force=True)  # see interactivity's force=True comment
        time.sleep(1.5)

        visibility_text_map = {
            "everyone": "Everyone",
            "friends": "Friends",
            "only_you": "Only you",
        }

        option_text = visibility_text_map.get(visibility, "Everyone")
        option_xpath = f"//div[@role='option' and contains(., '{option_text}')]"

        option = page.locator(f"xpath={option_xpath}")
        option.scroll_into_view_if_needed()
        time.sleep(0.5)
        option.click(force=True)

        logger.debug(f"Successfully set visibility to: {visibility}")

    except Exception as e:
        # carrying on would post a private video publicly
        raise FailedToUpload(f"Could not set visibility to {visibility}: {e}") from e


def _set_schedule_video(page: Page, schedule: datetime.datetime) -> None:
    """
    Sets the schedule of the video
    """
    logger.debug("Setting schedule")

    timezone_str = page.evaluate("Intl.DateTimeFormat().resolvedOptions().timeZone")
    driver_timezone = pytz.timezone(timezone_str)

    schedule = schedule.astimezone(driver_timezone)

    month = schedule.month
    day = schedule.day
    hour = schedule.hour
    minute = schedule.minute

    try:
        switch = page.locator(f"xpath={config.selectors.schedule.switch}")
        switch.click(force=True)  # see _set_interactivity's force=True comment
        _accept_schedule_consent(page)
        __date_picker(page, schedule.year, month, day)
        __time_picker(page, hour, minute)
    except Exception as e:
        raise FailedToUpload(f"Failed to set schedule: {e}") from e


def _accept_schedule_consent(page: Page) -> None:
    """
    Accepts the one-time "Allow your video to be saved for scheduled
    posting?" dialog shown after the Schedule radio is picked. A no-op when
    it does not appear (already accepted this session); the date picker's
    own wait surfaces a real failure.
    """
    try:
        allow_btn = page.locator(f"xpath={config.selectors.schedule.consent_allow}")
        # Playwright ignores is_visible(timeout=...): wait for the dialog to appear instead.
        allow_btn.first.wait_for(state="visible", timeout=3000)
        allow_btn.first.click(force=True)
    except Exception:
        pass


def __date_picker(page: Page, year: int, month: int, day: int) -> None:
    # The date is a combobox that opens a calendar dialog; the month is walked
    # with its arrows by the distance in months (the year counts, so December
    # to January goes forward).
    logger.debug("Picking date")

    date_picker = page.locator(f"xpath={config.selectors.schedule.date_picker}")
    date_picker.click(force=True)  # see _set_interactivity's force=True comment

    calendar = page.locator(f"xpath={config.selectors.schedule.calendar}")
    calendar.wait_for(state="visible")

    shown_month = datetime.datetime.strptime(
        page.locator(f"xpath={config.selectors.schedule.calendar_month}").inner_text(),
        "%B",
    ).month
    shown_year = int(
        page.locator(f"xpath={config.selectors.schedule.calendar_year}").inner_text()
    )
    months_ahead = (year - shown_year) * 12 + (month - shown_month)
    arrows = page.locator(f"xpath={config.selectors.schedule.calendar_arrows}")
    for _ in range(abs(months_ahead)):
        (arrows.last if months_ahead > 0 else arrows.first).click(force=True)
        time.sleep(0.3)

    valid_days = page.locator(
        f"xpath={config.selectors.schedule.calendar_valid_days}"
    ).all()

    day_to_click = None
    for day_option in valid_days:
        if int(day_option.inner_text()) == day:
            day_to_click = day_option
            break
    if day_to_click:
        day_to_click.click(force=True)
    else:
        raise Exception("Day not found in calendar")

    __verify_date_picked_is_correct(page, year, month, day)


def __verify_date_picked_is_correct(
    page: Page, year: int, month: int, day: int
) -> None:
    # the trigger shows "Nov 2, 2026"
    date_selected = page.locator(
        f"xpath={config.selectors.schedule.date_picker_text}"
    ).inner_text()
    picked = datetime.datetime.strptime(date_selected.strip(), "%b %d, %Y")

    if (picked.year, picked.month, picked.day) == (year, month, day):
        logger.debug("Date picked correctly")
    else:
        msg = (
            f"Something went wrong with the date picker, expected "
            f"{year}-{month:02d}-{day:02d} but got {picked:%Y-%m-%d}"
        )
        raise Exception(msg)


def __time_picker(page: Page, hour: int, minute: int) -> None:
    # The time is a combobox that opens two listboxes; each option is picked by
    # its own label ("Hours 14", "Minutes 25"), not by its index. Minutes are
    # offered in steps of five.
    logger.debug("Picking time")

    time_picker = page.locator(f"xpath={config.selectors.schedule.time_picker}")
    time_picker.click(force=True)  # see _set_interactivity's force=True comment

    time_picker_container = page.locator(
        f"xpath={config.selectors.schedule.time_picker_container}"
    )
    time_picker_container.wait_for(state="visible")

    hour_to_click = page.locator(
        "xpath=" + config.selectors.schedule.timepicker_hour.format(value=f"{hour:02d}")
    )
    minute_to_click = page.locator(
        "xpath="
        + config.selectors.schedule.timepicker_minute.format(value=f"{minute:02d}")
    )

    hour_to_click.scroll_into_view_if_needed()
    time.sleep(0.5)
    hour_to_click.click(force=True)

    minute_to_click.scroll_into_view_if_needed()
    time.sleep(0.5)
    minute_to_click.click(force=True)

    page.keyboard.press("Escape")  # close the wheel
    time.sleep(0.5)

    __verify_time_picked_is_correct(page, hour, minute)


def __verify_time_picked_is_correct(page: Page, hour: int, minute: int) -> None:
    # the trigger shows "14:25"
    time_selected = page.locator(
        f"xpath={config.selectors.schedule.time_picker_text}"
    ).inner_text()
    time_selected_hour = int(time_selected.split(":")[0])
    time_selected_minute = int(time_selected.split(":")[1])

    if time_selected_hour == hour and time_selected_minute == minute:
        logger.debug("Time picked correctly")
    else:
        msg = (
            f"Something went wrong with the time picker, "
            f"expected {hour:02d}:{minute:02d} "
            f"but got {time_selected_hour:02d}:{time_selected_minute:02d}"
        )
        raise Exception(msg)


def _post_video(page: Page, skip_restricted: bool = False) -> None:
    """
    Posts the video
    """
    logger.debug("Clicking the post button")

    _dismiss_blocking_modals(page)

    post_btn = page.locator(f"xpath={config.selectors.upload.post}")
    try:

        def is_enabled():
            return post_btn.get_attribute("data-disabled") == "false"

        for _ in range(int(config.uploading_wait / 2)):
            if is_enabled():
                break
            time.sleep(2)

        # the content check has finished by the time posting is enabled
        if skip_restricted and _content_is_restricted(page):
            raise ContentRestricted()

        post_btn.scroll_into_view_if_needed()
        post_btn.click()

    except ContentRestricted:
        raise
    except Exception:
        logger.debug("Trying to click on the button again (fallback)")
        page.evaluate('document.querySelector(".TUXButton--primary").click()')

    # "Continue to post?" asks for a second confirmation after the click
    # (upstream issue #225); it animates in, so wait for it rather than look
    try:
        post_now = page.locator(f"xpath={config.selectors.upload.post_now}").first
        _click_if_visible(post_now, timeout=5)
    except Exception:
        pass

    _wait_for_post_result(page)

    logger.debug("Video posted successfully")


def _wait_for_post_result(page: Page) -> None:
    """
    Waits for TikTok to confirm the post, either with its "uploaded" message or
    by sending the browser to the content list, and fails at once if TikTok
    reports "Something went wrong" (upstream issue #238) instead of waiting
    out the whole timeout
    """
    confirmation = page.locator(f"xpath={config.selectors.upload.post_confirmation}")
    error = page.locator(f"xpath={config.selectors.upload.post_error}")

    deadline = time.monotonic() + config.explicit_wait
    while time.monotonic() < deadline:
        if confirmation.count() or POSTED_URL_FRAGMENT in page.url:
            return
        if error.count() and error.first.is_visible():
            raise FailedToUpload(
                f"TikTok rejected the post: {error.first.inner_text()}"
            )
        time.sleep(1)

    raise FailedToUpload(
        f"TikTok did not confirm the post within {config.explicit_wait} seconds"
    )


def _content_is_restricted(page: Page) -> bool:
    """
    Whether TikTok's content check warns that the video may be restricted
    """
    warning = page.locator(f"xpath={config.selectors.upload.content_restricted}")
    return any(w.is_visible() for w in warning.all())


def _set_ai_label(page: Page, ai_label: bool) -> None:
    """
    Sets TikTok's "AI-generated content" label, which lives under "Show more"
    """
    logger.debug(f"Setting AI-generated content label: {ai_label}")

    try:
        _expand_more_options(page)

        switch = page.locator(f"xpath={config.selectors.upload.ai_label_switch}")
        wanted = "checked" if ai_label else "unchecked"
        if switch.get_attribute("data-state") == wanted:
            return

        switch.click(force=True)
        if ai_label:
            # turning the label on asks for confirmation first
            page.locator(f"xpath={config.selectors.upload.ai_label_confirm}").click()

        for _ in range(10):
            if switch.get_attribute("data-state") == wanted:
                return
            time.sleep(0.5)
        raise Exception(f"the switch did not change to {wanted}")
    except Exception as e:
        # the label was asked for explicitly, so do not post with it wrong
        msg = f"Failed to set the AI-generated content label: {e}"
        raise FailedToUpload(msg) from e


def _save_draft(page: Page) -> None:
    """
    Saves the video as a draft instead of posting it
    """
    logger.debug("Clicking the save draft button")

    _dismiss_blocking_modals(page)

    draft_btn = page.locator(f"xpath={config.selectors.upload.save_draft}")

    # the button stays disabled until the video has finished uploading
    for _ in range(int(config.uploading_wait / 2)):
        if draft_btn.get_attribute("data-disabled") != "true":
            break
        time.sleep(2)

    draft_btn.scroll_into_view_if_needed()
    draft_btn.click()

    # the upload form closes once the draft is saved
    draft_btn.wait_for(state="detached", timeout=config.explicit_wait * 1000)

    logger.debug("Video saved as draft")


def _set_sound(page: Page, sound_name: str, sound_artist: str | None = None) -> None:
    """
    Picks a sound from TikTok's library: the first result whose title matches
    `sound_name` (and whose artist contains `sound_artist`, if given), else
    the first result. A sound that cannot be set is logged and skipped.
    """
    logger.debug(f"Setting sound: {sound_name}")
    selectors = config.selectors.upload.sound

    try:
        add_sound_btn = page.locator(f"xpath={selectors.add_sound_button}")
        add_sound_btn.wait_for(state="visible", timeout=config.implicit_wait * 1000)
        add_sound_btn.click()

        search_input = page.locator(f"xpath={selectors.search_input}")
        search_input.wait_for(state="visible", timeout=config.implicit_wait * 1000)
        search_input.fill(sound_name)
        search_input.press("Enter")  # also closes the autocomplete suggestions

        items = page.locator(f"xpath={selectors.result_items}")
        items.first.wait_for(state="visible", timeout=config.implicit_wait * 1000)
        time.sleep(1)  # results keep arriving after the first one renders

        matched = _match_sound(items.all(), sound_name, sound_artist)
        if matched is None:
            logger.warning(
                "No exact match for sound '%s'%s, using the first result",
                sound_name,
                f" by '{sound_artist}'" if sound_artist else "",
            )
            matched = items.first

        matched.locator(f"xpath={selectors.result_add_button}").click()

        save_btn = page.locator(f"xpath={selectors.save_button}")
        save_btn.wait_for(state="visible", timeout=config.implicit_wait * 1000)
        save_btn.click()
        save_btn.wait_for(state="hidden", timeout=config.implicit_wait * 1000)

        logger.debug(f"Sound '{sound_name}' selected")

    except Exception as e:
        logger.warning(
            "Failed to set sound '%s', posting without it: %s", sound_name, e
        )
        try:
            page.keyboard.press("Escape")
        except Exception:
            pass


def _match_sound(
    items: list[Locator], sound_name: str, sound_artist: str | None
) -> Locator | None:
    """
    The first sound result titled `sound_name` whose artist contains
    `sound_artist` (case-insensitive), or None
    """
    selectors = config.selectors.upload.sound
    target_title = sound_name.strip().lower()
    target_artist = sound_artist.strip().lower() if sound_artist else None

    for item in items:
        try:
            title = item.locator(f"xpath={selectors.result_title}").inner_text()
            if title.strip().lower() != target_title:
                continue
            if target_artist:
                artist = item.locator(f"xpath={selectors.result_artist}").inner_text()
                if target_artist not in artist.lower():
                    continue
            return item
        except Exception:
            continue
    return None


def _add_product_link(page: Page, product_id: str) -> None:
    """
    Adds the product link
    """
    logger.debug(f"Attempting to add product link for ID: {product_id}...")
    try:
        add_link_button = page.locator(
            "//button[contains(@class, 'Button__root') and contains(., 'Add')]"
        )
        add_link_button.click()
        time.sleep(1)

        try:
            first_next = page.locator(
                "//button[contains(@class, 'TUXButton--primary') and .//div[text()='Next']]"
            )
            if first_next.is_visible(timeout=3000):
                first_next.click()
                time.sleep(1)
        except Exception:
            pass

        search_input = page.locator("//input[@placeholder='Search products']")
        search_input.fill(product_id)
        search_input.press("Enter")
        time.sleep(3)

        product_radio = page.locator(
            f"//tr[.//span[contains(text(), '{product_id}')] or .//div[contains(text(), '{product_id}')]]//input[@type='radio' and contains(@class, 'TUXRadioStandalone-input')]"
        )
        product_radio.click()
        time.sleep(1)

        # the product table overlaps the first step's (hidden) Next button, so
        # the visible one is picked from the modal footer (upstream issue #230)
        second_next = page.locator(
            "//div[contains(@class, 'common-modal-footer')]//button[contains(@class, 'TUXButton--primary') and .//div[text()='Next']]"
        )
        second_next.scroll_into_view_if_needed()
        second_next.click()
        time.sleep(1)

        final_add = page.locator(
            "//button[contains(@class, 'TUXButton--primary') and .//div[text()='Add']]"
        )
        final_add.click()

        final_add.wait_for(state="hidden")

    except Exception as e:
        logger.warning(
            "Could not add product %s, posting without it: %s", product_id, e
        )


def _set_cover(page: Page, cover_path: str) -> None:
    """
    Adds a custom cover
    """
    logger.debug(f"Attempting to add custom cover: {cover_path}...")
    try:
        if not _check_valid_cover_path(cover_path):
            raise Exception("Invalid cover image file path")

        if _set_cover_studio(page, cover_path):
            return

        preview_loc = page.locator(
            f"xpath={config.selectors.upload.cover.cover_preview}"
        )
        current_cover_src = preview_loc.get_attribute("src")

        edit_cover_btn = page.locator(
            f"xpath={config.selectors.upload.cover.edit_cover_button}"
        )
        edit_cover_btn.click()

        upload_tab = page.locator(
            f"xpath={config.selectors.upload.cover.upload_cover_tab}"
        )
        upload_tab.click()

        upload_box = page.locator(f"xpath={config.selectors.upload.cover.upload_cover}")
        upload_box.set_input_files(cover_path)

        confirm_btn = page.locator(
            f"xpath={config.selectors.upload.cover.upload_confirmation}"
        )
        confirm_btn.click()

        def check_src_change():
            return preview_loc.get_attribute("src") != current_cover_src

        for _ in range(20):
            if check_src_change():
                break
            time.sleep(0.5)

    except Exception as e:
        logger.warning("Could not set the cover, posting with TikTok's: %s", e)
        try:
            exit_icon = page.locator(
                f"xpath={config.selectors.upload.cover.exit_cover_container}"
            )
            if exit_icon.is_visible():
                exit_icon.click()
        except Exception:
            pass


def _set_cover_studio(page: Page, cover_path: str) -> bool:
    """
    Sets the cover through TikTok Studio's "Edit cover" modal. Returns False,
    with the modal closed again, when that flow is not available, so the
    legacy flow can be tried instead.
    """
    selectors = config.selectors.upload.cover
    try:
        edit_cover = page.locator(f"xpath={selectors.studio_edit_cover}").last
        if not _click_if_visible(edit_cover, timeout=5):
            return False

        upload_input = page.locator(f"xpath={selectors.studio_upload_cover}").last
        upload_input.wait_for(state="attached", timeout=config.implicit_wait * 1000)
        upload_input.set_input_files(cover_path)

        save_btn = page.locator(f"xpath={selectors.studio_save}").first
        save_btn.wait_for(state="visible", timeout=config.implicit_wait * 1000)
        # Save stays disabled until the image has been processed
        for _ in range(20):
            if save_btn.is_enabled():
                break
            time.sleep(0.5)
        save_btn.click()
        save_btn.wait_for(state="hidden", timeout=config.implicit_wait * 1000)

        logger.debug("Cover set through the Studio modal")
        return True
    except Exception as e:
        logger.debug(f"Studio cover flow failed, trying the legacy flow: {e}")
        try:
            cancel = page.locator(f"xpath={selectors.studio_cancel}").first
            if cancel.is_visible():
                cancel.click()
        except Exception:
            pass
        return False


def _check_valid_path(path: object) -> bool:
    # descriptions and schedules are checked too while a video dict is sorted out
    if not isinstance(path, str):
        return False
    return exists(path) and path.split(".")[-1] in config.supported_file_types


def _check_valid_cover_path(path: str) -> bool:
    return exists(path) and path.split(".")[-1] in config.supported_image_file_types


def _get_valid_schedule_minute(
    schedule: datetime.datetime, valid_multiple
) -> datetime.datetime:
    if _is_valid_schedule_minute(schedule.minute, valid_multiple):
        return schedule
    else:
        return _set_valid_schedule_minute(schedule, valid_multiple)


def _is_valid_schedule_minute(minute: int, valid_multiple) -> bool:
    if minute % valid_multiple != 0:
        return False
    else:
        return True


def _set_valid_schedule_minute(
    schedule: datetime.datetime, valid_multiple: int
) -> datetime.datetime:
    minute = schedule.minute
    remainder = minute % valid_multiple
    integers_to_valid_multiple = 5 - remainder
    schedule += datetime.timedelta(minutes=integers_to_valid_multiple)
    return schedule


def _check_valid_schedule(schedule: datetime.datetime) -> bool:
    valid_tiktok_minute_multiple = 5
    margin_to_complete_upload_form = 5
    datetime_utc_now = datetime.datetime.now(datetime.timezone.utc)
    min_datetime_tiktok_valid = datetime_utc_now + datetime.timedelta(minutes=15)
    min_datetime_tiktok_valid += datetime.timedelta(
        minutes=margin_to_complete_upload_form
    )
    max_datetime_tiktok_valid = datetime_utc_now + datetime.timedelta(days=10)
    if schedule < min_datetime_tiktok_valid or schedule > max_datetime_tiktok_valid:
        return False
    elif not _is_valid_schedule_minute(schedule.minute, valid_tiktok_minute_multiple):
        return False
    else:
        return True


def _convert_videos_dict(
    videos_list_of_dictionaries: list[dict[str, Any]],
) -> list[VideoDict]:
    if not videos_list_of_dictionaries:
        raise RuntimeError("No videos to upload")

    valid_path = config.valid_path_names
    valid_description = config.valid_descriptions

    correct_path = valid_path[0]
    correct_description = valid_description[0]

    def intersection(lst1, lst2):
        return list(set(lst1) & set(lst2))

    return_list: list[VideoDict] = []
    for elem in videos_list_of_dictionaries:
        elem = {k.strip().lower(): v for k, v in elem.items()}
        keys = elem.keys()
        path_intersection = intersection(valid_path, keys)
        description_intersection = intersection(valid_description, keys)

        if path_intersection:
            path = elem[path_intersection.pop()]
            if not _check_valid_path(path):
                raise RuntimeError("Invalid path: " + path)
            elem[correct_path] = path
        else:
            for _, value in elem.items():
                if _check_valid_path(value):
                    elem[correct_path] = value
                    break
            else:
                raise RuntimeError("Path not found in dictionary: " + str(elem))

        if description_intersection:
            elem[correct_description] = elem[description_intersection.pop()]
        else:
            for key, value in elem.items():
                # a known option (visibility, cover, sound_name...) is never
                # the description, only a value under an unrecognised key
                if (
                    key not in VideoDict.__annotations__
                    and isinstance(value, str)
                    and not _check_valid_path(value)
                ):
                    elem[correct_description] = value
                    break
            else:
                elem[correct_description] = ""

        return_list.append(elem)  # type: ignore

    return return_list


class DescriptionTooLong(Exception):
    def __init__(self, message: str | None = None):
        super().__init__(message or self.__doc__)


class FailedToUpload(Exception):
    def __init__(self, message=None):
        super().__init__(message or self.__doc__)


class ContentRestricted(FailedToUpload):
    """
    TikTok's content check warned that the video may be restricted, so it was
    not posted (skip_restricted)
    """
