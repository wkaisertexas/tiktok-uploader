import datetime
import os
import re
from collections import defaultdict

# Now you can import modules from the added directory as if they were installed packages


import arrow

from src.tiktok_uploader import logger
from src.tiktok_uploader.upload import upload_video

from src.tiktok_uploader.get_latest_cookies import get_latest_local_cookies
import arrow

PROJECT_START_DATE = arrow.get(datetime.datetime(2024, 1, 26, tzinfo=None))
MEDITATIONS_DIR = r"C:\Users\RoiHa\OneDrive\Documents\Adobe\Premiere Pro\23.0\export\מדיטציות"


def upload_range(start_id, finish_id):

    mapped_videos = map_meditation_videos(MEDITATIONS_DIR)
    # Starting video id, finish video id
    for v_id in range(start_id, finish_id + 1):
        date = PROJECT_START_DATE.shift(days=v_id)
        try:
            filepath = os.path.join(MEDITATIONS_DIR, mapped_videos[v_id])
        except KeyError as e:
            logger.error(f"Missing video {v_id} for date {date}")
            continue
        try:
            # Schedule hour is ignored
            cookies = get_latest_local_cookies()
            result = upload_video(
                filename=filepath,
                description='',
                schedule=date.datetime.replace(tzinfo=None),
                cookies=cookies,
                proxy=None
            )
        except Exception as e:
            logger.error(f"Couldn't upload file {filepath} for {date}")
            logger.error(e)


def map_meditation_videos(directory_path):
    # Regular expression to match the sequence number and any additional versioning information
    pattern = re.compile(r'Meditations (\d+)(?: Copy (\d+)|_(\d+))?')

    # Dictionary to hold the files with their sequence as key and version details as values
    files_dict = defaultdict(list)

    # List all files in the directory and process them
    for filename in os.listdir(directory_path):
        if filename.endswith(".mp4") or "Copy" in filename or "_" in filename:
            match = pattern.search(filename)
            if match:
                # Sequence number
                seq_num = int(match.group(1))
                # Versioning number, defaulting to 0 if not present
                version_num = max(int(num) if num is not None else 0 for num in match.groups()[1:])
                files_dict[seq_num].append((version_num, filename))

    # Sort and select the latest version of each file
    latest_files = {seq: max(file, key=lambda x: x[0])[1] for seq, file in sorted(files_dict.items())}

    return latest_files













