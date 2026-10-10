"""
Tests the command line argument validation
"""

from argparse import Namespace

from pytest import raises

from tiktok_uploader.cli import validate_uploader_args


def _args(**overrides) -> Namespace:
    defaults = {
        "video": __file__,
        "cover": None,
        "cookies": "cookies.txt",
        "username": None,
        "password": None,
        "schedule": None,
        "draft": False,
    }
    defaults.update(overrides)
    return Namespace(**defaults)


def test_draft_alone_is_valid() -> None:
    validate_uploader_args(_args(draft=True))


def test_draft_and_schedule_are_mutually_exclusive() -> None:
    with raises(ValueError):
        validate_uploader_args(_args(draft=True, schedule="2026-10-16 18:30"))


def _run_main(**overrides):
    """
    Runs the CLI with the given args and returns the description it uploaded with
    """
    from unittest.mock import MagicMock, patch

    from tiktok_uploader import cli

    defaults = {
        "description": None,
        "no_auto_caption": False,
        "no_ai_label": False,
        "product_id": None,
        "visibility": "everyone",
        "proxy": None,
        "sessionid": None,
        "attach": False,
    }
    args = _args(**{**defaults, **overrides})
    with (
        patch.object(cli, "get_uploader_args", return_value=args),
        patch.object(cli, "auto_caption", return_value="Generated #dance") as caption,
        patch.object(cli, "TikTokUploader") as uploader_class,
    ):
        uploader = MagicMock()
        uploader_class.return_value.__enter__.return_value = uploader
        cli.main()
    return uploader.upload_video.call_args.kwargs["description"], caption


def test_cli_generates_caption_without_description() -> None:
    description, caption = _run_main()

    assert description == "Generated #dance"
    caption.assert_called_once_with(__file__)


def test_cli_description_overrides_generated_caption() -> None:
    description, caption = _run_main(description="My own title #mine")

    assert description == "My own title #mine"
    caption.assert_not_called()


def test_cli_no_auto_caption_uploads_without_description() -> None:
    description, caption = _run_main(no_auto_caption=True)

    assert description == ""
    caption.assert_not_called()


def test_cli_ai_label_on_by_default() -> None:
    from unittest.mock import MagicMock, patch

    from tiktok_uploader import cli

    for flag, expected in ((False, True), (True, False)):
        args = _args(
            description="hi",
            no_auto_caption=False,
            no_ai_label=flag,
            product_id=None,
            visibility="everyone",
            proxy=None,
            sessionid=None,
            attach=False,
        )
        with (
            patch.object(cli, "get_uploader_args", return_value=args),
            patch.object(cli, "TikTokUploader") as uploader_class,
        ):
            uploader = MagicMock()
            uploader_class.return_value.__enter__.return_value = uploader
            cli.main()
        assert uploader.upload_video.call_args.kwargs["ai_label"] is expected
