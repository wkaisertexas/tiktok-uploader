import datetime

import sys

# Specify the directory you want to add to the Python path
directory_to_add = r"C:\Users\RoiHa\PycharmProjects\tiktok-uploader\src"

# Add the directory to the Python path
if directory_to_add not in sys.path:
    sys.path.append(directory_to_add)

# Now you can import modules from the added directory as if they were installed packages


import arrow
from src.tiktok_uploader.upload import upload_video

from src.tiktok_uploader.get_latest_cookies import get_latest_local_cookies

if __name__ == '__main__':
    filename = r"C:\Users\RoiHa\OneDrive\Documents\Adobe\Premiere Pro\23.0\export\פוסטים\Sequence 2.mp4"
    description = 'kaki'
    # Schedule hour is ignored
    schedule = datetime.datetime(2024, 2, 5)
    cookies = get_latest_local_cookies()

    result = upload_video(
        filename=filename,
        description=description,
        schedule=schedule,
        cookies=cookies,
        proxy=None
    )


















