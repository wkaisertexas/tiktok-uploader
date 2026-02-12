"""
Example of uploading a private video to TikTok
"""

from tiktok_uploader.types import VideoDict
from tiktok_uploader.upload import TikTokUploader

uploader = TikTokUploader(cookies="cookies.txt")

# Upload a private video (only visible to you)
uploader.upload_video(
    filename="video.mp4",
    description="This is a private video - only I can see it",
    visibility="only_you",  # Options: 'everyone', 'friends', 'only_you'
)

# Upload a friends-only video
uploader.upload_video(
    filename="video2.mp4",
    description="This video is only visible to my friends",
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

failed_videos = uploader.upload_videos(videos=videos)

if failed_videos:
    print(f"Failed to upload: {failed_videos}")
else:
    print("All videos uploaded successfully with their respective visibility settings!")