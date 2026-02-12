"""
Uploads multiple videos downloaded from the internet
"""

import urllib.request

from tiktok_uploader.types import VideoDict
from tiktok_uploader.upload import TikTokUploader

URL = "https://raw.githubusercontent.com/wkaisertexas/wkaisertexas.github.io/main/upload.mp4"
FILENAME = "upload.mp4"

videos: list[VideoDict] = [
    {
        "path": "upload.mp4",
        "description": "This is the first upload",
        "product_id": "YOUR_PRODUCT_ID_1",
    },
    {
        "path": "upload.mp4",
        "description": "This is my description",
        "product_id": "YOUR_PRODUCT_ID_2",
    },
]

if __name__ == "__main__":
    # download random video
    urllib.request.urlretrieve(URL, FILENAME)

    # authentication backend
    uploader = TikTokUploader(cookies="cookies.txt")

    # upload video to TikTok
    uploader.upload_videos(videos)