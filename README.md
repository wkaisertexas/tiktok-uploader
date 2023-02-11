# TikTok Uploader
A selenium-based uploader for TikTok Videos

## Usage

While Tik Tok is pretty good about blocking bots (giving "too many requests" with FireFox's default installation"), simply copying your session tokens is enough to bypass this restriction and be able to upload your videos.

### Uploading videos

This library revolves around the 'upload_video' function which takes in a list of videos which have **filenames** and **descriptions** and are passed as follows:

```python
videos = [
{'file': 'video0.mp4', 'desc': 'Video 1 is about ..'},
{'file': 'video1.mp4', 'desc': 'Video 1 is about ..'}
]

```

### Authentication
Authentication can come in the form of either: your saved cookies from Tik Tok (recommended) or your username and password. Optionally, both can be passed, an the program will automatically try and refresh your authentication tokens if the proccess begins to fail.

#### Cookie-based Authentication
To have the bot use your browser's cookies, log into TikTok with the computer which will be used as the bot.

Next, download [Get cookies.txt](https://chrome.google.com/webstore/detail/get-cookiestxt/bgaddhkoddajcdgocldbbfleckgcbcid?hl=en) from the **chrome web store**.

Right click while on TikTok and click `🍪 Get cookies.txt` to download the file.

Finally, pass the saved file path to `upload_videos`.

```python
upload_videos(cookies='cookies.txt')
```

> Optionally, if you would like to pass your own cookies you may do as an array of dictionaries with keys `name`, `value`, `domain`, `path` and `expiry` though there really is no need

#### Login-based Authentication
To use password authentication, pass your **username** and **password** as keyword arguments to `upload_videos`.

```python
upload_videos(username='mytiktokusername', password='*******')
# or
upload_videos(login_info=('mytiktokusername', '*********')
```

> As a side note, try to avoid keeping passwords as values in your code. You can read more about why [here](https://medium.com/twodigits/keep-passwords-out-of-source-code-why-and-how-e84f9004815a).

### Browser Selection

[Google Chrome](https://www.google.com/chrome) is the prefered browser for TikTokUploader. The default anti-detection techniques used in this packaged are optimized for this. However, if you wish to use a different browser you may specify that in `upload_videos`.

```python
upload_videos(browser=['chrome', 'safari', 'chromium', 'edge', 'firefox'].choice()) # randomly picks a web browser (not recommended)
```

### Custom Driver Options

This package has a set of default modifications to Selenium which help it avoid being detected by TikTok. However, you may pass custom driver configuration options as a keyword argument. 

```python
from selenium.webdriver.chrome.options import Options

options = Options()

options.add_argument('start-maximized')

upload_videos(options=options)
```

> Note: Options are Browser specific  

## Installation

A prequisite to using this program is the installation of a [Selenium-compatable Web Browser](https://www.selenium.dev/documentation/webdriver/getting_started/install_drivers/). [Google Chrome](https://www.google.com/chromei/) 

## MacOS and Linux

```python
pip install tt-uploader
```

## Windows

```python
pip install tt-uploader
```

## Initial Setup

[WebDriverManager](https://bonigarcia.dev/webdrivermanager/) is used to manage driver versions. On intial startup, you will be promted to install the correct driver for your selected broswer.

## Notes

This bot is not fool proof. I have personally not gotten banned while using this bot, but to do this, my use was kept minimal and large time gaps were placed between each action. 

Without a doubt, publishing hundreds or thousands of videos sequentially will likely get you ip banned.

> Please think of this package as more of a scheduled uploader for TikTok videos, rather than a spam bot
