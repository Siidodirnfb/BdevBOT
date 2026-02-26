import telebot
import re
from rapidfuzz import fuzz
import os
from dotenv import load_dotenv
from telethon import TelegramClient, events
import asyncio
import time
import threading

load_dotenv()

# --- Настройки ---
BOT_TOKEN = '8527923791:AAHAkZMPfeVHdL-dFC40JwcTFlxdoTuvS5w'
CHANNEL_USERNAME = '@BdevHub'

API_ID = 30753680
API_HASH = 'c238c9c45ed3243c173058b2b64ef1fe'

SOURCE_CHANNELS = ['@ArceusXCommunity', '@beconscript', '@scripttigraann', '@BdevHub']
TARGET_CHANNEL = '@HybridScripts'

telethon_client = TelegramClient('BdevSearch_session', API_ID, API_HASH)
bot = telebot.TeleBot(BOT_TOKEN)

# --- Вспомогательные функции ---

def extract_game_name(text):
    patterns = [
        r'Игра:\s*(.+?)(?:\n|$)',
        r'Game:\s*(.+?)(?:\n|$)'
    ]
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return match.group(1).strip()
    return None

def extract_lua_script(text):
    lua_patterns = [
        r'```lua\s*\n(.*?)\n```',
        r'```\s*\n(.*?)\n```',
        r'loadstring\(game:HttpGet\("([^"]+)"\)\)\(\)',
        r'--.*?function.*?end',
    ]
    for pattern in lua_patterns:
        matches = re.findall(pattern, text, re.DOTALL | re.IGNORECASE)
        if matches:
            if 'HttpGet' in pattern and matches:
                return f"loadstring(game:HttpGet(\"{matches[0]}\"))()"
            return '\n'.join(matches)

    lines = text.split('\n')
    lua_lines = []
    keywords = ['local', 'function', 'end', 'if', 'then', 'else', 'for', 'while', 'repeat', 'until', 'loadstring', 'HttpGet']
    for line in lines:
        line = line.strip()
        if any(keyword in line.lower() for keyword in keywords):
            lua_lines.append(line)
    return '\n'.join(lua_lines) if lua_lines else None

def fuzzy_match_game_name(requested_name, found_name):
    if not found_name:
        return False
    requested_clean = re.sub(r'[^\w\s]', '', requested_name)
    found_clean = re.sub(r'[^\w\s]', '', found_name)
    
    token_sort_ratio = fuzz.token_sort_ratio(requested_clean.lower(), found_clean.lower())
    if token_sort_ratio > 80:
        return True
    
    ratio = fuzz.ratio(requested_clean.lower(), found_clean.lower())
    partial_ratio = fuzz.partial_ratio(requested_clean.lower(), found_clean.lower())
    return (ratio > 70 and partial_ratio > 70)

# --- Логика поиска (ИЗМЕНЕНО: теперь ищет ВСЕ совпадения) ---

def search_channel_posts(place_name):
    results = []
    try:
        # Проходим по всем сообщениям в обратном порядке
        for message_data in reversed(channel_messages):
            text = message_data['text']
            game_name = extract_game_name(text)
            
            if game_name and fuzzy_match_game_name(place_name, game_name):
                lua_script = extract_lua_script(text)
                if lua_script:
                    # Добавляем скрипт, если такого же еще нет в списке результатов
                    if not any(res['script'] == lua_script for res in results):
                        results.append({'game': game_name, 'script': lua_script})
        return results
    except Exception as e:
        print(f"Error searching channel posts: {e}")
        return []

# --- Телеграм бот обработчики ---

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    welcome_text = """
🤖 **Welcome to the Roblox Script Bot!**
📋 **Public Chat Mode:**
Use commands like `!Blade Ball` to search for Roblox scripts.
📝 **Personal Messages Mode:**
Send me direct messages for private script requests.
🔄 **Auto-Forwarding:**
Automatically forwards new posts from monitored channels to @HybridScripts.
"""
    bot.reply_to(message, welcome_text, parse_mode='Markdown')

@bot.message_handler(func=lambda message: message.text and message.text.startswith('!'))
def handle_public_commands(message):
    command_text = message.text[1:].strip()
    if not command_text:
        bot.reply_to(message, "Please provide a place name after the '!' (e.g., !Blade Ball)")
        return

    bot.reply_to(message, f"🔍 Searching for all available '{command_text}' scripts...")
    
    results = search_channel_posts(command_text)
    
    if results:
        # Формируем одно сообщение со всеми скриптами
        full_response = f"✅ **Found {len(results)} script(s) for '{command_text}':**\n\n"
        
        for i, res in enumerate(results, 1):
            script_block = f"🔹 **Script #{i} ({res['game']})**\n```lua\n{res['script']}\n```\n\n"
            
            # Проверка лимита Telegram (4096 символов)
            if len(full_response + script_block) > 4000:
                full_response += "⚠️ *Some scripts were omitted because the message is too long.*"
                break
            
            full_response += script_block
            
        bot.reply_to(message, full_response, parse_mode='Markdown')
    else:
        bot.reply_to(message, f"❌ No script found for '{command_text}'. Try a different name.")

@bot.message_handler(func=lambda message: message.chat.type == 'private')
def handle_private_messages(message):
    bot.reply_to(message, "Personal messages mode is not yet implemented.")

# --- Telethon и системная часть ---

channel_messages = []
last_message_ids = {}
forwarding_active = False

async def load_channel_posts():
    global channel_messages
    try:
        await telethon_client.connect()
        if not await telethon_client.is_user_authorized():
            await telethon_client.start()
        
        channel = await telethon_client.get_entity(CHANNEL_USERNAME)
        messages = await telethon_client.get_messages(channel, limit=1000)
        
        channel_messages = []
        for message in messages:
            if message.text:
                channel_messages.append({
                    'text': message.text,
                    'date': message.date,
                    'message_id': message.id
                })
        print(f"✅ Loaded {len(channel_messages)} posts.")
        await setup_auto_forwarding()
        return True
    except Exception as e:
        print(f"❌ Error loading posts: {e}")
        return False

async def setup_auto_forwarding():
    global forwarding_active
    try:
        target_channel = await telethon_client.get_entity(TARGET_CHANNEL)
        for source in SOURCE_CHANNELS:
            try:
                entity = await telethon_client.get_entity(source)
                msgs = await telethon_client.get_messages(entity, limit=1)
                last_message_ids[source] = msgs[0].id if msgs else 0
            except:
                last_message_ids[source] = 0

        @telethon_client.on(events.NewMessage(chats=SOURCE_CHANNELS))
        async def instant_forward_handler(event):
            try:
                await telethon_client.forward_messages(target_channel, event.message, event.chat_id)
            except Exception as e:
                print(f"❌ Forward error: {e}")
        
        forwarding_active = True
        print("✅ Auto-forwarding active.")
    except Exception as e:
        print(f"❌ Setup error: {e}")

def main():
    if not BOT_TOKEN or not CHANNEL_USERNAME:
        print("❌ Config error.")
        return

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(load_channel_posts())

    print("🚀 Starting bot polling...")
    bot.polling(none_stop=True)

if __name__ == '__main__':
    main()
