"""
Test the browsers module.
"""

from unittest.mock import MagicMock, patch

import tiktok_uploader.browsers as browsers


@patch("tiktok_uploader.browsers.sync_playwright")
def test_get_browser(mock_sync_playwright):
    mock_p = MagicMock()
    mock_browser_type = MagicMock()
    mock_browser = MagicMock()
    mock_context = MagicMock()
    mock_page = MagicMock()

    mock_sync_playwright.return_value.start.return_value = mock_p
    # Default is chromium for chrome
    mock_p.chromium = mock_browser_type
    mock_browser_type.launch.return_value = mock_browser
    mock_browser.new_context.return_value = mock_context
    mock_context.new_page.return_value = mock_page

    page = browsers.get_browser("chrome")

    assert page == mock_page
    mock_p.chromium.launch.assert_called()

    # Check headless
    browsers.get_browser("chrome", headless=True)
    args, kwargs = mock_browser_type.launch.call_args
    assert kwargs["headless"] is True
