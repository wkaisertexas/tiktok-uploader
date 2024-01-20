<p align="center">
<img src="https://github.com/wkaisertexas/tiktok-uploader/assets/27795014/f991fdc7-287a-4c3b-9a84-22c7ad8a57bf" alt="video funcionando" />
</p>

<h1 align="center"> ⬆️ Cargador de TikTok </h1>
<p align="center">Un cargador de vídeos de <strong>TikTok</strong> automatizado basado en <strong>Selenium</strong></p>

<p align="center">
  <a href="https://github.com/wkaisertexas/tiktok-uploader"><strong>Inglés</strong></a> ·
  <a href="https://github.com/wkaisertexas/tiktok-uploader/blob/main/README.zh-Hans.md"><strong>Chino (simplificado)</strong></a> ·
  <a href="https://github.com/wkaisertexas/tiktok-uploader/blob/main/README.fr.md"><strong>Francés</strong></a> ·
  <a href="https://github.com/wkaisertexas/tiktok-uploader/blob/main/README.es.md"><strong>Español</strong></a> ·
  <a href="https://github.com/wkaisertexas/tiktok-uploader/blob/main/README.de.md"><strong>Alemán</strong></a>
</p>

> ➡️ [Echa un vistazo a tranzlate en GitHub](https://github.com/wkaisertexas/tranzlate/blob/main/README.es.md) una herramienta para traducir texto usando [ChatGPT](https://chat.openai.com)


<p align="center">
  <img alt="Forks" src="https://img.shields.io/github/forks/wkaisertexas/tiktok-uploader" />
  <img alt="Estrellas" src="https://img.shields.io/github/stars/wkaisertexas/tiktok-uploader" />
  <img alt="Observadores" src="https://img.shields.io/github/watchers/wkaisertexas/tiktok-uploader" />
</p>

<h1>Tabla de Contenidos</h1>

- [Instalación](#installation)
  - [MacOS, Windows y Linux](#macos-windows-and-linux)
    - [Descarga desde PyPI (Recomendado)](#pypi)
    - [Compilación desde el código fuente](#building-from-source)
- [Uso](#usage)
  - [💻 Interfaz de línea de comandos (CLI)](#cli)
  - [⬆ Carga de vídeos](#uploading-videos)
  - [🫵 Menciones y Hashtags](#mentions-and-hashtags)
  - [🪡 Hilo, duetos y comentarios](#stitches-duets-and-comments)
  - [🔐 Autenticación](#authentication)
  - [👀 Selección de navegador](#browser-selection)
  - [🚲 Opciones personalizadas de WebDriver](#custom-webdriver)
  - [🤯 Navegadores sin cabeza](#headless)
  - [🔨 Configuración inicial](#initial-setup)
- [♻️ Ejemplos](#examples)
- [📝 Notas](#notes)
- [Cuentas creadas con](#made-with)

# Instalación

Un requisito previo para utilizar este programa es la instalación de un navegador web compatible con [Selenium](https://www.selenium.dev/documentation/webdriver/getting_started/install_drivers/). Se recomienda [Google Chrome](https://www.google.com/intl/es_es/chrome/).

<h2 id="macos-windows-and-linux">MacOS, Windows y Linux</h2>

Instale Python 3 o una versión superior desde [python.org](https://www.python.org/downloads/)

<h3 id="pypi">Descarga desde PyPI (Recomendado)</h3>

Instale `tiktok-uploader` usando `pip`

```bash
pip install tiktok-uploader
```

<h3 id="building-from-source">Compilación desde el código fuente</h3>

La instalación desde el código fuente permite una mayor flexibilidad para modificar el código del módulo y ampliar el comportamiento predeterminado.

Primero, `clone` y entre en el repositorio. A continuación, instale `hatch`, la herramienta de construcción utilizada para este proyecto [^1]. Luego, `construya` el proyecto. Finalmente, `instale` el proyecto con el flag "-e" o editable.

```console
git clone https://github.com/wkaisertexas/tiktok-uploader.git
cd tiktok-uploader
pip install hatch
hatch build
pip install -e .
```

<h1 id="usage">Uso</h1>

`tiktok-uploader` funciona duplicando las **cookies** de su navegador, lo que engaña a **TikTok** haciéndole creer que has iniciado sesión en un navegador controlado de forma remota.

<h2 id="cli"> 💻 Interfaz de línea de comandos (CLI)</h2>

El uso de la CLI es tan sencillo como llamar a `tiktok-uploader` con la `ruta` de tus vídeos (-v), la `descripción`(-d) y las `cookies` (-c)

```bash
tiktok-uploader -v video.mp4 -d "este es mi \"descripción\" escapada" -c cookies.txt
```

```python
from tiktok_uploader.upload import upload_video, upload_videos
from tiktok_uploader.auth import AuthBackend

# video individual
upload_video('video.mp4',
            description='esta es mi descripción',
            cookies='cookies.txt')

# Varios vídeos
videos = [
    {
        'path': 'video.mp4',
        'description': 'esta es mi descripción'
    },
    {
        'path': 'video2.mp4',
        'description': 'esta es también mi descripción'
    }
]

auth = AuthBackend(cookies='cookies.txt')
upload_videos(videos=videos, auth=auth)
```

<h2 id="uploading-videos"> ⬆ Carga de vídeos</h2>

Esta biblioteca gira en torno a la función `upload_videos` que toma una lista de vídeos que tienen **nombres de archivo** y **descripciones** y se pasan de la siguiente manera:

```python
from tiktok_uploader.upload import upload_videos
from tiktok_uploader.auth import AuthBackend

videos = [
    {
        'video': 'video0.mp4',
        'description': 'El vídeo 1 trata sobre ...'
    },
    {
        'video': 'video1.mp4',
        'description': 'El vídeo 2 trata sobre ...'
    }
]

auth = AuthBackend(cookies='cookies.txt')
failed_videos = upload_videos(videos=videos, auth=auth)

for video in failed_videos: # cada objeto de vídeo de entrada que falló
    print(f'{video['video']} con descripción "{video['description']}" falló')
```

<h2 id="mentions-and-hashtags"> 🫵 Menciones y Hashtags</h2>

Las menciones y los hashtags ahora funcionan siempre que estén seguidos por un espacio. Sin embargo, usted como usuario es responsable de verificar si una mención o hashtag existe antes de publicar

**Ejemplo:**

```python
from tiktok_uploader.upload import upload_video

upload_video('video.mp4', '#fyp @icespicee', 'cookies.txt')
```

<h2 id="stitches-duets-and-comments"> 🪡 Hilo, duetos y comentarios</h2>

Para establecer si un vídeo cargado permite hilos, comentarios o duetos, simplemente especifique `comment`, `stitch` y/o `duet` como argumentos de palabras clave para `upload_video` o `upload_videos`.

```python
upload_video(..., comment=True, stitch=True, duet=True)
```

> Los comentarios, hilos, y duetos están permitidos por **defecto**

<h2 id="proxy"> 🌐 Proxy</h2>

Para establecer un proxy, actualmente sólo funciona con chrome como navegador, permite autenticación de usuario:pase.

```python
# proxy = {'user': 'miusuario', 'pass': 'micontra', 'host': '111.111.111', 'port': '99'}  # usuario:contraseña
proxy = {'host': '111.111.111', 'port': '99'}
upload_video(..., proxy=proxy)
```

<h2 id="schedule"> 📆 Programar</h2>

La fecha y la hora programadas para el vídeo se tratarán con la zona horaria UTC. <br>
La fecha y hora programadas deben estar al menos a 20 minutos en el futuro y un máximo de 10 días.

```python
import datetime
schedule = datetime.datetime(2020, 12, 20, 13, 00)
upload_video(..., schedule=schedule)
```

<h2 id="authentication"> 🔐 Autenticación</h2>

La autenticación utiliza las cookies de su navegador. Este procedimiento se realizó debido a la postura más estricta de TikTok sobre la autenticación mediante un navegador controlado por Selenium.

Su `sessionid` es todo lo que se requiere para la autenticación y puede pasarse como argumento a casi cualquier función

[🍪 Obtenga cookies.txt](https://github.com/kairi003/Get-cookies.txt-LOCALLY) facilita la obtención de cookies en un formato [NetScape cookies format](http://fileformats.archiveteam.org/wiki/Netscape_cookies.txt).

Después de la instalación, abra el menú de extensiones en [TikTok.com](https://tiktok.com/) y haga clic en `🍪 Get cookies.txt` para revelar sus cookies. Seleccione `Exportar como ⇩` y especifique una ubicación y nombre para guardar.

**Opcionalmente**, `cookies_list` es una lista de diccionarios con las claves `name`, `value`, `domain`, `path` y `expiry` que le permiten pasar sus propias cookies del navegador.

**Ejemplo:**

```python
cookies_list = [
    {
        'name': 'sessionid',
        'value': '**tu id de sesión**',
        'domain': 'https://tiktok.com',
        'path': '/',
        'expiry': '10/8/2023, 12:18:58 PM'
    }
]

upload_video(..., cookies_list=cookies_list)
```

<h2 id="browser-selection"> 👀 Selección de navegador</h2>

[Google Chrome](https://www.google.com/intl/es_es/chrome) es el navegador preferido para **TikTokUploader**. Las técnicas predeterminadas de detección de anti-detección utilizadas en este paquete están optimizadas para esto. Sin embargo, si deseas utilizar un navegador diferente, puedes especificar el `navegador` en `upload_video` o `upload_videos`.

```python
from tiktok_uploader.upload import upload_video

from random import choice

NAVEGADORES = [
    'chrome',
    'safari',
    'chromium',
    'edge',
    'firefox'
]

# selecciona un navegador web al azar
upload_video(..., browser=choice(NAVEGADORES))
```

✅ Navegadores admitidos:

- **Chrome** (Recomendado)
- **Safari**
- **Chromium**
- **Edge**
- **FireFox**

<h2 id="custom-webdriver"> 🚲 Opciones personalizadas de WebDriver</h2>

Se aplican modificaciones predeterminadas a Selenium que ayudan a evitar que sea detectado por TikTok.

Sin embargo, **puedes** pasar una configuración de controlador personalizada. Simplemente pasa `options` como un argumento de palabras clave para `upload_video` o `upload_videos`.

```python
from selenium.webdriver.chrome.options import Options

options = Options()

options.add_argument('start-maximized')

upload_videos(..., options=options)
```

> Nota: Asegúrate de usar las opciones correctas de selenium para tu navegador

<h2 id="headless"> 🤯 Navegadores sin cabeza</h2>

La navegación sin cabeza sólo funciona en Chrome. Al usar Chrome, agregar la bandera `--headless` usando la CLI o pasando `headless` como un argumento de palabras clave a `upload_video` o `upload_videos` es todo lo que se requiere.

```python
upload_video(..., headless=True)
upload_videos(..., headless=True)
```

<h2 id="initial-setup"> 🔨 Configuración inicial</h2>

[WebDriverManager](https://bonigarcia.dev/webdrivermanager/) se utiliza para administrar las versiones del controlador.

En el inicio inicial, **puede** que se te pida que instales el controlador adecuado para tu navegador seleccionado. Sin embargo, para **Chrome** y **Edge** se instala automáticamente el controlador.

<h2 id="examples"> ♻ Ejemplos</h2>

- **[Ejemplo básico de carga](examples/basic_upload.py):** utiliza `upload_video` para hacer una publicación.

- **[Varios vídeos a la vez](examples/multiple_videos_at_once.py):** sube el mismo vídeo varias veces utilizando `upload_videos`.

- **[Ejemplo de subida de serie](examples/series_upload.py):** Los vídeos se leen desde un archivo CSV usando [Pandas](https://pandas.pydata.org). Se intenta subir un vídeo y **si y sólo si** tiene éxito, se marcará el vídeo como subido.

<h1 id="notes"> 📝 Notas</h1>

Este bot no es infalible. Aunque no he recibido una prohibición oficial, el vídeo no se cargará después de demasiadas cargas. En las pruebas, esperar varias horas fue suficiente para solucionar este problema. Por esta razón, por favor piensa en esto más como un cargador programado para vídeos de TikTok, en lugar de un bot de spam.

<h1 id="made-with"> Cuentas creadas con</h1>

- [@C_Span](https://www.tiktok.com/@c_span?lang=en) - Un canal de pantalla dividida con juegos móviles abajo que presenta clips del canal de YouTube de C-Span
- [@habit_track](https://www.tiktok.com/@habit_track?lang=en) - Un bot de Reddit para ver qué SubReddit es más viral en TikTok

> Si te gusta este proyecto, por favor ⭐ en GitHub para mostrar tu apoyo! ❤️

[^1]: Si te interesa Hatch, visita el [sitio web](https://hatch.pypa.io/latest/build/)