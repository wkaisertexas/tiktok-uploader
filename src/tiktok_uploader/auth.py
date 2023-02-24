"""Handles authentication for TikTokUploader"""
from http import cookiejar
from time import time, sleep

from selenium.webdriver.common.by import By

from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from tiktok_uploader import config
from tiktok_uploader.browsers import get_browser

class AuthBackend:
    """
    Handles authentication for TikTokUploader
    """
    username: str
    password: str
    cookies: list

    def __init__(self, username: str = '', password: str = '',
                 cookies: list = None, cookies_path=None):
        """
        Creates the authenticaiton backend
        
        Keyword arguments:
        - username -> the accounts's username or email
        - password -> the account's password
        
        - cookies -> a list of cookie dictionaries of cookies which is Selenium-compatable
        """
        if (username and not password) or (password and not username):
            raise Exception("Only provided either a username or a password")

        self.cookies = self.get_cookies(path=cookies_path) if cookies_path else []
        self.cookies += cookies if cookies else []

        if not (self.cookies or (username and password)):
            raise Exception("Insufficient authentication")

        self.username = username
        self.password = password


    def authenticate_agent(self, driver):
        """
        Authenticates the agent using the browser backend
        """
        # tries to use cookies
        if not self.cookies and self.username and self.password:
            self.cookies = login(driver, username=self.username, password=self.password)

        driver.get(config['paths']['main'])

        WebDriverWait(driver, config['explicit_wait']).until(EC.title_contains("TikTok"))

        for cookie in self.cookies:
            try:
                driver.add_cookie(cookie)
            except:
                print(f'Cant add cookie {cookie}')

        return driver


    def get_cookies(self, path: str) -> dict:
        """
        Gets cookies from the passed file using the netscape standard
        """
        with open(path, 'r', encoding='utf-8') as file:
            lines = file.read().split('\n')

        return_cookies = []
        for line in lines:
            split = line.split('\t')
            if len(split) < 6:
                print("Skipped " + line)
                continue

            split = [x.strip() for x in split]

            try:
                split[4] = int(split[4])
            except ValueError:
                split[4] = None

            return_cookies.append({
                'name': split[5],
                'value': split[6],
                'domain': split[0],
                'path': split[2],
            })

            if split[4]:
                return_cookies[-1]['expiry'] = split[4]
        return return_cookies


def login_accounts(driver=None, accounts=[(None, None)], *args, **kwargs) -> list:
    """
    Authenticates the accounts using the browser backend and saves the required credentials

    Keyword arguments:
    - driver -> the webdriver to use
    - accounts -> a list of tuples of the form (username, password)
    """
    driver = driver or get_browser(headless=False, *args, **kwargs)

    cookies = {}
    for account in accounts:
        username, password = get_username_and_password(account)
    
        cookies[username] = login(driver, username, password)

    return cookies


def login(driver, username: str, password: str):
    """
    Logs in the user using the email and password
    """
    assert username and password, "Username and password are required"
    
    # checks if the browser is on TikTok
    if not config['paths']['main'] in driver.current_url:
        driver.get(config['paths']['main'])

    # checks if the user is already logged in
    if driver.get_cookie(config['selectors']['login']['cookie_of_interest']):
        # clears the existing cookies
        driver.delete_all_cookies()

    # goes to the login site
    driver.get(config['paths']['login'])

    # selects and fills the login and the password
    username_field = WebDriverWait(driver, config['explicit_wait']).until(
        EC.presence_of_element_located((By.XPATH, config['selectors']['login']['username_field']))
        )
    username_field.clear()
    username_field.send_keys(username)
 
    password_field = driver.find_element(By.XPATH, config['selectors']['login']['password_field'])
    password_field.clear()
    password_field.send_keys(password)
   
    # submits the form
    submit = driver.find_element(By.XPATH, config['selectors']['login']['login_button'])
    submit.click()

    print(f'Complete the captcha for {username}')

    # Wait until the session id cookie is set
    start_time = time()
    while not driver.get_cookie(config['selectors']['login']['cookie_of_interest']):
        sleep(0.5)
        if time() - start_time > config['explicit_wait']:
            raise Exception(f'Unable to get the cookie for {username}')

    # wait until the url changes
    WebDriverWait(driver, config['explicit_wait']).until(EC.url_changes(config['paths']['login']))

    return driver.get_cookies()


def get_username_and_password(input):
    """
    Parses the input into a username and password
    """
    if not isinstance(input, dict):
        return input[0], input[1]

    # checks if they used email or username
    if 'email' in input:
        return input['email'], input['password']
    elif 'username' in input:
        return input['username'], input['password']

    raise Exception("Invalid input")


def save_cookies(path, cookies: list):
    """
    Saves the cookies to a netscape file
    """
    # saves the cookies to a file
    cookie_jar = cookiejar.MozillaCookieJar(path)
    cookie_jar.load()

    for cookie in cookies:
        cookie_jar.set_cookie(cookie)

    cookie_jar.save()
