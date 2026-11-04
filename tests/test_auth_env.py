"""
Tests the $TIKTOK_COOKIES fallback when no login is given
"""

import os
from unittest.mock import patch

from pytest import raises

from tiktok_uploader.auth import AuthBackend, InsufficientAuth


def test_no_login_uses_the_tiktok_cookies_file() -> None:
    with patch.dict(os.environ, {"TIKTOK_COOKIES": "cookies.txt"}):
        auth = AuthBackend()

    assert auth.cookies_path == "cookies.txt"


def test_a_given_login_wins_over_tiktok_cookies() -> None:
    with patch.dict(os.environ, {"TIKTOK_COOKIES": "cookies.txt"}):
        auth = AuthBackend(sessionid="session")

    assert auth.cookies_path is None


def test_no_login_and_no_tiktok_cookies_is_insufficient() -> None:
    with patch.dict(os.environ):
        os.environ.pop("TIKTOK_COOKIES", None)
        with raises(InsufficientAuth):
            AuthBackend()
