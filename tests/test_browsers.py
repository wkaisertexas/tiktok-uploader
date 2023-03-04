"""
Test the browsers module.
"""
import pytest

import tiktok_uploader.browsers as browsers

SUPPORTED_BROWSERS = ['chrome', 'firefox', 'safari', 'edge']
SERVICES = ['chrome', 'firefox', 'edge']

# Default behavior testing
def test_get_browser():
    """
    Tests the get_browser function.

    Requires all browsers to be installed on the system.
    """
    browser = browsers.get_browser()
    assert browser is not None


def test_get_driver():
    """
    Tests the get_driver function.
    """
    default = browsers.get_driver()
    assert default is not None

    # pytest throws exception test
    with pytest.raises(browsers.UnsupportedBrowserException):
        browsers.get_driver('invalid')


def test_get_service():
    """
    Tests the get_service function.
    """
    default = browsers.get_service()

    assert default is not None


# Test each default
def test_chrome_defaults():
    """
    Tests the chrome_defaults function.
    """
    options = browsers.chrome_defaults()
    headless = browsers.chrome_defaults(headless=True)
    assert options is not None
    assert headless is not None


def test_firefox_defaults():
    """
    Tests the firefox_defaults function.
    """
    options = browsers.firefox_defaults()
    headless = browsers.firefox_defaults(headless=True)
    assert options is not None
    assert headless is not None


def test_safari_defaults():
    """
    Tests the safari_defaults function.
    """
    options = browsers.safari_defaults()
    headless = browsers.safari_defaults(headless=True)
    assert options is not None
    assert headless is not None


def test_edge_defaults():
    """
    Tests the edge_defaults function.
    """
    options = browsers.edge_defaults()
    headless = browsers.edge_defaults(headless=True)

    assert options is not None
    assert headless is not None
