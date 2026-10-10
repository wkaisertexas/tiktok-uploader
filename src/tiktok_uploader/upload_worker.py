"""
Runs one upload in its own process, for the MCP server

Playwright's sync API can only be started once per thread, so the server runs
every upload in a fresh process instead of its own worker threads. The job is
read as JSON from stdin and the result is written as JSON to stdout; all logs
go to stderr.
"""

import datetime
import json
import sys
from typing import Any

from tiktok_uploader.upload import TikTokUploader


def run(job: dict[str, Any]) -> bool:
    schedule = job.get("schedule")
    with TikTokUploader(cookies=job["cookies"], headless=True) as uploader:
        return uploader.upload_video(
            filename=job["video"],
            description=job["description"],
            schedule=datetime.datetime.fromisoformat(schedule) if schedule else None,
            visibility=job["visibility"],
            draft=job["draft"],
            ai_label=job["ai_label"],
        )


def main() -> None:
    job = json.load(sys.stdin)

    # the uploader prints progress, which must not mix with the JSON result
    result_stream, sys.stdout = sys.stdout, sys.stderr
    try:
        result: dict[str, Any] = {"success": run(job)}
    except Exception as e:
        result = {"success": False, "error": f"{type(e).__name__}: {e}"}
    finally:
        sys.stdout = result_stream

    json.dump(result, sys.stdout)


if __name__ == "__main__":
    main()
