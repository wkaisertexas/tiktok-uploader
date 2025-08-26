"""
Tests uploader
"""

from tiktok_uploader.upload import (
    _convert_videos_dict,
    _get_valid_schedule_minute,
    _check_valid_schedule,
    upload_video,
)
from tiktok_uploader.types import VideoDict
import os
import datetime
from freezegun import freeze_time
from pytest import raises
import pytz
from unittest.mock import patch, MagicMock
from typing import Literal

# before each create a file called test.mp4 and test.jpg
FILENAME = "test.mp4"
timezone = pytz.UTC


def setup_function() -> None:
    """
    Creates a dummy file
    """
    with open(FILENAME, "w", encoding="utf-8") as file:
        file.write("test")


# delete the file after each test
def teardown_function() -> None:
    """
    Deletes the dummy file
    """
    os.remove(FILENAME)


def test_convert_videos_dict_good() -> None:
    """Tests the videos dictionary with the good names"""
    good_dict = {
        "path": FILENAME,
        "description": "this is my description",
    }

    array = _convert_videos_dict([good_dict])

    assert array[0]["path"] == FILENAME
    assert array[0]["description"] == "this is my description"


def test_convert_videos_dict_wrong_names() -> None:
    """
    Tests the videos dictionary with the wrong names
    """
    wrong_dict = {
        "video": FILENAME,
        "desc": "this is my description",
    }

    array = _convert_videos_dict([wrong_dict])

    assert array[0]["path"] == FILENAME
    assert array[0]["description"] == "this is my description"


def test_convert_videos_bad() -> None:
    """
    Tests the videos dictionary with the wrong dictionaries
    """
    bad_dict = {
        "nothing": "asfs",
        "wrong": "wrong",
    }
    with raises(RuntimeError):
        _convert_videos_dict([bad_dict])


def test_convert_videos_filename() -> None:
    """
    Tests the videos dictionary with the wrong dictionaries
    """
    bad_dict = {
        "nothing": FILENAME,
    }
    array = _convert_videos_dict([bad_dict])

    assert array[0]["path"] == FILENAME
    assert array[0]["description"] == ""


def test_get_valid_schedule_minute() -> None:
    """
    Tests the get valid schedule minute
    """
    valid_tiktok_multiple = 5

    schedule = datetime.datetime(2023, 1, 1, 12, 56)
    schedule = timezone.localize(schedule)
    assert _get_valid_schedule_minute(schedule, valid_tiktok_multiple).minute == 0

    schedule = datetime.datetime(2023, 1, 1, 12, 9)
    schedule = timezone.localize(schedule)
    assert _get_valid_schedule_minute(schedule, valid_tiktok_multiple).minute == 10

    schedule = datetime.datetime(2023, 1, 1, 12, 5)
    schedule = timezone.localize(schedule)
    assert _get_valid_schedule_minute(schedule, valid_tiktok_multiple).minute == 5

    schedule = datetime.datetime(2023, 1, 1, 12, 0)
    schedule = timezone.localize(schedule)
    assert _get_valid_schedule_minute(schedule, valid_tiktok_multiple).minute == 0

    schedule = datetime.datetime(2023, 1, 1, 12, 30)
    schedule = timezone.localize(schedule)
    assert _get_valid_schedule_minute(schedule, valid_tiktok_multiple).minute == 30


@freeze_time("2020-01-01 12:00")
def test_check_valid_schedule_min_limit() -> None:
    """
    Tests the min limit of check_valid_schedule
    """

    schedule = datetime.datetime(2020, 1, 1, 12, 25)
    schedule = timezone.localize(schedule)
    assert _check_valid_schedule(schedule) is True

    schedule = datetime.datetime(2020, 1, 1, 12, 20)
    schedule = timezone.localize(schedule)
    assert _check_valid_schedule(schedule) is True

    schedule = datetime.datetime(2020, 1, 1, 12, 15)
    schedule = timezone.localize(schedule)
    assert _check_valid_schedule(schedule) is False

    schedule = datetime.datetime(2019, 1, 1, 12, 00)
    schedule = timezone.localize(schedule)
    assert _check_valid_schedule(schedule) is False


@freeze_time("2020-01-01 12:00")
def test_check_valid_schedule_max_limit() -> None:
    """
    Tests the max limit of check_valid_schedule
    """

    schedule = datetime.datetime(2020, 1, 9, 12, 00)
    schedule = timezone.localize(schedule)
    assert _check_valid_schedule(schedule) is True

    schedule = datetime.datetime(2020, 1, 10, 11, 55)
    schedule = timezone.localize(schedule)
    assert _check_valid_schedule(schedule) is True

    schedule = datetime.datetime(2020, 1, 11, 12, 00)
    schedule = timezone.localize(schedule)
    assert _check_valid_schedule(schedule) is True

    schedule = datetime.datetime(2020, 1, 11, 12, 5)
    schedule = timezone.localize(schedule)
    assert _check_valid_schedule(schedule) is False

    schedule = datetime.datetime(2021, 1, 11, 12, 5)
    schedule = timezone.localize(schedule)
    assert _check_valid_schedule(schedule) is False


@freeze_time("2020-01-01 12:00")
def test_check_valid_schedule_minute_valid() -> None:
    """
    Tests the minutes valid multiple
    """

    schedule = datetime.datetime(2020, 1, 2, 12, 00)
    schedule = timezone.localize(schedule)
    assert _check_valid_schedule(schedule) is True

    schedule = datetime.datetime(2020, 1, 2, 12, 1)
    schedule = timezone.localize(schedule)
    assert _check_valid_schedule(schedule) is False

    schedule = datetime.datetime(2020, 1, 2, 12, 2)
    schedule = timezone.localize(schedule)
    assert _check_valid_schedule(schedule) is False

    schedule = datetime.datetime(2020, 1, 2, 12, 3)
    schedule = timezone.localize(schedule)
    assert _check_valid_schedule(schedule) is False

    schedule = datetime.datetime(2020, 1, 2, 12, 4)
    schedule = timezone.localize(schedule)
    assert _check_valid_schedule(schedule) is False

    schedule = datetime.datetime(2020, 1, 2, 12, 5)
    schedule = timezone.localize(schedule)
    assert _check_valid_schedule(schedule) is True


def test_convert_videos_dict_with_visibility() -> None:
    """
    Tests that visibility parameter is properly handled in video dict conversion
    """
    # Test with visibility set to "only_you"
    video_dict = {
        "path": FILENAME,
        "description": "Private video",
        "visibility": "only_you",
    }

    array = _convert_videos_dict([video_dict])

    assert array[0]["path"] == FILENAME
    assert array[0]["description"] == "Private video"
    assert array[0]["visibility"] == "only_you"

    # Test with visibility set to "friends"
    video_dict = {
        "path": FILENAME,
        "description": "Friends only video",
        "visibility": "friends",
    }

    array = _convert_videos_dict([video_dict])

    assert array[0]["path"] == FILENAME
    assert array[0]["visibility"] == "friends"

    # Test without visibility (should not be in dict if not provided)
    video_dict = {"path": FILENAME, "description": "Public video"}

    array = _convert_videos_dict([video_dict])

    assert array[0]["path"] == FILENAME
    assert "visibility" not in array[0] or array[0].get("visibility") == "everyone"


def test_visibility_parameter_validation() -> None:
    """
    Tests that visibility parameter accepts valid values
    """
    valid_visibilities: list[Literal["everyone", "friends", "only_you"]] = [
        "everyone",
        "friends",
        "only_you",
    ]

    for visibility in valid_visibilities:
        video_dict = {
            "path": FILENAME,
            "description": f"Video with {visibility} visibility",
            "visibility": visibility,
        }

        # Should not raise any errors
        array = _convert_videos_dict([video_dict])
        assert array[0]["visibility"] == visibility


@patch("tiktok_uploader.upload.get_browser")
@patch("tiktok_uploader.auth.AuthBackend.authenticate_agent")
@patch("tiktok_uploader.upload.complete_upload_form")
def test_upload_video_with_visibility(
    mock_complete_upload, mock_auth, mock_browser
) -> None:
    """
    Tests that upload_video properly passes visibility parameter through
    """
    # Setup mocks
    mock_driver = MagicMock()
    mock_browser.return_value = mock_driver
    mock_auth.return_value = mock_driver

    # Test uploading with "only_you" visibility
    upload_video(
        filename=FILENAME,
        description="Test private video",
        sessionid="test_session",
        visibility="only_you",
    )

    # Verify complete_upload_form was called with visibility parameter
    mock_complete_upload.assert_called_once()
    call_args = mock_complete_upload.call_args

    # Check that visibility was passed to complete_upload_form
    assert call_args[0][7] == "only_you"  # visibility is the 7th positional argument

    # Reset mocks
    mock_complete_upload.reset_mock()

    # Test uploading with "friends" visibility
    upload_video(
        filename=FILENAME,
        description="Test friends video",
        sessionid="test_session",
        visibility="friends",
    )

    call_args = mock_complete_upload.call_args
    assert call_args[0][7] == "friends"

    # Reset mocks
    mock_complete_upload.reset_mock()

    # Test uploading with default visibility (everyone)
    upload_video(
        filename=FILENAME, description="Test public video", sessionid="test_session"
    )

    call_args = mock_complete_upload.call_args
    assert call_args[0][7] == "everyone"  # Default value


@patch("tiktok_uploader.upload.WebDriverWait")
@patch("tiktok_uploader.upload.EC")
def test_set_visibility_dropdown_interaction(mock_ec, mock_wait) -> None:
    """
    Tests the _set_visibility function's interaction with the dropdown
    """
    from tiktok_uploader.upload import _set_visibility

    # Create mock driver and elements
    mock_driver = MagicMock()
    mock_dropdown = MagicMock()
    mock_option = MagicMock()

    # Setup the wait to return our mock elements
    mock_wait_instance = MagicMock()
    mock_wait.return_value = mock_wait_instance
    mock_wait_instance.until.side_effect = [mock_dropdown, mock_option]

    # Test setting visibility to "only_you"
    _set_visibility(mock_driver, "only_you")

    # Verify dropdown was clicked
    mock_dropdown.click.assert_called_once()

    # Verify the option was clicked
    mock_option.click.assert_called_once()

    # Test setting visibility to "friends"
    mock_dropdown.reset_mock()
    mock_option.reset_mock()
    mock_wait_instance.until.side_effect = [mock_dropdown, mock_option]

    _set_visibility(mock_driver, "friends")

    mock_dropdown.click.assert_called_once()
    mock_option.click.assert_called_once()


def test_video_dict_type_with_visibility() -> None:
    """
    Tests that VideoDict TypedDict includes visibility field
    """
    # This test verifies the type definition includes visibility
    video: VideoDict = {
        "path": FILENAME,
        "description": "Test video",
        "visibility": "only_you",
    }

    assert video["visibility"] == "only_you"

    # Test all valid visibility values
    visibility_options: list[Literal["everyone", "friends", "only_you"]] = [
        "everyone",
        "friends",
        "only_you",
    ]
    for visibility_value in visibility_options:
        test_video: VideoDict = {
            "path": FILENAME,
            "visibility": visibility_value,
        }
        assert test_video["visibility"] == visibility_value
