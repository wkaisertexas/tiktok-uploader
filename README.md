# ⬆️ TikTok Uploader

![Downloads](https://img.shields.io/github/downloads/wkaisertexas/tiktok-uploader/total)

> A **Selenium**-based uploader for **TikTok** Videos
S
## Installation

A prequisite to using this program is the installation of a [Selenium-compatable Web Browser](https://www.selenium.dev/documentation/webdriver/getting_started/install_drivers/). [Google Chrome](https://www.google.com/chrome/) is recommended

### MacOS, Windows and Linux

```bash
$ pip install tiktok-uploader
```

## Usage

While TikTok is strict about login in from Selenium, simply copying your session tokens is enough to bypass this restriction and be able to upload your videos.

```bash
$ tiktok-uploader -v video.mp4 -d "this is my description" -c cookies.txt
```

```python
from tiktok_uploader.upload import upload_video, upload_videos
from tiktok_uploaader.auth import AuthBackend

# single video
upload_video('video.mp4', description='this is my description', cookies='cookies.txt')

# Multiple Videos
videos = [
    {'path': 'video.mp4', 'description': 'this is my description'},
    {'path': 'video2.mp4', 'description': 'this is also my description'}
]
auth = AuthBackend(cookies='cookies.txt')
upload_videos(videos=videos, auth=auth)
```

### Uploading videos

This library revolves around the `upload_videos` function which takes in a list of videos which have **filenames** and **descriptions** and are passed as follows:

```python
from tiktok_uploader.upload import upload_videos
from tiktok_uploader.auth import AuthBackend

videos = [
{'video': 'video0.mp4', 'description': 'Video 1 is about ..'},
{'video': 'video1.mp4', 'description': 'Video 1 is about ..'}
]

auth = AuthBackend(cookies='cookies.txt')
failed = upload_videos(videos=videos, auth=auth)

for fail in failed: # each input video object which failed
    print(fail)
```

### Authentication
Authentication uses your browser's cookies. This workaround was done due to TikTok's stricter stance on authetication. 

To get your cookies, download [🍪 Get cookies.txt](https://chrome.google.com/webstore/detail/get-cookiestxt/bgaddhkoddajcdgocldbbfleckgcbcid?hl=en) from the **chrome web store**.

Right click while on TikTok and click `🍪 Get cookies.txt` to download the file.

> Optionally, if you would like to pass your own cookies you may do as an array of dictionaries with keys `name`, `value`, `domain`, `path` and `expiry` 

> The login script does have a `login_accounts` function, but this gets detected by the 

### Browser Selection

[Google Chrome](https://www.google.com/chrome) is the prefered browser for **TikTokUploader**. The default anti-detection techniques used in this packaged are optimized for this. However, if you wish to use a different browser you may specify that in `upload_videos`.

```python
from random import choice

upload_videos(browser=choice(['chrome', 'safari', 'chromium', 'edge', 'firefox'])) # randomly picks a web browser (not recommended)
```

Supported Browsers:
- Chrome (Recommended)
- Safari
- Chromium
- Edge 
- FireFox

### Custom Driver Options

This package has a set of default modifications to Selenium which help it avoid being detected by TikTok. However, you may pass custom driver configuration options as a keyword argument. 

```python
from selenium.webdriver.chrome.options import Options

options = Options()

options.add_argument('start-maximized')

upload_videos(options=options)
```

> Note: Make sure to use the right selenium options for your browser

### Headless Browsers

**Headless browsers do not work at this time** 

> If more experienced in Webscraping, I would really appreciate helping make this work. [undetected-chromedriver](https://github.com/ultrafunkamsterdam/undetected-chromedriver) was already tried and did not work

### Initial Setup

[WebDriverManager](https://bonigarcia.dev/webdrivermanager/) is used to manage driver versions. On intial startup, you will be promted to install the correct driver for your selected broswer.

## Notes

This bot is not fool proof. I have personally not gotten banned while using this bot, but to do this, my use was kept minimal and large time gaps were placed between each action. 

Without a doubt, publishing hundreds or thousands of videos sequentially will likely get you ip banned.

> Please think of this package as more of a scheduled uploader for TikTok videos, rather than a spam bot

## Accounts made using TikTok Uploader

- [@C_Span](https://www.tiktok.com/@c_span?lang=en), a C-Span clips channel with split-screen video in the background
