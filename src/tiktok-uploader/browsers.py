"""Gets the browser's given the user's input"""
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.safarinoptions import Options as SafariOptions
from selenium.webdriver.chromimum.options import Options as ChromimiumOptions
from selenium.webdriver.edge.options import Options as EdgeOptions

# TODO: implement the browser manager into the project


from selenium import webdriver

def get_browser(name: str, *args, **kwargs):
	"""
	Gets a browser based on the name with the ability to pass in additional arguments
	"""
	# get the web driver for the browser
	driver = get_driver(name=name)

	# gets the options for the browser
	options = get_default_options(name=name, *args, **kwargs)
	
	# combines them together into a completed driver
	return driver(options=options)


def get_driver(name: str = 'chrome'):
	"""
	Gets the web driver function for the browser
	"""
	match name.strip().lower():
		case 'chrome':
			return webdriver.Chrome
		case 'firefox':
			return webdriver.Firefox
		case 'chromimum':
			return webdriver.Chromium
		case 'edge':
			return webdriver.Edge
		case _:
			raise Exception(f'{name} is not a supported browser')		


def get_default_options(name: str, *args, **kwargs):
	"""
	Gets the default options for each browser to help remain undetected
	"""
	match name.strip().lower():
		case 'chrome':
			return chrome_defaults(*args, **kwargs)
		case 'firefox':
			return firefox_defaults(*args, **kwargs)
		case 'safari':
			return safari_defaults(*args, **kwargs)
		case 'edge':
			return edge_defaults(*args, **kwargs)
		case _:
			raise Exception(f'{name} is not a supported browser')


# Default Options
def chrome_defaults(headless: Bool = False, *args, **kwargs):
	"""
	Creates Chrome with Options
	"""	
	options = ChromeOptions()
	
	# default options
	
	## regular
	options.add_argument('--disable-blink-features=AutomationControlled')
	
	options.add_argument('--profile-directory=Default')
	# TODO: Implement a way to have a relative path to the app data directory

	## experimental
	options.add_experimental_option('excludeSwitches', ['enable-automation'])
	options.add_experimental_option('useAutomationExtension', False)
	
	## user-defined
	# TODO: figure out an elegant way to control user-defined arguments

	# headless	
	if headless:
		options.add_argument('--headless')

	return webdriver.Chrome(options=options)


def firefox_defaults():
	pass


def safari_defaults():
	pass


def chromimium_defaults():
	pass


def edge_defaults():
	pass
