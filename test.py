from tiktok_uploader.upload import upload_video

if __name__ == '__main__':
    # Uploads a video to TikTok
    upload_video('../../Desktop/video.mp4', description='test', cookies='../../Desktop/cookies.txt')
