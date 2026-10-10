"""
Shared test setup
"""

from pytest import MonkeyPatch, fixture

from tiktok_uploader import config


@fixture(autouse=True)
def no_default_cookies(monkeypatch: MonkeyPatch, tmp_path) -> None:
    """
    Keeps tests from finding the real default cookies file and logging in to TikTok
    """
    monkeypatch.delenv("TIKTOK_COOKIES", raising=False)
    monkeypatch.setattr(config, "default_cookies", str(tmp_path / "no-cookies.txt"))
