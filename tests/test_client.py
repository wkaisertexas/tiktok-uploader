"""
Tests for the TikTokUploader class
"""

import os
from unittest.mock import MagicMock, patch

from tiktok_uploader.upload import TikTokUploader

FILENAME = "test.mp4"

def setup_function() -> None:
    """
    Creates a dummy file
    """
    with open(FILENAME, "w", encoding="utf-8") as file:
        file.write("test")


def teardown_function() -> None:
    """
    Deletes the dummy file
    """
    if os.path.exists(FILENAME):
        os.remove(FILENAME)


@patch("tiktok_uploader.upload.get_browser")
@patch("tiktok_uploader.auth.AuthBackend.authenticate_agent")
@patch("tiktok_uploader.upload.complete_upload_form")
def test_tiktok_uploader_lazy_loading(
    mock_complete_upload, mock_auth, mock_browser
) -> None:
    """
    Tests that the browser is not created until upload is called
    """
    mock_page = MagicMock()
    mock_browser.return_value = mock_page
    mock_auth.return_value = mock_page

    # Create uploader
    uploader = TikTokUploader(cookies="cookies.txt")
    
    # Browser should not be called yet
    mock_browser.assert_not_called()
    
    # Upload video
    uploader.upload_video(FILENAME, description="Test")
    
    # Now browser should be called
    mock_browser.assert_called_once()
    mock_auth.assert_called_once()
    mock_complete_upload.assert_called_once()


@patch("tiktok_uploader.upload.get_browser")
@patch("tiktok_uploader.auth.AuthBackend.authenticate_agent")
@patch("tiktok_uploader.upload.complete_upload_form")
def test_tiktok_uploader_reuse_browser(
    mock_complete_upload, mock_auth, mock_browser
) -> None:
    """
    Tests that the browser is reused for multiple uploads
    """
    mock_page = MagicMock()
    mock_browser.return_value = mock_page
    mock_auth.return_value = mock_page

    uploader = TikTokUploader(cookies="cookies.txt")
    
    # First upload
    uploader.upload_video(FILENAME, description="Test 1")
    
    # Second upload
    uploader.upload_video(FILENAME, description="Test 2")
    
    # Browser should be called only once
    mock_browser.assert_called_once()
    # Auth should be called only once
    mock_auth.assert_called_once()
    
    # Complete upload should be called twice
    assert mock_complete_upload.call_count == 2
