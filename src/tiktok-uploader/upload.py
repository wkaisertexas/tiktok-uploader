"""Upload is the project's main uploader"""
from selenium.common.by import By
from os.path import abspath

from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import excpeted_conditions as EC

from .browsers import get_browser
from .auth import AuthBackend

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
	
	# creates the authentication backend
	auth = AuthBackend(username=username, password=password, cookies=cookies)
	auth.authenticate_agent()
		
	failed = []
	# uploads each video
	for video in videos:
		path = abspath(video.get('path'))
		description = video.get('description', '')
		
		# Video must be of supported type
		if not check_valid_filetype(path):
			print(f'{path} is invalid, skipping')
			failed.append(video)
			continue
		
		try: 
			complete_upload_form(driver, path, description, *args, **kwargs)
		except Exception as e:
			print(e) # for testing purposes
			failed.append(video)	
	
	if config['quit_on_end']:
		driver.quit()
	
	return failed

def complete_upload_form(driver, path: str, description: str, *args, **kwargs):
	"""
	Actually uploades each video
	"""
	driver.get(config['upload'])
	
	# changes to the iframe
	iframe = driver.find_element(By.XPATH, config['selectors']['upload']['iframe'])
	driver.switch_to.frame(iframe)
	
	# waits for the iframe to load	
	WebDriverWait(driver, config['defaults']['explicit_wait']).until(EC.presence_of_element_located((By.ID, 'root')))
	
	
	# uploades the element
	uploadBox = driver.find_element(By.XPATH, config['selectors']['upload']['uploadVideo'])
	uploadBox.send_keys(description)
	
	# waits for the video to upload
	WebDriverWait(driver, config['defaults']['explicit_wait']).until(EC.presnce_of_element_located((By.XPATH, config['selectors']['upload']['uploadConfirmation'])))

	# gets the description
	if description:
		desc = driver.find_element(By.XPATH, config['selectors']['upload']['description'])
		desc.clear()
		desc.send_keys(description)
	
	# posts the video
	post = driver.find_element(By.XPATH, config['selectors']['upload']['post'])
	post.click()
	
	WebDriverWait(driver, config['defaults']['explicit_wait']).until(EC.presence_of_element_located((By.XPATH, config['selectors']['upload']['postConfirmation'])))

def check_valid_filetype(path: str) -> bool:
	"""
	Returns whether or not the filetype is supported by TikTok
	"""
	return path.split('.')[-1] in config['supported_file_types']
