"""
`tiktok_uploader` module for uploading videos to TikTok

Key Functions
-------------
upload_video : Uploads a single TikTok video
upload_videos : Uploads multiple TikTok videos
"""

import datetime
import threading
import time
from collections.abc import Callable
from os.path import abspath, exists
from typing import Any, Literal

import pytz
from playwright.sync_api import Page, expect, TimeoutError as PlaywrightTimeoutError

from tiktok_uploader import config, logger
from tiktok_uploader.auth import AuthBackend
from tiktok_uploader.browsers import get_browser
# from tiktok_uploader.proxy_auth_extension.proxy_auth_extension import proxy_is_working # No longer needed
from tiktok_uploader.types import Cookie, ProxyDict, VideoDict
from tiktok_uploader.utils import bold, green, red


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
    *args,
    **kwargs,
) -> list[VideoDict]:
    """
    Uploads a single TikTok video.

    Consider using `upload_videos` if using multiple videos
    """
    auth = AuthBackend(
        username=username,
        password=password,
        cookies=cookies,
        cookies_list=cookies_list,
        cookies_str=cookies_str,
        sessionid=sessionid,
    )

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

    return upload_videos(
        [video_dict],
        auth,
        proxy,
        *args,
        **kwargs,
    )


def upload_videos(
    videos: list[VideoDict],
    auth: AuthBackend,
    proxy: ProxyDict | None = None,
    browser: Literal["chrome", "safari", "chromium", "edge", "firefox"] = "chrome",
    browser_agent: Page | None = None,
    on_complete: Callable[[VideoDict], None] | None = None,
    headless: bool = False,
    num_retries: int = 1,
    skip_split_window: bool = False,
    *args,
    **kwargs,
) -> list[VideoDict]:
    """
    Uploads multiple videos to TikTok
    """
    videos = _convert_videos_dict(videos)  # type: ignore

    if videos and len(videos) > 1:
        logger.debug("Uploading %d videos", len(videos))

    if not browser_agent:  # user-specified browser agent
        logger.debug(
            "Create a %s browser instance %s",
            browser,
            "in headless mode" if headless else "",
        )
        page = get_browser(browser, headless=headless, proxy=proxy, *args, **kwargs)
    else:
        logger.debug("Using user-defined browser agent")
        page = browser_agent

    # Proxy check is handled by Playwright launch, if it fails it throws error usually.
    # We can skip explicit proxy check for now or implement a simple check.
    
    page = auth.authenticate_agent(page)

    failed = []
    # uploads each video
    for video in videos:
        try:
            path = abspath(video.get("path", "."))
            description = video.get("description", "")
            schedule = video.get("schedule", None)
            product_id = video.get("product_id", None)
            cover_path = video.get("cover", None)
            if cover_path is not None:
                cover_path = abspath(cover_path)

            visibility = video.get("visibility", "everyone")

            logger.debug(
                "Posting %s%s",
                bold(video.get("path", "")),
                (
                    f"\n{' ' * 15}with description: {bold(description)}"
                    if description
                    else ""
                ),
            )

            # Video must be of supported type
            if not _check_valid_path(path):
                print(f"{path} is invalid, skipping")
                failed.append(video)
                continue

            # Video must have a valid datetime for tiktok's scheduler
            if schedule:
                timezone = pytz.UTC
                if schedule.tzinfo is None:
                    schedule = schedule.astimezone(timezone)
                elif (utc_offset := schedule.utcoffset()) is not None and int(
                    utc_offset.total_seconds()
                ) == 0:  # Equivalent to UTC
                    schedule = timezone.localize(schedule)
                else:
                    print(
                        f"{schedule} is invalid, the schedule datetime must be naive or aware with UTC timezone, skipping"
                    )
                    failed.append(video)
                    continue

                valid_tiktok_minute_multiple = 5
                schedule = _get_valid_schedule_minute(
                    schedule, valid_tiktok_minute_multiple
                )
                if not _check_valid_schedule(schedule):
                    print(
                        f"{schedule} is invalid, the schedule datetime must be as least 20 minutes in the future, and a maximum of 10 days, skipping"
                    )
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
                headless,
                *args,
                **kwargs,
            )
        except Exception as exception:
            logger.error("Failed to upload %s", path)
            logger.error(exception)
            failed.append(video)
            import traceback
            traceback.print_exc()

        if on_complete and callable(on_complete):  # calls the user-specified on-complete function
            on_complete(video)

    if config.quit_on_end:
        page.context.browser.close()

    return failed


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
    **kwargs,
) -> None:
    """
    Actually uploads each video
    """
    _go_to_upload(page)
    _remove_cookies_window(page)

    _set_video(page, path=path, num_retries=num_retries, **kwargs)

    if cover_path:
        _set_cover(page, cover_path)
    if not skip_split_window:
        _remove_split_window(page)
    _set_interactivity(page, **kwargs)
    _set_description(page, description)
    if visibility != "everyone":
        _set_visibility(page, visibility)
    if schedule:
        _set_schedule_video(page, schedule)
    if product_id:
        _add_product_link(page, product_id)
    _post_video(page)


def _go_to_upload(page: Page) -> None:
    """
    Navigates to the upload page
    """
    logger.debug(green("Navigating to upload page"))

    if page.url != config.paths.upload:
        page.goto(str(config.paths.upload))
    else:
        # refresh
        page.reload()
        # TODO: handle alert if any (Playwright auto-dismisses dialogs usually, or we can handle)
        page.on("dialog", lambda dialog: dialog.accept())

    # waits for the root to load
    page.wait_for_selector("#root", timeout=config.explicit_wait * 1000)


def _set_description(page: Page, description: str) -> None:
    """
    Sets the description of the video
    """
    if description is None:
        return

    logger.debug(green("Setting description"))

    # Remove any characters outside the BMP range (emojis, etc) & Fix accents
    description = description.encode("utf-8", "ignore").decode("utf-8")
    saved_description = description

    try:
        desc_locator = page.locator(f"xpath={config.selectors.upload.description}")
        desc_locator.wait_for(state="visible", timeout=config.implicit_wait * 1000)
        
        desc_locator.click()
        
        # Wait until it populates or is ready
        # In Playwright, click waits for actionability.

        # Clear existing text
        # desc_locator.fill("") # .fill() usually clears but contenteditable might be tricky
        # For contenteditable, we can select all and delete
        desc_locator.press("Control+A") # Or Meta+A on mac, Playwright handles 'Control' as Meta on mac usually?
        # Actually Playwright has 'Meta'.
        # Safest generic clear for contenteditable:
        desc_locator.press("Control+A")
        desc_locator.press("Backspace")
        
        # Wait for empty?
        # expect(desc_locator).to_have_text("")

        desc_locator.click()
        time.sleep(1)

        words = description.split(" ")
        for word in words:
            if word[0] == "#":
                desc_locator.press_sequentially(word, delay=50)
                # desc_locator.press("Space")
                # Remove space if needed or just space to trigger tag
                # The original code: sends word, sends space+backspace, waits for mention box, then enter.
                
                # Logic from original:
                # desc.send_keys(word)
                # desc.send_keys(" " + Keys.BACKSPACE)
                # wait for mention box
                # enter
                
                # Playwright:
                # desc_locator.type(word) # deprecated
                desc_locator.press_sequentially(word)
                time.sleep(0.5)
                
                # We need to trigger the hashtag menu.
                # Sometimes just typing #tag is enough.
                
                mention_box = page.locator(f"xpath={config.selectors.upload.mention_box}")
                try:
                    mention_box.wait_for(state="visible", timeout=config.add_hashtag_wait * 1000)
                    desc_locator.press("Enter")
                except:
                    # If no mention box, just continue?
                    pass
                
                # Add space if needed? Original code adds space then backspace then enter.
                # The enter likely confirms the tag.
                
            elif word[0] == "@":
                logger.debug(green("- Adding Mention: " + word))
                desc_locator.press_sequentially(word)
                # desc_locator.press("Space")
                time.sleep(1)
                # desc_locator.press("Backspace")

                mention_box_user_id = page.locator(f"xpath={config.selectors.upload.mention_box_user_id}")
                try:
                    mention_box_user_id.first.wait_for(state="visible", timeout=5000)
                    
                    # Search for match
                    # This is tricky in Playwright because we need to iterate elements
                    found = False
                    user_ids = mention_box_user_id.all()
                    
                    target_username = word[1:].lower()
                    
                    for i, user_el in enumerate(user_ids):
                        if user_el.is_visible():
                            text = user_el.inner_text().split(" ")[0]
                            if text.lower() == target_username:
                                found = True
                                print("Matching User found : Clicking User")
                                # Navigate down to it?
                                for _ in range(i):
                                    desc_locator.press("ArrowDown")
                                desc_locator.press("Enter")
                                break
                    
                    if not found:
                         desc_locator.press_sequentially(" ")
                         
                except:
                     desc_locator.press_sequentially(" ")

            else:
                desc_locator.press_sequentially(word + " ")

    except Exception as exception:
        print("Failed to set description: ", exception)
        # fallback
        _clear(desc_locator)
        desc_locator.fill(saved_description)


def _clear(locator) -> None:
    """
    Clears the text of the element
    """
    locator.press("Control+A")
    locator.press("Backspace")


def _set_video(
    page: Page, path: str = "", num_retries: int = 3, **kwargs
) -> None:
    """
    Sets the video to upload
    """
    logger.debug(green("Uploading video file"))

    for _ in range(num_retries):
        try:
            upload_box = page.locator(f"xpath={config.selectors.upload.upload_video}")
            upload_box.set_input_files(path)

            # wait until a non-draggable image is found (process confirmation)
            process_confirmation = page.locator(f"xpath={config.selectors.upload.process_confirmation}")
            process_confirmation.wait_for(state="attached", timeout=config.explicit_wait * 1000)
            return
        except PlaywrightTimeoutError as exception:
            print("TimeoutException occurred:\n", exception)
        except Exception as exception:
            print(exception)
            raise FailedToUpload(exception)


def _remove_cookies_window(page: Page) -> None:
    """
    Removes the cookies window if it is open
    """
    logger.debug(green("Removing cookies window"))
    
    # Playwright handles shadow DOM automatically
    # banner = "tiktok-cookie-banner"
    # button = "div.button-wrapper"
    
    # We can try to find the button inside the banner
    try:
        # Selector: tiktok-cookie-banner >> div.button-wrapper button
        # We want the "Decline all" button usually? 
        # Original code finds "button" in "div.button-wrapper".
        # Let's assume the first button or specific text.
        
        # We can construct a selector that pierces shadow DOM
        selector = f"{config.selectors.upload.cookies_banner.banner} >> {config.selectors.upload.cookies_banner.button} >> button"
        
        button = page.locator(selector).first
        if button.is_visible(timeout=5000):
            button.click()
            
    except Exception:
        # Remove it via JS if failing
        page.evaluate(f"""
            const banner = document.querySelector("{config.selectors.upload.cookies_banner.banner}");
            if (banner) banner.remove();
        """)


def _remove_split_window(page: Page) -> None:
    """
    Remove the split window if it is open
    """
    logger.debug(green("Removing split window"))
    window_xpath = config.selectors.upload.split_window

    try:
        window = page.locator(f"xpath={window_xpath}")
        if window.is_visible(timeout=config.implicit_wait * 1000):
            window.click()
    except PlaywrightTimeoutError:
        logger.debug(red("Split window not found or operation timed out"))


def _set_interactivity(
    page: Page,
    comment: bool = True,
    stitch: bool = True,
    duet: bool = True,
    *args,
    **kwargs,
) -> None:
    """
    Sets the interactivity settings of the video
    """
    try:
        logger.debug(green("Setting interactivity settings"))

        comment_box = page.locator(f"xpath={config.selectors.upload.comment}")
        stitch_box = page.locator(f"xpath={config.selectors.upload.stitch}")
        duet_box = page.locator(f"xpath={config.selectors.upload.duet}")

        # Checkboxes in Playwright
        # We need to know if they are checked.
        # .is_checked() works if input type=checkbox.
        # XPATH points to 'input'.
        
        if comment ^ comment_box.is_checked():
            comment_box.click()

        if stitch ^ stitch_box.is_checked():
            stitch_box.click()

        if duet ^ duet_box.is_checked():
            duet_box.click()

    except Exception as _:
        logger.error("Failed to set interactivity settings")


def _set_visibility(
    page: Page, visibility: Literal["everyone", "friends", "only_you"]
) -> None:
    """
    Sets the visibility/privacy of the video
    """
    try:
        logger.debug(green(f"Setting visibility to: {visibility}"))

        dropdown_xpath = (
            "//div[@data-e2e='video_visibility_container']//button[@role='combobox']"
        )
        dropdown = page.locator(f"xpath={dropdown_xpath}")
        dropdown.click()
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
        option.click()

        logger.debug(green(f"Successfully set visibility to: {visibility}"))

    except Exception as e:
        logger.error(red(f"Failed to set visibility: {e}"))


def _set_schedule_video(page: Page, schedule: datetime.datetime) -> None:
    """
    Sets the schedule of the video
    """
    logger.debug(green("Setting schedule"))

    # Timezone handling
    # Playwright's page timezone can be retrieved via evaluate
    timezone_str = page.evaluate("Intl.DateTimeFormat().resolvedOptions().timeZone")
    driver_timezone = pytz.timezone(timezone_str)
    
    schedule = schedule.astimezone(driver_timezone)

    month = schedule.month
    day = schedule.day
    hour = schedule.hour
    minute = schedule.minute

    try:
        switch = page.locator(f"xpath={config.selectors.schedule.switch}")
        switch.click()
        __date_picker(page, month, day)
        __time_picker(page, hour, minute)
    except Exception as e:
        msg = f"Failed to set schedule: {e}"
        logger.error(red(msg))
        raise FailedToUpload()


def __date_picker(page: Page, month: int, day: int) -> None:
    logger.debug(green("Picking date"))

    date_picker = page.locator(f"xpath={config.selectors.schedule.date_picker}")
    date_picker.click()

    calendar = page.locator(f"xpath={config.selectors.schedule.calendar}")
    calendar.wait_for(state="visible")

    calendar_month = page.locator(f"xpath={config.selectors.schedule.calendar_month}").inner_text()
    n_calendar_month = datetime.datetime.strptime(calendar_month, "%B").month
    
    if n_calendar_month != month:
        arrows = page.locator(f"xpath={config.selectors.schedule.calendar_arrows}")
        if n_calendar_month < month:
            # Next month (last arrow)
            arrows.last.click()
        else:
            # Prev month (first arrow)
            arrows.first.click()
            
    valid_days = page.locator(f"xpath={config.selectors.schedule.calendar_valid_days}").all()

    day_to_click = None
    for day_option in valid_days:
        if int(day_option.inner_text()) == day:
            day_to_click = day_option
            break
    if day_to_click:
        day_to_click.click()
    else:
        raise Exception("Day not found in calendar")

    __verify_date_picked_is_correct(page, month, day)


def __verify_date_picked_is_correct(page: Page, month: int, day: int) -> None:
    date_selected = page.locator(f"xpath={config.selectors.schedule.date_picker}").inner_text()
    date_selected_month = int(date_selected.split("-")[1])
    date_selected_day = int(date_selected.split("-")[2])

    if date_selected_month == month and date_selected_day == day:
        logger.debug(green("Date picked correctly"))
    else:
        msg = f"Something went wrong with the date picker, expected {month}-{day} but got {date_selected_month}-{date_selected_day}"
        logger.error(msg)
        raise Exception(msg)


def __time_picker(page: Page, hour: int, minute: int) -> None:
    logger.debug(green("Picking time"))

    time_picker = page.locator(f"xpath={config.selectors.schedule.time_picker}")
    time_picker.click()

    time_picker_container = page.locator(f"xpath={config.selectors.schedule.time_picker_container}")
    time_picker_container.wait_for(state="visible")

    hour_options = page.locator(f"xpath={config.selectors.schedule.timepicker_hours}")
    minute_options = page.locator(f"xpath={config.selectors.schedule.timepicker_minutes}")

    # Note: nth(index) is 0-based
    hour_to_click = hour_options.nth(hour)
    minute_option_correct_index = int(minute / 5)
    minute_to_click = minute_options.nth(minute_option_correct_index)

    hour_to_click.scroll_into_view_if_needed()
    time.sleep(0.5)
    hour_to_click.click()

    minute_to_click.scroll_into_view_if_needed()
    time.sleep(0.5)
    minute_to_click.click()

    # click somewhere else
    time_picker.click()
    time.sleep(0.5)
    
    __verify_time_picked_is_correct(page, hour, minute)


def __verify_time_picked_is_correct(page: Page, hour: int, minute: int) -> None:
    time_selected = page.locator(f"xpath={config.selectors.schedule.time_picker_text}").inner_text()
    time_selected_hour = int(time_selected.split(":")[0])
    time_selected_minute = int(time_selected.split(":")[1])

    if time_selected_hour == hour and time_selected_minute == minute:
        logger.debug(green("Time picked correctly"))
    else:
        msg = (
            f"Something went wrong with the time picker, "
            f"expected {hour:02d}:{minute:02d} "
            f"but got {time_selected_hour:02d}:{time_selected_minute:02d}"
        )
        raise Exception(msg)


def _post_video(page: Page) -> None:
    """
    Posts the video
    """
    logger.debug(green("Clicking the post button"))

    # Wait for post button to be enabled
    post_btn = page.locator(f"xpath={config.selectors.upload.post}")
    try:
        # custom wait
        def is_enabled():
            return post_btn.get_attribute("data-disabled") == "false"
            
        # Poll for enabled
        for _ in range(int(config.uploading_wait / 2)):
             if is_enabled():
                 break
             time.sleep(2)
             
        post_btn.scroll_into_view_if_needed()
        post_btn.click()
        
    except Exception:
        logger.debug(green("Trying to click on the button again (fallback)"))
        page.evaluate('document.querySelector(".TUXButton--primary").click()')

    # 'Post now' button handling
    try:
        post_now = page.locator(f"xpath={config.selectors.upload.post_now}")
        if post_now.is_visible(timeout=5000):
            post_now.click()
    except Exception:
        pass

    # Confirmation
    post_confirmation = page.locator(f"xpath={config.selectors.upload.post_confirmation}")
    post_confirmation.wait_for(state="attached", timeout=config.explicit_wait * 1000)

    logger.debug(green("Video posted successfully"))


def _add_product_link(page: Page, product_id: str) -> None:
    """
    Adds the product link
    """
    logger.debug(green(f"Attempting to add product link for ID: {product_id}..."))
    try:
        # Step 1
        add_link_button = page.locator("//button[contains(@class, 'Button__root') and contains(., 'Add')]")
        add_link_button.click()
        time.sleep(1)

        # Step 2: Next in modal
        try:
             first_next = page.locator("//button[contains(@class, 'TUXButton--primary') and .//div[text()='Next']]")
             if first_next.is_visible(timeout=3000):
                 first_next.click()
                 time.sleep(1)
        except:
            pass

        # Step 3: Search
        search_input = page.locator("//input[@placeholder='Search products']")
        search_input.fill(product_id)
        search_input.press("Enter")
        time.sleep(3)

        # Step 4: Radio
        product_radio = page.locator(f"//tr[.//span[contains(text(), '{product_id}')] or .//div[contains(text(), '{product_id}')]]//input[@type='radio' and contains(@class, 'TUXRadioStandalone-input')]")
        product_radio.click()
        time.sleep(1)

        # Step 5: Next
        second_next = page.locator("//button[contains(@class, 'TUXButton--primary') and .//div[text()='Next']]")
        second_next.click()
        time.sleep(1)

        # Step 6: Add
        final_add = page.locator("//button[contains(@class, 'TUXButton--primary') and .//div[text()='Add']]")
        final_add.click()
        
        # Wait for modal close
        final_add.wait_for(state="hidden")

    except Exception as e:
        logger.error(red(f"Error adding product link: {e}"))


def _set_cover(page: Page, cover_path: str) -> None:
    """
    Adds a custom cover
    """
    logger.debug(green(f"Attempting to add custom cover: {cover_path}..."))
    try:
        if not _check_valid_cover_path(cover_path):
            raise Exception("Invalid cover image file path")

        preview_loc = page.locator(f"xpath={config.selectors.upload.cover.cover_preview}")
        current_cover_src = preview_loc.get_attribute("src")

        # Edit Cover button
        edit_cover_btn = page.locator(f"xpath={config.selectors.upload.cover.edit_cover_button}")
        edit_cover_btn.click()

        # Upload cover tab
        upload_tab = page.locator(f"xpath={config.selectors.upload.cover.upload_cover_tab}")
        upload_tab.click()

        # File input
        upload_box = page.locator(f"xpath={config.selectors.upload.cover.upload_cover}")
        upload_box.set_input_files(cover_path)

        # Confirmation
        confirm_btn = page.locator(f"xpath={config.selectors.upload.cover.upload_confirmation}")
        confirm_btn.click()

        # Wait for change
        # We need to wait until src changes
        def check_src_change():
            return preview_loc.get_attribute("src") != current_cover_src
            
        # Poll
        for _ in range(20):
            if check_src_change():
                break
            time.sleep(0.5)

    except Exception as e:
        logger.error(red(f"Error setting cover: {e}"))
        # Close container if open
        try:
             exit_icon = page.locator(f"xpath={config.selectors.upload.cover.exit_cover_container}")
             if exit_icon.is_visible():
                 exit_icon.click()
        except:
            pass


# HELPERS (Unchanged mostly)

def _check_valid_path(path: str) -> bool:
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
    datetime_utc_now = pytz.UTC.localize(datetime.datetime.utcnow())
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
            for _, value in elem.items():
                if not _check_valid_path(value):
                    elem[correct_description] = value
                    break
            else:
                elem[correct_description] = ""

        return_list.append(elem) # type: ignore

    return return_list

class DescriptionTooLong(Exception):
    def __init__(self, message: str | None = None):
        super().__init__(message or self.__doc__)

class FailedToUpload(Exception):
    def __init__(self, message=None):
        super().__init__(message or self.__doc__)