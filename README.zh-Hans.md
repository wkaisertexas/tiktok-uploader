<p align="center">
<img src="https://github.com/wkaisertexas/tiktok-uploader/assets/27795014/f991fdc7-287a-4c3b-9a84-22c7ad8a57bf" alt="video working" />
</p>

<h1 align="center"> ⬆️ TikTok上传器 </h1>
<p align="center">一个基于<strong>Selenium</strong>的自动化<strong>TikTok</strong>视频上传器</p>

<p align="center">
  <a href="https://github.com/wkaisertexas/tiktok-uploader"><strong>英文</strong></a> ·
  <a href="https://github.com/wkaisertexas/tiktok-uploader/blob/main/README.zh-Hans.md"><strong>简体中文</strong></a> ·
  <a href="https://github.com/wkaisertexas/tiktok-uploader/blob/main/README.fr.md"><strong>法文</strong></a> ·
  <a href="https://github.com/wkaisertexas/tiktok-uploader/blob/main/README.es.md"><strong>西班牙文</strong></a> ·
  <a href="https://github.com/wkaisertexas/tiktok-uploader/blob/main/README.de.md"><strong>德文</strong></a>
</p>

> ➡️ 在GitHub上查看[tranzlate](https://github.com/wkaisertexas/tranzlate/blob/main/README.zh-Hans.md)，这是一个使用[ChatGPT](https://chat.openai.com)翻译文本的工具。

<p align="center">
  <img alt="Forks" src="https://img.shields.io/github/forks/wkaisertexas/tiktok-uploader" />
  <img alt="Stars" src="https://img.shields.io/github/stars/wkaisertexas/tiktok-uploader" />
  <img alt="Watchers" src="https://img.shields.io/github/watchers/wkaisertexas/tiktok-uploader" />
</p>

<h1>目录</h1>

- [安装](#installation)
  - [MacOS、Windows 和 Linux](#macos-windows-and-linux)
    - [从PyPI下载 (推荐)](#pypi)
    - [从源码构建](#building-from-source)
- [使用方式](#usage)
  - [💻 命令行界面 (CLI)](#cli)
  - [⬆ 上传视频](#uploading-videos)
  - [🫵 提及和主题标签](#mentions-and-hashtags)
  - [🪡 接缝，二人行和评论](#stitches-duets-and-comments)
  - [🔐 认证](#authentication)
  - [👀 浏览器选择](#browser-selection)
  - [🚲 自定义WebDriver选项](#custom-webdriver)
  - [🤯 无头浏览器](#headless)
  - [🔨 初始设置](#initial-setup)
- [♻️ 实例](#examples)
- [📝 批注](#notes)
- [账户制作](#made-with)

# 安装

使用此程序的前提是安装一个[Selenium兼容](https://www.selenium.dev/documentation/webdriver/getting_started/install_drivers/)的网络浏览器。推荐使用[Google Chrome](https://www.google.com/chrome/)。

<h2 id="macos-windows-and-linux">MacOS, Windows 和 Linux</h2>

从[python.org](https://www.python.org/downloads/)安装Python 3或更高版本。

<h3 id="pypi">从PyPI下载（推荐）</h3>

使用 `pip` 安装 `tiktok-uploader`

```bash
pip install tiktok-uploader
```

<h3 id="building-from-source">从源码构建</h3>

从源码安装允许更大的灵活性来修改模块的代码以扩展默认行为。

首先， `clone`并移动到存储库。然后，安装 `hatch`，这是此项目使用的构建工具[^1]。然后，`build`项目。最后，使用 `-e` 或可编辑标志 `install` 项目。

```console
git clone https://github.com/wkaisertexas/tiktok-uploader.git
cd tiktok-uploader
pip install hatch
hatch build
pip install -e .
```

<h1 id="usage">使用方式</h1>

`tiktok-uploader`的工作原理是复制您浏览器的**cookies**，这使**TikTok**认为你是在一个远程控制的浏览器上登录的。

<h2 id="cli"> 💻 命令行界面 (CLI)</h2>

使用CLI就像使用您的`path`（-v）、`description`（-d）和`cookies`（-c）调用`tiktok-uploader`一样简单:

```bash
tiktok-uploader -v video.mp4 -d "this is my escaped \"description\"" -c cookies.txt
```

```python
from tiktok_uploader.upload import upload_video, upload_videos
from tiktok_uploader.auth import AuthBackend

# 单个视频
upload_video('video.mp4',
            description='this is my description',
            cookies='cookies.txt')

# 多个视频
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

<h2 id="uploading-videos"> ⬆ 上传视频</h2>

这个库围绕`upload_videos`函数展开，该函数接收一个包含**文件名**和**描述**的视频列表，如下所示：

```python
from tiktok_uploader.upload import upload_videos
from tiktok_uploader.auth import AuthBackend

videos = [
    {
        'video': 'video0.mp4',
        'description': 'Video 1 关于 ……'
    },
    {
        'video': 'video1.mp4',
        'description': 'Video 2 关于 ……'
    }
]

auth = AuthBackend(cookies='cookies.txt')
failed_videos = upload_videos(videos=videos, auth=auth)

for video in failed_videos: #每个上传失败的输入视频对象 
    print(f'{video['video']} with description "{video['description']}" failed')
```

<h2 id="mentions-and-hashtags"> 🫵 提及和主题标签</h2>

现在只要在后面跟着空格，提及和主题标签都可以工作。然而，你作为用户有责任在发布前验证提及或主题标签是否存在。

**例子:**

```python
from tiktok_uploader.upload import upload_video

upload_video('video.mp4', '#fyp @icespicee', 'cookies.txt')
```

<h2 id="stitches-duets-and-comments"> 🪡 接缝，二人行和评论</h2>

要设置上传的视频是否允许接缝、评论或二人行，只需分别将 `comment`、`stitch` 和/或 `duet` 作为关键词参数传递给 `upload_video` 或 `upload_videos`。

```python
upload_video(..., comment=True, stitch=True, duet=True)
```

> 默认情况下，允许评论，接缝和二人行。

<h2 id="proxy"> 🌐 代理</h2>

要设置一个代理，只能在浏览器设置为chrome时工作，允许用户:密码认证。

```python
# proxy = {'user': 'myuser', 'pass': 'mypass', 'host': '111.111.111', 'port': '99'}  # user:pass
proxy = {'host': '111.111.111', 'port': '99'}
upload_video(..., proxy=proxy)
```

<h2 id="schedule"> 📆 计划</h2>

计划视频的datetime将被视为UTC时区。 
计划的时间必须至少在未来的20分钟以内，最多为10天。

```python
import datetime
schedule = datetime.datetime(2020, 12, 20, 13, 00)
upload_video(..., schedule=schedule)
```

<h2 id="authentication"> 🔐 认证</h2>

认证使用浏览器的cookies。这种变通方法是由于TikTok对由Selenium控制的浏览器的身份验证持更严格的立场。

您的 `sessionid`是认证所需的所有内容，可以作为参数传递给几乎任何函数。

[🍪获取cookies.txt](https://github.com/kairi003/Get-cookies.txt-LOCALLY)使得获取[NetScape cookies格式](http://fileformats.archiveteam.org/wiki/Netscape_cookies.txt)的cookies变得容易。

安装后，在[TikTok.com](https://tiktok.com/)上打开扩展菜单，点击 `🍪 获取 cookies.txt` 显示您的cookies 。选择`导出为⇩`，并指定位置和名称以保存。

**可选的**， `cookies_list`是一个包含`name`、`value` 、`domain`、`path`和`expiry` 键的字典列表，允许您传递您自己的浏览器cookies。

** 示例: **

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

<h2 id="browser-selection"> 👀 浏览器选择</h2>

[Google Chrome](https://www.google.com/chrome)是**TikTok上传器**的首选浏览器。此包中使用的默认反检测技术是为此优化的。然而，如果您想使用不同的浏览器，您可以在 `upload_video` 或 `upload_videos` 中指定 `browser`。

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

# 随机选择一款网络浏览器
upload_video(..., browser=choice(BROWSERS))
```

✅ 支持的浏览器:

- **Chrome** (推荐使用)
- **Safari**
- **Chromium**
- **Edge**
- **FireFox**

<h2 id="custom-webdriver"> 🚲 自定WebDriver选项</h2>

默认应为Selenium应用了一些修改，这可以帮助它避免被TikTok检济出。

然而，你 **可以** 传入自定义的驱动配置选项。只需将 `options` 作为关键词参数传递给 `upload_video` 或 `upload_videos` 即可。

```python
from selenium.webdriver.chrome.options import Options

options = Options()

options.add_argument('start-maximized')

upload_videos(..., options=options)
```

>注意：确保使用适合您浏览器的selenium选项

<h2 id="headless"> 🤯 无头浏览器 </h2>

无头浏览器只能在Chrome上工作。使用Chrome时，使用CLI添加 `--headless` 标志或将 `headless`作为关键词参数传递给 `upload_video` 或 `upload_videos` 就足够了。

```python
upload_video(..., headless=True)
upload_videos(..., headless=True)
```

<h2 id="initial-setup"> 🔨 最初设置</h2>

[WebDriverManager](https://bonigarcia.dev/webdrivermanager/)用于管理驱动版本。

在最初启动时，您**可能**会被提示安装所选浏览器的正确驱动程序。然而，对于**Chrome** 和 **Edge**，驱动程序会自动安装。

<h2 id="examples"> ♻ 实例</h2>

- **[基本上传示例](examples/basic_upload.py):** 使用 `upload_video` 发布一个帖子。

- **[一次上传多个视频](examples/multiple_videos_at_once.py):** 使用 `upload_videos` 多次上传同一视频。

- **[系列上传示例](examples/series_upload.py):** 使用[Pandas](https://pandas.pydata.org)从CSV文件中读取视频。将尝试上传视频，**只有在上传成功时**，视频将被标记为已上传。

<h1 id="notes"> 📝 批注</h1>

这个bot并不完美。虽然我并没有被正式禁止，但是在上传过多视频后，视频将无法上传。在测试中，等待几个小时就足以解决这个问题。出于这个原因，请将这个工具更多的看作是一个用于TikTok视频的定时上传器，而不是一个垃圾邮件机器。

<h1 id="made-with"> 使用账户</h1>

- [@C_Span](https://www.tiktok.com/@c_span?lang=en) - 一个分屏频道，底部是移动游戏画面，上面是来自C-Span的YouTube频道的片段
- [@habit_track](https://www.tiktok.com/@habit_track?lang=en) - 一个Reddit机器人，查看哪个SubReddit在TikTok上最火

> 如果你喜欢这个项目，请在GitHub上给它⭐以表达你的支持！❤️

[^1]: 如果对Hatch感兴趣，请查看[网站](https://hatch.pypa.io/latest/build/)
