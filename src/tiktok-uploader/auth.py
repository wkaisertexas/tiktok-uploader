"""Handles authentication for TikTokUploader"""
from http import cookiejar

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
			cookies = cookies | cookies_from_file(cookies_path)
		
		if not (cookies or (username and password)):
			raise Exception("Insufficient authentication")
		
		self.username = username
		self.password = password
	
		
	def authenticate_agent(self, driver):
		"""
		Authenticates the agent using the browser backend
		"""
		driver.get('https://tiktok.com')		

		# tries to use cookies

		# if cookies do not work, login the user

		pass
	
	def get_cookies(self):

def cookies_from_file(path: str) -> dict:
	"""
	Gets cookies from the file using the Nestscape standard
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
