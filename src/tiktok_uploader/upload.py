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
from selenium.common.exceptions import (
    ElementClickInterceptedException,
    NoSuchElementException,
    NoSuchShadowRootException,
    TimeoutException,
)
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from tiktok_uploader import config, logger
from tiktok_uploader.auth import AuthBackend
from tiktok_uploader.browsers import get_browser
from tiktok_uploader.proxy_auth_extension.proxy_auth_extension import proxy_is_working
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

    Parameters
    ----------
    filename : str
        The path to the video to upload
    description : str
        The description to set for the video
    schedule: datetime.datetime
        The datetime to schedule the video, must be naive or aware with UTC timezone, if naive it will be aware with UTC timezone
    cookies : str
        The cookies to use for uploading
    sessionid: str
        The `sessionid` is the only required cookie for uploading,
            but it is recommended to use all cookies to avoid detection
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
    browser_agent: WebDriver | None = None,
    on_complete: Callable[[VideoDict], None] | None = None,
    headless: bool = False,
    num_retries: int = 1,
    skip_split_window: bool = False,
    *args,
    **kwargs,
) -> list[VideoDict]:
    """
    Uploads multiple videos to TikTok

    Parameters
    ----------
    videos : list
        A list of dictionaries containing the video's ('path') and description ('description')
    proxy: dict
        A dictionary containing the proxy user, pass, host and port
    browser : str
        The browser to use for uploading
    browser_agent : selenium.webdriver
        A selenium webdriver object to use for uploading
    on_complete : function
        A function to call when the upload is complete
    headless : bool
        Whether or not the browser should be run in headless mode
    num_retries : int
        The number of retries to attempt if the upload fails
    options : SeleniumOptions
        The options to pass into the browser -> custom privacy settings, etc.
    *args :
        Additional arguments to pass into the upload function
    **kwargs :
        Additional keyword arguments to pass into the upload function

    Returns
    -------
    failed : list
        A list of videos which failed to upload
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
        driver = get_browser(browser, headless=headless, proxy=proxy, *args, **kwargs)
    else:
        logger.debug("Using user-defined browser agent")
        driver = browser_agent
    if proxy:
        if proxy_is_working(driver, proxy["host"]):
            logger.debug(green("Proxy is working"))
        else:
            logger.error("Proxy is not working")
            driver.quit()
            raise Exception("Proxy is not working")
    driver = auth.authenticate_agent(driver)

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
                driver,
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

        if on_complete is callable:  # calls the user-specified on-complete function
            on_complete(video)

    if config.quit_on_end:
        driver.quit()

    return failed


def complete_upload_form(
    driver: WebDriver,
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

    Parameters
    ----------
    driver : selenium.webdriver
        The selenium webdriver to use for uploading
    path : str
        The path to the video to upload
    """
    _go_to_upload(driver)
    _remove_cookies_window(driver)

    upload_complete_event = threading.Event()

    # Function to call _set_video and set the event when it's done
    def upload_video():
        _set_video(driver, path=path, **kwargs)
        upload_complete_event.set()

    # Start the upload_video function in a separate thread
    upload_thread = threading.Thread(target=upload_video)
    upload_thread.start()

    # Wait for the upload to complete before proceeding
    upload_complete_event.wait()

    if cover_path:
        _set_cover(driver, cover_path)
    if not skip_split_window:
        _remove_split_window(driver)
    _set_interactivity(driver, **kwargs)
    _set_description(driver, description)
    if visibility != "everyone":
        _set_visibility(driver, visibility)
    if schedule:
        _set_schedule_video(driver, schedule)
    if product_id:
        _add_product_link(driver, product_id)
    _post_video(driver)


def _go_to_upload(driver: WebDriver) -> None:
    """
    Navigates to the upload page, switches to the iframe and waits for it to load

    Parameters
    ----------
    driver : selenium.webdriver
    """
    logger.debug(green("Navigating to upload page"))

    # if the upload page is not open, navigate to it
    if driver.current_url != config.paths.upload:
        driver.get(str(config.paths.upload))
    # otherwise, refresh the page and accept the reload alert
    else:
        _refresh_with_alert(driver)

    # changes to the iframe
    # _change_to_upload_iframe(driver)

    # waits for the iframe to load
    root_selector = EC.presence_of_element_located((By.ID, "root"))
    WebDriverWait(driver, config.explicit_wait).until(root_selector)

    # Return to default webpage
    driver.switch_to.default_content()


def _change_to_upload_iframe(driver: WebDriver) -> None:
    """
    Switch to the iframe of the upload page

    Parameters
    ----------
    driver : selenium.webdriver
    """
    iframe_selector = EC.presence_of_element_located(
        (By.XPATH, config.selectors.upload.iframe)
    )
    iframe = WebDriverWait(driver, config.explicit_wait).until(iframe_selector)
    driver.switch_to.frame(iframe)


def _set_description(driver: WebDriver, description: str) -> None:
    """
    Sets the description of the video

    Parameters
    ----------
    driver : selenium.webdriver
    description : str
        The description to set
    """
    if description is None:
        # if no description is provided, filename
        return

    logger.debug(green("Setting description"))


    # Remove any characters outside the BMP range (emojis, etc) & Fix accents
    description = description.encode("utf-8", "ignore").decode("utf-8")

    saved_description = description  # save the description in case it fails

    WebDriverWait(driver, config.implicit_wait).until(
        EC.presence_of_element_located((By.XPATH, config.selectors.upload.description))
    )

    desc = driver.find_element(By.XPATH, config.selectors.upload.description)

    desc.click()

    # desc populates with filename before clearing
    WebDriverWait(driver, config.explicit_wait).until(lambda driver: desc.text != "")

    desc.send_keys(Keys.END)
    _clear(desc)

    WebDriverWait(driver, config.explicit_wait).until(lambda driver: desc.text == "")

    desc.click()

    time.sleep(1)

    try:
        words = description.split(" ")
        for word in words:
            if word[0] == "#":
                desc.send_keys(word)
                desc.send_keys(" " + Keys.BACKSPACE)
                WebDriverWait(driver, config.implicit_wait).until(
                    EC.presence_of_element_located(
                        (By.XPATH, config.selectors.upload.mention_box)
                    )
                )
                time.sleep(config.add_hashtag_wait)
                desc.send_keys(Keys.ENTER)
            elif word[0] == "@":
                logger.debug(green("- Adding Mention: " + word))
                desc.send_keys(word)
                desc.send_keys(" ")
                time.sleep(1)
                desc.send_keys(Keys.BACKSPACE)

                WebDriverWait(driver, config.explicit_wait).until(
                    EC.presence_of_element_located(
                        (By.XPATH, config.selectors.upload.mention_box_user_id)
                    )
                )

                found = False
                waiting_interval = 0.5
                timeout = 5
                start_time = time.time()

                while not found and (time.time() - start_time < timeout):
                    user_id_elements = driver.find_elements(
                        By.XPATH, config.selectors.upload.mention_box_user_id
                    )
                    time.sleep(1)

                    for i in range(len(user_id_elements)):
                        user_id_element = user_id_elements[i]
                        if user_id_element and user_id_element.is_enabled():
                            username = user_id_element.text.split(" ")[0]
                            if username.lower() == word[1:].lower():
                                found = True
                                print("Matching User found : Clicking User")
                                for j in range(i):
                                    desc.send_keys(Keys.DOWN)
                                desc.send_keys(Keys.ENTER)
                                break

                        if not found:
                            print(
                                f"No match. Waiting for {waiting_interval} seconds..."
                            )
                            time.sleep(waiting_interval)

            else:
                desc.send_keys(word + " ")

    except Exception as exception:
        print("Failed to set description: ", exception)
        _clear(desc)
        desc.send_keys(saved_description)


def _clear(element) -> None:
    """
    Clears the text of the element (an issue with the TikTok website when automating)

    Parameters
    ----------
    element
        The text box to clear
    """
    element.send_keys(2 * len(element.text) * Keys.BACKSPACE)


def _set_video(
    driver: WebDriver, path: str = "", num_retries: int = 3, **kwargs
) -> None:
    """
    Sets the video to upload

    Parameters
    ----------
    driver : selenium.webdriver
    path : str
        The path to the video to upload
    num_retries : number of retries (can occasionally fail)
    """
    # uploads the element
    logger.debug(green("Uploading video file"))

    for _ in range(num_retries):
        try:
            # _change_to_upload_iframe(driver)
            # Wait For Input File
            driverWait = WebDriverWait(driver, config.explicit_wait)
            upload_boxWait = EC.presence_of_element_located(
                (By.XPATH, config.selectors.upload.upload_video)
            )
            driverWait.until(upload_boxWait)
            upload_box = driver.find_element(
                By.XPATH, config.selectors.upload.upload_video
            )
            upload_box.send_keys(path)

            # wait until a non-draggable image is found
            process_confirmation = EC.presence_of_element_located(
                (By.XPATH, config.selectors.upload.process_confirmation)
            )
            WebDriverWait(driver, config.explicit_wait).until(process_confirmation)
            return
        except TimeoutException as exception:
            print("TimeoutException occurred:\n", exception)
        except Exception as exception:
            print(exception)
            raise FailedToUpload(exception)


def _remove_cookies_window(driver) -> None:
    """
    Removes the cookies window if it is open

    Parameters
    ----------
    driver : selenium.webdriver
    """

    logger.debug(green("Removing cookies window"))
    cookies_banner = WebDriverWait(driver, config.implicit_wait).until(
        EC.presence_of_element_located(
            (By.TAG_NAME, config.selectors.upload.cookies_banner.banner)
        )
    )

    # Debug: pause here to allow visual inspection before interacting with the cookies banner
    # This helps identify DOM/selector issues when running non-headless

    # try:
    #     item = WebDriverWait(driver, config.implicit_wait).until(
    #         EC.visibility_of(
    #             cookies_banner.shadow_root.find_element(
    #                 By.CSS_SELECTOR,
    #                 config.selectors.upload.cookies_banner.button,
    #             )
    #         )
    #     )

    #     # Wait that the Decline all button is clickable
    #     decline_button = WebDriverWait(driver, config.implicit_wait).until(
    #         EC.element_to_be_clickable(item.find_elements(By.TAG_NAME, "button")[0])
    #     )
    #     decline_button.click()

    # # If shadow root is not found, we remove it
    # except NoSuchShadowRootException:
    #     driver.execute_script(
    #         "document.querySelector(arguments[0]).remove()",
    #         config.selectors.upload.cookies_banner.banner,
    #     )


def _remove_split_window(driver: WebDriver) -> None:
    """
    Remove the split window if it is open

    Parameters
    ----------
    driver : selenium.webdriver
    """
    logger.debug(green("Removing split window"))
    window_xpath = config.selectors.upload.split_window

    # try:
    #     condition = EC.presence_of_element_located((By.XPATH, window_xpath))
    #     window = WebDriverWait(driver, config.implicit_wait).until(condition)
    #     window.click()

    # except TimeoutException:
    #     logger.debug(red("Split window not found or operation timed out"))


def _set_interactivity(
    driver: WebDriver,
    comment: bool = True,
    stitch: bool = True,
    duet: bool = True,
    *args,
    **kwargs,
) -> None:
    """
    Sets the interactivity settings of the video

    Parameters
    ----------
    driver : selenium.webdriver
    comment : bool
        Whether or not to allow comments
    stitch : bool
        Whether or not to allow stitching
    duet : bool
        Whether or not to allow duets
    """
    try:
        logger.debug(green("Setting interactivity settings"))

        comment_box = driver.find_element(By.XPATH, config.selectors.upload.comment)
        stitch_box = driver.find_element(By.XPATH, config.selectors.upload.stitch)
        duet_box = driver.find_element(By.XPATH, config.selectors.upload.duet)

        # xor the current state with the desired state
        if comment ^ comment_box.is_selected():
            comment_box.click()

        if stitch ^ stitch_box.is_selected():
            stitch_box.click()

        if duet ^ duet_box.is_selected():
            duet_box.click()

    except Exception as _:
        logger.error("Failed to set interactivity settings")


def _set_visibility(
    driver: WebDriver, visibility: Literal["everyone", "friends", "only_you"]
) -> None:
    """
    Sets the visibility/privacy of the video

    Parameters
    ----------
    driver : selenium.webdriver
    visibility : str
        The visibility setting - "everyone", "friends", or "only_you"
    """
    try:
        logger.debug(green(f"Setting visibility to: {visibility}"))

        # Find the dropdown button for visibility
        dropdown_xpath = (
            "//div[@data-e2e='video_visibility_container']//button[@role='combobox']"
        )
        dropdown = WebDriverWait(driver, config.implicit_wait).until(
            EC.element_to_be_clickable((By.XPATH, dropdown_xpath))
        )

        # Click to open the dropdown
        dropdown.click()
        time.sleep(1.5)  # Wait for dropdown animation

        # Map visibility values to the text that appears in the dropdown
        visibility_text_map = {
            "everyone": "Everyone",
            "friends": "Friends",
            "only_you": "Only you",
        }

        option_text = visibility_text_map.get(visibility, "Everyone")

        # Use the selector that actually works (verified through testing)
        option_xpath = f"//div[@role='option' and contains(., '{option_text}')]"
        option = WebDriverWait(driver, config.implicit_wait).until(
            EC.element_to_be_clickable((By.XPATH, option_xpath))
        )

        driver.execute_script("arguments[0].scrollIntoView(true);", option)
        time.sleep(0.5)
        option.click()

        logger.debug(green(f"Successfully set visibility to: {visibility}"))

    except TimeoutException:
        logger.error(red("Failed to set visibility - dropdown not found"))
    except Exception as e:
        logger.error(red(f"Failed to set visibility: {e}"))


def _set_schedule_video(driver: WebDriver, schedule: datetime.datetime) -> None:
    """
    Sets the schedule of the video

    Parameters
    ----------
    driver : selenium.webdriver
    schedule : datetime.datetime
        The datetime to set
    """

    logger.debug(green("Setting schedule"))

    driver_timezone = __get_driver_timezone(driver)
    schedule = schedule.astimezone(driver_timezone)

    month = schedule.month
    day = schedule.day
    hour = schedule.hour
    minute = schedule.minute

    try:
        switch = driver.find_element(By.XPATH, config.selectors.schedule.switch)
        switch.click()
        __date_picker(driver, month, day)
        __time_picker(driver, hour, minute)
    except Exception as e:
        msg = f"Failed to set schedule: {e}"
        logger.error(red(msg))
        raise FailedToUpload()


def __date_picker(driver: WebDriver, month: int, day: int) -> None:
    logger.debug(green("Picking date"))

    condition = EC.presence_of_element_located(
        (By.XPATH, config.selectors.schedule.date_picker)
    )
    date_picker = WebDriverWait(driver, config.implicit_wait).until(condition)
    date_picker.click()

    condition = EC.presence_of_element_located(
        (By.XPATH, config.selectors.schedule.calendar)
    )
    WebDriverWait(driver, config.implicit_wait).until(condition)

    calendar_month = driver.find_element(
        By.XPATH, config.selectors.schedule.calendar_month
    ).text
    n_calendar_month = datetime.datetime.strptime(calendar_month, "%B").month
    if n_calendar_month != month:  # Max can be a month before or after
        if n_calendar_month < month:
            arrow = driver.find_elements(
                By.XPATH, config.selectors.schedule.calendar_arrows
            )[-1]
        else:
            arrow = driver.find_elements(
                By.XPATH, config.selectors.schedule.calendar_arrows
            )[0]
        arrow.click()
    valid_days = driver.find_elements(
        By.XPATH, config.selectors.schedule.calendar_valid_days
    )

    day_to_click = None
    for day_option in valid_days:
        if int(day_option.text) == day:
            day_to_click = day_option
            break
    if day_to_click:
        day_to_click.click()
    else:
        raise Exception("Day not found in calendar")

    __verify_date_picked_is_correct(driver, month, day)


def __verify_date_picked_is_correct(driver: WebDriver, month: int, day: int) -> None:
    date_selected = driver.find_element(
        By.XPATH, config.selectors.schedule.date_picker
    ).text
    date_selected_month = int(date_selected.split("-")[1])
    date_selected_day = int(date_selected.split("-")[2])

    if date_selected_month == month and date_selected_day == day:
        logger.debug(green("Date picked correctly"))
    else:
        msg = f"Something went wrong with the date picker, expected {month}-{day} but got {date_selected_month}-{date_selected_day}"
        logger.error(msg)
        raise Exception(msg)


def __time_picker(driver: WebDriver, hour: int, minute: int) -> None:
    logger.debug(green("Picking time"))

    condition = EC.presence_of_element_located(
        (By.XPATH, config.selectors.schedule.time_picker)
    )
    time_picker = WebDriverWait(driver, config.implicit_wait).until(condition)
    time_picker.click()

    condition = EC.presence_of_element_located(
        (By.XPATH, config.selectors.schedule.time_picker_container)
    )
    WebDriverWait(driver, config.implicit_wait).until(condition)

    # 00 = 0, 01 = 1, 02 = 2, 03 = 3, 04 = 4, 05 = 5, 06 = 6, 07 = 7, 08 = 8, 09 = 9, 10 = 10, 11 = 11, 12 = 12,
    # 13 = 13, 14 = 14, 15 = 15, 16 = 16, 17 = 17, 18 = 18, 19 = 19, 20 = 20, 21 = 21, 22 = 22, 23 = 23
    hour_options = driver.find_elements(
        By.XPATH, config.selectors.schedule.timepicker_hours
    )
    # 00 == 0, 05 == 1, 10 == 2, 15 == 3, 20 == 4, 25 == 5, 30 == 6, 35 == 7, 40 == 8, 45 == 9, 50 == 10, 55 == 11
    minute_options = driver.find_elements(
        By.XPATH, config.selectors.schedule.timepicker_minutes
    )

    hour_to_click = hour_options[hour]
    minute_option_correct_index = int(minute / 5)
    minute_to_click = minute_options[minute_option_correct_index]

    time.sleep(1)  # temporay fix => might be better to use an explicit wait
    driver.execute_script(
        "arguments[0].scrollIntoView({block: 'center', inline: 'nearest'});",
        hour_to_click,
    )
    time.sleep(1)  # temporay fix => might be better to use an explicit wait
    hour_to_click.click()

    driver.execute_script(
        "arguments[0].scrollIntoView({block: 'center', inline: 'nearest'});",
        minute_to_click,
    )
    time.sleep(2)  # temporary fixed => Might be better to use an explicit wait
    minute_to_click.click()

    # click somewhere else to close the time picker
    time_picker.click()

    time.sleep(0.5)  # wait for the DOM change
    __verify_time_picked_is_correct(driver, hour, minute)


def __verify_time_picked_is_correct(driver: WebDriver, hour: int, minute: int) -> None:
    time_selected = driver.find_element(
        By.XPATH, config.selectors.schedule.time_picker_text
    ).text
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


def _post_video(driver: WebDriver) -> None:
    """
    Posts the video by clicking the post button

    Parameters
    ----------
    driver : selenium.webdriver
    """
    logger.debug(green("Clicking the post button"))

    try:
        post = WebDriverWait(driver, config.uploading_wait).until(
            lambda d: (el := d.find_element(By.XPATH, config.selectors.upload.post))
            and el.get_attribute("data-disabled") == "false"
            and el
        )
        driver.execute_script(
            "arguments[0].scrollIntoView({block: 'center', inline: 'nearest'});", post
        )
        post.click()

    except ElementClickInterceptedException:
        logger.debug(green("Trying to click on the button again"))
        driver.execute_script('document.querySelector(".TUXButton--primary").click()')

    # wait for button with text "Post now" and click it if it exists
    try:
        time.sleep(1)
        logger.debug(green("Waiting for 'Post sekarang' button"))
        post_now_button = WebDriverWait(driver, config.explicit_wait).until(
            EC.element_to_be_clickable((By.XPATH, config.selectors.upload.post_now))
        )
        post_now_button.click()
    except TimeoutException:
        logger.debug("No 'Post now' button found, proceeding without it")

    # waits for the video to upload
    time.sleep(1)
    # the toast gone so fast it couldn't be detected
    # post_confirmation = EC.presence_of_element_located(
    #     (By.XPATH, config.selectors.upload.post_confirmation)
    # )
    # WebDriverWait(driver, config.explicit_wait).until(post_confirmation)

    logger.debug(green("Video posted successfully"))


# HELPERS


def _check_valid_path(path: str) -> bool:
    """
    Returns whether or not the filetype is supported by TikTok
    """
    return exists(path) and path.split(".")[-1] in config.supported_file_types


def _check_valid_cover_path(path: str) -> bool:
    """
    Returns whether or not the cover image filetype is supported by TikTok
    """
    return exists(path) and path.split(".")[-1] in config.supported_image_file_types


def _get_valid_schedule_minute(
    schedule: datetime.datetime, valid_multiple
) -> datetime.datetime:
    """
    Returns a datetime.datetime with valid minute for TikTok
    """
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
    """
    Returns if the schedule is supported by TikTok
    """
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


def _get_splice_index(
    nearest_mention: int, nearest_hashtag: int, description: str
) -> int:
    """
    Returns the index to splice the description at

    Parameters
    ----------
    nearest_mention : int
        The index of the nearest mention
    nearest_hashtag : int
        The index of the nearest hashtag

    Returns
    -------
    int
        The index to splice the description at
    """
    if nearest_mention == -1 and nearest_hashtag == -1:
        return len(description)
    elif nearest_hashtag == -1:
        return nearest_mention
    elif nearest_mention == -1:
        return nearest_hashtag
    else:
        return min(nearest_mention, nearest_hashtag)


def _convert_videos_dict(
    videos_list_of_dictionaries: list[dict[str, Any]],
) -> list[VideoDict]:
    """
    Takes in a videos dictionary and converts it.

    This allows the user to use the wrong stuff and thing to just work
    """
    if not videos_list_of_dictionaries:
        raise RuntimeError("No videos to upload")

    valid_path = config.valid_path_names
    valid_description = config.valid_descriptions

    correct_path = valid_path[0]
    correct_description = valid_description[0]

    def intersection(lst1, lst2):
        """return the intersection of two lists"""
        return list(set(lst1) & set(lst2))

    return_list: list[VideoDict] = []
    for elem in videos_list_of_dictionaries:
        # preprocess the dictionary
        elem = {k.strip().lower(): v for k, v in elem.items()}

        keys = elem.keys()
        path_intersection = intersection(valid_path, keys)
        description_intersection = intersection(valid_description, keys)

        if path_intersection:
            # we have a path
            path = elem[path_intersection.pop()]

            if not _check_valid_path(path):
                raise RuntimeError("Invalid path: " + path)

            elem[correct_path] = path
        else:
            # iterates over the elem and find a key which is a path with a valid extension
            for _, value in elem.items():
                if _check_valid_path(value):
                    elem[correct_path] = value
                    break
            else:
                # no valid path found
                raise RuntimeError("Path not found in dictionary: " + str(elem))

        if description_intersection:
            # we have a description
            elem[correct_description] = elem[description_intersection.pop()]
        else:
            # iterates over the elem and finds a description which is not a valid path
            for _, value in elem.items():
                if not _check_valid_path(value):
                    elem[correct_description] = value
                    break
            else:
                elem[correct_description] = ""  # null description is fine

        return_list.append(elem)  # type: ignore

    return return_list


def __get_driver_timezone(driver: WebDriver) -> Any:
    """
    Returns the timezone of the driver
    """
    timezone_str = driver.execute_script(
        "return Intl.DateTimeFormat().resolvedOptions().timeZone"
    )
    return pytz.timezone(timezone_str)


def _refresh_with_alert(driver: WebDriver) -> None:
    try:
        # attempt to refresh the page
        driver.refresh()

        # wait for the alert to appear
        WebDriverWait(driver, config.explicit_wait).until(EC.alert_is_present())

        # accept the alert
        driver.switch_to.alert.accept()
    except Exception as e:
        print(f"Exception when refreshing alert {e}")


class DescriptionTooLong(Exception):
    """
    A video description longer than the maximum allowed by TikTok's website (not app) uploader
    """

    def __init__(self, message: str | None = None):
        super().__init__(message or self.__doc__)


class FailedToUpload(Exception):
    """
    A video failed to upload
    """

    def __init__(self, message=None):
        super().__init__(message or self.__doc__)


def _add_product_link(driver: WebDriver, product_id: str) -> None:
    """
    Adds the product link to the video using the provided product ID.
    """
    logger.debug(green(f"Attempting to add product link for ID: {product_id}..."))
    try:
        wait = WebDriverWait(driver, 20)  # Wait up to 20 seconds

        # -- Step 1: Find and click the 'Add Product Link' button --
        add_link_button_xpath = (
            "//button[contains(@class, 'Button__root') and contains(., 'Add')]"
        )
        add_link_button = wait.until(
            EC.element_to_be_clickable((By.XPATH, add_link_button_xpath))
        )
        # Optional: Scroll to the button if it might be off-screen
        # driver.execute_script("arguments[0].scrollIntoView(true);", add_link_button)
        # time.sleep(0.5) # Short pause after scrolling
        add_link_button.click()
        logger.debug(green("Clicked 'Add Product Link' button."))
        time.sleep(1)  # Wait for modal animation

        # -- Step 2: Click the 'Next' button in the first modal (if it exists) --
        try:
            first_next_button_xpath = "//button[contains(@class, 'TUXButton--primary') and .//div[text()='Next']]"
            # Ensure this button belongs to the correct modal context if multiple exist
            first_next_button = wait.until(
                EC.element_to_be_clickable((By.XPATH, first_next_button_xpath))
            )
            first_next_button.click()
            logger.debug(green("Clicked first 'Next' button in modal."))
            time.sleep(1)  # Wait for the next part of the modal to load
        except TimeoutException:
            logger.debug("First 'Next' button not found or not needed, proceeding...")

        # -- Step 3: Find search input, enter product ID, and press Enter --
        search_input_xpath = "//input[@placeholder='Search products']"
        search_input = wait.until(
            EC.visibility_of_element_located((By.XPATH, search_input_xpath))
        )
        search_input.clear()
        search_input.send_keys(product_id)
        search_input.send_keys(Keys.RETURN)  # Press Enter to search
        logger.debug(green(f"Entered product ID '{product_id}' and pressed Enter."))
        # Wait for search results - Replace sleep with explicit wait if possible
        # e.g., wait for a specific element in the results table to appear
        time.sleep(3)  # Increased wait time slightly

        # -- Step 4: Find and select the radio button for the product --
        # !!! CRITICAL: Verify and adjust this XPath based on actual HTML structure !!!
        # It assumes the product ID is visible within a span or div in the same table row (tr)
        product_radio_xpath = f"//tr[.//span[contains(text(), '{product_id}')] or .//div[contains(text(), '{product_id}')]]//input[@type='radio' and contains(@class, 'TUXRadioStandalone-input')]"
        logger.debug(f"Looking for radio button with XPath: {product_radio_xpath}")
        product_radio = wait.until(
            EC.element_to_be_clickable((By.XPATH, product_radio_xpath))
        )
        # Use JavaScript click for potentially troublesome radio buttons
        driver.execute_script("arguments[0].click();", product_radio)
        logger.debug(green(f"Selected product radio for ID: {product_id}"))
        time.sleep(1)  # Pause after selection

        # -- Step 5: Find and click the 'Next' button (after selecting radio) --
        second_next_button_xpath = (
            "//button[contains(@class, 'TUXButton--primary') and .//div[text()='Next']]"
        )
        # Add more context if needed to distinguish this 'Next' button
        second_next_button = wait.until(
            EC.element_to_be_clickable((By.XPATH, second_next_button_xpath))
        )
        second_next_button.click()
        logger.debug(green("Clicked second 'Next' button."))
        time.sleep(1)  # Wait for the next modal/confirmation step

        # -- Step 6: Find and click the final 'Add' button --
        final_add_button_xpath = (
            "//button[contains(@class, 'TUXButton--primary') and .//div[text()='Add']]"
        )
        final_add_button = wait.until(
            EC.element_to_be_clickable((By.XPATH, final_add_button_xpath))
        )
        final_add_button.click()
        logger.debug(green("Clicked final 'Add' button. Product link should be added."))

        # Wait for the modal to close (e.g., wait for the final 'Add' button to disappear)
        wait.until(
            EC.invisibility_of_element_located((By.XPATH, final_add_button_xpath))
        )
        logger.debug(green("Product link modal closed."))

    except TimeoutException:
        logger.error(
            red(
                "Error: Timed out waiting for element during product link addition. XPath might be wrong or element didn't appear."
            )
        )
        # logger.error(f"Timeout details: {e}")
        # Decide whether to raise error or continue upload without link
        print(
            f"Warning: Failed to add product link {product_id} due to timeout. Continuing upload without link."
        )
    except NoSuchElementException:
        logger.error(
            red(
                "Error: Could not find element during product link addition. XPath might be wrong."
            )
        )
        # logger.error(f"NoSuchElement details: {e}")
        print(
            f"Warning: Failed to add product link {product_id} because an element was not found. Continuing upload without link."
        )
    except Exception as e:
        logger.error(
            red(f"An unexpected error occurred while adding product link: {e}")
        )


def _set_cover(driver, cover_path: str) -> None:
    """
    Adds a custom cover to the video using the provided cover image path.
    """
    logger.debug(green(f"Attempting to add custom cover: {cover_path}..."))
    try:
        if not _check_valid_cover_path(cover_path):
            raise Exception("Invalid cover image file path")

        # First, get the current cover image blob source
        WebDriverWait(driver, config.implicit_wait).until(
            EC.presence_of_element_located(
                (By.XPATH, config.selectors.upload.cover.edit_cover_button)
            )
        )
        current_cover_preview = driver.find_element(
            By.XPATH, config.selectors.upload.cover.cover_preview
        ).get_attribute("src")

        # Click the "Edit Cover" button
        WebDriverWait(driver, config.implicit_wait).until(
            EC.presence_of_element_located(
                (By.XPATH, config.selectors.upload.cover.edit_cover_button)
            )
        )
        edit_cover_button = driver.find_element(
            By.XPATH, config.selectors.upload.cover.edit_cover_button
        )
        edit_cover_button.click()

        # Enter the Custom Cover tab
        WebDriverWait(driver, config.implicit_wait).until(
            EC.presence_of_element_located(
                (By.XPATH, config.selectors.upload.cover.upload_cover_tab)
            )
        )
        upload_cover_tab = driver.find_element(
            By.XPATH, config.selectors.upload.cover.upload_cover_tab
        )
        upload_cover_tab.click()

        # Wait For Input File
        driverWait = WebDriverWait(driver, config.explicit_wait)
        upload_boxWait = EC.presence_of_element_located(
            (By.XPATH, config.selectors.upload.cover.upload_cover)
        )
        driverWait.until(upload_boxWait)
        upload_box = driver.find_element(
            By.XPATH, config.selectors.upload.cover.upload_cover
        )
        upload_box.send_keys(cover_path)

        # Wait until image is loaded and click confirmation button
        WebDriverWait(driver, config.implicit_wait).until(
            EC.presence_of_element_located(
                (By.XPATH, config.selectors.upload.cover.upload_confirmation)
            )
        )
        upload_confirmation = driver.find_element(
            By.XPATH, config.selectors.upload.cover.upload_confirmation
        )
        upload_confirmation.click()

        # At last, wait until the cover image preview changes blob source
        WebDriverWait(driver, config.implicit_wait).until_not(
            EC.text_to_be_present_in_element_attribute(
                (By.XPATH, config.selectors.upload.cover.cover_preview),
                "src",
                current_cover_preview,
            )
        )

    except Exception as e:
        logger.error(red(f"Error: {e}. Using default cover instead."))

        try:
            # If the edit cover container is open, close it
            cover_container = driver.find_element(
                By.XPATH, config.selectors.upload.cover.edit_cover_container
            )
            if cover_container.is_displayed():
                exit_icon = WebDriverWait(driver, config.implicit_wait).until(
                    EC.presence_of_element_located(
                        (By.XPATH, config.selectors.upload.cover.exit_cover_container)
                    )
                )
                exit_icon.click()
        except Exception as e:
            logger.error(red("Could not print with the default color"))
        return

    logger.debug(green("Custom cover posted successfully"))
