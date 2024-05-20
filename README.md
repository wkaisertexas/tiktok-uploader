<p align="center">
<img src="https://github.com/wkaisertexas/tiktok-uploader/assets/27795014/f991fdc7-287a-4c3b-9a84-22c7ad8a57bf" alt="video working" />
</p>

<h1 align="center"> ⬆️ TikTok Uploader </h1>
<p align="center">A <strong>Selenium</strong>-based automated <strong>TikTok</strong> video uploader</p>

<p align="center">
  <a href="https://github.com/wkaisertexas/tiktok-uploader"><strong>English</strong></a> ·
  <a href="https://github.com/wkaisertexas/tiktok-uploader/blob/main/README.zh-Hans.md"><strong>Chinese (Simplified)</strong></a> ·
  <a href="https://github.com/wkaisertexas/tiktok-uploader/blob/main/README.fr.md"><strong>French</strong></a> ·
  <a href="https://github.com/wkaisertexas/tiktok-uploader/blob/main/README.es.md"><strong>Spanish</string></a> ·
  <a href="https://github.com/wkaisertexas/tiktok-uploader/blob/main/README.de.md"><strong>German</strong></a>
</p>

<p align="center">
  <img alt="Forks" src="https://img.shields.io/github/forks/wkaisertexas/tiktok-uploader" />
  <img alt="Stars" src="https://img.shields.io/github/stars/wkaisertexas/tiktok-uploader" />
  <img alt="Watchers" src="https://img.shields.io/github/watchers/wkaisertexas/tiktok-uploader" />
</p>

<h1>Table of Contents</h1>

- [Installation](#installation)
  - [MacOS, Windows and Linux](#macos-windows-and-linux)
    - [Downloading from PyPI (Recommended)](#pypi)
    - [Building from source](#building-from-source)
- [Usage](#usage)
  - [💻 Command Line Interface (CLI)](#cli)
  - [⬆ Uploading Videos](#uploading-videos)
  - [🫵 Mentions and Hashtags](#mentions-and-hashtags)
  - [🪡 Stitches, Duets and Comments](#stitches-duets-and-comments)
  - [🔐 Authentication](#authentication)
  - [👀 Browser Selection](#browser-selection)
  - [🚲 Custom WebDriver Options](#custom-webdriver)
  - [🤯 Headless Browsers](#headless)
  - [🔨 Initial Setup](#initial-setup)
- [♻️ Examples](#examples)
- [📝 Notes](#notes)
- [Accounts made with](#made-with)

# Installation

A prequisite to using this program is the installation of a [Selenium-compatible](https://www.selenium.dev/documentation/webdriver/getting_started/install_drivers/) web browser. [Google Chrome](https://www.google.com/chrome/) is recommended.

<h2 id="macos-windows-and-linux">MacOS, Windows and Linux</h2>

Install Python 3 or greater from [python.org](https://www.python.org/downloads/)

<h3 id="pypi">Downloading from PyPI (Recommended)</h3>

Install `tiktok-uploader` using `pip`

```bash
pip install tiktok-uploader
```

<h3 id="building-from-source">Building from source</h3>

Installing from source allows greater flexibility to modify the module's code to extend default behavior.

First, `clone` and move into the repository. Next, install `hatch`, the build tool used for this project [^1]. Then, `build` the project. Finally, `install` the project with the `-e` or editable flag.

```console
git clone https://github.com/wkaisertexas/tiktok-uploader.git
cd tiktok-uploader
pip install hatch
hatch build
pip install -e .
```

<h1 id="usage">Usage</h1>

`tiktok-uploader` works by duplicating your browser's **cookies** which tricks **TikTok** into believing you are logged in on a remote-controlled browser.

<h2 id="cli"> 💻 Command Line Interface (CLI)</h2>

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

<h2 id="uploading-videos"> ⬆ Uploading Videos</h2>

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

<h2 id="mentions-and-hashtags"> 🫵 Mentions and Hashtags</h2>

Mentions and Hashtags now work so long as they are followed by a space. However, **you** as the user **are responsible** for verifying a mention or hashtag exists before posting

**Example:**

```python
from tiktok_uploader.upload import upload_video

upload_video('video.mp4', '#fyp @icespicee', 'cookies.txt')
```

<h2 id="stitches-duets-and-comments"> 🪡 Stitches, Duets and Comments</h2>

To set whether or not a video uploaded allows stitches, comments or duet, simply specify `comment`, `stitch` and/or `duet` as keyword arguments to `upload_video` or `upload_videos`.

```python
upload_video(..., comment=True, stitch=True, duet=True)
```

> Comments, Stitches and Duets are allowed by **default**

<h2 id="proxy"> 🌐 Proxy</h2>

To set a proxy, currently only works with chrome as the browser, allow user:pass auth.

```python
# proxy = {'user': 'myuser', 'pass': 'mypass', 'host': '111.111.111', 'port': '99'}  # user:pass
proxy = {'host': '111.111.111', 'port': '99'}
upload_video(..., proxy=proxy)
```

<h2 id="schedule"> 📆 Schedule</h2>

The datetime to schedule the video will be treated with the UTC timezone. <br>
The scheduled datetime must be at least 20 minutes in the future and a maximum of 10 days.

```python
import datetime
schedule = datetime.datetime(2020, 12, 20, 13, 00)
upload_video(..., schedule=schedule)
```

<h2 id="authentication"> 🔐 Authentication</h2>

Authentication uses your browser's cookies. This workaround was done due to TikTok's stricter stance on authentication by a Selenium-controlled browser.

Your `sessionid` is all that is required for authentication and can be passed as an argument to nearly any function

[🍪 Get cookies.txt](https://github.com/kairi003/Get-cookies.txt-LOCALLY) makes getting cookies in a [NetScape cookies format](http://fileformats.archiveteam.org/wiki/Netscape_cookies.txt).

After installing, open the extensions menu on [TikTok.com](https://tiktok.com/) and click `🍪 Get cookies.txt` to reveal your cookies. Select `Export As ⇩` and specify a location and name to save.

```python
upload_video(..., cookies='cookies.txt')
```

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
    },
    # the rest of your cookies all in a list
]

upload_video(..., cookies_list=cookies_list)
```

<h2 id="browser-selection"> 👀 Browser Selection</h2>

[Google Chrome](https://www.google.com/chrome) is the preferred browser for **TikTokUploader**. The default anti-detection techniques used in this packaged are optimized for this. However, if you wish to use a different browser you may specify the `browser` in `upload_video` or `upload_videos`.

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

<h2 id="custom-webdriver"> 🚲 Custom WebDriver Options</h2>

Default modifications to Selenium are applied which help it avoid being detected by TikTok.

However, you **may** pass a custom driver configuration options. Simply pass `options` as a keyword argument to either `upload_video` or `upload_videos`.

```python
from selenium.webdriver.chrome.options import Options

options = Options()

options.add_argument('start-maximized')

upload_videos(..., options=options)
```

> Note: Make sure to use the right selenium options for your browser

<h2 id="headless"> 🤯 Headless Browsers </h2>

Headless browsing only works on Chrome. When using Chrome, adding the `--headless` flag using the CLI or passing `headless` as a keyword argument to `upload_video` or `upload_videos` is all that is required.

```python
upload_video(..., headless=True)
upload_videos(..., headless=True)
```

<h2 id="initial-setup"> 🔨 Initial Setup</h2>

[WebDriverManager](https://bonigarcia.dev/webdrivermanager/) is used to manage driver versions.

On initial startup, you **may** be prompted to install the correct driver for your selected browser. However, for **Chrome** and **Edge** the driver is automatically installed.

<h2 id="examples"> ♻ Examples</h2>

- **[Basic Upload Example](examples/basic_upload.py):** Uses `upload_video` to make one post.

- **[Multiple Videos At Once](examples/multiple_videos_at_once.py):** Uploads the same video multiple times using `upload_videos`.

- **[Series Upload Example](examples/series_upload.py):** Videos are read from a CSV file using [Pandas](https://pandas.pydata.org). A video upload attempt is made and **if and only if** it is successful will the video be marked as uploaded.

<h1 id="notes"> 📝 Notes</h1>

This bot is **not fool proof**. Though I have not gotten an official ban, the video will fail to upload after too many uploads. In testing, waiting several hours was sufficient to fix this problem. For this reason, please think of this more as a scheduled uploader for TikTok videos, rather than a **spam bot.**

> If you like this project, please ⭐ it on GitHub to show your support! ❤️

![Star History Chart](https://api.star-history.com/svg?repos=wkaisertexas/tiktok-uploader&type=Date)

[^1]: If interested in Hatch, checkout the [website](https://hatch.pypa.io/latest/build/)
