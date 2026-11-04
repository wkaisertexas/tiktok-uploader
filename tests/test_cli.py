"""
Tests the CLI's schedule parsing and the batch upload command
"""

import datetime
import os
from argparse import Namespace
from typing import Any
from unittest.mock import patch

import pytz
from pytest import raises

from tiktok_uploader.cli import (
    build_batch_videos,
    generate_schedule_times,
    get_batch_args,
    parse_schedule,
)

FILENAME = "test.mp4"


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


def _batch_args(**overrides: Any) -> Namespace:
    """
    Batch arguments for two videos, with `overrides` applied
    """
    args = Namespace(
        video=[FILENAME, FILENAME],
        description=["first"],
        schedule_from=None,
        schedule_interval=60,
        timezone="UTC",
        proxy=None,
        visibility="everyone",
        sound_name=None,
        sound_artist=None,
        draft=False,
        ai_label=None,
        skip_restricted=False,
        cookies="cookies.txt",
        sessionid=None,
        username=None,
        password=None,
        attach=False,
    )
    vars(args).update(overrides)
    return args


def _tomorrow() -> str:
    tomorrow = datetime.datetime.now(pytz.UTC) + datetime.timedelta(days=1)
    return tomorrow.strftime("%Y-%m-%d %H:%M")


def test_parse_schedule_returns_an_aware_utc_datetime() -> None:
    schedule = parse_schedule("2026-03-20 10:00")

    assert schedule == datetime.datetime(2026, 3, 20, 10, 0, tzinfo=pytz.UTC)
    assert schedule is not None and schedule.tzinfo is not None


def test_parse_schedule_converts_from_the_given_timezone() -> None:
    schedule = parse_schedule("2026-07-01 10:00", "Europe/London")

    assert schedule == datetime.datetime(2026, 7, 1, 9, 0, tzinfo=pytz.UTC)


def test_parse_schedule_without_a_time() -> None:
    assert parse_schedule(None) is None


def test_generate_schedule_times() -> None:
    start = datetime.datetime(2026, 3, 20, 10, 0, tzinfo=pytz.UTC)

    times = generate_schedule_times(start, 90, 3)

    assert times == [
        start,
        start + datetime.timedelta(minutes=90),
        start + datetime.timedelta(minutes=180),
    ]


def test_build_batch_videos_pairs_descriptions_in_order() -> None:
    videos = build_batch_videos(_batch_args())

    assert [v["description"] for v in videos] == ["first", ""]
    assert all("schedule" not in v for v in videos)


def test_build_batch_videos_schedules_at_the_interval() -> None:
    videos = build_batch_videos(_batch_args(schedule_from=_tomorrow()))

    first, second = videos[0]["schedule"], videos[1]["schedule"]
    assert first.tzinfo is not None
    assert second - first == datetime.timedelta(minutes=60)


def test_build_batch_videos_rejects_a_schedule_past_the_ten_day_limit() -> None:
    args = _batch_args(schedule_from=_tomorrow(), schedule_interval=60 * 24 * 10)

    with raises(ValueError, match="10-day limit"):
        build_batch_videos(args)


def test_build_batch_videos_rejects_a_scheduled_draft() -> None:
    with raises(ValueError, match="Drafts cannot be scheduled"):
        build_batch_videos(_batch_args(schedule_from=_tomorrow(), draft=True))


def test_build_batch_videos_rejects_an_unknown_timezone() -> None:
    args = _batch_args(schedule_from=_tomorrow(), timezone="Not/AZone")

    with raises(ValueError, match="Unknown timezone"):
        build_batch_videos(args)


def test_build_batch_videos_copies_the_post_options() -> None:
    args = _batch_args(sound_name="song", ai_label=False, skip_restricted=True)

    for video in build_batch_videos(args):
        assert video["sound_name"] == "song"
        assert video["ai_label"] is False
        assert video["skip_restricted"] is True


def test_get_batch_args_parses_repeated_videos_and_the_ai_label() -> None:
    argv = ["tiktok-uploader-batch", "-v", "a.mp4", "-v", "b.mp4", "--no-ai-label"]

    with patch("sys.argv", argv):
        args = get_batch_args()

    assert args.video == ["a.mp4", "b.mp4"]
    assert args.ai_label is False
    assert args.schedule_interval == 1440
