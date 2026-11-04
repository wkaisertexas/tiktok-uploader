"""
TikTok Uploader Initialization
"""

import logging
from os.path import abspath, dirname, join

from tiktok_uploader.settings import load_config

## Load Config
config_dir = abspath(dirname(__file__))
config = load_config(join(config_dir, "config.toml"))

## Logging
# The application chooses the handlers and level: INFO gives each upload's
# outcome, DEBUG every step. Unconfigured, Python still prints WARNING+.
logger = logging.getLogger(__name__)

from tiktok_uploader.upload import TikTokUploader, upload_video, upload_videos  # noqa: E402, I001

__all__ = ["TikTokUploader", "upload_video", "upload_videos"]
