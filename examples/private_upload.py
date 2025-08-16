"""
Example of uploading a private video to TikTok
"""

from tiktok_uploader.upload import upload_video, upload_videos
from tiktok_uploader.auth import AuthBackend
from tiktok_uploader.types import VideoDict

# Upload a private video (only visible to you)
upload_video(
    filename="video.mp4",
    description="This is a private video - only I can see it",
    cookies="cookies.txt",
    visibility="only_you",  # Options: 'everyone', 'friends', 'only_you'
)

# Upload a friends-only video
upload_video(
    filename="video2.mp4",
    description="This video is only visible to my friends",
    cookies="cookies.txt",
    visibility="friends",
)

# Using multiple videos with different visibility settings

videos: list[VideoDict] = [
    {
        "path": "public_video.mp4",
        "description": "This is a public video",
        "visibility": "everyone",  # Public video
    },
    {
        "path": "private_video.mp4",
        "description": "This is a private video",
        "visibility": "only_you",  # Private video
    },
    {
        "path": "friends_video.mp4",
        "description": "This is for friends only",
        "visibility": "friends",  # Friends-only video
    },
]

auth = AuthBackend(cookies="cookies.txt")
failed_videos = upload_videos(videos=videos, auth=auth)

if failed_videos:
    print(f"Failed to upload: {failed_videos}")
else:
    print("All videos uploaded successfully with their respective visibility settings!")
