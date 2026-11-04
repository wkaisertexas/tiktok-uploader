"""
Tests the upload form steps: modal dismissal, interactivity, sounds, drafts,
the AI-generated content label and the post result
"""

import datetime
import itertools
import logging
import os
from typing import Any
from unittest.mock import DEFAULT, MagicMock, patch

import pytz
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError
from pytest import LogCaptureFixture, raises

from tiktok_uploader import config
from tiktok_uploader.upload import (
    ContentRestricted,
    FailedToUpload,
    TikTokUploader,
    _check_valid_path,
    _click_if_visible,
    _convert_videos_dict,
    _dismiss_blocking_modals,
    _go_to_upload,
    _match_sound,
    _post_video,
    _save_draft,
    _set_ai_label,
    _set_interactivity,
    _set_schedule_video,
    _set_visibility,
    _wait_for_post_result,
    complete_upload_form,
    upload_video,
)

FILENAME = "test.mp4"

FORM_STEPS = (
    "_go_to_upload",
    "_remove_cookies_window",
    "_set_video",
    "_dismiss_blocking_modals",
    "_remove_split_window",
    "_set_interactivity",
    "_set_description",
    "_set_sound",
    "_set_ai_label",
    "_post_video",
    "_save_draft",
)


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


def _page_with(locators: dict[str, MagicMock]) -> MagicMock:
    """
    A page whose locator() returns the mock keyed by a substring of the selector
    """
    page = MagicMock()
    page.locator.side_effect = lambda selector: next(
        (locator for key, locator in locators.items() if key in selector),
        MagicMock(),
    )
    return page


def _run_form(page: MagicMock, **options: Any) -> Any:
    """
    Runs complete_upload_form with every step mocked, returning the step mocks
    """
    with patch.multiple(
        "tiktok_uploader.upload", **{step: DEFAULT for step in FORM_STEPS}
    ) as steps:
        complete_upload_form(page, FILENAME, "description", None, False, **options)
    return steps


def test_click_if_visible_clicks_once_visible() -> None:
    locator = MagicMock()

    assert _click_if_visible(locator, timeout=2) is True

    locator.wait_for.assert_called_once_with(state="visible", timeout=2000)
    locator.click.assert_called_once()


def test_click_if_visible_skips_an_element_that_never_shows() -> None:
    locator = MagicMock()
    locator.wait_for.side_effect = PlaywrightTimeoutError("not visible")

    assert _click_if_visible(locator, timeout=2) is False

    locator.click.assert_not_called()


def test_dismiss_blocking_modals_clicks_each_stacked_modal() -> None:
    page = MagicMock()
    button = page.locator.return_value.first
    button.wait_for.side_effect = [None, None, PlaywrightTimeoutError("gone")]

    _dismiss_blocking_modals(page)

    assert button.click.call_count == 2
    page.keyboard.press.assert_called_once_with("Escape")
    page.evaluate.assert_called_once()
    assert page.evaluate.call_args.args[1] == config.selectors.upload.modal_overlay


def test_dismiss_blocking_modals_survives_an_intercepted_click() -> None:
    page = MagicMock()
    page.locator.return_value.first.click.side_effect = PlaywrightTimeoutError(
        "intercepted"
    )

    _dismiss_blocking_modals(page)

    page.evaluate.assert_called_once()


@patch("tiktok_uploader.upload.time.sleep")
def test_set_interactivity_sets_reuse_of_content_from_stitch_and_duet(
    mock_sleep,
) -> None:
    comment = MagicMock()
    comment.is_checked.return_value = True
    reuse = MagicMock()
    reuse.count.return_value = 1
    reuse.is_checked.return_value = True
    stitch = MagicMock()
    page = _page_with(
        {"Reuse of content": reuse, "'Comment'": comment, "'Stitch'": stitch}
    )

    _set_interactivity(page, comment=True, stitch=False, duet=True)

    comment.click.assert_not_called()
    reuse.click.assert_called_once_with(force=True)
    stitch.click.assert_not_called()


@patch("tiktok_uploader.upload.time.sleep")
def test_set_interactivity_prefers_an_explicit_reuse_of_content(mock_sleep) -> None:
    reuse = MagicMock()
    reuse.count.return_value = 1
    reuse.is_checked.return_value = True
    page = _page_with({"Reuse of content": reuse})

    _set_interactivity(page, stitch=False, duet=False, reuse_of_content=True)

    reuse.click.assert_not_called()


@patch("tiktok_uploader.upload.time.sleep")
def test_set_interactivity_sets_stitch_and_duet_on_the_legacy_form(
    mock_sleep,
) -> None:
    reuse = MagicMock()
    reuse.count.return_value = 0
    stitch = MagicMock()
    stitch.is_checked.return_value = False
    duet = MagicMock()
    duet.is_checked.return_value = True
    page = _page_with({"Reuse of content": reuse, "'Stitch'": stitch, "'Duet'": duet})

    _set_interactivity(page, stitch=True, duet=True)

    stitch.click.assert_called_once_with(force=True)
    duet.click.assert_not_called()
    reuse.click.assert_not_called()


def test_complete_upload_form_posts_by_default() -> None:
    page = MagicMock()

    steps = _run_form(page)

    steps["_post_video"].assert_called_once_with(page, skip_restricted=False)
    steps["_save_draft"].assert_not_called()
    steps["_set_sound"].assert_not_called()
    steps["_set_ai_label"].assert_not_called()


def test_complete_upload_form_saves_a_draft_instead_of_posting() -> None:
    page = MagicMock()

    steps = _run_form(page, draft=True)

    steps["_save_draft"].assert_called_once_with(page)
    steps["_post_video"].assert_not_called()


def test_complete_upload_form_routes_the_post_options() -> None:
    page = MagicMock()

    steps = _run_form(
        page,
        sound_name="song",
        sound_artist="artist",
        ai_label=False,
        skip_restricted=True,
        comment=False,
    )

    steps["_set_sound"].assert_called_once_with(page, "song", "artist")
    steps["_set_ai_label"].assert_called_once_with(page, False)
    steps["_post_video"].assert_called_once_with(page, skip_restricted=True)
    assert steps["_set_interactivity"].call_args.kwargs["comment"] is False


@patch("tiktok_uploader.upload.get_browser")
@patch("tiktok_uploader.auth.AuthBackend.authenticate_agent")
@patch("tiktok_uploader.upload.complete_upload_form")
def test_upload_video_passes_the_post_options(
    mock_complete_upload, mock_auth, mock_browser
) -> None:
    mock_browser.return_value = mock_auth.return_value = MagicMock()

    upload_video(
        filename=FILENAME,
        sessionid="test_session",
        sound_name="song",
        draft=True,
        ai_label=False,
        skip_restricted=True,
    )

    options = mock_complete_upload.call_args.kwargs
    assert options["sound_name"] == "song"
    assert options["draft"] is True
    assert options["ai_label"] is False
    assert options["skip_restricted"] is True


@patch("tiktok_uploader.upload.get_browser")
@patch("tiktok_uploader.auth.AuthBackend.authenticate_agent")
@patch("tiktok_uploader.upload.complete_upload_form")
def test_upload_video_leaves_the_ai_label_alone_by_default(
    mock_complete_upload, mock_auth, mock_browser
) -> None:
    mock_browser.return_value = mock_auth.return_value = MagicMock()

    upload_video(filename=FILENAME, sessionid="test_session")

    assert "ai_label" not in mock_complete_upload.call_args.kwargs
    assert "draft" not in mock_complete_upload.call_args.kwargs


@patch("tiktok_uploader.upload.get_browser")
@patch("tiktok_uploader.auth.AuthBackend.authenticate_agent")
@patch("tiktok_uploader.upload.complete_upload_form")
def test_a_videos_own_options_override_the_batch_keywords(
    mock_complete_upload, mock_auth, mock_browser
) -> None:
    mock_browser.return_value = mock_auth.return_value = MagicMock()
    uploader = TikTokUploader(sessionid="test_session")

    uploader.upload_videos(
        [{"path": FILENAME, "comment": False}, {"path": FILENAME}], comment=True
    )

    first, second = mock_complete_upload.call_args_list
    assert first.kwargs["comment"] is False
    assert second.kwargs["comment"] is True


@patch("tiktok_uploader.upload.get_browser")
@patch("tiktok_uploader.auth.AuthBackend.authenticate_agent")
@patch("tiktok_uploader.upload.complete_upload_form")
def test_a_scheduled_draft_is_rejected(
    mock_complete_upload, mock_auth, mock_browser
) -> None:
    mock_browser.return_value = mock_auth.return_value = MagicMock()
    uploader = TikTokUploader(sessionid="test_session")
    schedule = datetime.datetime.now(pytz.UTC) + datetime.timedelta(days=1)

    failed = uploader.upload_videos(
        [{"path": FILENAME, "schedule": schedule, "draft": True}]
    )

    assert len(failed) == 1
    mock_complete_upload.assert_not_called()


@patch("tiktok_uploader.upload.get_browser")
@patch("tiktok_uploader.auth.AuthBackend.authenticate_agent")
@patch("tiktok_uploader.upload.complete_upload_form")
def test_upload_videos_logs_each_outcome(
    mock_complete_upload, mock_auth, mock_browser, caplog: LogCaptureFixture
) -> None:
    mock_browser.return_value = mock_auth.return_value = MagicMock()
    mock_complete_upload.side_effect = [None, None, None, FailedToUpload("rejected")]
    schedule = datetime.datetime.now(pytz.UTC) + datetime.timedelta(days=1)
    caplog.set_level(logging.INFO, logger="tiktok_uploader")

    TikTokUploader(sessionid="test_session").upload_videos(
        [
            {"path": FILENAME},
            {"path": FILENAME, "draft": True},
            {"path": FILENAME, "schedule": schedule},
            {"path": FILENAME},
        ]
    )

    path = os.path.abspath(FILENAME)
    logged = [(r.levelname, r.getMessage()) for r in caplog.records]
    assert logged[0] == ("INFO", f"Posted {path}")
    assert logged[1] == ("INFO", f"Saved {path} as a draft")
    assert logged[2][1].startswith(f"Scheduled {path} for ")
    assert logged[3] == ("ERROR", f"Failed to upload {path}: rejected")
    assert logged[4] == ("INFO", "Uploaded 3 of 4 videos")


def test_set_visibility_failure_stops_the_upload() -> None:
    page = MagicMock()
    page.locator.return_value.click.side_effect = PlaywrightTimeoutError("intercepted")

    with raises(FailedToUpload, match="only_you"):
        _set_visibility(page, "only_you")


def test_set_schedule_failure_keeps_its_reason() -> None:
    page = MagicMock()
    page.evaluate.return_value = "UTC"
    page.locator.return_value.click.side_effect = PlaywrightTimeoutError("intercepted")
    schedule = datetime.datetime.now(pytz.UTC) + datetime.timedelta(days=1)

    with raises(FailedToUpload, match="Failed to set schedule: intercepted"):
        _set_schedule_video(page, schedule)


@patch("tiktok_uploader.upload._dismiss_blocking_modals")
def test_post_video_stops_on_a_restriction_warning(mock_dismiss) -> None:
    warning = MagicMock()
    warning.all.return_value = [MagicMock(is_visible=MagicMock(return_value=True))]
    post_btn = MagicMock()
    post_btn.get_attribute.return_value = "false"
    page = _page_with(
        {"post_video_button": post_btn, "Content may be restricted": warning}
    )

    with raises(ContentRestricted):
        _post_video(page, skip_restricted=True)

    post_btn.click.assert_not_called()


@patch("tiktok_uploader.upload._dismiss_blocking_modals")
def test_post_video_ignores_the_restriction_warning_unless_asked(
    mock_dismiss,
) -> None:
    warning = MagicMock()
    warning.all.return_value = [MagicMock(is_visible=MagicMock(return_value=True))]
    post_btn = MagicMock()
    post_btn.get_attribute.return_value = "false"
    page = _page_with(
        {"post_video_button": post_btn, "Content may be restricted": warning}
    )

    _post_video(page)

    post_btn.click.assert_called_once()


def _post_result_page(url: str, error_visible: bool) -> MagicMock:
    """
    A page that has not confirmed the post, showing TikTok's error or not
    """
    confirmation = MagicMock()
    confirmation.count.return_value = 0
    error = MagicMock()
    error.count.return_value = 1 if error_visible else 0
    error.first.is_visible.return_value = error_visible
    error.first.inner_text.return_value = "Something went wrong"
    page = _page_with(
        {"Your video has been uploaded": confirmation, "Something went wrong": error}
    )
    page.url = url
    return page


def test_wait_for_post_result_fails_fast_on_tiktoks_error() -> None:
    page = _post_result_page("https://www.tiktok.com/tiktokstudio/upload", True)

    with raises(FailedToUpload, match="Something went wrong"):
        _wait_for_post_result(page)


def test_wait_for_post_result_accepts_the_redirect_to_the_content_list() -> None:
    page = _post_result_page("https://www.tiktok.com/tiktokstudio/content", False)

    _wait_for_post_result(page)


@patch("tiktok_uploader.upload.time.sleep")
@patch("tiktok_uploader.upload.time.monotonic", side_effect=itertools.count(0, 1000))
def test_wait_for_post_result_times_out(mock_monotonic, mock_sleep) -> None:
    page = _post_result_page("https://www.tiktok.com/tiktokstudio/upload", False)

    with raises(FailedToUpload, match="did not confirm"):
        _wait_for_post_result(page)


def _ai_label_page(states: list[str]) -> MagicMock:
    """
    A page whose AI label switch reports the given data-state values in order
    """
    switch = MagicMock()
    switch.get_attribute.side_effect = states
    page = _page_with({"aigc_container": switch})
    page.switch = switch
    return page


@patch("tiktok_uploader.upload.time.sleep")
def test_set_ai_label_turns_on_and_confirms(mock_sleep) -> None:
    page = _ai_label_page(["unchecked", "checked"])

    _set_ai_label(page, True)

    page.switch.click.assert_called_once()
    confirms = [c for c in page.locator.call_args_list if "Turn on" in c.args[0]]
    assert len(confirms) == 1


@patch("tiktok_uploader.upload.time.sleep")
def test_set_ai_label_leaves_a_matching_switch_alone(mock_sleep) -> None:
    page = _ai_label_page(["checked"])

    _set_ai_label(page, True)

    page.switch.click.assert_not_called()


@patch("tiktok_uploader.upload.time.sleep")
def test_set_ai_label_failure_stops_the_upload(mock_sleep) -> None:
    page = _ai_label_page(["unchecked"] * 20)

    with raises(FailedToUpload):
        _set_ai_label(page, True)


@patch("tiktok_uploader.upload._dismiss_blocking_modals")
def test_save_draft_clicks_the_button_and_waits_for_the_form_to_close(
    mock_dismiss,
) -> None:
    page = MagicMock()
    draft_btn = page.locator.return_value
    draft_btn.get_attribute.return_value = "false"

    _save_draft(page)

    draft_btn.click.assert_called_once()
    assert draft_btn.wait_for.call_args.kwargs["state"] == "detached"


def _sound(title: str, artist: str) -> MagicMock:
    """
    A sound search result with the given title and artist
    """
    item = MagicMock()
    item.locator.side_effect = lambda selector: MagicMock(
        inner_text=MagicMock(
            return_value=title if "infoBasicTitle" in selector else artist
        )
    )
    return item


def test_match_sound_matches_title_and_artist() -> None:
    wrong_artist = _sound("Song", "Someone Else")
    right = _sound("song ", "The Artist")

    assert _match_sound([wrong_artist, right], "Song", "artist") is right


def test_match_sound_takes_the_first_title_match_without_an_artist() -> None:
    first = _sound("Song", "A")
    second = _sound("Song", "B")

    assert _match_sound([_sound("Other", "A"), first, second], "song", None) is first


def test_match_sound_returns_none_without_a_match() -> None:
    assert _match_sound([_sound("Other", "A")], "Song", None) is None


def test_go_to_upload_registers_the_dialog_handler_once() -> None:
    page = MagicMock()

    _go_to_upload(page)
    _go_to_upload(page)

    assert page.on.call_count == 1


def test_check_valid_path_rejects_values_that_are_not_paths() -> None:
    assert _check_valid_path(False) is False
    assert _check_valid_path(datetime.datetime.now()) is False


def test_convert_videos_dict_with_non_string_values() -> None:
    array = _convert_videos_dict([{"path": FILENAME, "draft": True}])

    assert array[0]["path"] == FILENAME
    assert array[0]["description"] == ""


def test_convert_videos_dict_never_takes_an_option_as_the_description() -> None:
    array = _convert_videos_dict(
        [{"path": FILENAME, "visibility": "only_you", "sound_name": "song"}]
    )

    assert array[0]["description"] == ""


def test_convert_videos_dict_still_takes_an_unknown_key_as_the_description() -> None:
    array = _convert_videos_dict([{"path": FILENAME, "caption_text": "hello"}])

    assert array[0]["description"] == "hello"
