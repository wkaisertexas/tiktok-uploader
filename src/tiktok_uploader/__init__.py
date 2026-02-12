"""
TikTok Uploader Initialization
"""

import logging
from os.path import abspath, dirname, join

from tiktok_uploader.settings import load_config

## Load Config
config_dir = abspath(dirname(__file__))
config = load_config(join(config_dir, "config.toml"))

## Setup Logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

formatter = logging.Formatter("%(asctime)s %(message)s", datefmt="[%H:%M:%S]")

stream_handler = logging.StreamHandler()
stream_handler.setLevel(logging.DEBUG)
stream_handler.setFormatter(formatter)
logger.addHandler(stream_handler)

from tiktok_uploader.upload import TikTokUploader, upload_video, upload_videos  # noqa: E402

__all__ = ["TikTokUploader", "upload_video", "upload_videos"]