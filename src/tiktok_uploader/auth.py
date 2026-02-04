"""Handles authentication for TikTokUploader"""

from http import cookiejar
from time import sleep, time
from typing import Any

from playwright.sync_api import Page, expect

from tiktok_uploader import config, logger
from tiktok_uploader.browsers import get_browser
from tiktok_uploader.types import Cookie, cookie_from_dict
from tiktok_uploader.utils import green


class AuthBackend:
    """
    Handles authentication for TikTokUploader
    """

    username: str
    password: str
    cookies: list[Cookie]

    def __init__(
        self,
        username: str = "",
        password: str = "",
        cookies_list: list[Cookie] = [],
        cookies: str | None = None,
        cookies_str: str | None = None,
        sessionid: str | None = None,
    ):
        """
        Creates the authentication backend

        Keyword arguments:
        - username -> the accounts's username or email
        - password -> the account's password

        - cookies -> a list of cookie dictionaries of cookies which is Playwright-compatible
        """
        if (username and not password) or (password and not username):
            raise InsufficientAuth()

        self.cookies = self.get_cookies(path=cookies) if cookies else []
        self.cookies += self.get_cookies(cookies_str=cookies_str) if cookies_str else []
        self.cookies += cookies_list
        self.cookies += [{"name": "sessionid", "value": sessionid}] if sessionid else []

        if not (self.cookies or (username and password)):
            raise InsufficientAuth()

        self.username = username
        self.password = password

        if cookies:
            logger.debug(green("Authenticating browser with cookies"))
        elif username and password:
            logger.debug(green("Authenticating browser with username and password"))
        elif sessionid:
            logger.debug(green("Authenticating browser with sessionid"))
        elif cookies_list:
            logger.debug(green("Authenticating browser with cookies_list"))

    def authenticate_agent(self, page: Page) -> Page:
        """
        Authenticates the agent using the browser backend
        """
        # tries to use cookies
        if not self.cookies and self.username and self.password:
            self.cookies = login(page, username=self.username, password=self.password)

        logger.debug(green("Authenticating browser with cookies"))

        # Fix cookie keys for Playwright
        playwright_cookies = []
        for cookie in self.cookies:
            c = cookie.copy()
            if "expiry" in c:
                c["expires"] = c.pop("expiry")
            # Playwright requires strict types for sameSite
            if "sameSite" in c:
                if c["sameSite"] not in ["Strict", "Lax", "None"]:
                    c.pop("sameSite")
            
            # Playwright might fail if domain starts with a dot
            # if c.get("domain", "").startswith("."):
            #     c["domain"] = c["domain"][1:]
            
            # logger.debug(f"Adding cookie: {c}")
            print(f"DEBUG: Adding cookie: {c}")
            playwright_cookies.append(c)

        try:
            for pc in playwright_cookies:
                try:
                    page.context.add_cookies([pc])
                except Exception as e:
                    print(f"DEBUG: Failed to add individual cookie {pc['name']}: {e}")
        except Exception as e:
            logger.error(f"Failed to add cookies: {e}")

        page.goto(str(config.paths.main))

        # Check if we are redirected to a login or explore page
        current_url = page.url
        if "login" in current_url or "explore" in current_url:
             # Check if we have the sessionid cookie
             cookies = page.context.cookies()
             has_sessionid = any(c['name'] == 'sessionid' for c in cookies)
             if not has_sessionid:
                 logger.error(f"Redirected to {current_url} and sessionid cookie is missing")
                 raise InsufficientAuth(f"Authentication failed: Redirected to {current_url}. Please ensure your cookies are valid and include a sessionid.")

        # WaitForTitle is not directly available, but we can wait for load or selector
        # Using expect(page).to_have_title(...) is better but authenticate_agent expects to return page.
        # We can just wait for network idle or a specific element.
        # However, for title check:
        import re
        expect(page).to_have_title(re.compile(r"TikTok"), timeout=config.explicit_wait * 1000)

        return page

    def get_cookies(
        self, path: str | None = None, cookies_str: str | None = None
    ) -> list[Cookie]:
        """
        Gets cookies from the passed file using the netscape standard
        """
        if path:
            with open(path, encoding="utf-8") as file:
                lines = file.read().split("\n")
        elif cookies_str is not None:
            lines = cookies_str.split("\n")
        else:
            raise ValueError("Must have either a path or a cookies_str")

        return_cookies: list[Cookie] = []
        for line in lines:
            split = line.split("\t")
            if len(split) < 6:
                continue

            split = [x.strip() for x in split]

            name = split[5]
            value = split[6]
            domain = split[0]
            path = split[2]

            cookie = {
                "name": name,
                "value": value,
                "domain": domain,
                "path": path,
            }

            try:
                cookie["expiry"] = int(split[4])
            except ValueError:
                pass
            
            return_cookies.append(cookie) # type: ignore
        return return_cookies


def login_accounts(
    page: Page | None = None, accounts=[(None, None)], *args, **kwargs
) -> dict[str, list[Cookie]]:
    """
    Authenticates the accounts using the browser backend and saves the required credentials

    Keyword arguments:
    - page -> the playwright page to use
    - accounts -> a list of tuples of the form (username, password)
    """
    page = page or get_browser(headless=False, *args, **kwargs)

    cookies = {}
    for account in accounts:
        username, password = get_username_and_password(account)

        cookies[username] = login(page, username, password)

    return cookies


def login(page: Page, username: str, password: str) -> list[Cookie]:
    """
    Logs in the user using the email and password
    """
    assert username and password, "Username and password are required"

    # checks if the browser is on TikTok
    if str(config.paths.main) not in page.url:
        page.goto(str(config.paths.main))

    # checks if the user is already logged in
    # We check cookies in context
    cookies = page.context.cookies()
    session_cookie = next((c for c in cookies if c["name"] == config.selectors.login.cookie_of_interest), None)
    
    if session_cookie:
        # clears the existing cookies
        page.context.clear_cookies()

    # goes to the login site
    page.goto(str(config.paths.login))

    # selects and fills the login and the password
    username_field = page.locator(f"xpath={config.selectors.login.username_field}")
    username_field.wait_for(state="visible", timeout=config.explicit_wait * 1000)
    username_field.clear()
    username_field.fill(username)

    password_field = page.locator(f"xpath={config.selectors.login.password_field}")
    password_field.clear()
    password_field.fill(password)

    # submits the form
    submit = page.locator(f"xpath={config.selectors.login.login_button}")
    submit.click()

    print(f"Complete the captcha for {username}")

    # Wait until the session id cookie is set
    # Playwright doesn't have a direct "wait for cookie" so we poll or wait for navigation
    start_time = time()
    while True:
        cookies = page.context.cookies()
        if any(c["name"] == config.selectors.login.cookie_of_interest for c in cookies):
            break
        sleep(0.5)
        if time() - start_time > config.explicit_wait:
            raise InsufficientAuth()

    # wait until the url changes
    # page.wait_for_url(lambda url: str(config.paths.login) not in url) # simplified
    # or just wait for it to not be login
    try:
        page.wait_for_function(f"window.location.href !== '{config.paths.login}'", timeout=config.explicit_wait * 1000)
    except:
        pass # might have already changed

    return page.context.cookies()


def get_username_and_password(login_info: tuple | dict):
    """
    Parses the input into a username and password
    """
    if not isinstance(login_info, dict):
        return login_info[0], login_info[1]

    # checks if they used email or username
    if "email" in login_info:
        return login_info["email"], login_info["password"]
    elif "username" in login_info:
        return login_info["username"], login_info["password"]

    raise InsufficientAuth()


def save_cookies(path: str, cookies: list[Cookie]) -> None:
    """
    Saves the cookies to a netscape file
    """
    # saves the cookies to a file
    cookie_jar = cookiejar.MozillaCookieJar(path)
    # No need to load for new file or we can if we want to append
    # cookie_jar.load() 

    for cookie in cookies:
        cookie_jar.set_cookie(cookie_from_dict(cookie))

    cookie_jar.save()


class InsufficientAuth(Exception):
    """
    Insufficient authentication:

    > TikTok uses cookies to keep track of the user's authentication or session.

    Either:
        - Use a cookies file passed as the `cookies` argument
            - easily obtained using https://github.com/kairi003/Get-cookies.txt-LOCALLY
        - Use a cookies list passed as the `cookies_list` argument
            - can be obtained from your browser's developer tools under storage -> cookies
            - only the `sessionid` cookie is required
    """

    def __init__(self, message: str | None = None):
        super().__init__(message or self.__doc__)