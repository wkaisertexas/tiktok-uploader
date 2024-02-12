import sys
from collections import defaultdict

from src.tiktok_uploader import cli

# Specify the directory you want to add to the Python path
directory_to_add = r"C:\Users\RoiHa\PycharmProjects\social-automation\src"

# Add the directory to the Python path
if directory_to_add not in sys.path:
    sys.path.append(directory_to_add)


if __name__ == '__main__':
    cli.main()
    