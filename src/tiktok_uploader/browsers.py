"""Gets the browser's given the user's input"""

from typing import Any, Literal

from playwright.sync_api import Page, sync_playwright

from tiktok_uploader import config
from tiktok_uploader.types import ProxyDict

# Type alias for supported browsers
browser_t = Literal["chrome", "firefox", "webkit", "edge", "safari", "chromium"]


def get_browser(
    name: browser_t = "chrome",
    headless: bool = False,
    proxy: ProxyDict | None = None,
    *args,
    **kwargs,
) -> Page:
    """
    Gets a browser based on the name with the ability to pass in additional arguments
    """
    p = sync_playwright().start()

    # Map browser names to Playwright launch functions
    if name == "chrome" or name == "edge" or name == "chromium":
        browser_type = p.chromium
    elif name == "firefox":
        browser_type = p.firefox
    elif name == "webkit" or name == "safari":
        browser_type = p.webkit
    else:
        browser_type = p.chromium  # Default to chromium

    launch_args: dict[str, Any] = {
        "headless": headless,
        "args": [
            "--disable-blink-features=AutomationControlled",
        ],
    }

    if name == "chrome":
        launch_args["channel"] = "chrome"
    elif name == "edge":
        launch_args["channel"] = "msedge"

    if proxy and proxy.get("host") and proxy.get("port"):
        server = f"{proxy['host']}:{proxy['port']}"
        if not (
            server.startswith("http://")
            or server.startswith("https://")
            or server.startswith("socks5://")
        ):
            server = f"http://{server}"

        proxy_config: dict[str, Any] = {"server": server}
        if "user" in proxy and "password" in proxy:
            proxy_config["username"] = str(proxy["user"])
            proxy_config["password"] = str(proxy["password"])

        launch_args["proxy"] = proxy_config

    browser = browser_type.launch(**launch_args)

    # Create a new context with stealth-like options if needed
    # For now, we use standard context but set locale/timezone if passed in kwargs
    # or rely on defaults.

    context_args: dict[str, Any] = {
        "viewport": {"width": 1280, "height": 720},
        "user_agent": config.disguising.user_agent,
        "locale": "en-US",
    }

    context = browser.new_context(**context_args)

    # Add init script to mask webdriver
    context.add_init_script("""
        Object.defineProperty(navigator, 'webdriver', {
            get: () => undefined
        });
    """)

    page = context.new_page()
    page.set_default_timeout(config.implicit_wait * 1000)  # Convert seconds to ms

    return page
