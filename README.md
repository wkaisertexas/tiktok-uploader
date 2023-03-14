# ⬆️ TikTok Uploader

![Forks](https://img.shields.io/github/forks/wkaisertexas/tiktok-uploader)
![Stars](https://img.shields.io/github/stars/wkaisertexas/tiktok-uploader)
![Forks](https://img.shields.io/github/watchers/wkaisertexas/tiktok-uploader)

> A **Selenium**-based automated **TikTok** video uploader

# Installation

A prequisite to using this program is the installation of a [Selenium-compatable](https://www.selenium.dev/documentation/webdriver/getting_started/install_drivers/) web browser. [Google Chrome](https://www.google.com/chrome/) is recommended.

## MacOS, Windows and Linux

Install Python 3 or greater from [python.org](https://www.python.org/downloads/)

### Downloading from PyPI (Recommended)

Install `tiktok-uploader` using `pip`

```bash
$ pip install tiktok-uploader
```

## Building from source

Installing from source allows greater flexability to modify the module's code to extend default behavior. 

First, `clone` and move into the repository. Next, install `hatch`, the build tool used for this project [^1]. Then, `build` the projet. Finally, `install` the project with the `-e` or editable flag.  
```bash
$ git clone https://github.com/wkaisertexas/tiktok-uploader.git
$ cd tiktok-uploader
$ pip install hatch
$ hatch build
$ pip install -e . 
```

# Usage

While TikTok is strict about login in from Selenium, simply copying your session tokens is enough to bypass this restriction and be able to upload your videos.

## 💻 Commmand Line Interface (CLI)

Using the CLI is as simple as calling `tiktok-uploader` with your videos: `path` (-v), `description`(-d) and `cookies` (-c)

```bash
$ tiktok-uploader \
-v video.mp4 \
-d "this is my escaped \"description\"" \
-c cookies.txt
```

```python
from tiktok_uploader.upload import upload_video, upload_videos
from tiktok_uploaader.auth import AuthBackend

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

## ⬆️ Uploading videos

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

Example:

```python
from tiktok_uploader.upload import upload_video

upload_video('video.mp4', '#fyp @icespicee', 'cookies.txt')
```

## 🪡 Stitches, Duets and Comments

To set whether or not a video uploaded allows stitches, comments or duet, simply specifiy `comment`, `stitch` and `duet` as keyword arguments to `upload_video` or `upload_videos`.

```python
upload_video(..., comment=True, stitch=True, duet=True)
```

> Comments, Stiches and Duets are allowed by **default**

## 🔐 Authentication
Authentication uses your browser's cookies. This workaround was done due to TikTok's stricter stance on authetication. 

To get your cookies, download [🍪 Get cookies.txt](https://chrome.google.com/webstore/detail/get-cookiestxt/bgaddhkoddajcdgocldbbfleckgcbcid?hl=en) from the **Chrome Web Store**.

Open the extensions menu on TikTok and click `🍪 Get cookies.txt` to reveal your cookies. Select `Export As ⇩` and specify a location and name to save.

> Optionally, if you would like to pass your own cookies you may do as an array of dictionaries with keys `name`, `value`, `domain`, `path` and `expiry` 

## 👀 Browser Selection

[Google Chrome](https://www.google.com/chrome) is the prefered browser for **TikTokUploader**. The default anti-detection techniques used in this packaged are optimized for this. However, if you wish to use a different browser you may specify that in `upload_videos`.

```python
from tiktok_uploader.upload import upload_video

from random import choice

BROWSERS = ['chrome', 'safari', 'chromium', 'edge', 'firefox']

# randomly picks a web browser 
upload_video(browser=choice(BROWSERS))
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

upload_videos(options=options)
```

> Note: Make sure to use the right selenium options for your browser

## 🤯 Headless Browsers

**Headless browsers do not work at this time** 

> If more experienced in Webscraping, I would really appreciate helping make this work. [undetected-chromedriver](https://github.com/ultrafunkamsterdam/undetected-chromedriver) was already tried and did not work

## 🔨 Initial Setup

[WebDriverManager](https://bonigarcia.dev/webdrivermanager/) is used to manage driver versions. 

On intial startup, you **may** be prompted to install the correct driver for your selected broswer. However, for **Chrome** and **Edge** this works without issue.

# ♻️ Examples

[Scheduled Uploader]() is an automation which is based off this package. Videos are read from a CSV file using [Pandas](https://pandas.pydata.org). A video upload attempt is made and **if and only if** it is successfull will the video be marked as uploaded.

## 📝 Notes

This bot is not fool proof. Though I have not gotten an official ban, when the video will fail to upload after too many uploads. When testing, waiting several hours was sufficient to fix this problem. For this reason, please thing of this more as a scheduled uploader for TikTok videos, rather than a spam bot.

> Please think of this package as more of a scheduled uploader for TikTok videos, rather than a spam bot

## Accounts made using `tiktok-uploader`

- [@C_Span](https://www.tiktok.com/@c_span?lang=en) - A split-screen channel with mobile games below featuring clips from C-Span's YouTube channel
- [@habit_track](https://www.tiktok.com/@habit_track?lang=en) - A generic Dhar Mann TikTok bot

[^1]: If interested in Hatch, checkout the [website](https://hatch.pypa.io/latest/build/)