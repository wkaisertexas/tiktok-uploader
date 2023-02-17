"""
TikTok Uploader Initialization
"""
import toml
from os.path import abspath, join, dirname

src_dir = abspath(dirname(__file__))
config = toml.load(join(src_dir, 'config.toml'))