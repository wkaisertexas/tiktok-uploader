"""
Unit tests for proxy parsing and browser launch proxy configuration.
"""

from unittest.mock import MagicMock, patch
from tiktok_uploader.cli import parse_proxy
import tiktok_uploader.browsers as browsers


def test_parse_proxy_standard_url():
    res = parse_proxy("http://myuser:mypass@proxy.example.com:8080")
    assert res["host"] == "proxy.example.com"
    assert res["port"] == "8080"
    assert res["user"] == "myuser"
    assert res["password"] == "mypass"


def test_parse_proxy_socks5():
    res = parse_proxy("socks5://user:secret@127.0.0.1:1080")
    assert res["host"] == "127.0.0.1"
    assert res["port"] == "1080"
    assert res["user"] == "user"
    assert res["password"] == "secret"


def test_parse_proxy_schemeless_with_credentials():
    res = parse_proxy("user:secret@127.0.0.1:8080")
    assert res["host"] == "127.0.0.1"
    assert res["port"] == "8080"
    assert res["user"] == "user"
    assert res["password"] == "secret"


def test_parse_proxy_host_port_only():
    res = parse_proxy("127.0.0.1:8080")
    assert res["host"] == "127.0.0.1"
    assert res["port"] == "8080"
    assert "user" not in res
    assert "password" not in res


def test_parse_proxy_empty_and_none():
    assert parse_proxy(None) == {}
    assert parse_proxy("") == {}
    assert parse_proxy("   ") == {}


@patch("tiktok_uploader.browsers.sync_playwright")
def test_get_browser_with_proxy(mock_sync_playwright):
    mock_p = MagicMock()
    mock_browser_type = MagicMock()
    mock_browser = MagicMock()
    mock_context = MagicMock()
    mock_page = MagicMock()

    mock_sync_playwright.return_value.start.return_value = mock_p
    mock_p.chromium = mock_browser_type
    mock_browser_type.launch.return_value = mock_browser
    mock_browser.new_context.return_value = mock_context
    mock_context.new_page.return_value = mock_page

    proxy = {"host": "proxy.example.com", "port": "8080", "user": "admin", "password": "pwd"}
    browsers.get_browser("chrome", proxy=proxy)

    args, kwargs = mock_browser_type.launch.call_args
    assert "proxy" in kwargs
    assert kwargs["proxy"]["server"] == "http://proxy.example.com:8080"
    assert kwargs["proxy"]["username"] == "admin"
    assert kwargs["proxy"]["password"] == "pwd"
