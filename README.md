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
  - [🤖 Auto Captions](#auto-captions)
  - [🙈 Drafts](#drafts)
  - [🤯 AI-Generated Content Label](#ai-label)
  - [🫵 Mentions and Hashtags](#mentions-and-hashtags)
  - [🪡 Stitches, Duets and Comments](#stitches-duets-and-comments)
  - [🌐 Proxy](#proxy)
  - [📆 Schedule](#schedule)
  - [🛍️ Product Link](#product-link)
  - [🔐 Authentication](#authentication)
  - [👀 Browser Selection](#browser-selection)
  - [🤯 Headless Browsers](#headless)
  - [🔨 Initial Setup](#initial-setup)
- [♻️ Examples](#examples)
- [📝 Notes](#notes)
- [📡 MCP Server](#mcpserver)
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
uploader = TikTokUploader(cookies='cookies.txt')
uploader.upload_video('video.mp4', description='this is my description')

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

uploader = TikTokUploader(cookies='cookies.txt')
uploader.upload_videos(videos=videos)
```

<h2 id="uploading-videos"> ⬆ Uploading Videos</h2>

This library revolves around the `TikTokUploader` class which has a `upload_videos` function which takes in a list of videos which have **filenames** and **descriptions** and are passed as follows:

```python
from tiktok_uploader.upload import TikTokUploader

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

uploader = TikTokUploader(cookies='cookies.txt')
failed_videos = uploader.upload_videos(videos=videos)

for video in failed_videos:  # each input video object which failed
    print(f"{video['video']} with description {video['description']} failed")
```

<h2 id="auto-captions"> 🤖 Auto Captions</h2>

If you do not pass a description, an English caption with hashtags is written from the video's original title (its `.txt` sidecar or its filename) by an OpenAI-compatible model. The model is configured in the `[captions]` section of `config.toml`:

```toml
[captions]
endpoint = "https://inference.do-ai.run/v1/chat/completions" # any OpenAI-compatible API
model = "anthropic-claude-sonnet-5.5"
api_key_env = "MODEL_ACCESS_KEY" # environment variable holding the API key
min_hashtags = 3
max_hashtags = 5
timeout = 30 # seconds
```

The environment variable named by `api_key_env` must be set. If the model can not be reached, the original title is used as the caption instead. Skip caption generation for one upload with the CLI flag `--no-auto-caption`.

<h2 id="drafts"> 🙈 Drafts</h2>

Save a video to your TikTok drafts instead of posting it by passing `draft=True` to `upload_video` / `upload_videos`, or `--draft` on the CLI:

```python
uploader = TikTokUploader(cookies='cookies.txt')
uploader.upload_video('video.mp4', description='work in progress', draft=True)
```

Drafts can not be scheduled: combining `draft` with `schedule` raises an error.

<h2 id="ai-label"> 🤯 AI-Generated Content Label</h2>

Uploads are posted with TikTok's "AI-generated content" label **on** by default. Turn it off for one upload with `ai_label=False` (CLI: `--no-ai-label`):

```python
uploader.upload_video('video.mp4', description='shot on my phone', ai_label=False)
```

If the label can not be set the way you asked, the upload fails instead of posting with the wrong label.

<h2 id="mentions-and-hashtags"> 🫵 Mentions and Hashtags</h2>

Mentions and Hashtags now work so long as they are followed by a space. However, **you** as the user **are responsible** for verifying a mention or hashtag exists before posting

```python
from tiktok_uploader.upload import TikTokUploader

uploader = TikTokUploader(cookies='cookies.txt')
uploader.upload_video('video.mp4', description='#fyp @icespicee')
```

<h2 id="stitches-duets-and-comments"> 🪡 Stitches, Duets and Comments</h2>

To set whether or not a video uploaded allows stitches, comments or duet, simply specify `comment`, `stitch` and/or `duet` as keyword arguments to `upload_video` or `upload_videos`.

```python
uploader = TikTokUploader(cookies='cookies.txt')
uploader.upload_video(..., comment=True, stitch=True, duet=True)
```

> Comments, Stitches and Duets are allowed by **default**

<h2 id="proxy"> 🌐 Proxy</h2>

To set a proxy, currently only works with chrome as the browser, allow user:pass auth.

```python
# proxy = {'user': 'myuser', 'pass': 'mypass', 'host': '111.111.111', 'port': '99'}  # user:pass
proxy = {'host': '111.111.111', 'port': '99'}

uploader = TikTokUploader(cookies='cookies.txt', proxy=proxy)
uploader.upload_video(...)
```

<h2 id="schedule"> 📆 Schedule</h2>

The datetime to schedule the video will be treated with the UTC timezone. <br>
The scheduled datetime must be at least 20 minutes in the future and a maximum of 10 days.

```python
import datetime
from tiktok_uploader.upload import TikTokUploader

schedule = datetime.datetime(2020, 12, 20, 13, 00)

uploader = TikTokUploader(cookies='cookies.txt')
uploader.upload_video(..., schedule=schedule)
```

<h2 id="covers"> 🖼️ Covers</h2>

You can add a custom cover image when uploading a video. <br>
TikTok supports ".png", ".jpeg" and ".jpg".

```python
my_cover = "crazy_cover.jpg"

uploader = TikTokUploader(cookies='cookies.txt')
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

uploader = TikTokUploader(cookies='cookies.txt')

# Single video
uploader.upload_video('video.mp4',
            description='this is my description',
            product_id='YOUR_PRODUCT_ID')

# Multiple videos
videos = [
    {
        'path': 'video.mp4',
        'description': 'this is my description',
        'product_id': 'YOUR_PRODUCT_ID_1' # Add product link to this video
    },
    {
        'path': 'video2.mp4',
        'description': 'this is also my description' # No product link for this video
    }
]

uploader.upload_videos(videos=videos)
```

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
uploader = TikTokUploader(cookies='cookies.txt')
uploader.upload_video(...)
```

**Optionally**, `cookies_list` is a list of dictionaries with keys `name`, `value`, `domain`, `path` and `expiry` which allow you to pass your own browser cookies.

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

uploader = TikTokUploader(cookies_list=cookies_list)
uploader.upload_video(...)
```

<h2 id="browser-selection"> 👀 Browser Selection</h2>

[Google Chrome](https://www.google.com/chrome) is the preferred browser for **TikTokUploader**. The default anti-detection techniques used in this packaged are optimized for this. However, if you wish to use a different browser you may specify the `browser` in `TikTokUploader`.

```python
from tiktok_uploader.upload import TikTokUploader

from random import choice

BROWSERS = [
    'chrome',
    'safari',
    'chromium',
    'edge',
    'firefox'
]

# randomly picks a web browser
uploader = TikTokUploader(cookies='cookies.txt', browser=choice(BROWSERS))
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
uploader = TikTokUploader(cookies='cookies.txt', headless=True)
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

<h2 id="mcpserver"> 📡 MCP Server</h2>

This library ships a built-in [Model Context Protocol (MCP)](https://modelcontextprotocol.org/) server that lets an LLM-powered tool (like Claude or Codex) drive your uploads directly: list the videos in a folder, ask for a caption suggestion, and then post, schedule, or draft a video — all without touching the browser yourself.

Unlike the CLI, the MCP server does **not** take descriptions as positional arguments. Instead, it exposes three tools:

| Tool | Description |
|------|-------------|
| `list_videos(directory)` | Lists the uploadable videos in a directory, newest first, with each video's path and original title |
| `suggest_caption(video_path)` | Writes an English TikTok caption with hashtags from the video's original title, **without uploading anything** |
| `upload_video(video_path, description?, schedule?, draft?, ai_label?, visibility?)` | Posts, schedules, or saves a video to drafts |

**Starting the server:**

```bash
tiktok-uploader-mcp
```

Once running, an MCP client (such as the `claude` MCP client or any MCP host) can connect to the server over its configured transport (stdio by default) and call the tools above.

**Prerequisite configuration:**

The MCP server reuses the cookies-based authentication described in [🔐 Authentication](#authentication), plus the caption-generation settings from [🤖 Auto Captions](#auto-captions):

*   Set the TikTok cookies (either the `TIKTOK_COOKIES` environment variable or the default cookies file) so the server can log in.
*   The variable named by `api_key_env` in the `[captions]` section of `config.toml` (its API key) must be set in the environment for `suggest_caption` to generate a caption.

<table>
<tr><th>Variable</th><th>Purpose</th></tr>
<tr><td><code>TIKTOK_COOKIES</code></td><td>Path to the NetScape-format cookies file to authenticate with</td></tr>
<tr><td><code>captions.api_key_env</code> <em>(from <code>config.toml</code>)</em></td><td>Name of the environment variable holding the OpenAI-compatible API key used to write the suggested caption</td></tr>
</table>

The tools are plain functions, so you can also call them directly from your own code:

```python
from tiktok_uploader import mcp_server

videos = mcp_server.list_videos(directory="downloads")
path = videos[0]["path"]

# write an English caption + hashtags from the video's original title
caption = mcp_server.suggest_caption(path)

# post the video with the generated caption
result = mcp_server.upload_video(path, description=caption)
```

**Scheduling and drafts** work through the same tool: pass `schedule` (a UTC `"YYYY-MM-DD HH:MM"`, 20 minutes to 10 days ahead) to post later, or `draft=True` to save to your drafts instead of posting.

![Star History Chart](https://api.star-history.com/svg?repos=wkaisertexas/tiktok-uploader&type=Date)
