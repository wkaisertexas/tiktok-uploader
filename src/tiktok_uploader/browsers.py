"""Gets the browser's given the user's input"""
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.safari.options import Options as SafariOptions
from selenium.webdriver.chromium import options as ChromiumOptions # for some reason this is not Options. Weird
from selenium.webdriver.edge.options import Options as EdgeOptions
from selenium.webdriver.ie.options import Options as IEOptions

# Webdriver managers
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager, ChromeType
from webdriver_manager.core.utils import ChromeType
from webdriver_manager.microsoft import IEDriverManager
from selenium.webdriver.ie.service import Service as IEService
from selenium.webdriver.safari.service import Service as SafariService
from selenium.webdriver.firefox.service import Service as FirefoxService
from webdriver_manager.firefox import GeckoDriverManager
from webdriver_manager.microsoft import EdgeChromiumDriverManager
from selenium.webdriver.edge.service import Service as EdgeService

from selenium import webdriver


def get_browser(name: str, *args, **kwargs) -> webdriver:
	"""
	Gets a browser based on the name with the ability to pass in additional arguments
	"""
	# get the web driver for the browser
	driver = get_driver(name=name)

	# gets the options for the browser
	options = get_default_options(name=name, *args, **kwargs)
	
	# combines them together into a completed driver
	return driver(options=options)


def get_driver(name: str = 'chrome') -> webdriver:
	"""
	Gets the web driver function for the browser
	"""
	name = name.strip().lower()
	if(name == 'chrome'):
		return webdriver.Chrome
	elif(name == 'firefox'):
		return webdriver.Firefox
	elif(name == 'safari'):
		return webdriver.Safari
	elif(name == 'edge'):
		return webdriver.ChromiumEdge # Edge is a chromium browser

	raise Exception(f'{name} is not a supported browser')


def get_service(name: str = 'chrome'):
	"""
	Gets a service to install the browser driver per webdriver-manager docs

	https://pypi.org/project/webdriver-manager/
	"""
	name = name.strip().lower()
	if(name == 'chrome'):
		return ChromeService(ChromeDriverManager().install())
	elif(name == 'firefox'):
		return FirefoxService(GeckoDriverManager().install())
	elif(name == 'edge'):
		return EdgeService(EdgeChromiumDriverManager().install())

	return None	# Safari does not need a service


def get_default_options(name: str, *args, **kwargs):
	"""
	Gets the default options for each browser to help remain undetected
	"""
	name = name.strip().lower()
	if(name == 'chrome'):
		return chrome_defaults(*args, **kwargs)
	elif(name == 'firefox'):
		return firefox_defaults(*args, **kwargs)
	elif(name == 'safari'):
		return safari_defaults(*args, **kwargs)
	elif(name == 'edge'):
		return edge_defaults(*args, **kwargs)
	
	raise Exception(f'{name} is not a supported browser')


def chrome_defaults(headless: bool = False, *args, **kwargs) -> ChromeOptions:
	"""
	Creates Chrome with Options
	"""	
	options = ChromeOptions()
	
	# default options
	
	## regular
	options.add_argument('--disable-blink-features=AutomationControlled')
	
	options.add_argument('--profile-directory=Default')

	## experimental
	options.add_experimental_option('excludeSwitches', ['enable-automation'])
	options.add_experimental_option('useAutomationExtension', False)
	
	# headless	
	if headless:
		options.add_argument('--headless')

	return options

def firefox_defaults(headless: bool = False, *args, **kwargs) -> FirefoxOptions:
	"""
	Creates Firefox with default options
	"""

	options = FirefoxOptions()

	# default options

	if headless:
		options.add_argument('--headless')
	
	return options


def safari_defaults(headless: bool, *args, **kwargs) -> SafariOptions:
	"""
	Creates Safari with default options
	"""
	options = SafariOptions()

	# default options

	if headless:
		options.add_argument('--headless')

	return options


def edge_defaults(headless: bool, *args, **kwargs) -> EdgeOptions:
	"""
	Creates Edge with default options
	"""
	options = EdgeOptions()

	# default options

	if headless:
		options.add_argument('--headless')

	return options

