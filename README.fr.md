<p align="center">
<img src="https://github.com/wkaisertexas/tiktok-uploader/assets/27795014/f991fdc7-287a-4c3b-9a84-22c7ad8a57bf" alt="vidéo en cours de fonctionnement" />
</p>

<h1 align="center"> ⬆️ TikTok Uploader </h1>
<p align="center">Un programme automatisé de téléchargement de vidéos <strong>TikTok</strong> basé sur <strong>Selenium</strong></p>

<p align="center">
  <a href="https://github.com/wkaisertexas/tiktok-uploader"><strong>Anglais</strong></a> ·
  <a href="https://github.com/wkaisertexas/tiktok-uploader/blob/main/README.zh-Hans.md"><strong>Chinois (Simplifié)</strong></a> ·
  <a href="https://github.com/wkaisertexas/tiktok-uploader/blob/main/README.fr.md"><strong>Français</strong></a> ·
  <a href="https://github.com/wkaisertexas/tiktok-uploader/blob/main/README.es.md"><strong>Espagnol</string></a> ·
  <a href="https://github.com/wkaisertexas/tiktok-uploader/blob/main/README.de.md"><strong>Allemand</strong></a>
</p>

> ➡️ [Découvrez tranzlate sur GitHub](https://github.com/wkaisertexas/tranzlate/blob/main/README.fr.md) un outil pour traduire du texte en utilisant [ChatGPT](https://chat.openai.com)


<p align="center">
  <img alt="Forks" src="https://img.shields.io/github/forks/wkaisertexas/tiktok-uploader" />
  <img alt="Stars" src="https://img.shields.io/github/stars/wkaisertexas/tiktok-uploader" />
  <img alt="Watchers" src="https://img.shields.io/github/watchers/wkaisertexas/tiktok-uploader" />
</p>

<h1>Table des matières</h1>

- [Installation](#installation)
  - [MacOS, Windows et Linux](#macos-windows-et-linux)
    - [Téléchargement depuis PyPI (Recommandé)](#pypi)
    - [Compilation depuis la source](#compilation-depuis-la-source)
- [Utilisation](#utilisation)
  - [💻 Interface en ligne de commande (CLI)](#cli)
  - [⬆ Téléchargement de vidéos](#telechargement-de-vidéos)
  - [🫵 Mentions et hashtags](#mentions-et-hashtags)
  - [🪡 Recousus, Duos et Commentaires](#recousus-duos-et-commentaires)
  - [🔐 Authentification](#authentification)
  - [👀 Sélection du navigateur](#selection-du-navigateur)
  - [🚲 Options personnalisées du WebDriver](#options-personnalisees-du-webdriver)
  - [🤯 Navigateurs en mode sans tête](#navigateurs-en-mode-sans-tête)
  - [🔨 Configuration initiale](#configuration-initiale)
- [♻️ Exemples](#exemples)
- [📝 Remarques](#remarques)
- [Comptes créés avec](#comptes-crées-avec)

# Installation

Le prérequis pour utiliser ce programme est l'installation d'un navigateur Web compatible [Selenium](https://www.selenium.dev/documentation/webdriver/getting_started/install_drivers/). [Google Chrome](https://www.google.com/chrome/) est recommandé.

<h2 id="macos-windows-et-linux">MacOS, Windows et Linux</h2>

Installez Python 3 ou une version plus récente depuis [python.org](https://www.python.org/downloads/)

<h3 id="pypi">Téléchargement depuis PyPI (Recommandé)</h3>

Installez `tiktok-uploader` en utilisant `pip`

```bash
pip install tiktok-uploader
```

<h3 id="compilation-depuis-la-source">Compilation depuis la source</h3>

L'installation depuis la source permet une plus grande flexibilité pour modifier le code du module afin d'étendre le comportement par défaut.

D'abord, `clonez` et naviguez dans le dépôt. Ensuite, installez `hatch`, l'outil de construction utilisé pour ce projet [^1]. Ensuite, `build` le projet. Enfin, `installez` le projet avec le flag `-e` ou éditable.

```console
git clone https://github.com/wkaisertexas/tiktok-uploader.git
cd tiktok-uploader
pip install hatch
hatch build
pip install -e .
```

<h1 id="utilisation">Utilisation</h1>

`tiktok-uploader` fonctionne en dupliquant les **cookies** de votre navigateur, ce qui trompe **TikTok** en lui faisant croire que vous êtes connecté sur un navigateur télécommandé.

<h2 id="cli"> 💻 Interface en ligne de commande (CLI)</h2>

Utiliser la CLI est aussi simple que d'appeler `tiktok-uploader` avec votre vidéos: `chemin` (-v), `description`(-d) et `cookies` (-c)

```bash
tiktok-uploader -v video.mp4 -d "c'est ma \"description\" échappée" -c cookies.txt
```

```python
from tiktok_uploader.upload import upload_video, upload_videos
from tiktok_uploader.auth import AuthBackend

# vidéo unique
upload_video('video.mp4',
            description='voici ma description',
            cookies='cookies.txt')

# Plusieurs vidéos
videos = [
    {
        'path': 'video.mp4',
        'description': 'voici ma description'
    },
    {
        'path': 'video2.mp4',
        'description': 'voici aussi ma description'
    }
]

auth = AuthBackend(cookies='cookies.txt')
upload_videos(videos=videos, auth=auth)
```

<h2 id="telechargement-de-vidéos"> ⬆ Téléchargement de vidéos</h2>

Cette bibliothèque tourne autour de la fonction `upload_videos` qui prend en entrée une liste de vidéos qui ont des **noms de fichier** et des **descriptions** et sont passées comme suit:

```python
from tiktok_uploader.upload import upload_videos
from tiktok_uploader.auth import AuthBackend

videos = [
    {
        'video': 'video0.mp4',
        'description': 'La vidéo 1 parle de ...'
    },
    {
        'video': 'video1.mp4',
        'description': 'La vidéo 2 parle de ...'
    }
]

auth = AuthBackend(cookies='cookies.txt')
failed_videos = upload_videos(videos=videos, auth=auth)

for video in failed_videos: # chaque objet vidéo d'entrée qui a échoué
    print(f'{video['video']} avec la description "{video['description']}" a échoué')
```

<h2 id="mentions-et-hashtags"> 🫵 Mentions et Hashtags</h2>

Les mentions et les hashtags fonctionnent maintenant tant qu'ils sont suivis d'un espace. Cependant, vous en tant qu'utilisateur êtes responsable de vérifier qu'une mention ou un hashtag existe avant de poster

**Exemple:**

```python
from tiktok_uploader.upload import upload_video

upload_video('video.mp4', '#fyp @icespicee', 'cookies.txt')
```

<h2 id="recousus-duos-et-commentaires"> 🪡 Recousus, Duos et Commentaires</h2>

Pour définir si une vidéo téléchargée permet des recousus, des commentaires ou des duos, il suffit de spécifier `comment`, `stitch` et/ou `duet` comme arguments clés à `upload_video` ou `upload_videos`.

```python
upload_video(..., comment=True, stitch=True, duet=True)
```

> Les commentaires, recousus et duos sont autorisés par **défaut**

<h2 id="proxy"> 🌐 Proxy</h2>

Pour définir un proxy, cela fonctionne actuellement seulement avec Chrome comme navigateur, autorise l'authentification utilisateur:mot de passe.

```python
# proxy = {'user': 'monutilisateur', 'pass': 'monmotdepasse', 'host': '111.111.111', 'port': '99'}  # utilisateur:mot de passe
proxy = {'host': '111.111.111', 'port': '99'}
upload_video(..., proxy=proxy)
```

<h2 id="schedule"> 📆 Planification</h2>

La date et l'heure de planification de la vidéo seront traitées avec le fuseau horaire UTC. <br>
La date et l'heure planifiées doivent être d'au moins 20 minutes dans le futur et au maximum de 10 jours.

```python
import datetime
schedule = datetime.datetime(2020, 12, 20, 13, 00)
upload_video(..., schedule=schedule)
```

<h2 id="authentification"> 🔐 Authentification</h2>

L'authentification utilise les cookies de votre navigateur. Cette solution de contournement a été réalisée en raison de la position plus stricte de TikTok sur l'authentification par un navigateur contrôlé par Selenium.

Votre `sessionid` est tout ce qui est nécessaire pour l'authentification et peut être passé en argument à presque n'importe quelle fonction

[🍪 Obtenez cookies.txt](https://github.com/kairi003/Get-cookies.txt-LOCALLY) facilite l'obtention des cookies dans un format de cookies [NetScape](http://fileformats.archiveteam.org/wiki/Netscape_cookies.txt).

Après l'installation, ouvrez le menu d'extensions sur [TikTok.com](https://tiktok.com/) et cliquez sur `🍪 Obtenez cookies.txt` pour révéler vos cookies. Sélectionnez `Export As ⇩` et spécifiez un emplacement et un nom pour sauvegarder.

**En option**, `cookies_list` est une liste de dictionnaires avec les clés `name`, `value`, `domain`, `path` et `expiry` qui vous permettent de passer vos propres cookies de navigateur.

**Exemple:**

```python
cookies_list = [
    {
        'name': 'sessionid',
        'value': '**votre id de session**',
        'domain': 'https://tiktok.com',
        'path': '/',
        'expiry': '10/8/2023, 12:18:58 PM'
    }
]

upload_video(..., cookies_list=cookies_list)
```

<h2 id="selection-du-navigateur"> 👀 Sélection du navigateur</h2>

[Google Chrome](https://www.google.com/chrome) est le navigateur préféré pour **TikTokUploader**. Les techniques anti-détection par défaut utilisées dans ce package sont optimisées pour cela. Cependant, si vous souhaitez utiliser un autre navigateur, vous pouvez spécifier le `navigateur` dans `upload_video` ou `upload_videos`.

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

# choisit au hasard un navigateur web
upload_video(..., browser=choice(BROWSERS))
```

✅ Navigateurs pris en charge:

- **Chrome** (Recommandé)
- **Safari**
- **Chromium**
- **Edge**
- **FireFox**

<h2 id="options-personnalisees-du-webdriver"> 🚲 Options personnalisées du WebDriver</h2>

Des modifications par défaut à Selenium sont appliquées qui l'aident à éviter d'être détecté par TikTok.

Cependant, vous **pouvez** passer des options de configuration de pilote personnalisées. Il suffit de passer `options` comme argument clé à `upload_video` ou `upload_videos`.

```python
from selenium.webdriver.chrome.options import Options

options = Options()

options.add_argument('start-maximized')

upload_videos(..., options=options)
```

> Note: Assurez-vous d'utiliser les bonnes options selenium pour votre navigateur

<h2 id="navigateurs-en-mode-sans-tête"> 🤯 Navigateurs en mode sans tête </h2>

La navigation sans tête ne fonctionne que sur Chrome. Lors de l'utilisation de Chrome, l'ajout du flag `--headless` en utilisant la CLI ou en passant `headless` comme argument clé à `upload_video` ou `upload_videos` est tout ce qui est nécessaire.

```python
upload_video(..., headless=True)
upload_videos(..., headless=True)
```

<h2 id="configuration-initiale"> 🔨 Configuration initiale</h2>

[WebDriverManager](https://bonigarcia.dev/webdrivermanager/) est utilisé pour gérer les versions des pilotes.

Au démarrage initial, il se **peut** que l'on vous demande d'installer le pilote correct pour votre navigateur sélectionné. Cependant, pour **Chrome** et **Edge**, le pilote est automatiquement installé.

<h2 id="exemples"> ♻ Exemples</h2>

- **[Exemple de base de téléchargement](examples/basic_upload.py):** Utilise `upload_video` pour faire un seul post.

- **[Plusieurs vidéos à la fois](examples/multiple_videos_at_once.py):** Télécharge la même vidéo plusieurs fois en utilisant `upload_videos`.

- **[Exemple de téléchargement en série](examples/series_upload.py):** Les vidéos sont lues à partir d'un fichier CSV en utilisant [Pandas](https://pandas.pydata.org). Un essai de téléchargement de vidéo est effectué et **si et seulement si** il est réussi, la vidéo sera marquée comme téléchargée.

<h1 id="remarques"> 📝 Remarques</h1>

Ce bot n'est pas infaillible. Bien que je n'aie pas eu de bannissement officiel, la vidéo échouera à être téléchargée après trop de téléchargements. Dans les tests, attendre plusieurs heures a été suffisant pour résoudre ce problème. Pour cette raison, veuillez penser à cela davantage comme un téléchargeur programmé pour les vidéos TikTok, plutôt que comme un bot de spam.

<h1 id="comptes-crées-avec"> Comptes créés avec</h1>

- [@C_Span](https://www.tiktok.com/@c_span?lang=en) - Une chaîne à écran partagé avec des jeux mobiles en dessous mettant en vedette des clips de la chaîne YouTube C-Span
- [@habit_track](https://www.tiktok.com/@habit_track?lang=en) - Un bot Reddit pour voir quel SubReddit est le plus viral sur TikTok

> Si vous aimez ce projet, veuillez le ⭐ sur GitHub pour montrer votre soutien! ❤️

[^1]: Si vous êtes intéressé par Hatch, consultez le [site web](https://hatch.pypa.io/latest/build/)