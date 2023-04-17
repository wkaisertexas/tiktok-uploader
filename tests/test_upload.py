"""
Tests uploader
"""

from tiktok_uploader.upload import _convert_videos_dict

import os

from pytest import raises

# before each create a file called test.mp4 and test.jpg
FILENAME = 'test.mp4'

def setup_function():
    """
    Creates a dummy file
    """
    with open(FILENAME, 'w', encoding='utf-8') as file:
        file.write('test')

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

    assert array[0]['path'] == FILENAME
    assert array[0]['description'] == "this is my description"

def test_convert_videos_dict_wrong_names():
    """
    Tests the videos dictionary with the wrong names
    """
    wrong_dict = {
        'video': FILENAME,
        'desc': 'this is my description',
    }

    array = _convert_videos_dict([wrong_dict])

    assert array[0]['path'] == FILENAME
    assert array[0]['description'] == "this is my description"

def test_convert_videos_bad():
    """
    Tests the videos dictionary with the wrong dictionaries
    """
    bad_dict = {
        'nothing': 'asfs',
        'wrong': 'wrong',
    }
    with raises(RuntimeError):
        _convert_videos_dict([bad_dict])

def test_convert_videos_filename():
    """
    Tests the videos dictionary with the wrong dictionaries
    """
    bad_dict = {
        'nothing': FILENAME,
    }
    array = _convert_videos_dict([bad_dict])

    assert array[0]['path'] == FILENAME
    assert array[0]['description'] == ""
