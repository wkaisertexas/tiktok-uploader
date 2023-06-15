# ⬆️ TikTok Uploader

![Forks](https://img.shields.io/github/forks/wkaisertexas/tiktok-uploader)
![Stars](https://img.shields.io/github/stars/wkaisertexas/tiktok-uploader)
![Watchers](https://img.shields.io/github/watchers/wkaisertexas/tiktok-uploader)


![output](https://github.com/wkaisertexas/tiktok-uploader/assets/27795014/f991fdc7-287a-4c3b-9a84-22c7ad8a57bf)

A **Selenium**-based automated **TikTok** video uploader

# Table of Contents
- [Installation](#installation)
  - [MacOS, Windows and Linux](#macos-windows-and-linux)
    - [Downloading from PyPI (Recommended)](#downloading-from-pypi-recommended)
    - [Building from source](#building-from-source)
- [Usage](#usage)
  - [💻 Commmand Line Interface (CLI)](#-commmand-line-interface-cli)
  - [⬆ Uploading Videos](#-uploading-videos)
  - [🫵 Mentions and Hashtags](#-mentions-and-hashtags)
  - [🪡 Stitches, Duets and Comments](#-stitches-duets-and-comments)
  - [🔐 Authentication](#-authentication)
  - [👀 Browser Selection](#-browser-selection)
  - [🚲 Custom WebDriver Driver Options](#-custom-webdriver-driver-options)
  - [🤯 Headless Browsers](#-headless-browsers)
  - [🔨 Initial Setup](#-initial-setup)
- [♻️ Examples](#-examples)
- [📝 Notes](#-notes)
- [Accounts made with](#accounts-made-using-tiktok-uploader)
# Installation

A prequisite to using this program is the installation of a [Selenium-compatable](https://www.selenium.dev/documentation/webdriver/getting_started/install_drivers/) web browser. [Google Chrome](https://www.google.com/chrome/) is recommended.

## MacOS, Windows and Linux

Install Python 3 or greater from [python.org](https://www.python.org/downloads/)

### Downloading from PyPI (Recommended)

Install `tiktok-uploader` using `pip`

```bash
pip install tiktok-uploader
```

### Building from source

Installing from source allows greater flexability to modify the module's code to extend default behavior. 

First, `clone` and move into the repository. Next, install `hatch`, the build tool used for this project [^1]. Then, `build` the project. Finally, `install` the project with the `-e` or editable flag.  
```console
git clone https://github.com/wkaisertexas/tiktok-uploader.git
cd tiktok-uploader
pip install hatch
hatch build
pip install -e . 
```

# Usage

`tiktok-uploader` works by duplicating your browser's **cookies** which tricks **TikTok** into believing you are logged in on a remote-controlled browser.

## 💻 Commmand Line Interface (CLI)

Using the CLI is as simple as calling `tiktok-uploader` with your videos: `path` (-v), `description`(-d) and `cookies` (-c)

```bash
tiktok-uploader -v video.mp4 -d "this is my escaped \"description\"" -c cookies.txt
```

```python
from tiktok_uploader.upload import upload_video, upload_videos
from tiktok_uploader.auth import AuthBackend

# single video
upload_video('video.mp4', 
            description='this is my description', 
            cookies='cookies.txt')

# Multiple Videos
videos = [
    {
        'path': 'video.mp4', 
        'description': 'this is my description'
    },
    {
        'path': 'video2.mp4', 
        'description': 'this is also my description'
    }
]

auth = AuthBackend(cookies='cookies.txt')
upload_videos(videos=videos, auth=auth)
```

## ⬆ Uploading Videos

This library revolves around the `upload_videos` function which takes in a list of videos which have **filenames** and **descriptions** and are passed as follows:

```python
from tiktok_uploader.upload import upload_videos
from tiktok_uploader.auth import AuthBackend

videos = [
    {
        'video': 'video0.mp4',
        'description': 'Video 1 is about ...'
    },
    {
        'video': 'video1.mp4',
        'description': 'Video 2 is about ...'
    }
]

auth = AuthBackend(cookies='cookies.txt')
failed_videos = upload_videos(videos=videos, auth=auth)

for video in failed_videos: # each input video object which failed
    print(f'{video['video']} with description "{video['description']}" failed')
```

## 🫵 Mentions and Hashtags

Mentions and Hashtags now work so long as they are followed by a space. However, you as the user are responsible for verifying a mention or hashtag exists before posting

**Example:**
```python
from tiktok_uploader.upload import upload_video

upload_video('video.mp4', '#fyp @icespicee', 'cookies.txt')
```

## 🪡 Stitches, Duets and Comments

To set whether or not a video uploaded allows stitches, comments or duet, simply specify `comment`, `stitch` and/or `duet` as keyword arguments to `upload_video` or `upload_videos`.

```python
upload_video(..., comment=True, stitch=True, duet=True)
```

> Comments, Stiches and Duets are allowed by **default**

## 🔐 Authentication
Authentication uses your browser's cookies. This workaround was done due to TikTok's stricter stance on authetication by a Selenium-controlled browser.

Your `sessionid` is all that is required for authentication and can be passed as an argument to nearly any function

[🍪 Get cookies.txt](https://github.com/kairi003/Get-cookies.txt-LOCALLY) makes getting cookies in a [NetScape cookies format](http://fileformats.archiveteam.org/wiki/Netscape_cookies.txt).

After installing, open the extensions menu on [TikTok.com](https://tiktok.com/) and click `🍪 Get cookies.txt` to reveal your cookies. Select `Export As ⇩` and specify a location and name to save.

**Optionally**, `cookies_list` is a list of dictionaries with keys `name`, `value`, `domain`, `path` and `expiry` which allow you to pass your own browser cookies. 

**Example:**

```python
cookies_list = [
    {
        'name': 'sessionid',
        'value': '**your session id**',
        'domain': 'https://tiktok.com',
        'path': '/',
        'expiry': '10/8/2023, 12:18:58 PM'
    }
]

upload_video(..., cookies_list=cookies_list)
```

## 👀 Browser Selection

[Google Chrome](https://www.google.com/chrome) is the prefered browser for **TikTokUploader**. The default anti-detection techniques used in this packaged are optimized for this. However, if you wish to use a different browser you may specify the `browser` in `upload_video` or `upload_videos`.

```python
from tiktok_uploader.upload import upload_video

from random import choice

BROWSERS = [
    'chrome',
    'safari',
    'chromium',
    'edge',
    'firefox'
]

# randomly picks a web browser 
upload_video(..., browser=choice(BROWSERS))
```

✅ Supported Browsers:
- **Chrome** (Recommended)
- **Safari**
- **Chromium**
- **Edge**
- **FireFox** 

## 🚲 Custom WebDriver Driver Options

Default modifications to Selenium are applied which help it avoid being detected by TikTok. 

However, you **may** pass a custom driver configuration options. Simply pass `options` as a keyword argument to either `upload_video` or `upload_videos`. 

```python
from selenium.webdriver.chrome.options import Options

options = Options()

options.add_argument('start-maximized')

upload_videos(..., options=options)
```

> Note: Make sure to use the right selenium options for your browser

## 🤯 Headless Browsers

Headless browsing only works on Chrome. When using Chrome, adding the `--headless` flag using the CLI or passing `headless` as a keyword argument to `upload_video` or `upload_videos` is all that is required.

```python
upload_video(..., headless=True)
upload_videos(..., headless=True)
```

## 🔨 Initial Setup

[WebDriverManager](https://bonigarcia.dev/webdrivermanager/) is used to manage driver versions. 

On intial startup, you **may** be prompted to install the correct driver for your selected browser. However, for **Chrome** and **Edge** the driver is automatically installed.

# ♻ Examples

- **[Basic Upload Example](exmples/basic_upload.py):** Uses `upload_video` to make one post.

- **[Series Upload Example](examples/series_upload.py):** Uploads the same video multiple times using `upload_videos`.

- **[Scheduled Uploader Example](examples/example_series_upload.py):** Videos are read from a CSV file using [Pandas](https://pandas.pydata.org). A video upload attempt is made and **if and only if** it is successful will the video be marked as uploaded.

# 📝 Notes

This bot is not fool proof. Though I have not gotten an official ban, the video will fail to upload after too many uploads. In testing, waiting several hours was sufficient to fix this problem. For this reason, please thing of this more as a scheduled uploader for TikTok videos, rather than a spam bot.

# Accounts made with

- [@C_Span](https://www.tiktok.com/@c_span?lang=en) - A split-screen channel with mobile games below featuring clips from C-Span's YouTube channel
- [@habit_track](https://www.tiktok.com/@habit_track?lang=en) - A Reddit bot to see which SubReddit is most viral on TikTok

[^1]: If interested in Hatch, checkout the [website](https://hatch.pypa.io/latest/build/)
