"""
Utilities for TikTok Uploader
"""

HEADER = '\033[95m'
OKBLUE = '\033[94m'
OKCYAN = '\033[96m'
OKGREEN = '\033[92m'
WARNING = '\033[93m'
FAIL = '\033[91m'
ENDC = '\033[0m'
BOLD = '\033[1m'
UNDERLINE = '\033[4m'

def bold(to_bold: str) -> str:
    """
    Returns the input bolded
    """
    return BOLD + to_bold + ENDC

def green(to_green: str) -> str:
    """
    Returns the input green
    """
    return OKGREEN + to_green + ENDC
