import os
import time
import shutil
import random
import telegram
from telegram import Update
from telegram.ext import Application, CommandHandler, CallbackContext
import threading
from tiktokautouploader import upload_tiktok

# Path configuration
path = r'C:\Path\To\All\Videos\Here'
left = os.path.join(path, '!')  # "! Folder" will store uploaded videos to keep things organized
if not os.path.exists(left):
    os.makedirs(left)  # Create the folder if it doesn't exist

# Fetching and sorting video files
vids = sorted([f for f in os.listdir(path) if f.endswith('.mp4')],
              key=lambda f: int(f.split('.')[0]))  # Sort videos in ascending numerical order

# Video details
desc = 'Description here'
tags = ['#fyp', '#viral', '#other Tags here']
acct = 'Account name here'

# Telegram bot details
bot_token = 'Bot token here'
group_id = # Group ID here
bot = telegram.Bot(token=bot_token)

# Global variables for tracking upload state
last_vid = ""  # Last uploaded video
last_acc = ""  # Account used for the last upload
upld_inp = False  # Whether an upload is in progress
curr_vid = None  # Current video being uploaded
nxt_upld = 0  # Timestamp for the next upload
upld_strk = 0  # Streak of successful uploads
skip_timer = False  # Flag to skip the timer
last_upload_time = None  # Timestamp of the last upload

# Send a message to the group using the bot
def send_msg(message: str):
    bot.send_message(chat_id=group_id, text=message)

# Calculate the remaining time for the next upload
def time_left():
    wait_time = max(nxt_upld - time.time(), 0)
    if wait_time > 0:
        h = int(wait_time // 3600)
        m = int((wait_time % 3600) // 60)
        s = int(wait_time % 60)
        return f"{h}h {m}m {s}s"
    return "Ready for next upload"

# Calculate time since the last upload
def timeafterupload():
    if last_upload_time:
        elapsed_time = time.time() - last_upload_time
        h = int(elapsed_time // 3600)
        m = int((elapsed_time % 3600) // 60)
        s = int(elapsed_time % 60)
        return f"{h}h {m}m {s}s"
    return "N/A"

# Upload status message
def update_stats():
    vids_left = len([f for f in os.listdir(path) if f.endswith('.mp4')])  # Count remaining videos
    stats_msg = "<b>📊 Upload Status</b>\n"
    stats_msg += "<b>===========================</b>\n"
    stats_msg += f"<b>🎥 Currently Uploading:</b> {curr_vid if upld_inp else 'N/A'}\n"
    stats_msg += f"<b>📅 Last Upload Time:</b> {time.strftime('%Y-%m-%d, %I:%M:%S %p', time.localtime(last_upload_time)) if last_upload_time else 'N/A'}\n"
    stats_msg += f"<b>📅 Next Upload Time:</b> {time.strftime('%Y-%m-%d, %I:%M:%S %p', time.localtime(nxt_upld)) if nxt_upld else 'N/A'}\n"
    stats_msg += f"<b>⏳ Next Upload In:</b> {time_left() if not upld_inp else 'Uploading now'}\n"
    stats_msg += f"<b>⏳ Uploaded Since:</b> {timeafterupload()}\n"
    stats_msg += f"<b>📂 Videos Left:</b> {vids_left}\n"
    stats_msg += f"<b>🔄 Last Uploaded Video:</b> {last_vid if last_vid else 'N/A'}\n"
    stats_msg += f"<b>🚀 Uploaded To:</b> {last_acc if last_acc else 'N/A'}\n"
    stats_msg += f"<b>🔥 Upload Streak:</b> {upld_strk}\n"
    stats_msg += "<b>===========================</b>\n"
    return stats_msg

# Telegram command: /status
async def status_cmd(update: Update, context: CallbackContext):
    stats_msg = update_stats()
    await context.bot.send_message(chat_id=update.effective_chat.id, text=stats_msg, parse_mode='HTML')

# Console timer for next upload
def console_timer():
    global skip_timer
    while True:
        if skip_timer:  # Stop the timer if skip is triggered
            skip_timer = False
            break
        wait_time = max(nxt_upld - time.time(), 0)
        if wait_time > 0:
            h = int(wait_time // 3600)
            m = int((wait_time % 3600) // 60)
            s = int(wait_time % 60)
            print(f"Next upload in: {h}h {m}m {s}s", end='\r')
            time.sleep(1)
        else:
            print("Ready for next upload", end='\r')
            break

# Telegram command: /skip
async def skip_cmd(update: Update, context: CallbackContext):
    global skip_timer, nxt_upld
    skip_timer = True
    nxt_upld = time.time()  # Immediately trigger next upload
    print("\n------------------\nTimer skipped!\n------------------")
    message = "<b>📢 Timer Skipped!</b>\n"
    message += "<b>===========================</b>\n"
    message += "<b>⏩ Starting next upload...</b>\n"
    message += "<b>===========================</b>\n"
    await context.bot.send_message(chat_id=update.effective_chat.id, text=message, parse_mode='HTML')
    threading.Thread(target=console_timer).start()

# Upload video
def upld_vid(video):
    global last_vid, last_acc, upld_inp, curr_vid, nxt_upld, upld_strk, skip_timer, last_upload_time
    try:
        upld_inp, curr_vid = True, video
        vidz = os.path.join(path, video)
        upload_tiktok(video=vidz, description=desc, accountname=acct, hashtags=tags, sound_name='Swimming', sound_aud_vol='background')
        print(f"Uploaded {video}\n===========================")
        last_vid, last_acc, upld_strk = video, acct, upld_strk + 1
        shutil.move(vidz, os.path.join(left, video))  # Move video to "!" folder after upload
        # Randomize the next upload time between 6 and 9 hours to avoid rate limits
        h, m, s = random.randint(6, 9), random.randint(0, 59), random.randint(0, 59)
        nxt_upld = time.time() + h * 3600 + m * 60 + s
        last_upload_time = time.time()
        threading.Thread(target=console_timer).start()
    except Exception as e:
        send_msg(f"Error {video}: {str(e)}")
        upld_strk = 0  # Reset streak on failure
    finally:
        skip_timer = False
        upld_inp, curr_vid = False, None

# Upload all videos in the folder
def upld_all():
    global skip_timer, nxt_upld
    for vid in vids:
        if skip_timer:
            nxt_upld = time.time()
        upld_vid(vid)
        while time.time() < nxt_upld:
            if skip_timer:  # Skip timer if triggered
                nxt_upld = time.time()
                break
            time.sleep(1)

# Start the Telegram bot
def start_bot():
    application = Application.builder().token(bot_token).build()
    application.add_handler(CommandHandler('status', status_cmd))  # Show current upload status
    application.add_handler(CommandHandler('stats', status_cmd))  # Alias for /status
    application.add_handler(CommandHandler('skip', skip_cmd))  # Skip timer for immediate upload
    application.run_polling()

# Main function to start upload and bot
def main():
    upload_thread = threading.Thread(target=upld_all)
    upload_thread.start()
    start_bot()

if __name__ == '__main__':
    main()
