"""
Uploads multiple videos downloaded from the internet
"""
from tiktok_uploader.upload import upload_videos

import urllib.request

URL = "https://raw.githubusercontent.com/wkaisertexas/wkaisertexas.github.io/main/upload.mp4"
FILENAME = "upload.mp4"

videos = [
    {
        "path": "upload.mp4",
        "description": "This is the first upload"
    },
    {
        "filename": "upload.mp4",
        "desc": "This is my description"
    }
]

if __name__ == "__main__":
    # download random video
    urllib.request.urlretrieve(URL, FILENAME)
    
    # authentication backend
    auth = AuthBackend(cookies="cookies.txt")

    # upload video to TikTok
    upload_videos(videos, auth=auth)
