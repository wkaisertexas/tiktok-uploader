"""
MCP server for the uploader: list videos, write captions, and post, schedule or
draft videos on TikTok

Configured with environment variables:
- TIKTOK_COOKIES: the Netscape cookies file to log in with, if not the
  `default_cookies` file from config.toml
- the variable named by `api_key_env` in config.toml, for generated captions
"""

import datetime
import json
import re
import subprocess
import sys
import threading
from pathlib import Path
from typing import Literal

import pytz
from mcp.server.mcpserver import MCPServer
from mcp.server.mcpserver.exceptions import ToolError
from mcp.types import ToolAnnotations

from tiktok_uploader import config
from tiktok_uploader.auth import default_cookies_path
from tiktok_uploader.captions import auto_caption, source_title
from tiktok_uploader.upload import (
    _check_valid_path,
    _check_valid_schedule,
    _get_valid_schedule_minute,
)

server = MCPServer(
    name="tiktok-uploader",
    instructions="Uploads videos to the TikTok account whose cookies the server was "
    + "started with. Without a description, an English caption with hashtags is "
    + "written from the video's .txt title or filename. Posting is public; use "
    + "draft=True or visibility='only_you' when unsure.",
)

# one browser at a time: TikTok sessions do not like parallel uploads
_upload_lock = threading.Lock()

# below the 600 second tool timeout the MCP host is configured with
UPLOAD_TIMEOUT = 540  # seconds

ANSI_ESCAPE = re.compile(r"\x1b\[[0-9;]*m")


def _last_lines(log: str, count: int = 8) -> str:
    """
    The end of an upload's log, without colors or lines that carry cookie values
    """
    lines = [
        ANSI_ESCAPE.sub("", line)
        for line in log.splitlines()
        if line.strip() and "Adding cookie" not in line and "'value'" not in line
    ]
    return "\nLast log lines:\n" + "\n".join(lines[-count:])


def _run_upload(job: dict) -> None:
    """
    Runs one upload in a fresh process: Playwright's sync API can not be started
    twice in the server's reused worker threads
    """
    try:
        worker = subprocess.run(
            [sys.executable, "-m", "tiktok_uploader.upload_worker"],
            input=json.dumps(job),
            capture_output=True,
            text=True,
            timeout=UPLOAD_TIMEOUT,
        )
    except subprocess.TimeoutExpired as e:
        log = e.stderr.decode() if isinstance(e.stderr, bytes) else (e.stderr or "")
        raise ToolError(
            f"Upload timed out after {UPLOAD_TIMEOUT} seconds.{_last_lines(log)}"
        ) from e

    try:
        result = json.loads(worker.stdout)
    except json.JSONDecodeError:
        result = {"success": False, "error": f"worker exited with {worker.returncode}"}

    if not result.get("success"):
        error = result.get("error") or "the upload did not complete"
        raise ToolError(f"Upload failed: {error}{_last_lines(worker.stderr)}")


def _video_path(video_path: str) -> str:
    path = str(Path(video_path).expanduser().resolve())
    if not _check_valid_path(path):
        raise ToolError(f"Not a supported video file: {video_path}")
    return path


def _parse_schedule(schedule: str) -> datetime.datetime:
    try:
        parsed = datetime.datetime.strptime(schedule, "%Y-%m-%d %H:%M")
    except ValueError as e:
        raise ToolError("schedule must be a UTC time like '2026-10-16 18:30'") from e

    parsed = _get_valid_schedule_minute(pytz.UTC.localize(parsed), 5)
    if not _check_valid_schedule(parsed):
        raise ToolError(
            "schedule must be at least 20 minutes and at most 10 days in the future"
        )
    return parsed


@server.tool(annotations=ToolAnnotations(read_only_hint=True))
def list_videos(directory: str) -> list[dict[str, str]]:
    """
    Lists the uploadable videos in a directory, newest first, with each video's
    original title (from its .txt sidecar or filename).
    """
    folder = Path(directory).expanduser()
    if not folder.is_dir():
        raise ToolError(f"Not a directory: {directory}")

    videos = sorted(
        (p for p in folder.iterdir() if _check_valid_path(str(p))),
        key=lambda p: p.stat().st_mtime,
        reverse=True,
    )
    return [{"path": str(p), "title": source_title(str(p))} for p in videos]


@server.tool(annotations=ToolAnnotations(read_only_hint=True, open_world_hint=True))
def suggest_caption(video_path: str) -> str:
    """
    Writes an English TikTok caption with hashtags from the video's original title,
    without uploading anything. Falls back to the original title if the caption
    model can not be reached.
    """
    return auto_caption(_video_path(video_path))


@server.tool(
    annotations=ToolAnnotations(
        read_only_hint=False, destructive_hint=False, open_world_hint=True
    )
)
def upload_video(
    video_path: str,
    description: str | None = None,
    schedule: str | None = None,
    draft: bool = False,
    ai_label: bool = True,
    visibility: Literal["everyone", "friends", "only_you"] = "everyone",
) -> dict[str, str | bool | None]:
    """
    Uploads a video to TikTok. Takes one to two minutes.

    - description: the caption, used as given. Leave it out to write an English
      caption with hashtags from the video's original title.
    - schedule: post later instead of now, as a UTC time 'YYYY-MM-DD HH:MM',
      20 minutes to 10 days ahead. Minutes round up to a multiple of 5.
    - draft: save to the account's drafts instead of posting. Can not be scheduled.
    - ai_label: turn on TikTok's "AI-generated content" label. Leave it on for AI
      videos: TikTok may remove realistic AI content that is not labeled.
    - visibility: who can see the post.
    """
    path = _video_path(video_path)
    if draft and schedule:
        raise ToolError("A draft can not be scheduled")

    cookies = default_cookies_path()
    if not cookies:
        raise ToolError(
            "No cookies file: set TIKTOK_COOKIES or save one at "
            + config.default_cookies
        )

    when = _parse_schedule(schedule) if schedule else None
    if description is None:
        description = auto_caption(path)

    job = {
        "video": path,
        "cookies": cookies,
        "description": description,
        "schedule": when.isoformat() if when else None,
        "visibility": visibility,
        "draft": draft,
        "ai_label": ai_label,
    }
    with _upload_lock:
        _run_upload(job)

    return {
        "video": path,
        "description": description,
        "scheduled_for_utc": when.strftime("%Y-%m-%d %H:%M") if when else None,
        "draft": draft,
        "ai_label": ai_label,
        "visibility": visibility,
    }


def main() -> None:
    server.run()


if __name__ == "__main__":
    main()
