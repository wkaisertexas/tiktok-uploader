"""
Uploads a series of videos to TikTok
"""
from sys import argv

import pandas as pd

from tiktok_uploader.upload import upload_video

# NOTE: A TOML file with the following information also works
# Good for when you have multiple accounts
COOKIES = "/Desktop/cookies.txt"
INFO = "/Desktop/info.xslx"
KEY = "uploaded"

def main():
    """
    Posts a vdeo to TikTok from INFO, a spreadsheet containing: file_path, description, and uploaded
    """
    set_config() # Sets global variables based on arguments parsed from the command line

    frame = pd.read_excel(INFO)
    index = frame.index[frame[KEY] is False].to_list()[0]
    video_info = frame.iloc[index]

    failed = upload_video(video_info['file_path'], video_info['description'], cookies=COOKIES)

    if not failed:
        video_info[KEY] = True # Registers the video has been uploaded
        frame.to_excel(INFO)

# checks if the user passed in a file path
def set_config() -> dict:
    """
    Gets the optional file path from the command line
    """
    if len(argv) < 2 or not argv[1].endswith('.toml'):
        print("No file path was provided")
        return

    import toml
    dictionary = toml.load(argv[1])

    global COOKIES, INFO, KEY
    COOKIES = dictionary['COOKIES']
    INFO = dictionary['INFO']
    KEY = dictionary['KEY']

if __name__ == '__main__':
    main()
