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


@patch("tiktok_uploader.browsers.sync_playwright")
def test_get_browser_installs_a_persistent_tour_dismissal_script(mock_sync_playwright):
    """The tour dismissal is a context-level init script, which survives every
    navigation and re-render, not a one-off page.evaluate() call."""
    mock_p = MagicMock()
    mock_browser_type = MagicMock()
    mock_browser = MagicMock()
    mock_context = MagicMock()

    mock_sync_playwright.return_value.start.return_value = mock_p
    mock_p.chromium = mock_browser_type
    mock_browser_type.launch.return_value = mock_browser
    mock_browser.new_context.return_value = mock_context
    mock_context.new_page.return_value = MagicMock()

    browsers.get_browser("chrome")

    scripts = [call.args[0] for call in mock_context.add_init_script.call_args_list]
    tour_scripts = [s for s in scripts if "react-joyride" in s]
    assert len(tour_scripts) == 1
    assert "MutationObserver" in tour_scripts[0]
    # the step tooltips are siblings of the portal, not inside it
    assert "react-joyride-portal" in tour_scripts[0]
    assert "react-joyride-step-" in tour_scripts[0]
