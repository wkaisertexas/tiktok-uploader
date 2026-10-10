"""
Tests the MCP server's tools without starting a browser
"""

import datetime
import io
import json
import os
import subprocess
from unittest.mock import MagicMock, patch

import pytz
from mcp.server.mcpserver.exceptions import ToolError
from pytest import MonkeyPatch, raises

from tiktok_uploader import mcp_server


def _video(tmp_path, name: str = "26-10-07_KevwT-dFgBI_Dance_Cover.mp4") -> str:
    video = tmp_path / name
    video.write_text("")
    return str(video)


def _cookies(tmp_path, monkeypatch: MonkeyPatch) -> None:
    cookies = tmp_path / "cookies.txt"
    cookies.write_text("")
    monkeypatch.setenv("TIKTOK_COOKIES", str(cookies))


def test_list_videos_newest_first_with_titles(tmp_path) -> None:
    old = _video(tmp_path, "26-10-07_aaaaaaaaaaa_Old_one.mp4")
    new = _video(tmp_path, "26-10-07_bbbbbbbbbbb_New_one.mp4")
    (tmp_path / "26-10-07_bbbbbbbbbbb_New_one.txt").write_text("새로운 #dance")
    (tmp_path / "notes.md").write_text("")
    os.utime(old, (1, 1))

    assert mcp_server.list_videos(str(tmp_path)) == [
        {"path": new, "title": "새로운 #dance"},
        {"path": old, "title": "Old one"},
    ]


@patch("tiktok_uploader.mcp_server.auto_caption", return_value="Generated #dance")
def test_suggest_caption_uses_the_videos_title(
    mock_caption: MagicMock, tmp_path
) -> None:
    video = _video(tmp_path)

    assert mcp_server.suggest_caption(video) == "Generated #dance"
    mock_caption.assert_called_once_with(video)

    notes = tmp_path / "notes.md"
    notes.write_text("")
    with raises(ToolError, match="Not a supported video file"):
        mcp_server.suggest_caption(str(notes))


def test_upload_rejects_scheduled_draft(tmp_path, monkeypatch: MonkeyPatch) -> None:
    _cookies(tmp_path, monkeypatch)

    with raises(ToolError, match="draft"):
        mcp_server.upload_video(
            _video(tmp_path), draft=True, schedule="2026-10-16 18:30"
        )


def test_upload_needs_cookies(tmp_path, monkeypatch: MonkeyPatch) -> None:
    monkeypatch.delenv("TIKTOK_COOKIES", raising=False)

    with raises(ToolError, match="TIKTOK_COOKIES"):
        mcp_server.upload_video(_video(tmp_path), description="hi")


def test_upload_rejects_schedule_out_of_range(
    tmp_path, monkeypatch: MonkeyPatch
) -> None:
    _cookies(tmp_path, monkeypatch)
    too_late = datetime.datetime.now(pytz.UTC) + datetime.timedelta(days=11)

    with raises(ToolError, match="10 days"):
        mcp_server.upload_video(
            _video(tmp_path), schedule=too_late.strftime("%Y-%m-%d %H:%M")
        )


@patch("tiktok_uploader.mcp_server.subprocess.run")
def test_upload_schedule_rounds_minutes_and_reports_the_time(
    mock_run: MagicMock, tmp_path, monkeypatch: MonkeyPatch
) -> None:
    _cookies(tmp_path, monkeypatch)
    mock_run.return_value = _worker('{"success": true}')
    when = datetime.datetime.now(pytz.UTC).replace(
        second=0, microsecond=0
    ) + datetime.timedelta(hours=1)
    rounded = when + datetime.timedelta(minutes=(5 - when.minute % 5) % 5)

    result = mcp_server.upload_video(
        _video(tmp_path), description="hi", schedule=when.strftime("%Y-%m-%d %H:%M")
    )

    job = json.loads(mock_run.call_args.kwargs["input"])
    assert job["schedule"] == rounded.isoformat()
    assert result["scheduled_for_utc"] == rounded.strftime("%Y-%m-%d %H:%M")

    with raises(ToolError, match="schedule must be a UTC time"):
        mcp_server.upload_video(
            _video(tmp_path), description="hi", schedule="next tuesday"
        )


def _worker(stdout: str, stderr: str = "", returncode: int = 0) -> MagicMock:
    return MagicMock(stdout=stdout, stderr=stderr, returncode=returncode)


@patch("tiktok_uploader.mcp_server.auto_caption", return_value="Generated #dance")
@patch("tiktok_uploader.mcp_server.subprocess.run")
def test_upload_runs_in_a_worker_with_caption_and_options(
    mock_run: MagicMock,
    mock_caption: MagicMock,
    tmp_path,
    monkeypatch: MonkeyPatch,
) -> None:
    _cookies(tmp_path, monkeypatch)
    mock_run.return_value = _worker('{"success": true}')
    video = _video(tmp_path)

    result = mcp_server.upload_video(video, draft=True, visibility="only_you")

    assert result["description"] == "Generated #dance"
    command = mock_run.call_args.args[0]
    assert command[-2:] == ["-m", "tiktok_uploader.upload_worker"]
    job = json.loads(mock_run.call_args.kwargs["input"])
    assert job["video"] == video
    assert job["description"] == "Generated #dance"
    assert job["draft"] is True
    assert job["ai_label"] is True
    assert job["visibility"] == "only_you"
    assert job["schedule"] is None


@patch("tiktok_uploader.mcp_server.subprocess.run")
def test_each_upload_gets_its_own_worker(
    mock_run: MagicMock, tmp_path, monkeypatch: MonkeyPatch
) -> None:
    _cookies(tmp_path, monkeypatch)
    mock_run.return_value = _worker('{"success": true}')

    mcp_server.upload_video(_video(tmp_path), description="one")
    mcp_server.upload_video(_video(tmp_path), description="two")

    assert mock_run.call_count == 2


@patch("tiktok_uploader.mcp_server.auto_caption")
@patch("tiktok_uploader.mcp_server.subprocess.run")
def test_upload_failure_reports_log_without_cookies(
    mock_run: MagicMock,
    mock_caption: MagicMock,
    tmp_path,
    monkeypatch: MonkeyPatch,
) -> None:
    _cookies(tmp_path, monkeypatch)
    log = (
        "DEBUG: Adding cookie: {'name': 'sessionid', 'value': 'secret123'}\n"
        "[03:22:28] \x1b[92mSetting schedule\x1b[0m\n"
        "[03:22:58] Failed to set schedule\n"
    )
    mock_run.return_value = _worker(
        '{"success": false, "error": "FailedToUpload: x"}', stderr=log
    )

    with raises(ToolError) as error:
        mcp_server.upload_video(_video(tmp_path), description="My own #title")

    message = str(error.value)
    assert "Failed to set schedule" in message
    assert "[03:22:28] Setting schedule" in message
    assert "secret123" not in message
    mock_caption.assert_not_called()
    job = json.loads(mock_run.call_args.kwargs["input"])
    assert job["description"] == "My own #title"


@patch("tiktok_uploader.mcp_server.subprocess.run")
def test_upload_reports_a_crashed_worker(
    mock_run: MagicMock, tmp_path, monkeypatch: MonkeyPatch
) -> None:
    _cookies(tmp_path, monkeypatch)
    mock_run.return_value = _worker("", stderr="Traceback ...", returncode=1)

    with raises(ToolError, match="exited with 1"):
        mcp_server.upload_video(_video(tmp_path), description="hi")


@patch("tiktok_uploader.mcp_server.subprocess.run")
def test_upload_reports_a_timeout(
    mock_run: MagicMock, tmp_path, monkeypatch: MonkeyPatch
) -> None:
    _cookies(tmp_path, monkeypatch)
    mock_run.side_effect = subprocess.TimeoutExpired(
        cmd="worker", timeout=540, stderr=b"upload stalled\n"
    )

    with raises(ToolError) as error:
        mcp_server.upload_video(_video(tmp_path), description="hi")

    message = str(error.value)
    assert "timed out after 540 seconds" in message
    assert "upload stalled" in message


@patch("tiktok_uploader.upload_worker.TikTokUploader")
def test_worker_runs_the_job_and_prints_json(
    mock_uploader_class: MagicMock, monkeypatch: MonkeyPatch, capsys
) -> None:
    from tiktok_uploader import upload_worker

    uploader = mock_uploader_class.return_value.__enter__.return_value
    uploader.upload_video.return_value = True
    job = {
        "video": "/v.mp4",
        "cookies": "/c.txt",
        "description": "hi",
        "schedule": "2026-10-16T18:30:00+00:00",
        "visibility": "everyone",
        "draft": False,
        "ai_label": True,
    }
    monkeypatch.setattr("sys.stdin", io.StringIO(json.dumps(job)))

    upload_worker.main()

    assert json.loads(capsys.readouterr().out) == {"success": True}
    kwargs = uploader.upload_video.call_args.kwargs
    assert kwargs["schedule"] == datetime.datetime(
        2026, 10, 16, 18, 30, tzinfo=pytz.UTC
    )
    assert kwargs["ai_label"] is True


@patch("tiktok_uploader.upload_worker.TikTokUploader")
def test_worker_reports_exceptions_as_json(
    mock_uploader_class: MagicMock, monkeypatch: MonkeyPatch, capsys
) -> None:
    from tiktok_uploader import upload_worker

    mock_uploader_class.return_value.__enter__.side_effect = Exception("expired")
    job = {
        "video": "/v.mp4",
        "cookies": "/c.txt",
        "description": "",
        "schedule": None,
        "visibility": "everyone",
        "draft": False,
        "ai_label": True,
    }
    monkeypatch.setattr("sys.stdin", io.StringIO(json.dumps(job)))

    upload_worker.main()

    assert json.loads(capsys.readouterr().out) == {
        "success": False,
        "error": "Exception: expired",
    }
