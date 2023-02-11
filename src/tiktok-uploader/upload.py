"""Upload is the project's main uploader"""
from .browsers import get_browser



# CONSTANTS
CONSTANTS = {
	'login_page': 'https://www.tiktok.com/login/phone-or-email/email',
	'upload_page': 'https://www.tiktok.com/upload',
}

def upload_video(filename=None, description='', *args, **kwargs):
	"""
	Uploads a single TikTok video. If doing multiple at a time, consider using upload_videos for greater efficiency
	"""
	return upload_videos(videos=[{'video':filename, 'description':description}], *args, **kwargs)


def upload_videos(videos=None, browser='chrome', browser_agent=None, headless=False, *args, **kwargs):
	"""
	Uploads multiple videos to TikTok. This function is the heart of the api and requires

	- 
	- 
	- 
	"""
	if not Videos:
		print("No videos were provided")
		return 

	if not browser_agent: # user-specified browser agent
		browser = get_browser(name=browser, headless=headless)
	
	# setup the browser in a funciton so that it can be redone if need be 

def setup_browser():
	"""
	Sets up the browser using the authentication method
	"""
	pass

