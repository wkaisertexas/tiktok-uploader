"""
TikTok Uploader Initialization
"""

import tomllib

with open('config.toml', mode='rb') as f:
	config = toml.load(f)
