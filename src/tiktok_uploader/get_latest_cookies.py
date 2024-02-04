import os
import glob
import re


def get_latest_local_cookies(directory=None, base_filename=None):
    # Specify the directory and base filename
    if not directory:
        directory = r"C:\Users\RoiHa\Downloads\chrome_downloads"
    if not base_filename:
        base_filename = "www.tiktok.com_cookies"

    # Construct the search pattern to match all versions of the file
    search_pattern = os.path.join(directory, f"{base_filename} *.txt")
    # Find all files that match the pattern
    files = glob.glob(search_pattern)

    # Extract version numbers and file paths
    version_file_pairs = []
    for file in files:
        match = re.search(r'\((\d+)\)\.txt$', file)
        if match:
            version = int(match.group(1))
            version_file_pairs.append((version, file))

    # Sort the list by version number in descending order
    version_file_pairs.sort(reverse=True)

    # Return the file with the highest version number, if any
    return version_file_pairs[0][1] if version_file_pairs else None


latest_file = get_latest_local_cookies()
