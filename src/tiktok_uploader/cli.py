"""
CLI is a controller for the command line use of this library
"""

import datetime
import logging
from argparse import ArgumentParser, BooleanOptionalAction, Namespace
from os.path import exists, join

import pytz

from tiktok_uploader.auth import login_accounts, save_cookies
from tiktok_uploader.types import ProxyDict, VideoDict
from tiktok_uploader.upload import TikTokUploader

# TikTok schedules at most this far ahead
MAX_SCHEDULE_AHEAD = datetime.timedelta(days=10)


def configure_logging() -> None:
    """
    Prints every step of the uploader, as the library did before it left
    logging to the application
    """
    logging.basicConfig(format="%(asctime)s %(message)s", datefmt="[%H:%M:%S]")
    logging.getLogger("tiktok_uploader").setLevel(logging.DEBUG)


def main() -> None:
    """
    Passes arguments into the program
    """
    configure_logging()
    args = get_uploader_args()
    validate_uploader_args(args)

    # parse args
    schedule = parse_schedule(args.schedule)
    proxy = parse_proxy(args.proxy)
    product_id = args.product_id
    visibility = args.visibility

    # runs the program using the arguments provided
    with TikTokUploader(
        username=args.username,
        password=args.password,
        cookies=args.cookies,
        proxy=proxy,
        sessionid=args.sessionid,
        headless=not args.attach,
    ) as uploader:
        result = uploader.upload_video(
            filename=args.video,
            description=args.description,
            schedule=schedule,
            product_id=product_id,
            cover=args.cover,
            visibility=visibility,
            sound_name=args.sound_name,
            sound_artist=args.sound_artist,
            draft=args.draft,
            ai_label=args.ai_label,
            skip_restricted=args.skip_restricted,
        )

    print("-------------------------")
    if not result:
        print("Error while uploading video")
    else:
        print("Video uploaded successfully")
    print("-------------------------")
    if not result:
        raise SystemExit(1)


def get_uploader_args() -> Namespace:
    """
    Generates a parser which is used to get all of the video's information
    """
    parser = ArgumentParser(
        description="TikTok uploader is a video uploader which can upload a"
        + "video from your computer to the TikTok using playwright automation"
    )

    # primary arguments
    parser.add_argument("-v", "--video", help="Video file", required=True)
    parser.add_argument("-d", "--description", help="Description", default="")

    # secondary arguments
    parser.add_argument(
        "-t",
        "--schedule",
        help="Schedule UTC time in %%Y-%%m-%%d %%H:%%M format ",
        default=None,
    )
    parser.add_argument(
        "--proxy", help="Proxy user:pass@host:port or host:port format", default=None
    )
    parser.add_argument(
        "--product-id",
        help="ID of the product to link in the video (if applicable)",
        default=None,
    )
    parser.add_argument(
        "--visibility",
        help="Video visibility: everyone (default), friends, or only_you",
        choices=["everyone", "friends", "only_you"],
        default="everyone",
    )
    parser.add_argument("--cover", help="Custom cover image file", default=None)
    add_post_option_args(parser)
    add_login_args(parser)

    return parser.parse_args()


def add_post_option_args(parser: ArgumentParser) -> None:
    """
    The per-post options shared by the single and the batch upload commands
    """
    parser.add_argument(
        "--sound-name",
        help="Name of a TikTok library sound to add (the first result if none matches)",
        default=None,
    )
    parser.add_argument(
        "--sound-artist",
        help="Artist of --sound-name, to pick between sounds of the same name",
        default=None,
    )
    parser.add_argument(
        "--draft",
        action="store_true",
        default=False,
        help="Save to the account's drafts instead of posting (cannot be scheduled)",
    )
    parser.add_argument(
        "--ai-label",
        action=BooleanOptionalAction,
        default=None,
        help="Turn TikTok's 'AI-generated content' label on (--ai-label) or off "
        "(--no-ai-label); left as TikTok sets it when omitted",
    )
    parser.add_argument(
        "--skip-restricted",
        action="store_true",
        default=False,
        help="Do not post if TikTok's content check warns it may be restricted",
    )


def add_login_args(parser: ArgumentParser) -> None:
    """
    The authentication and browser arguments shared by the upload commands
    """
    parser.add_argument("-c", "--cookies", help="The cookies you want to use")
    parser.add_argument("-s", "--sessionid", help="The session id you want to use")

    parser.add_argument("-u", "--username", help="Your TikTok email / username")
    parser.add_argument("-p", "--password", help="Your TikTok password")

    # playwright arguments
    parser.add_argument(
        "--attach",
        "-a",
        action="store_true",
        default=False,
        help="Runs the program in headful mode (shows browser window)",
    )


def validate_uploader_args(args: Namespace) -> None:
    """
    Preforms validation on each input given
    """

    # Makes sure the video file exists
    if not exists(args.video):
        raise FileNotFoundError(f"Could not find the video file at {args.video}")

    # Makes sure the optional cover image file exists
    if args.cover and not exists(args.cover):
        raise FileNotFoundError(f"Could not find the cover image file at {args.cover}")

    # User can not pass in both cookies and username / password
    if args.cookies and (args.username or args.password):
        raise ValueError("You can not pass in both cookies and username / password")


def auth() -> None:
    """
    Authenticates the user
    """
    configure_logging()
    args = get_auth_args()
    validate_auth_args(args=args)

    # runs the program using the arguments provided
    if args.input:
        login_info = get_login_info(path=args.input, header=args.header)
    else:
        login_info = [(args.username, args.password)]

    username_and_cookies = login_accounts(accounts=login_info)

    for username, cookies in username_and_cookies.items():
        save_cookies(path=join(args.output, username + ".txt"), cookies=cookies)


def get_auth_args() -> Namespace:
    """
    Generates a parser which is used to get all of the authentication information
    """
    parser = ArgumentParser(
        description="TikTok Auth is a program which can log you into multiple accounts sequentially"
    )

    # authentication arguments
    parser.add_argument(
        "-o", "--output", default="tmp", help="The output folder to save the cookies to"
    )
    parser.add_argument("-i", "--input", help="A csv file with username and password")
    # parser.add_argument('-h', '--header', default=True,
    # help='The header of the csv file which contains the username and password')
    parser.add_argument("-u", "--username", help="Your TikTok email / username")
    parser.add_argument("-p", "--password", help="Your TikTok password")

    return parser.parse_args()


def validate_auth_args(args: Namespace) -> None:
    """
    Preforms validation on each input given
    """
    # username and password or input files are mutually exclusive
    if args.username and args.password and args.input:
        raise ValueError("You can not pass in both username / password and input file")


def get_login_info(path: str, header: bool = True) -> list[tuple[str, str]]:
    """
    Parses the input file into a list of usernames and passwords
    """

    def extract_username_and_pass(input_str: str) -> tuple[str, str]:
        split_string = input_str.strip().split(",")
        if len(split_string) != 2:
            raise ValueError(f"{input_str} not valid")

        user, password = split_string

        return user, password

    with open(path, encoding="utf-8") as file:
        parsed_file = file.readlines()
        if header:
            parsed_file = parsed_file[1:]

        return [extract_username_and_pass(line) for line in parsed_file]


def parse_schedule(
    schedule_raw: str | None, timezone: str = "UTC"
) -> datetime.datetime | None:
    """
    Parses a "%Y-%m-%d %H:%M" time in `timezone` into an aware UTC datetime
    """
    if not schedule_raw:
        return None
    naive = datetime.datetime.strptime(schedule_raw, "%Y-%m-%d %H:%M")
    return pytz.timezone(timezone).localize(naive).astimezone(pytz.UTC)


def generate_schedule_times(
    schedule_from: datetime.datetime, interval_minutes: int, count: int
) -> list[datetime.datetime]:
    """
    `count` times, `interval_minutes` apart, starting at `schedule_from`
    """
    return [
        schedule_from + datetime.timedelta(minutes=i * interval_minutes)
        for i in range(count)
    ]


def batch_upload() -> None:
    """
    Uploads several videos in one browser session, optionally scheduled at a
    fixed interval:

        tiktok-uploader-batch -v a.mp4 -v b.mp4 -d "first" -d "second" \\
            --schedule-from "2026-03-20 10:00" --schedule-interval 240 -c cookies.txt
    """
    configure_logging()
    args = get_batch_args()
    videos = build_batch_videos(args)
    proxy = parse_proxy(args.proxy)

    with TikTokUploader(
        username=args.username or "",
        password=args.password or "",
        cookies=args.cookies or "",
        proxy=proxy,
        sessionid=args.sessionid,
        headless=not args.attach,
    ) as uploader:
        failed = uploader.upload_videos(videos)

    # each video's outcome and the totals are already logged
    if failed:
        raise SystemExit(1)


def get_batch_args() -> Namespace:
    """
    Generates a parser for the batch upload command
    """
    parser = ArgumentParser(
        description="Uploads several TikTok videos, optionally scheduled at an interval"
    )

    parser.add_argument(
        "-v",
        "--video",
        action="append",
        required=True,
        help="Video file (repeat for each video: -v a.mp4 -v b.mp4)",
    )
    parser.add_argument(
        "-d",
        "--description",
        action="append",
        default=[],
        help="Description of each video, in the order of -v",
    )
    parser.add_argument(
        "--schedule-from",
        help="Time of the first video in %%Y-%%m-%%d %%H:%%M format, in --timezone",
        default=None,
    )
    parser.add_argument(
        "--schedule-interval",
        type=int,
        default=1440,
        help="Minutes between consecutive videos (default: 1440, one day)",
    )
    parser.add_argument(
        "--timezone",
        default="UTC",
        help="tz database zone of --schedule-from, e.g. Europe/London (default: UTC)",
    )
    parser.add_argument(
        "--proxy", help="Proxy user:pass@host:port or host:port format", default=None
    )
    parser.add_argument(
        "--visibility",
        choices=["everyone", "friends", "only_you"],
        default="everyone",
        help="Video visibility: everyone (default), friends, or only_you",
    )
    add_post_option_args(parser)
    add_login_args(parser)

    return parser.parse_args()


def build_batch_videos(args: Namespace) -> list[VideoDict]:
    """
    Validates the batch arguments and turns them into one VideoDict per video
    """
    for path in args.video:
        if not exists(path):
            raise FileNotFoundError(f"Could not find the video file at {path}")

    if args.cookies and (args.username or args.password):
        raise ValueError("You can not pass in both cookies and username / password")

    if len(args.description) > len(args.video):
        raise ValueError("More descriptions (-d) were given than videos (-v)")

    schedules: list[datetime.datetime | None] = [None] * len(args.video)
    if args.schedule_from:
        if args.draft:
            raise ValueError("Drafts cannot be scheduled")
        try:
            schedule_from = parse_schedule(args.schedule_from, args.timezone)
        except pytz.UnknownTimeZoneError as e:
            raise ValueError(f"Unknown timezone: {args.timezone!r}") from e
        assert schedule_from is not None
        times = generate_schedule_times(
            schedule_from, args.schedule_interval, len(args.video)
        )
        latest = datetime.datetime.now(datetime.timezone.utc) + MAX_SCHEDULE_AHEAD
        if times[-1] > latest:
            raise ValueError(
                f"The last video would be scheduled at {times[-1]:%Y-%m-%d %H:%M} "
                f"UTC, beyond TikTok's {MAX_SCHEDULE_AHEAD.days}-day limit. Reduce "
                "--schedule-interval or the number of videos."
            )
        schedules = list(times)

    videos: list[VideoDict] = []
    for i, path in enumerate(args.video):
        video: VideoDict = {
            "path": path,
            "description": args.description[i] if i < len(args.description) else "",
        }
        schedule = schedules[i]
        if schedule is not None:
            video["schedule"] = schedule
        if args.visibility != "everyone":
            video["visibility"] = args.visibility
        if args.sound_name:
            video["sound_name"] = args.sound_name
        if args.sound_artist:
            video["sound_artist"] = args.sound_artist
        if args.draft:
            video["draft"] = True
        if args.ai_label is not None:
            video["ai_label"] = args.ai_label
        if args.skip_restricted:
            video["skip_restricted"] = True
        videos.append(video)

    return videos


def parse_proxy(proxy_raw: str | None) -> ProxyDict:
    proxy: ProxyDict = {}
    if proxy_raw:
        if "@" in proxy_raw:
            proxy["user"] = proxy_raw.split("@")[0].split(":")[0]
            proxy["password"] = proxy_raw.split("@")[0].split(":")[1]
            proxy["host"] = proxy_raw.split("@")[1].split(":")[0]
            proxy["port"] = proxy_raw.split("@")[1].split(":")[1]
        else:
            proxy["host"] = proxy_raw.split(":")[0]
            proxy["port"] = proxy_raw.split(":")[1]
    return proxy
