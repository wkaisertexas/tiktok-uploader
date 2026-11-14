"""AI disclosure must be explicitly requested and verified before posting."""

from unittest.mock import MagicMock, patch

from pytest import raises

from tiktok_uploader import upload
from tiktok_uploader.cli import main


def ai_page(checked=False, confirmation=True, succeeds=True):
    page = MagicMock()
    control = page.locator.return_value
    state = {"checked": checked}
    control.is_visible.return_value = True
    control.get_attribute.side_effect = lambda _: str(state["checked"]).lower()
    confirm = page.get_by_role.return_value.filter.return_value.get_by_role.return_value

    def toggle():
        if not confirmation and succeeds:
            state["checked"] = True

    def confirm_label():
        if succeeds:
            state["checked"] = True

    control.click.side_effect = toggle
    confirm.click.side_effect = confirm_label
    if not confirmation:
        confirm.wait_for.side_effect = upload.PlaywrightTimeoutError("No dialog")

    def assert_attribute(name, value, **kwargs):
        assert control.get_attribute(name) == value

    assertion = MagicMock()
    assertion.to_have_attribute.side_effect = assert_attribute
    return page, control, confirm, assertion


def test_ai_label_default_does_not_change_the_page():
    page = MagicMock()
    upload._set_ai_generated(page, False)
    assert not page.mock_calls


def test_ai_label_handles_first_use_confirmation():
    page, control, confirm, assertion = ai_page()
    with patch("tiktok_uploader.upload.expect", return_value=assertion):
        upload._set_ai_generated(page, True)
    control.click.assert_called_once()
    confirm.click.assert_called_once()
    assert control.get_attribute("aria-checked") == "true"


def test_ai_label_already_enabled_is_not_toggled_off():
    page, control, confirm, assertion = ai_page(checked=True)
    with patch("tiktok_uploader.upload.expect", return_value=assertion):
        upload._set_ai_generated(page, True)
    control.click.assert_not_called()
    confirm.click.assert_not_called()


def test_ai_label_expands_collapsed_settings():
    page, control, _, assertion = ai_page()
    control.is_visible.return_value = False
    with patch("tiktok_uploader.upload.expect", return_value=assertion):
        upload._set_ai_generated(page, True)
    page.get_by_text.assert_called_once_with("Show more", exact=True)
    page.get_by_text.return_value.click.assert_called_once()


def test_ai_label_handles_accounts_without_the_first_use_dialog():
    page, control, confirm, assertion = ai_page(confirmation=False)
    with patch("tiktok_uploader.upload.expect", return_value=assertion):
        upload._set_ai_generated(page, True)
    assert control.get_attribute("aria-checked") == "true"
    confirm.click.assert_not_called()


def test_requested_label_failure_prevents_posting():
    page, _, _, assertion = ai_page(succeeds=False)
    with (
        patch("tiktok_uploader.upload.expect", return_value=assertion),
        patch("tiktok_uploader.upload._go_to_upload"),
        patch("tiktok_uploader.upload._remove_cookies_window"),
        patch("tiktok_uploader.upload._set_video"),
        patch("tiktok_uploader.upload._set_interactivity"),
        patch("tiktok_uploader.upload._set_description"),
        patch("tiktok_uploader.upload._post_video") as post,
        raises(upload.FailedToUpload),
    ):
        upload.complete_upload_form(
            page, "example.mp4", "AI remix", None, True, ai_generated=True
        )
    post.assert_not_called()


def test_cli_forwards_ai_generated_flag(tmp_path):
    video = tmp_path / "example.mp4"
    video.write_bytes(b"offline test")
    with (
        patch("sys.argv", ["tiktok-uploader", "-v", str(video), "--ai-generated"]),
        patch("tiktok_uploader.cli.TikTokUploader") as client,
    ):
        main()
    instance = client.return_value.__enter__.return_value
    assert instance.upload_video.call_args.kwargs["ai_generated"] is True


def test_single_upload_forwards_ai_label_to_form():
    client = upload.TikTokUploader(sessionid="offline")
    with patch.object(client, "upload_videos", return_value=[]) as batch:
        assert client.upload_video("example.mp4", ai_generated=True)
    assert batch.call_args.args[0][0]["ai_generated"] is True


def test_convenience_upload_forwards_ai_label():
    with patch("tiktok_uploader.upload.TikTokUploader") as client:
        client.return_value.upload_videos.return_value = []
        assert upload.upload_video("example.mp4", ai_generated=True) == []
    assert (
        client.return_value.upload_videos.call_args.args[0][0]["ai_generated"] is True
    )
