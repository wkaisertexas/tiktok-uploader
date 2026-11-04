<p align="center">
<img src="https://github.com/wkaisertexas/tiktok-uploader/assets/27795014/f991fdc7-287a-4c3b-9a84-22c7ad8a57bf" alt="video working" />
</p>

<h1 align="center"> ⬆️ TikTok Uploader </h1>
<p align="center">A <strong>Playwright</strong>-based automated <strong>TikTok</strong> video uploader</p>

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
  - [🌐 Proxy](#proxy)
  - [📆 Schedule](#schedule)
  - [🛍️ Product Link](#product-link)
  - [🎵 Sounds](#sounds)
  - [📝 Drafts](#drafts)
  - [🤖 AI-generated Content Label](#ai-label)
  - [🚫 Restricted Content](#restricted-content)
  - [📦 Batch CLI](#batch-cli)
  - [📜 Logging](#logging)
  - [🔐 Authentication](#authentication)
  - [👀 Browser Selection](#browser-selection)
  - [🤯 Headless Browsers](#headless)
  - [🔨 Initial Setup](#initial-setup)
- [♻️ Examples](#examples)
- [📝 Notes](#notes)
- [Accounts made with](#made-with)

# Installation

A prerequisite to using this program is the installation of [Playwright](https://playwright.dev/) browsers.

<h2 id="macos-windows-and-linux">MacOS, Windows and Linux</h2>

Install Python 3 or greater from [python.org](https://www.python.org/downloads/)

<h3 id="pypi">Downloading from PyPI (Recommended)</h3>

Install `tiktok-uploader` using `pip`

```bash
pip install tiktok-uploader
playwright install
```

<h3 id="building-from-source">Building from source</h3>

Installing from source allows greater flexibility to modify the module's code to extend default behavior.

First, install [`uv`](https://docs.astral.sh/uv/getting-started/installation/) a really fast python package manager.

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

Next, clone the repository using `git`. Then change directories and run the project with `uv run tiktok-uploader`.

```bash
git clone https://github.com/wkaisertexas/tiktok-uploader
cd tiktok-uploader
uv sync
uv run playwright install
uv run tiktok-uploader
```

After `uv` installs the required packages, you should see something like the following:

```console
usage: tiktok-uploader [-h] -v VIDEO [-d DESCRIPTION] [-t SCHEDULE] [--proxy PROXY] [--product-id PRODUCT_ID]
                       [-c COOKIES] [-s SESSIONID] [-u USERNAME] [-p PASSWORD] [--attach]
```

<h1 id="usage">Usage</h1>

`tiktok-uploader` works by duplicating your browser's **cookies** which tricks **TikTok** into believing you are logged in on a remote-controlled browser.

<h2 id="cli"> 💻 Command Line Interface (CLI)</h2>

Using the CLI is as simple as calling `tiktok-uploader` with your videos: `path` (-v), `description`(-d), and `cookies` (-c).

```bash
tiktok-uploader -v video.mp4 -d "this is my escaped \"description\"" -c cookies.txt
```

```python
from tiktok_uploader.upload import TikTokUploader

# single video
uploader = TikTokUploader(cookies="cookies.txt")
uploader.upload_video("video.mp4", description="this is my description")

# Multiple Videos
videos = [
    {"path": "video.mp4", "description": "this is my description"},
    {"path": "video2.mp4", "description": "this is also my description"},
]

uploader = TikTokUploader(cookies="cookies.txt")
uploader.upload_videos(videos=videos)
```

<h2 id="uploading-videos"> ⬆ Uploading Videos</h2>

This library revolves around the `TikTokUploader` class which has a `upload_videos` function which takes in a list of videos which have **filenames** and **descriptions** and are passed as follows:

```python
from tiktok_uploader.upload import TikTokUploader

videos = [
    {"video": "video0.mp4", "description": "Video 1 is about ..."},
    {"video": "video1.mp4", "description": "Video 2 is about ..."},
]

uploader = TikTokUploader(cookies="cookies.txt")
failed_videos = uploader.upload_videos(videos=videos)

for video in failed_videos:  # each input video object which failed
    print(f"{video['video']} with description {video['description']} failed")
```

<h2 id="mentions-and-hashtags"> 🫵 Mentions and Hashtags</h2>

Mentions and Hashtags now work so long as they are followed by a space. However, **you** as the user **are responsible** for verifying a mention or hashtag exists before posting

```python
from tiktok_uploader.upload import TikTokUploader

uploader = TikTokUploader(cookies="cookies.txt")
uploader.upload_video("video.mp4", description="#fyp @icespicee")
```

<h2 id="stitches-duets-and-comments"> 🪡 Stitches, Duets and Comments</h2>

To set whether or not a video uploaded allows stitches, comments or duet, simply specify `comment`, `stitch` and/or `duet` as keyword arguments to `upload_video` or `upload_videos`.

```python
uploader = TikTokUploader(cookies="cookies.txt")
uploader.upload_video(..., comment=True, stitch=True, duet=True)
```

> Comments, Stitches and Duets are allowed by **default**

TikTok Studio has merged Duet and Stitch into a single "Reuse of content" checkbox. It is allowed only when both `stitch` and `duet` are, unless you set it directly with `reuse_of_content=True/False`. Each of these can also be set per video in `upload_videos`, overriding the keyword:

```python
uploader.upload_videos(
    [
        {"path": "video.mp4", "description": "...", "comment": False},
        {"path": "video2.mp4", "description": "..."},
    ],
    comment=True,
)
```

<h2 id="proxy"> 🌐 Proxy</h2>

To set a proxy, currently only works with chrome as the browser, allow user:pass auth.

```python
# proxy = {'user': 'myuser', 'pass': 'mypass', 'host': '111.111.111', 'port': '99'}  # user:pass
proxy = {"host": "111.111.111", "port": "99"}

uploader = TikTokUploader(cookies="cookies.txt", proxy=proxy)
uploader.upload_video(...)
```

<h2 id="schedule"> 📆 Schedule</h2>

The datetime to schedule the video will be treated with the UTC timezone; a timezone-aware datetime is converted to UTC. <br>
The scheduled datetime must be at least 20 minutes in the future and a maximum of 10 days.

```python
import datetime
from tiktok_uploader.upload import TikTokUploader

schedule = datetime.datetime(2020, 12, 20, 13, 00)

uploader = TikTokUploader(cookies="cookies.txt")
uploader.upload_video(..., schedule=schedule)
```

<h2 id="covers"> 🖼️ Covers</h2>

You can add a custom cover image when uploading a video. <br>
TikTok supports ".png", ".jpeg" and ".jpg".

```python
my_cover = "crazy_cover.jpg"

uploader = TikTokUploader(cookies="cookies.txt")
uploader.upload_video(..., cover=my_cover)
```

<h2 id="product-link"> 🛍️ Product Link</h2>

You can automatically add a product link to your uploaded video.

**Prerequisites:**

*   Your TikTok account must be eligible to add showcase products to your videos.
*   You need to obtain the product ID beforehand. To do this:
    1. Go to the TikTok upload page in your browser.
    2. Click the "Add link" button and select "Product".
    3. A modal will appear showing your available showcase products along with their IDs.
    4. Copy the ID of the product you want to link.

**Usage:**

Provide the `product_id` when calling the uploader.

**Command Line:**

```bash
tiktok-uploader -v video.mp4 -d "this is my description" -c cookies.txt --product-id YOUR_PRODUCT_ID
```

**Python:**

```python
from tiktok_uploader.upload import TikTokUploader

uploader = TikTokUploader(cookies="cookies.txt")

# Single video
uploader.upload_video(
    "video.mp4", description="this is my description", product_id="YOUR_PRODUCT_ID"
)

# Multiple videos
videos = [
    {
        "path": "video.mp4",
        "description": "this is my description",
        "product_id": "YOUR_PRODUCT_ID_1",  # Add product link to this video
    },
    {
        "path": "video2.mp4",
        "description": "this is also my description",  # No product link for this video
    },
]

uploader.upload_videos(videos=videos)
```

<h2 id="sounds"> 🎵 Sounds</h2>

Add a sound from TikTok's library with `sound_name`. The first result with that exact title is used (and, with `sound_artist`, whose artist contains it); with no exact match, the first result is used. A sound that cannot be set is logged and the video is posted without it.

```python
uploader.upload_video(..., sound_name="Espresso", sound_artist="Sabrina Carpenter")
```

```bash
tiktok-uploader -v video.mp4 -d "..." -c cookies.txt --sound-name "Espresso" --sound-artist "Sabrina Carpenter"
```

<h2 id="drafts"> 📝 Drafts</h2>

`draft=True` (CLI `--draft`) saves the video to the account's drafts instead of posting it. Drafts cannot be scheduled.

<h2 id="ai-label"> 🤖 AI-generated Content Label</h2>

`ai_label=True` turns on TikTok's "AI-generated content" label, and `ai_label=False` turns it off (CLI `--ai-label` / `--no-ai-label`). Left out, the label is left as TikTok sets it. If the label was asked for but cannot be set, the video is not posted.

<h2 id="restricted-content"> 🚫 Restricted Content</h2>

`skip_restricted=True` (CLI `--skip-restricted`) does not post a video when TikTok's content check warns that it "may be restricted"; it is reported as failed instead.

<h2 id="batch-cli"> 📦 Batch CLI</h2>

`tiktok-uploader-batch` uploads several videos in one browser session, optionally scheduled at a fixed interval. Descriptions pair with videos in order; the sound and post options apply to every video.

```bash
tiktok-uploader-batch -v a.mp4 -v b.mp4 -v c.mp4 -d "first" -d "second" -d "third" \
    --schedule-from "2026-03-20 10:00" --timezone Europe/London --schedule-interval 240 \
    -c cookies.txt
```

`--schedule-from` is read in `--timezone` (default UTC), and the last video must still fall within TikTok's 10-day limit. The single-video `-t/--schedule` is read as UTC.

Both commands exit with status 1 if any video failed.

<h2 id="logging"> 📜 Logging</h2>

The uploader logs on the `tiktok_uploader` logger and leaves the handlers and level to your application:

- **INFO**: one line per video: `Posted <path>`, `Scheduled <path> for <time> UTC` or `Saved <path> as a draft`, then `Uploaded 3 of 4 videos` for a batch
- **WARNING**: a step that was skipped while the upload went on, such as a sound, cover or product link that could not be set
- **ERROR**: `Failed to upload <path>: <reason>` or `Skipped <path>: <reason>`
- **DEBUG**: every step of the form, and the traceback of each failure

```python
import logging

logging.basicConfig(level=logging.INFO)
```

With no logging configured, Python still prints warnings and errors. The CLI prints every step.

<h2 id="authentication"> 🔐 Authentication</h2>

Authentication uses your browser's cookies. This workaround was done due to TikTok's stricter stance on authentication by a Playwright-controlled browser.

Your `sessionid` is all that is required for authentication and can be passed as an argument to nearly any function

[🍪 Get cookies.txt](https://github.com/kairi003/Get-cookies.txt-LOCALLY) makes getting cookies in a [NetScape cookies format](http://fileformats.archiveteam.org/wiki/Netscape_cookies.txt).

After installing, open the extensions menu on [TikTok.com](https://tiktok.com/) and click `🍪 Get cookies.txt` to reveal your cookies. Select `Export As ⇩` and specify a location and name to save.

**Alternatively**, if you don't want to use an extension, you can use the following JavaScript line in the Developer Console (F12) on TikTok.com:

1. Copy the code below:
```javascript
(function(){const c=document.cookie.split("; ").map(x=>{const i=x.indexOf("=");return ".tiktok.com\tTRUE\t/\tFALSE\t2147483647\t"+x.substring(0,i)+"\t"+x.substring(i+1)}).join("\n");const b=new Blob([c],{type:"text/plain"});const a=document.createElement("a");a.href=URL.createObjectURL(b);a.download="cookies.txt";a.textContent="Download cookies.txt";a.style="position:fixed;top:20px;right:20px;z-index:9999;padding:10px;background:#fe2c55;color:white;border-radius:5px;text-decoration:none;font-weight:bold;font-family:sans-serif;";document.body.appendChild(a);if(!document.cookie.includes("sessionid"))alert("⚠️ sessionid is missing (HttpOnly). You must add it manually!");})();
```
2. Paste it into the console and press Enter.
3. A "Download cookies.txt" button will appear in the top-right corner. Click it to download your cookies file.
4. If alerted about the missing `sessionid`, follow the manual steps below.

> **⚠️ Important:** Browsers often hide the `sessionid` cookie from JavaScript (HttpOnly). If the script alerts you about this:
> 1. Go to **Application** > **Cookies** in DevTools.
> 2. Find `sessionid` and copy its value.
> 3. Manually add it to your downloaded `cookies.txt`: `.tiktok.com	TRUE	/	FALSE	2147483647	sessionid	YOUR_SESSION_ID`

```python
uploader = TikTokUploader(cookies="cookies.txt")
uploader.upload_video(...)
```

**Optionally**, `cookies_list` is a list of dictionaries with keys `name`, `value`, `domain`, `path` and `expiry` which allow you to pass your own browser cookies.

```python
cookies_list = [
    {
        "name": "sessionid",
        "value": "**your session id**",
        "domain": "https://tiktok.com",
        "path": "/",
        "expiry": "10/8/2023, 12:18:58 PM",
    },
    # the rest of your cookies all in a list
]

uploader = TikTokUploader(cookies_list=cookies_list)
uploader.upload_video(...)
```

**Without any login**, the cookies file named by the `TIKTOK_COOKIES` environment variable is used:

```bash
export TIKTOK_COOKIES=~/cookies.txt
```

<h2 id="browser-selection"> 👀 Browser Selection</h2>

[Google Chrome](https://www.google.com/chrome) is the preferred browser for **TikTokUploader**. The default anti-detection techniques used in this packaged are optimized for this. However, if you wish to use a different browser you may specify the `browser` in `TikTokUploader`.

```python
from tiktok_uploader.upload import TikTokUploader

from random import choice

BROWSERS = ["chrome", "safari", "chromium", "edge", "firefox"]

# randomly picks a web browser
uploader = TikTokUploader(cookies="cookies.txt", browser=choice(BROWSERS))
uploader.upload_video(...)
```

✅ Supported Browsers:

- **Chrome** (Recommended)
- **Safari**
- **Chromium**
- **Edge**
- **FireFox**

<h2 id="headless"> 🤯 Headless Browsers </h2>

When using Chrome, adding the `--headless` flag using the CLI or passing `headless` as a keyword argument to `TikTokUploader` is all that is required.

```python
uploader = TikTokUploader(cookies="cookies.txt", headless=True)
uploader.upload_video(...)
```

<h2 id="initial-setup"> 🔨 Initial Setup</h2>

You must install Playwright browsers:

```bash
playwright install
```

<h2 id="examples"> ♻ Examples</h2>

- **[Basic Upload Example](examples/basic_upload.py):** Uses `upload_video` to make one post.

- **[Multiple Videos At Once](examples/multiple_videos_at_once.py):** Uploads the same video multiple times using `upload_videos`.

- **[Series Upload Example](examples/series_upload.py):** Videos are read from a CSV file using [Pandas](https://pandas.pydata.org). A video upload attempt is made and **if and only if** it is successful will the video be marked as uploaded.

<h2 id="notes"> 📝 Notes</h2>

This bot is **not fool proof**. Though I have not gotten an official ban, the video will fail to upload after too many uploads. In testing, waiting several hours was sufficient to fix this problem. For this reason, please think of this more as a scheduled uploader for TikTok videos, rather than a **spam bot.**

> [!IMPORTANT]
> If you like this project, please ⭐ it on GitHub to show your support! ❤️

![Star History Chart](https://api.star-history.com/svg?repos=wkaisertexas/tiktok-uploader&type=Date)
