"""Upload is the project's main uploader"""
from os.path import abspath, exists

from selenium.webdriver.common.by import By

from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from tiktok_uploader.browsers import get_browser
from tiktok_uploader.auth import AuthBackend

from tiktok_uploader import config


def upload_video(filename=None, description='', username='',
                 password='', cookies='', *args, **kwargs):
    """
    Uploads a single TikTok video.

    Conder using `upload_videos` if using multiple videos
    """
    auth = AuthBackend(username=username, password=password, cookies_path=cookies)

    return upload_videos(
            videos=[ { 'path': filename, 'description': description } ],
            auth=auth,
            *args, **kwargs
        )


def upload_videos(videos: list = None, auth: AuthBackend = None, browser='chrome',
                  browser_agent=None, on_complete=None, headless=False, n = 1, *args, **kwargs):
    """
    Uploads multiplevideos to TikTok

    Parameters
    ----------
    videos : list
        A list of dictionaries containing the video's ('path') and description ('description')
    browser : str
        The browser to use for uploading
    browser_agent : selenium.webdriver
        A selenium webdriver object to use for uploading
    on_complete : function
        A function to call when the upload is complete
    headless : bool
        Whether or not the browser should be run in headless mode
    n : int
        The number of retries to attempt if the upload fails
    *args :
        Additional arguments to pass into the upload function
    **kwargs :
        Additional keyword arguments to pass into the upload function

    Returns
    -------
    failed : list
        A list of videos which failed to upload
    """
    if not videos:
        print("No videos were provided")
        return

    if not browser_agent: # user-specified browser agent
        driver = get_browser(name=browser, headless=headless, *args, **kwargs)
    else:
        driver = browser_agent

    driver = auth.authenticate_agent(driver)

    failed = []
    # uploads each video
    for video in videos:
        print(f'Uploading {video.get("path")}')
        try:
            path = abspath(video.get('path'))
            description = video.get('description', '')
        except Exception as _:
            print(f'Invalid video: {video}')
            failed.append(video)
            continue

        # Video must be of supported type
        if not check_valid_path(path):
            print(f'{path} is invalid, skipping')
            failed.append(video)
            continue

        for i in range(n): # retries the upload if it fails
            try:
                complete_upload_form(driver, path, description, *args, **kwargs)
                break
            except Exception as exception:
                print(exception)
                if i == n-1: # adds if the last retry
                    failed.append(video)

        if on_complete: # calls the user-specified on-complete function
            on_complete(video)

    if config['quit_on_end']:
        driver.quit()

    return failed


def complete_upload_form(driver, path: str, description: str, *args, **kwargs) -> None:
    """
    Actually uploades each video

    Parameters
    ----------
    driver : selenium.webdriver
        The selenium webdriver to use for uploading
    path : str
        The path to the video to upload
    """
    driver.get(config['paths']['upload'])

    # changes to the iframe
    iframe_selector = EC.presence_of_element_located(
        (By.XPATH, config['selectors']['upload']['iframe'])
        )
    iframe = WebDriverWait(driver, config['explicit_wait']).until(iframe_selector)
    driver.switch_to.frame(iframe)

    # waits for the iframe to load
    root_selector = EC.presence_of_element_located((By.ID, 'root'))
    WebDriverWait(driver, config['explicit_wait']).until(root_selector)

    # uploades the element
    upload_box = driver.find_element(By.XPATH, config['selectors']['upload']['upload_video'])
    upload_box.send_keys(path)

    # waits for the video to upload
    upload_confirmation = EC.presence_of_element_located(
        (By.XPATH, config['selectors']['upload']['upload_confirmation'])
        )
    WebDriverWait(driver, config['explicit_wait']).until(upload_confirmation)

    # gets the description
    desc = driver.find_element(By.XPATH, config['selectors']['upload']['description'])
    desc.click() # clicks the description box (required for the frames to load)

    if description:
        desc.clear()
        desc.send_keys(description)

    # wait until a non-draggable image is found
    process_confirmation = EC.presence_of_element_located(
        (By.XPATH, config['selectors']['upload']['process_confirmation'])
        )
    WebDriverWait(driver, config['explicit_wait']).until(process_confirmation)

    # posts the video
    post = driver.find_element(By.XPATH, config['selectors']['upload']['post'])
    post.click()

    post_confirmation = EC.presence_of_element_located(
        (By.XPATH, config['selectors']['upload']['post_confirmation'])
        )
    WebDriverWait(driver, config['explicit_wait']).until(post_confirmation)


def check_valid_path(path: str) -> bool:
    """
    Returns whether or not the filetype is supported by TikTok
    """
    return exists(path) and path.split('.')[-1] in config['supported_file_types']
