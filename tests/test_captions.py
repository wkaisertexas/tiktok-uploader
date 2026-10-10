"""
Tests writing captions from a video's original title
"""

import io
import json
from unittest.mock import MagicMock, patch

from pytest import MonkeyPatch, raises

from tiktok_uploader import captions
from tiktok_uploader.captions import (
    CaptionError,
    _parse_reply,
    auto_caption,
    rewrite_caption,
    source_title,
)


def _response(content: str) -> io.BytesIO:
    body = {"choices": [{"message": {"content": content}}]}
    return io.BytesIO(json.dumps(body).encode())


def test_source_title_prefers_sidecar(tmp_path) -> None:
    video = tmp_path / "26-10-07_KevwT-dFgBI_Dance_Cover.mp4"
    video.write_text("")
    video.with_suffix(".txt").write_text("휘파람(Whistle) - BLACKPINK | Dance cover\n")

    assert source_title(str(video)) == "휘파람(Whistle) - BLACKPINK | Dance cover"


def test_source_title_falls_back_to_filename(tmp_path) -> None:
    video = tmp_path / "26-10-07_KevwT-dFgBI_Old_school_dance_cover.mp4"
    video.write_text("")

    assert source_title(str(video)) == "Old school dance cover"


def test_parse_reply_joins_caption_and_cleans_hashtags() -> None:
    reply = 'Sure! {"caption": "Old school vibes", "hashtags": ["#Dance", "old school", "dance", "oldschool"]}'

    assert _parse_reply(reply) == "Old school vibes #dance #oldschool"


def test_parse_reply_drops_hashtags_that_do_not_fit(monkeypatch: MonkeyPatch) -> None:
    monkeypatch.setattr(captions.config, "max_description_length", 30)
    reply = json.dumps(
        {"caption": "Old school vibes", "hashtags": ["dance", "oldschool"]}
    )

    assert _parse_reply(reply) == "Old school vibes #dance"


def test_parse_reply_rejects_non_json() -> None:
    with raises(CaptionError):
        _parse_reply("I can not help with that")


def test_rewrite_caption_needs_api_key(monkeypatch: MonkeyPatch) -> None:
    monkeypatch.delenv(captions.config.captions.api_key_env, raising=False)

    with raises(CaptionError):
        rewrite_caption("Dance cover")


def test_rewrite_caption_rejects_unresolved_placeholder(
    monkeypatch: MonkeyPatch,
) -> None:
    """
    MCP hosts pass the raw "${VAR}" placeholder through when the key is unset
    """
    monkeypatch.setenv(captions.config.captions.api_key_env, "${MODEL_ACCESS_KEY}")

    with raises(CaptionError, match="MODEL_ACCESS_KEY is not set"):
        rewrite_caption("Dance cover")


@patch("tiktok_uploader.captions.urllib.request.urlopen")
def test_rewrite_caption_sends_title_and_key(
    mock_urlopen: MagicMock, monkeypatch: MonkeyPatch
) -> None:
    monkeypatch.setenv(captions.config.captions.api_key_env, "test-key")
    mock_urlopen.return_value.__enter__.return_value = _response(
        '{"caption": "Whistle by BLACKPINK", "hashtags": ["blackpink", "whistle"]}'
    )

    assert rewrite_caption("휘파람(Whistle) - BLACKPINK") == (
        "Whistle by BLACKPINK #blackpink #whistle"
    )

    request = mock_urlopen.call_args.args[0]
    assert request.get_header("Authorization") == "Bearer test-key"
    body = json.loads(request.data)
    assert body["model"] == captions.config.captions.model
    assert "휘파람(Whistle) - BLACKPINK" in body["messages"][0]["content"]


@patch("tiktok_uploader.captions.rewrite_caption")
def test_auto_caption_falls_back_to_original_title(
    mock_rewrite: MagicMock, tmp_path
) -> None:
    video = tmp_path / "clip.mp4"
    video.write_text("")
    video.with_suffix(".txt").write_text("好熟悉的歌！#dance")
    mock_rewrite.side_effect = CaptionError("offline")

    assert auto_caption(str(video)) == "好熟悉的歌！#dance"


@patch("tiktok_uploader.captions.urllib.request.urlopen")
def test_rewrite_caption_retries_an_empty_reply(
    mock_urlopen: MagicMock, monkeypatch: MonkeyPatch
) -> None:
    monkeypatch.setenv(captions.config.captions.api_key_env, "test-key")
    empty = io.BytesIO(
        json.dumps({"choices": [{"message": {"content": None}}]}).encode()
    )
    good = _response('{"caption": "Old school vibes", "hashtags": ["dance"]}')
    mock_urlopen.return_value.__enter__.side_effect = [empty, good]

    assert rewrite_caption("Old school dance cover") == "Old school vibes #dance"
    assert mock_urlopen.call_count == 2
