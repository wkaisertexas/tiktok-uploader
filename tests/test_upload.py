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


def test_remove_onboarding_tour_clicks_until_gone() -> None:
    """
    Tests that each tour step is dismissed and stops once no button is visible
    """
    from tiktok_uploader.upload import _remove_onboarding_tour

    mock_page = MagicMock()
    button = mock_page.locator.return_value.first
    button.is_visible.side_effect = [True, True, False]

    _remove_onboarding_tour(mock_page)

    assert button.click.call_count == 2
    mock_page.evaluate.assert_not_called()


def test_remove_onboarding_tour_falls_back_to_removing_overlay() -> None:
    """
    Tests that a tour which never closes is removed from the DOM
    """
    from tiktok_uploader.upload import _remove_onboarding_tour

    mock_page = MagicMock()
    mock_page.locator.return_value.first.is_visible.return_value = True

    _remove_onboarding_tour(mock_page, max_steps=3)

    assert mock_page.locator.return_value.first.click.call_count == 3
    mock_page.evaluate.assert_called_once()


@patch("tiktok_uploader.upload.get_browser")
@patch("tiktok_uploader.auth.AuthBackend.authenticate_agent")
@patch("tiktok_uploader.upload.complete_upload_form")
def test_upload_video_with_draft(mock_complete_upload, mock_auth, mock_browser) -> None:
    """
    Tests that upload_video passes the draft flag through, defaulting to False
    """
    mock_page = MagicMock()
    mock_browser.return_value = mock_page
    mock_auth.return_value = mock_page

    upload_video(filename=FILENAME, sessionid="test_session", draft=True)
    assert mock_complete_upload.call_args.kwargs["draft"] is True

    mock_complete_upload.reset_mock()

    upload_video(filename=FILENAME, sessionid="test_session")
    assert mock_complete_upload.call_args.kwargs["draft"] is False


@patch("tiktok_uploader.upload._set_ai_label")
@patch("tiktok_uploader.upload._post_video")
@patch("tiktok_uploader.upload._save_draft")
@patch("tiktok_uploader.upload._set_video")
def test_complete_upload_form_draft_skips_posting(
    mock_set_video, mock_save_draft, mock_post_video, mock_set_ai_label
) -> None:
    """
    Tests that a draft is saved instead of posted, and that posting is the default
    """
    from tiktok_uploader.upload import complete_upload_form

    mock_page = MagicMock()

    complete_upload_form(mock_page, FILENAME, "", None, True, draft=True)
    mock_save_draft.assert_called_once_with(mock_page)
    mock_post_video.assert_not_called()

    mock_save_draft.reset_mock()

    complete_upload_form(mock_page, FILENAME, "", None, True)
    mock_post_video.assert_called_once_with(mock_page)
    mock_save_draft.assert_not_called()


def test_save_draft_clicks_button_and_waits_for_form_to_close() -> None:
    """
    Tests that _save_draft clicks the draft button once it is enabled
    """
    from tiktok_uploader.upload import _save_draft

    mock_page = MagicMock()
    draft_btn = mock_page.locator.return_value
    draft_btn.get_attribute.return_value = "false"

    _save_draft(mock_page)

    draft_btn.click.assert_called_once()
    draft_btn.wait_for.assert_called_once()
    assert draft_btn.wait_for.call_args.kwargs["state"] == "detached"


@patch("tiktok_uploader.upload._set_ai_label")
@patch("tiktok_uploader.upload._post_video")
@patch("tiktok_uploader.upload._set_video")
def test_complete_upload_form_ai_label_defaults_on(
    mock_set_video, mock_post_video, mock_set_ai_label
) -> None:
    """
    Tests that the AI-generated content label is on unless turned off
    """
    from tiktok_uploader.upload import complete_upload_form

    mock_page = MagicMock()

    complete_upload_form(mock_page, FILENAME, "", None, True)
    mock_set_ai_label.assert_called_once_with(mock_page, True)

    mock_set_ai_label.reset_mock()

    complete_upload_form(mock_page, FILENAME, "", None, True, ai_label=False)
    mock_set_ai_label.assert_called_once_with(mock_page, False)


@patch("tiktok_uploader.upload.get_browser")
@patch("tiktok_uploader.auth.AuthBackend.authenticate_agent")
@patch("tiktok_uploader.upload.complete_upload_form")
def test_upload_video_passes_ai_label(
    mock_complete_upload, mock_auth, mock_browser
) -> None:
    """
    Tests that upload_video passes the AI label flag through, defaulting to on
    """
    mock_browser.return_value = mock_auth.return_value = MagicMock()

    upload_video(filename=FILENAME, sessionid="test_session")
    assert mock_complete_upload.call_args.kwargs["ai_label"] is True

    upload_video(filename=FILENAME, sessionid="test_session", ai_label=False)
    assert mock_complete_upload.call_args.kwargs["ai_label"] is False


def _ai_label_page(states: list[str]) -> MagicMock:
    """
    A page whose AI label switch reports the given data-state values in order
    """
    mock_page = MagicMock()
    switch = MagicMock()
    switch.get_attribute.side_effect = states
    mock_page.locator.side_effect = lambda selector: (
        switch if "aigc_container" in selector else MagicMock()
    )
    mock_page.switch = switch
    return mock_page


def test_set_ai_label_turns_on_and_confirms() -> None:
    from tiktok_uploader.upload import _set_ai_label

    mock_page = _ai_label_page(["unchecked", "checked"])

    _set_ai_label(mock_page, True)

    mock_page.switch.click.assert_called_once()
    confirms = [c for c in mock_page.locator.call_args_list if "Turn on" in c.args[0]]
    assert len(confirms) == 1


def test_set_ai_label_leaves_matching_switch_alone() -> None:
    from tiktok_uploader.upload import _set_ai_label

    mock_page = _ai_label_page(["checked"])

    _set_ai_label(mock_page, True)

    mock_page.switch.click.assert_not_called()


@patch("tiktok_uploader.upload.time.sleep")
def test_set_ai_label_failure_stops_the_upload(mock_sleep) -> None:
    from tiktok_uploader.upload import FailedToUpload, _set_ai_label

    mock_page = _ai_label_page(["unchecked"] * 20)

    with raises(FailedToUpload):
        _set_ai_label(mock_page, True)
