"""TikTok-Uploader entry point script"""

from tiktok_uploader import cli


def main() -> None:
    """
    Entry point for TikTok-Uploader, makes a call to CLI
    """
    cli.main()


if __name__ == "__main__":
    main()
