"""
Tests uploader
"""

from tiktok_uploader.upload import (
    _convert_videos_dict,
    _get_valid_schedule_minute,
    _check_valid_schedule,
)
import os
import datetime
from freezegun import freeze_time
from pytest import raises, fixture
import pytz

# before each create a file called test.mp4 and test.jpg
FILENAME = "test.mp4"
timezone = pytz.UTC


def setup_function():
    """
    Creates a dummy file
    """
    with open(FILENAME, "w", encoding="utf-8") as file:
        file.write("test")


# delete the file after each test
def teardown_function():
    """
    Deletes the dummy file
    """
    os.remove(FILENAME)


def test_convert_videos_dict_good():
    """Tests the videos dictionary with the good names"""
    good_dict = {
        "path": FILENAME,
        "description": "this is my description",
    }

    array = _convert_videos_dict([good_dict])

    assert array[0]["path"] == FILENAME
    assert array[0]["description"] == "this is my description"


def test_convert_videos_dict_wrong_names():
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


def test_convert_videos_bad():
    """
    Tests the videos dictionary with the wrong dictionaries
    """
    bad_dict = {
        "nothing": "asfs",
        "wrong": "wrong",
    }
    with raises(RuntimeError):
        _convert_videos_dict([bad_dict])


def test_convert_videos_filename():
    """
    Tests the videos dictionary with the wrong dictionaries
    """
    bad_dict = {
        "nothing": FILENAME,
    }
    array = _convert_videos_dict([bad_dict])

    assert array[0]["path"] == FILENAME
    assert array[0]["description"] == ""


def test_get_valid_schedule_minute():
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
def test_check_valid_schedule_min_limit():
    """
    Tests the min limit of check_valid_schedule
    """

    schedule = datetime.datetime(2020, 1, 1, 12, 25)
    schedule = timezone.localize(schedule)
    assert _check_valid_schedule(schedule) == True

    schedule = datetime.datetime(2020, 1, 1, 12, 20)
    schedule = timezone.localize(schedule)
    assert _check_valid_schedule(schedule) == True

    schedule = datetime.datetime(2020, 1, 1, 12, 15)
    schedule = timezone.localize(schedule)
    assert _check_valid_schedule(schedule) == False

    schedule = datetime.datetime(2019, 1, 1, 12, 00)
    schedule = timezone.localize(schedule)
    assert _check_valid_schedule(schedule) == False


@freeze_time("2020-01-01 12:00")
def test_check_valid_schedule_max_limit():
    """
    Tests the max limit of check_valid_schedule
    """

    schedule = datetime.datetime(2020, 1, 9, 12, 00)
    schedule = timezone.localize(schedule)
    assert _check_valid_schedule(schedule) == True

    schedule = datetime.datetime(2020, 1, 10, 11, 55)
    schedule = timezone.localize(schedule)
    assert _check_valid_schedule(schedule) == True

    schedule = datetime.datetime(2020, 1, 11, 12, 00)
    schedule = timezone.localize(schedule)
    assert _check_valid_schedule(schedule) == True

    schedule = datetime.datetime(2020, 1, 11, 12, 5)
    schedule = timezone.localize(schedule)
    assert _check_valid_schedule(schedule) == False

    schedule = datetime.datetime(2021, 1, 11, 12, 5)
    schedule = timezone.localize(schedule)
    assert _check_valid_schedule(schedule) == False


@freeze_time("2020-01-01 12:00")
def test_check_valid_schedule_minute_valid():
    """
    Tests the minutes valid multiple
    """

    schedule = datetime.datetime(2020, 1, 2, 12, 00)
    schedule = timezone.localize(schedule)
    assert _check_valid_schedule(schedule) == True

    schedule = datetime.datetime(2020, 1, 2, 12, 1)
    schedule = timezone.localize(schedule)
    assert _check_valid_schedule(schedule) == False

    schedule = datetime.datetime(2020, 1, 2, 12, 2)
    schedule = timezone.localize(schedule)
    assert _check_valid_schedule(schedule) == False

    schedule = datetime.datetime(2020, 1, 2, 12, 3)
    schedule = timezone.localize(schedule)
    assert _check_valid_schedule(schedule) == False

    schedule = datetime.datetime(2020, 1, 2, 12, 4)
    schedule = timezone.localize(schedule)
    assert _check_valid_schedule(schedule) == False

    schedule = datetime.datetime(2020, 1, 2, 12, 5)
    schedule = timezone.localize(schedule)
    assert _check_valid_schedule(schedule) == True
