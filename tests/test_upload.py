"""
Tests uploader
"""

import datetime
import os
from typing import Literal
from unittest.mock import MagicMock, patch

import pytz
from freezegun import freeze_time
from pytest import raises

from tiktok_uploader.types import VideoDict
from tiktok_uploader.upload import (
    _check_valid_schedule,
    _convert_videos_dict,
    _get_valid_schedule_minute,
    upload_video,
    upload_videos,
)

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
    mock_page = MagicMock()
    mock_browser.return_value = mock_page
    mock_auth.return_value = mock_page

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


def test_set_visibility_dropdown_interaction() -> None:
    """
    Tests the _set_visibility function's interaction with the dropdown
    """
    from tiktok_uploader.upload import _set_visibility

    # Create mock page and elements
    mock_page = MagicMock()

    # Run
    _set_visibility(mock_page, "only_you")

    # We expect calls to locator and click
    assert mock_page.locator.call_count >= 2
    mock_page.locator.return_value.click.assert_called()

    # Reset
    mock_page.reset_mock()

    _set_visibility(mock_page, "friends")

    assert mock_page.locator.call_count >= 2
    mock_page.locator.return_value.click.assert_called()


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


@patch("tiktok_uploader.upload.TikTokUploader.upload_videos")
@patch("tiktok_uploader.upload.TikTokUploader.close")
@patch("tiktok_uploader.auth.AuthBackend.authenticate_agent")
def test_upload_videos_with_browser_agent_authenticates(
    mock_authenticate_agent, _mock_close, mock_upload_videos
) -> None:
    """
    Tests that upload_videos still authenticates a user-provided browser agent.
    """
    browser_agent = MagicMock()
    mock_authenticate_agent.return_value = browser_agent
    mock_upload_videos.return_value = []

    upload_videos(
        videos=[{"path": FILENAME}],
        sessionid="test_session",
        browser_agent=browser_agent,
    )
    mock_authenticate_agent.assert_called_once_with(browser_agent)


# Schedule normalisation: pytz's localize() crashed on an already-aware UTC
# datetime, and a naive one was read as host-local time, not UTC as documented.


@freeze_time("2020-01-01 12:00")
@patch("tiktok_uploader.upload.get_browser")
@patch("tiktok_uploader.auth.AuthBackend.authenticate_agent")
@patch("tiktok_uploader.upload.complete_upload_form")
def test_upload_video_naive_schedule_is_utc(
    mock_complete_upload, mock_auth, mock_browser
) -> None:
    """A naive datetime is UTC, as the README documents, whatever the host's
    timezone."""
    mock_page = MagicMock()
    mock_browser.return_value = mock_page
    mock_auth.return_value = mock_page

    naive_schedule = datetime.datetime(2020, 1, 2, 12, 0)

    result = upload_video(
        filename=FILENAME,
        description="test",
        schedule=naive_schedule,
        sessionid="test_session",
    )

    assert result == []  # no failed videos
    passed_schedule = mock_complete_upload.call_args[0][3]
    assert passed_schedule == datetime.datetime(2020, 1, 2, 12, 0, tzinfo=pytz.UTC)


@freeze_time("2020-01-01 12:00")
@patch("tiktok_uploader.upload.get_browser")
@patch("tiktok_uploader.auth.AuthBackend.authenticate_agent")
@patch("tiktok_uploader.upload.complete_upload_form")
def test_upload_video_aware_utc_schedule_is_accepted(
    mock_complete_upload, mock_auth, mock_browser
) -> None:
    """An already-UTC-aware datetime schedules normally; pytz.UTC.localize()
    used to raise on it, so this input failed every time."""
    mock_page = MagicMock()
    mock_browser.return_value = mock_page
    mock_auth.return_value = mock_page

    aware_utc_schedule = datetime.datetime(
        2020, 1, 2, 12, 0, tzinfo=datetime.timezone.utc
    )

    result = upload_video(
        filename=FILENAME,
        description="test",
        schedule=aware_utc_schedule,
        sessionid="test_session",
    )

    assert result == []  # no failed videos
    mock_complete_upload.assert_called_once()
    passed_schedule = mock_complete_upload.call_args[0][3]
    assert passed_schedule == aware_utc_schedule


@freeze_time("2020-01-01 12:00")
@patch("tiktok_uploader.upload.get_browser")
@patch("tiktok_uploader.auth.AuthBackend.authenticate_agent")
@patch("tiktok_uploader.upload.complete_upload_form")
def test_upload_video_aware_non_utc_schedule_converts_to_utc(
    mock_complete_upload, mock_auth, mock_browser
) -> None:
    """An aware, non-UTC datetime must convert to the equivalent UTC instant
    rather than being rejected outright."""
    mock_page = MagicMock()
    mock_browser.return_value = mock_page
    mock_auth.return_value = mock_page

    eastern = datetime.timezone(datetime.timedelta(hours=-5))
    # 2020-01-02 07:00 -05:00 == 2020-01-02 12:00 UTC
    aware_eastern_schedule = datetime.datetime(2020, 1, 2, 7, 0, tzinfo=eastern)

    result = upload_video(
        filename=FILENAME,
        description="test",
        schedule=aware_eastern_schedule,
        sessionid="test_session",
    )

    assert result == []  # no failed videos
    passed_schedule = mock_complete_upload.call_args[0][3]
    assert passed_schedule == datetime.datetime(2020, 1, 2, 12, 0, tzinfo=pytz.UTC)
    assert passed_schedule.utcoffset() == datetime.timedelta(0)


# The react-joyride tour dismissal is tested in test_browsers.py: it is an
# init script installed by get_browser, not a helper in this module.
