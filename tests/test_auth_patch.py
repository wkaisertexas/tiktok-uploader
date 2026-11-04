"""
AuthBackend.authenticate_agent() used to print every cookie dict, session
credentials included, to stdout: cookie values must never be printed or logged.
"""

import logging
from unittest.mock import MagicMock, patch

from tiktok_uploader.auth import AuthBackend

SECRET_COOKIE_VALUE = "sessionid-VALUE-must-never-reach-stdout-or-logs"


def test_authenticate_agent_never_prints_or_logs_cookie_value(caplog, capsys) -> None:
    backend = AuthBackend(
        cookies_list=[
            {
                "name": "sessionid",
                "value": SECRET_COOKIE_VALUE,
                "domain": ".tiktok.com",
                "path": "/",
            }
        ]
    )

    fake_page = MagicMock()
    fake_page.url = "https://www.tiktok.com/foryou"
    fake_page.context.cookies.return_value = [
        {"name": "sessionid", "value": SECRET_COOKIE_VALUE}
    ]

    # The real assertion talks to a live Playwright page; stub it out so this
    # test only exercises the cookie-handling/logging path being patched.
    with patch("tiktok_uploader.auth.expect") as mock_expect:
        mock_expect.return_value.to_have_title = MagicMock()
        caplog.set_level(logging.DEBUG)
        backend.authenticate_agent(fake_page)

    captured = capsys.readouterr()
    assert SECRET_COOKIE_VALUE not in captured.out
    assert SECRET_COOKIE_VALUE not in captured.err
    assert SECRET_COOKIE_VALUE not in caplog.text


def test_authenticate_agent_logs_cookie_name_for_debugging(caplog) -> None:
    """The redaction should not blind debugging entirely — the cookie NAME
    (never its value) is still useful and safe to log."""
    backend = AuthBackend(
        cookies_list=[
            {
                "name": "sessionid",
                "value": SECRET_COOKIE_VALUE,
                "domain": ".tiktok.com",
                "path": "/",
            }
        ]
    )

    fake_page = MagicMock()
    fake_page.url = "https://www.tiktok.com/foryou"
    fake_page.context.cookies.return_value = [
        {"name": "sessionid", "value": SECRET_COOKIE_VALUE}
    ]

    with patch("tiktok_uploader.auth.expect") as mock_expect:
        mock_expect.return_value.to_have_title = MagicMock()
        caplog.set_level(logging.DEBUG)
        backend.authenticate_agent(fake_page)

    assert "sessionid" in caplog.text
