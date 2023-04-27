"""Gets a video from the internet and uplaods it"""

import urllib.request

from tiktok_uploader.upload import upload_video

URL = "https://raw.githubusercontent.com/wkaisertexas/wkaisertexas.github.io/main/upload.mp4"
FILENAME = "upload.mp4"

if __name__ == "__main__":
    # download random video
    urllib.request.urlretrieve(URL, FILENAME)

    # upload video to TikTok
    upload_video(FILENAME,
                 description="This is a video I just downloaded",
                 cookies="cookies.txt")
