<p align="center">
<img src="https://github.com/wkaisertexas/tiktok-uploader/assets/27795014/f991fdc7-287a-4c3b-9a84-22c7ad8a57bf" alt="video arbeitet" />
</p>

<h1 align="center"> ⬆️ TikTok-Uploader </h1>
<p align="center">Ein <strong>Selenium</strong>-basierter automatisierter <strong>TikTok</strong>-Videouploader</p>

<p align="center">
  <a href="https://github.com/wkaisertexas/tiktok-uploader"><strong>Englisch</strong></a> ·
  <a href="https://github.com/wkaisertexas/tiktok-uploader/blob/main/README.zh-Hans.md"><strong>Chinesisch (vereinfacht)</strong></a> ·
  <a href="https://github.com/wkaisertexas/tiktok-uploader/blob/main/README.fr.md"><strong>Französisch</strong></a> ·
  <a href="https://github.com/wkaisertexas/tiktok-uploader/blob/main/README.es.md"><strong>Spanisch</strong></a> ·
  <a href="https://github.com/wkaisertexas/tiktok-uploader/blob/main/README.de.md"><strong>Deutsch</strong></a>
</p>

> ➡️ [Schauen Sie sich tranzlate auf GitHub an](https://github.com/wkaisertexas/tranzlate/blob/main/README.de.md), ein Tool zum Übersetzen von Text mit Hilfe von [ChatGPT](https://chat.openai.com)


<p align="center">
  <img alt="Forks" src="https://img.shields.io/github/forks/wkaisertexas/tiktok-uploader" />
  <img alt="Sterne" src="https://img.shields.io/github/stars/wkaisertexas/tiktok-uploader" />
  <img alt="Beobachter" src="https://img.shields.io/github/watchers/wkaisertexas/tiktok-uploader" />
</p>

<h1>Inhaltsverzeichnis</h1>

- [Installation](#installation)
  - [MacOS, Windows und Linux](#macos-windows-and-linux)
    - [Herunterladen von PyPI (empfohlen)](#pypi)
    - [Erstellung aus der Quelle](#building-from-source)
- [Verwendung](#usage)
  - [💻 Befehlszeilenschnittstelle (CLI)](#cli)
  - [⬆ Hochladen von Videos](#uploading-videos)
  - [🫵 Erwähnungen und Hashtags](#mentions-and-hashtags)
  - [🪡 Stitches, Duette und Kommentare](#stitches-duets-and-comments)
  - [🔐 Authentifizierung](#authentication)
  - [👀 Browser-Auswahl](#browser-selection)
  - [🚲 Benutzerdefinierte WebDriver-Optionen](#custom-webdriver)
  - [🤯 Headless-Browser](#headless)
  - [🔨 Erstmalige Einrichtung](#initial-setup)
- [♻️ Beispiele](#examples)
- [📝 Notizen](#notes)
- [Accounts erstellt mit](#made-with)

# Installation

Eine Voraussetzung zur Verwendung dieses Programms ist die Installation eines [Selenium-kompatiblen](https://www.selenium.dev/documentation/webdriver/getting_started/install_drivers/) Webbrowsers. [Google Chrome](https://www.google.com/chrome/) wird empfohlen.

<h2 id="macos-windows-and-linux">MacOS, Windows und Linux</h2>

Installieren Sie Python 3 oder höher von [python.org](https://www.python.org/downloads/)

<h3 id="pypi">Herunterladen von PyPI (empfohlen)</h3>

Installieren Sie `tiktok-uploader` mit `pip`

```bash
pip install tiktok-uploader
```

<h3 id="building-from-source">Erstellung aus der Quelle</h3>

Die Installation aus der Quelle ermöglicht eine größere Flexibilität bei der Modifikation des Modulcodes, um das Standardverhalten zu erweitern.

Zuerst `clonen` Sie und wechseln Sie in das Repository. Installieren Sie anschließend `hatch`, das für dieses Projekt verwendete Build-Tool [^1]. Dann `bauen` Sie das Projekt. Schließlich `installieren` Sie das Projekt mit dem `-e` oder dem editierbaren Flag.

```console
git clone https://github.com/wkaisertexas/tiktok-uploader.git
cd tiktok-uploader
pip install hatch
hatch build
pip install -e .
```

<h1 id="usage">Verwendung</h1>

`tiktok-uploader` funktioniert, indem es die **Cookies** Ihres Browsers dupliziert, was **TikTok** dazu verleitet zu glauben, dass Sie in einem ferngesteuerten Browser eingeloggt sind.

<h2 id="cli"> 💻 Befehlszeilenschnittstelle (CLI)</h2>

Die Verwendung der CLI ist so einfach wie das Aufrufen von `tiktok-uploader` mit Ihrem Video: `Pfad` (-v), `Beschreibung`(-d) und `Cookies` (-c)

```bash
tiktok-uploader -v video.mp4 -d "das ist meine geschützte \"Beschreibung\"" -c cookies.txt
```

```python
from tiktok_uploader.upload import upload_video, upload_videos
from tiktok_uploader.auth import AuthBackend

# Einzelvideo
upload_video('video.mp4',
            description='das ist meine Beschreibung',
            cookies='cookies.txt')

# Mehrere Videos
videos = [
    {
        'path': 'video.mp4',
        'description': 'das ist meine Beschreibung'
    },
    {
        'path': 'video2.mp4',
        'description': 'das ist auch meine Beschreibung'
    }
]

auth = AuthBackend(cookies='cookies.txt')
upload_videos(videos=videos, auth=auth)
```

<h2 id="uploading-videos"> ⬆ Hochladen von Videos</h2>

Diese Bibliothek dreht sich um die Funktion `upload_videos`, die eine Liste von Videos entgegennimmt, die **Dateinamen** und **Beschreibungen** haben und wie folgt übergeben werden:

```python
from tiktok_uploader.upload import upload_videos
from tiktok_uploader.auth import AuthBackend

videos = [
    {
        'video': 'video0.mp4',
        'description': 'Video 1 handelt von ...'
    },
    {
        'video': 'video1.mp4',
        'description': 'Video 2 handelt von ...'
    }
]

auth = AuthBackend(cookies='cookies.txt')
failed_videos = upload_videos(videos=videos, auth=auth)

for video in failed_videos: # jedes eingabe video objekt, das fehlgeschlagen ist
    print(f'{video['video']} mit der Beschreibung "{video['description']}" ist fehlgeschlagen')
```

<h2 id="mentions-and-hashtags"> 🫵 Erwähnungen und Hashtags</h2>

Erwähnungen und Hashtags funktionieren jetzt, solange sie von einem Leerzeichen gefolgt werden. Sie als Benutzer sind jedoch dafür verantwortlich, zu überprüfen, ob eine Erwähnung oder ein Hashtag vorhanden ist, bevor Sie ihn posten

**Beispiel:**

```python
from tiktok_uploader.upload import upload_video

upload_video('video.mp4', '#fyp @icespicee', 'cookies.txt')
```

<h2 id="stitches-duets-and-comments"> 🪡 Stitches, Duette und Kommentare</h2>

Um festzulegen, ob ein hochgeladenes Video Stitches, Kommentare oder Duette zulässt, spezifizieren Sie einfach `comment`, `stitch` und/oder `duet` als Schlüsselargumente für `upload_video` oder `upload_videos`.

```python
upload_video(..., comment=True, stitch=True, duet=True)
```

> Kommentare, Stiche und Duette werden standardmäßig **erlaubt**

<h2 id="proxy"> 🌐 Proxy</h2>

Um einen Proxy einzustellen, der derzeit nur mit Chrome als Browser funktioniert, erlauben Sie die Benutzerauthentifizierung per User:Pass.

```python
# proxy = {'user': 'meinBenutzer', 'pass': 'meinPass', 'host': '111.111.111', 'port': '99'}  # Benutzer:Pass
proxy = {'host': '111.111.111', 'port': '99'}
upload_video(..., proxy=proxy)
```

<h2 id="schedule"> 📆 Zeitplan</h2>

Das Datum und die Uhrzeit der geplanten Videoveröffentlichung werden in der UTC-Zeitzone behandelt. <br>
Das geplante Datum muss mindestens 20 Minuten in der Zukunft und maximal 10 Tage in der Zukunft liegen.

```python
import datetime
schedule = datetime.datetime(2020, 12, 20, 13, 00)
upload_video(..., plan=schedule)
```

<h2 id="authentication"> 🔐 Authentifizierung</h2>

Die Authentifizierung verwendet die Cookies Ihres Browsers. Dieser Umweg wurde gemacht aufgrund der strengeren Einstellung von TikTok zur Authentifizierung durch einen von Selenium gesteuerten Browser.

Ihr `sessionid` ist alles, was für die Authentifizierung benötigt wird und kann fast jeder Funktion als Argument übergeben werden

[🍪 Get cookies.txt](https://github.com/kairi003/Get-cookies.txt-LOCALLY) erleichtert das Erhalten von Cookies in einem [NetScape-Cookies-Format](http://fileformats.archiveteam.org/wiki/Netscape_cookies.txt).

Nach der Installation öffnen Sie das Erweiterungsmenü auf [TikTok.com](https://tiktok.com/) und klicken Sie auf `🍪 Get cookies.txt`, um Ihre Cookies zu sehen. Wählen Sie `Export As ⇩` und legen Sie einen Speicherort und Namen zum Speichern fest.

**Optional** kann `cookies_list`, eine Liste von Wörterbüchern mit den Schlüsseln `name`, `value`, `domain`, `path` und `expiry`, verwendet werden, um Ihre eigenen Browser-Cookies zu übergeben.

**Beispiel:**

```python
cookies_list = [
    {
        'name': 'sessionid',
        'value': '**Ihre Sitzungs-ID**',
        'domain': 'https://tiktok.com',
        'path': '/',
        'expiry': '10/8/2023, 12:18:58 PM'
    }
]

upload_video(..., cookies_list=cookies_list)
```

<h2 id="browser-selection"> 👀 Browserauswahl</h2>

[Google Chrome](https://www.google.com/chrome) ist der bevorzugte Browser für **TikTokUploader**. Die standardmäßig verwendeten Anti-Detection-Techniken in diesem Paket sind dafür optimiert. Wenn Sie jedoch einen anderen Browser verwenden möchten, können Sie den `browser` in `upload_video` oder `upload_videos` spezifizieren.

```python
from tiktok_uploader.upload import upload_video

from random import choice

BROWSER = [
    'chrome',
    'safari',
    'chromium',
    'edge',
    'firefox'
]

# wählt zufällig einen Webbrowser
upload_video(..., browser=choice(BROWSER))
```

✅ Unterstützte Browser:

- **Chrome** (empfohlen)
- **Safari**
- **Chromium**
- **Edge**
- **FireFox**

<h2 id="custom-webdriver"> 🚲 Benutzerdefinierte WebDriver-Optionen</h2>

Standardmäßige Modifikationen von Selenium werden angewendet, die helfen, dass es von TikTok nicht erkannt wird.

Sie **können** jedoch eine benutzerdefinierte Treiberkonfigurationsoptionen übergeben. Übergeben Sie dazu einfach `Optionen` als Schlüsselargument an `upload_video` oder `upload_videos`.

```python
from selenium.webdriver.chrome.options import Options

options = Options()

options.add_argument('start-maximized')

upload_videos(..., options=options)
```

> Hinweis: Stellen Sie sicher, dass Sie die richtigen Selenium-Optionen für Ihren Browser verwenden

<h2 id="headless"> 🤯 Kopflose Browser </h2>

Kopfloses Browsen funktioniert nur in Chrome. Wenn Chrome verwendet wird, muss das `--headless`-Flag mithilfe der CLI hinzugefügt oder `headless` als Schlüsselargument an `upload_video` oder `upload_videos` übergeben werden.

```python
upload_video(..., headless=True)
upload_videos(..., headless=True)
```

<h2 id="initial-setup"> 🔨 Erstmalige Einrichtung</h2>

[WebDriverManager](https://bonigarcia.dev/webdrivermanager/) wird zur Verwaltung von Treiber-Versionen verwendet.

Bei der ersten Inbetriebnahme **kann** Sie möglicherweise aufgefordert werden, den richtigen Treiber für Ihren ausgewählten Browser zu installieren. Allerdings wird für **Chrome** und **Edge** der Treiber automatisch installiert.

<h2 id="examples"> ♻ Beispiele</h2>

- **[Grundlegendes Upload-Beispiel](examples/basic_upload.py):** Verwendet `upload_video`, um einen Beitrag zu machen.

- **[Mehrere Videos auf einmal](examples/multiple_videos_at_once.py):** Lädt das gleiche Video mehrmals mit `upload_videos` hoch.

- **[Serien-Upload-Beispiel](examples/series_upload.py):** Videos werden mit Hilfe von [Pandas](https://pandas.pydata.org) aus einer CSV-Datei gelesen. Ein Videoupload-Versuch wird gemacht und **nur wenn** er erfolgreich ist, wird das Video als hochgeladen markiert.

<h1 id="notes"> 📝 Notizen</h1>

Dieser Bot ist nicht narrensicher. Obwohl ich noch kein offizielles Verbot erhalten habe, wird das Video nach zu vielen Uploads nicht hochgeladen. In Tests hat eine Wartezeit von mehreren Stunden dieses Problem behoben. Sehen Sie dies bitte mehr als einen geplanten Uploader für TikTok-Videos und nicht als einen Spam-Bot.

<h1 id="made-with"> Accounts erstellt mit </h1>

- [@C_Span](https://www.tiktok.com/@c_span?lang=en) - Ein Split-Screen-Kanal mit mobilen Spielen unten mit Clips vom C-Span YouTube Kanal
- [@habit_track](https://www.tiktok.com/@habit_track?lang=en) - Ein Reddit-Bot, um zu sehen, welches SubReddit am viralsten auf TikTok ist

> Wenn Ihnen dieses Projekt gefällt, dann ⭐ es auf GitHub, um Ihre Unterstützung zu zeigen! ❤️

[^1]: Wenn Sie an Hatch interessiert sind, schauen Sie sich die [Website](https://hatch.pypa.io/latest/build/) an
