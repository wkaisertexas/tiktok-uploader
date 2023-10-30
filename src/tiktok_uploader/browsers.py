"""Gets the browser's given the user's input"""
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.safari.options import Options as SafariOptions
from selenium.webdriver.edge.options import Options as EdgeOptions

# Webdriver managers
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.firefox.service import Service as FirefoxService
from webdriver_manager.firefox import GeckoDriverManager
from webdriver_manager.microsoft import EdgeChromiumDriverManager
from selenium.webdriver.edge.service import Service as EdgeService

from selenium import webdriver

from tiktok_uploader import config
from tiktok_uploader.proxy_auth_extension.proxy_auth_extension import generate_proxy_auth_extension


def get_browser(name: str = 'chrome', options=None, *args, **kwargs) -> webdriver:
    """
    Gets a browser based on the name with the ability to pass in additional arguments
    """

    # get the web driver for the browser
    driver_to_use = get_driver(name=name, *args, **kwargs)

    # gets the options for the browser

    options = options or get_default_options(name=name, *args, **kwargs)

    # combines them together into a completed driver
    service = get_service(name=name)
    if service:
        driver = driver_to_use(service=service, options=options)
    else:
        driver = driver_to_use(options=options)

    driver.implicitly_wait(config['implicit_wait'])

    return driver


def get_driver(name: str = 'chrome', *args, **kwargs) -> webdriver:
    """
    Gets the web driver function for the browser
    """
    if _clean_name(name) in drivers:
        return drivers[name]

    raise UnsupportedBrowserException()


def get_service(name: str = 'chrome'):
    """
    Gets a service to install the browser driver per webdriver-manager docs

    https://pypi.org/project/webdriver-manager/
    """
    if _clean_name(name) in services:
        return services[name]()

    return None # Safari doesn't need a service


def get_default_options(name: str, *args, **kwargs):
    """
    Gets the default options for each browser to help remain undetected
    """
    name = _clean_name(name)

    if name in defaults:
        return defaults[name](*args, **kwargs)

    raise UnsupportedBrowserException()


def chrome_defaults(*args, headless: bool = False, proxy: dict = None, **kwargs) -> ChromeOptions:
    """
    Creates Chrome with Options
    """

    options = ChromeOptions()

    ## regular
    options.add_argument('--disable-blink-features=AutomationControlled')
    options.add_argument('--profile-directory=Default')

    ## experimental
    options.add_experimental_option('excludeSwitches', ['enable-automation'])
    options.add_experimental_option('useAutomationExtension', False)

    ## add english language to avoid languages translation error
    options.add_argument("--lang=en")
    
    # headless
    if headless:
        options.add_argument('--headless=new')
    if proxy:
        if 'user' in proxy.keys() and 'pass' in proxy.keys():
            # This can fail if you are executing the function more than once in the same time
            extension_file = 'temp_proxy_auth_extension.zip'
            generate_proxy_auth_extension(proxy['host'], proxy['port'], proxy['user'], proxy['pass'], extension_file)
            options.add_extension(extension_file)
        else:
            options.add_argument(f'--proxy-server={proxy["host"]}:{proxy["port"]}')

    return options


def firefox_defaults(*args, headless: bool = False, proxy: dict = None, **kwargs) -> FirefoxOptions:
    """
    Creates Firefox with default options
    """

    options = FirefoxOptions()

    # default options

    if headless:
        options.add_argument('--headless')
    if proxy:
        raise NotImplementedError('Proxy support is not implemented for this browser')
    return options


def safari_defaults(*args, headless: bool = False, proxy: dict = None, **kwargs) -> SafariOptions:
    """
    Creates Safari with default options
    """
    options = SafariOptions()

    # default options

    if headless:
        options.add_argument('--headless')
    if proxy:
        raise NotImplementedError('Proxy support is not implemented for this browser')
    return options


def edge_defaults(*args, headless: bool = False, proxy: dict = None, **kwargs) -> EdgeOptions:
    """
    Creates Edge with default options
    """
    options = EdgeOptions()

    # default options

    if headless:
        options.add_argument('--headless')
    if proxy:
        raise NotImplementedError('Proxy support is not implemented for this browser')
    return options

# Misc
class UnsupportedBrowserException(Exception):
    """
    Browser is not supported by the library

    Supported browsers are:
        - Chrome
        - Firefox
        - Safari
        - Edge
    """

    def __init__(self, message=None):
        super().__init__(message or self.__doc__)


def _clean_name(name: str) -> str:
    """
    Cleans the name of the browser to make it easier to use
    """
    return name.strip().lower()


drivers = {
    'chrome': webdriver.Chrome,
    'firefox': webdriver.Firefox,
    'safari': webdriver.Safari,
    'edge': webdriver.ChromiumEdge,
}

defaults = {
    'chrome': chrome_defaults,
    'firefox': firefox_defaults,
    'safari': safari_defaults,
    'edge': edge_defaults,
}


services = {
    'chrome': lambda : ChromeService(ChromeDriverManager().install()),
    'firefox': lambda : FirefoxService(GeckoDriverManager().install()),
    'edge': lambda : EdgeService(EdgeChromiumDriverManager().install()),
}
