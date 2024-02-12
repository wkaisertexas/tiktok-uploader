"""
CLI is a controller for the command line use of this library
"""

from argparse import ArgumentParser
from os.path import exists, join
import datetime
import json

from src.tiktok_uploader.upload import upload_video
from src.tiktok_uploader.auth import login_accounts, save_cookies
from src.tiktok_uploader.upload_meditations import upload_range

from src.tiktok_uploader.get_latest_cookies import get_latest_local_cookies


def main():
    """
    Passes arguments into the program
    """
    args = get_uploader_args()

    args = validate_uploader_args(args=args)
    if args.tiktok:
        # Specify your start and finish meditation ids, (e.g: 1, 5 - meanning upload days 1 to 5 including 5)
        # Make sure the videos exist on the meditations folder
        upload_range(11, 16)

    if args.cloud_function:
        pass
    # parse args
    # schedule = parse_schedule(args.schedule)
    # proxy = parse_proxy(args.proxy)

    print('-------------------------')
    print('Script finished')
    print('-------------------------')


def get_uploader_args():
    """
    Generates a parser which is used to get all of the video's information
    """
    parser = ArgumentParser(
        description='TikTok uploader is a video uploader which can upload a' +
        'video from your computer to the TikTok using selenium automation'
    )

    parser.add_argument('-t', '--tiktok', help='Upload to tiktok', default=False)
    parser.add_argument('-f', '--cloud-function', help='Run cloud function', default=False)


    # These args stay because they should be examined (username & password mainly)

    # primary arguments
    parser.add_argument('-v', '--video', help='Video file')
    parser.add_argument('-d', '--description', help='Description', default='')

    # secondary arguments
    # parser.add_argument('-t', '--schedule', help='Schedule UTC time in %Y-%m-%d %H:%M format ', default=None)
    parser.add_argument('--proxy', help='Proxy user:pass@host:port or host:port format', default=None)

    # authentication arguments
    parser.add_argument('-c', '--cookies', help='The cookies you want to use')
    parser.add_argument('-s', '--sessionid', help='The session id you want to use')

    parser.add_argument('-u', '--username', help='Your TikTok email / username')
    parser.add_argument('-p', '--password', help='Your TikTok password')

    # selenium arguments
    parser.add_argument('--attach', '-a', action='store_true', default=False,
                         help='Runs the program in headless mode (no browser window)')

    return parser.parse_args()


def validate_uploader_args(args: dict):
    """
    Preforms validation on each input given
    """

    # Makes sure the video file exists
    if not exists(args.video):
        raise FileNotFoundError(f'Could not find the video file at {args["video"]}')

    # User can not pass in both cookies and username / password
    if args.cookies and (args.username or args.password):
        raise ValueError('You can not pass in both cookies and username / password')

    return args


def auth():
    """
    Authenticates the user
    """
    args = get_auth_args()
    args = validate_auth_args(args=args)

    # runs the program using the arguments provided
    if args.input:
        login_info = get_login_info(path=args.input, header=args.header)
    else:
        login_info = [(args.username, args.password)]

    username_and_cookies = login_accounts(accounts=login_info)

    for username, cookies in username_and_cookies.items():
        save_cookies(path=join(args.output, username + '.txt'), cookies=cookies)


def get_auth_args():
    """
    Generates a parser which is used to get all of the authentication information
    """
    parser = ArgumentParser(
        description='TikTok Auth is a program which can log you into multiple accounts sequentially'
    )

    # authentication arguments
    parser.add_argument('-o', '--output', default='tmp',
                        help='The output folder to save the cookies to')
    parser.add_argument('-i', '--input', help='A csv file with username and password')
    # parser.add_argument('-h', '--header', default=True,
    # help='The header of the csv file which contains the username and password')
    parser.add_argument('-u', '--username', help='Your TikTok email / username')
    parser.add_argument('-p', '--password', help='Your TikTok password')

    return parser.parse_args()

def validate_auth_args(args):
    """
    Preforms validation on each input given
    """
    # username and password or input files are mutually exclusive
    if (args['username'] and args['password']) and args['input']:
        raise ValueError('You can not pass in both username / password and input file')

    return args


def get_login_info(path: str, header=True) -> list:
    """
    Parses the input file into a list of usernames and passwords
    """
    with open(path, 'r', encoding='utf-8') as file:
        file = file.readlines()
        if header:
            file = file[1:]
        return [line.split(',')[:2] for line in file]


def parse_schedule(schedule_raw):
    if schedule_raw:
        schedule = datetime.datetime.strptime(schedule_raw, '%Y-%m-%d %H:%M')
    else:
        schedule = None
    return schedule


def parse_proxy(proxy_raw):
    proxy = {}
    if proxy_raw:
        if '@' in proxy_raw:
            proxy['user'] = proxy_raw.split('@')[0].split(':')[0]
            proxy['pass'] = proxy_raw.split('@')[0].split(':')[1]
            proxy['host'] = proxy_raw.split('@')[1].split(':')[0]
            proxy['port'] = proxy_raw.split('@')[1].split(':')[1]
        else:
            proxy['host'] = proxy_raw.split(':')[0]
            proxy['port'] = proxy_raw.split(':')[1]
    return proxy
