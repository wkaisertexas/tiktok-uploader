"""
TikTok Uploader Initialization
"""

from os.path import abspath, join, dirname
import logging

from tiktok_uploader.config import load_config

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
