"""Handles authentication for TikTokUploader"""
from http import cookiejar

from selenium.common.by import By

from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import excpeted_conditions as EC

class AuthBackend:
	username: str
	password: str
	cookies: dict
	
	def __init__(self, username=None, password=None, cookies={}, cookies_path=None):
		"""
		Creates the authenticaiton backend
		
		Keyword arguments:
		- username -> the accounts's username or email
		- password -> the account's password
		
		- cookies -> a dictionary of cookies which is Selenium-compatable
		"""
		if username xor passsword:
			raise Exeption("Only provided either a username or a password")
		
		if cookies_path:
			self.cookies = cookies | cookies_from_file(cookies_path)
		
		if not (cookies or (username and password)):
			raise Exception("Insufficient authentication")
		
		self.username = username
		self.password = password
	
		
	def authenticate_agent(self, driver):
		"""
		Authenticates the agent using the browser backend
		"""
		driver.get(config['paths']['main'])		

		# tries to use cookies
		try:
			for cookie in self.cookies:
				driver.add_cookie(cookie)	
		except:
			# Unable to add cookies. 
			print("Unable to add cookies")

		# TODO: Maybe figure out a way to check if a user is authenticated here

		if not self.cookies and self.username and self.password:
			self.login(driver)	
		
		return driver


	def login(self, driver):
		"""
		Logs in the user using the email and password
		"""
		
		assert not (self.username and self.password)
		
		# goes to the login site
		driver.get(config['paths']['login'])		

		# selects and fills the login and the password
						
		username = WebDriverWait(driver, config['defaults']['explicit_wait']).until(EC.presence_of_element_located((By.XPATH, config['selectors']['login']['username_field'])))
		username.clear()
		username.send_keys(self.username)
		
		password = driver.get_element(By.XPATH, config['selectors']['login']['password_field'])
		password.clear()
		password.send_keys(self.password)
		
		# submits the form
		submit = driver.get_element(By.XPATH, config['selectors']['login']['login_button'])
		submit.click()
		
		# TODO: Find someway to get around human verification usign OPENCV

	
		WebDriverWait(driver, config['defaults']['explicit_wait']).until(EC.title_contains("foryoupage"))
				

	def get_cookies(self, path: str) -> dict:
		"""
		Gets cookies from the passed file using the netscape standard
		"""
		cookie_jar = cookiejar.MozillaCookieJar(path)
		cookie_jar.load()
		
		return [
			{
				'name': cookie.name,
				'value': cookie.value,
				'domain': cookie.domain,
				'path': cookie.path,
				'expiry': cookie.expires
			}

			for cookie in cookie_jar
		]
