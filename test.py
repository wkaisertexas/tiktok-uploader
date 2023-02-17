from tiktok_uploader.upload import upload_video
from os import system
import tiktok_uploader.auth

if __name__ == '__main__':
    # Uploads a video to TikTok
    # upload_video('../../Desktop/video.mp4', description='this is a story about why I don', cookies='../../Desktop/cookies.txt', headless=True)

    # tests cookies for accounts -> Works except I get too many requests error (really sad)
    # tiktok_uploader.auth.login_accounts(accounts=[('server314159@gmail.com', 'asdfse12323dfsd!')])
    system('tiktok_uploader -v ../../Desktop/video.mp4 -d "this is a story about why I don\'t like tiktok" -c ../../Desktop/cookies.txt')