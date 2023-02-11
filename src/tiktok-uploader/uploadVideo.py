from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import time
from random_user_agent.user_agent import UserAgent
from http import cookiejar
from os.path import abspath

from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def upload_tiktok(username, password, file_path, descrption=""):
	# initialize a webdriver instance
	options = get_options()
	# user_agents = UserAgent()
	# user_agent = user_agents.get_random_user_agent()
	# print(user_agent) 
	# options.add_argument(f'user-agent={user_agent}')
	driver = webdriver.Chrome() # make this use chrome

	
	# Slow down the web scraping process
	driver.implicitly_wait(20) # seconds

	# Load cookies from a file 
	# driver.get("https://www.tiktok.com/login/phone-or-email/email")
	# driver.delete_all_cookies()
	# with open('cookies.txt', 'r') as f:
	# 	cookies = json.loads(f.read())
	# 	for cookie in cookies:
	# 		driver.aDd_cookie(cookie)
	# driver.refresh()


	# navigate to TikTok's website
	# driver.get("https://www.tiktok.com/login/phone-or-email/email")
	
	# # log in -> More difficult because of the image autenthication
	# text_box = driver.find_element(by=By.LINK_TEXT, value="Log In")
	# text_box.click()

	# submit_button = driver.find_element(by=By.CSS_SELECTOR, value="button")
	
	driver.get('https://www.tiktok.com')

	for cookie in get_cookies('tiktok.com_cookies.txt'):
		driver.add_cookie(cookie)
	
	driver.get('https://www.tiktok.com/upload')
	
	# finds the upload button by is two elements outside of an element with inner text "Upload"
	# upload_button = driver.find_element(by=By.XPATH, value="//*[text()='Select file']/../..")
	
	# prints out the html of the driver

	# waits for the root element to load
	iframe = driver.find_element(By.TAG_NAME, "iframe")
	driver.switch_to.frame(iframe)

	try:
		print("Waiting for web driver to load...")
		root = WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.ID, "root")))
	except:
		print("Root element not found")
	finally:
		print("Root element found")
	
	time.sleep(5)
	# elem = None
	# while elem is not [1, 2,3 ]:
	# 	try:
	# 		with open('output.html', 'w') as f:
	# 			f.write(driver.page_source)
	# 		path = input("Enter the xpath of the element:")
	# 		if path == "quit":
	# 			break

	# 		elem = driver.find_element(By.CSS_SELECTOR, path)
			
	# 		print(elem)
	# 		print(elem.text)
	# 	except Exception as e:
	# 		print(e)
	# 		print("Element not found")
	# 		time.sleep(5)
	# Trys to get each element
	try:
		upload_button = driver.find_element(By.CSS_SELECTOR, 'input[type="file"]')
		print("found the upload button")
		time.sleep(5)
		caption_box = driver.find_element(by=By.XPATH, value='//div[@contenteditable="true"]')
		time.sleep(5)
		print("found the caption box")
		post_button = driver.find_element(by=By.XPATH, value='//button[.="Post"]')
		time.sleep(5)
		print("found the post button")
	except:
		print("Element not found")

	# upload_button = driver.find_element(by=By.XPATH, value="//input[@type='file']") # going to fail

	time.sleep(5)
	try:
		upload_button.send_keys(abspath(file_path))
		print("Uploaded the file")
	except:
		print("Failed to send keys to upload button")


	time.sleep(20)
	try:
		caption_box.clear()
		caption_box.send_keys(descrption)
		print("Sent keys to caption box")
	except:
		print("Failed to send keys to caption box")
	
	time.sleep(20)
	try:
		post_button.click()
		print("Clicked the post button")
	except:
		print("Failed to click post button")
	# print(upload_button)
	
	# # sends keys to the upload button
	# upload_button.send_keys(file_path)

	# # finds the caption box and sends keys to it
	# caption_box = driver.find_element(by=By.XPATH, value='//div[contenteditable="true"]')
	# print(caption_box.text)
	# caption_box.send_keys("This is a test")

	# # finds the post button and clicks it
	# post_button = driver.find_element(by=By.XPATH, value="//button[text()='Post']/../..")
	# post_button.click()

	# close the webdriver
	time.sleep(400)
	# driver.quit()

def get_options(): # TODO : consider making the user agent random
	options = Options()
	options.add_argument("start-maximized")

	# Chrome is controlled by automated test software
	# options.add_experimental_option("excludeSwitches", ["enable-automation"])
	# options.add_experimental_option('useAutomationExtension', False)

	# avoiding detection
	# options.add_argument('--disable-blink-features=AutomationControlled')

	# Default User Profile
	options.add_argument("--profile-directory=Default")
	options.add_argument("--user-data-dir=C:/Users/Admin/AppData/Local/Google/Chrome/User Data")

	return options

def get_cookies(name: str) -> dict:
	"""Get cookies from a file"""
	# read the cookies from a Netscape cookies file
	cookie_jar = cookiejar.MozillaCookieJar(name)
	cookie_jar.load()

	# convert the cookies to a list of dictionaries
	cookies = []
	for cookie in cookie_jar:
		cookies.append({'name': cookie.name, 'value': cookie.value, 'domain': cookie.domain, 'path': cookie.path, 'expiry': cookie.expires})

	return cookies

# example usage

if __name__ == "__main__":
	upload_tiktok("paywall.lessee-0a@icloud.com", "nojziq-6xuFda", "video.mp4")


# Go to https://www.tiktok.com/login/phone-or-email/email
# 'Email or phone number' field
# 'Password' field
# Click Login Button

# 
