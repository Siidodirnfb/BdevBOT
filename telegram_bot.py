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

BOT_TOKEN = '8527923791:AAHAkZMPfeVHdL-dFC40JwcTFlxdoTuvS5w'
CHANNEL_USERNAME = '@BdevHub'

API_ID = 30753680
API_HASH = 'c238c9c45ed3243c173058b2b64ef1fe'

SOURCE_CHANNELS = ['@ArceusXCommunity', '@beconscript', '@scripttigraann', '@BdevHub']
TARGET_CHANNEL = '@HybridScripts'

telethon_client = TelegramClient('BdevSearch_session', API_ID, API_HASH)

bot = telebot.TeleBot(BOT_TOKEN)

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

    for line in lines:
        line = line.strip()
        if any(keyword in line.lower() for keyword in ['local', 'function', 'end', 'if', 'then', 'else', 'for', 'while', 'repeat', 'until', 'loadstring', 'HttpGet']):
            lua_lines.append(line)

    return '\n'.join(lua_lines) if lua_lines else None

def fuzzy_match_game_name(requested_name, found_name):
    if not found_name:
        return False

    requested_clean = re.sub(r'[^\w\s]', '', requested_name.lower())
    found_clean = re.sub(r'[^\w\s]', '', found_name.lower())

    ratio = fuzz.ratio(requested_clean, found_clean)
    partial_ratio = fuzz.partial_ratio(requested_clean, found_clean)
    token_sort_ratio = fuzz.token_sort_ratio(requested_clean, found_clean)
    token_set_ratio = fuzz.token_set_ratio(requested_clean, found_clean)

    strict_match = (
        ratio > 70 and
        partial_ratio > 70 and
        token_sort_ratio > 70
    ) or token_sort_ratio > 80

    common_words = ['break', 'block', 'ball', 'battle', 'grounds', 'game', 'play']
    requested_words = set(requested_clean.split())
    found_words = set(found_clean.split())

    if (requested_words.intersection(common_words) and found_words.intersection(common_words) and
        token_sort_ratio < 85):
        significant_requested = requested_words - set(common_words)
        significant_found = found_words - set(common_words)

        if not significant_requested.intersection(significant_found) and token_sort_ratio < 70:
            return False

    return strict_match

channel_messages = []

last_message_ids = {}
forwarding_active = False

async def load_channel_posts():
    global channel_messages
    try:
        await telethon_client.connect()

        if not await telethon_client.is_user_authorized():
            print("⚠️  Telethon needs authentication. Please complete the setup in the terminal.")
            await telethon_client.start()
            print("✅ Authentication completed!")

        print(f"🔍 Looking for channel: {CHANNEL_USERNAME}")
        channel = await telethon_client.get_entity(CHANNEL_USERNAME)

        print("📥 Loading channel posts...")
        messages = await telethon_client.get_messages(channel, limit=1000)

        channel_messages = []
        for message in messages:
            if message.text:
                channel_messages.append({
                    'text': message.text,
                    'date': message.date,
                    'message_id': message.id
                })

        print(f"✅ Loaded {len(channel_messages)} posts from {CHANNEL_USERNAME}")

        await setup_auto_forwarding()

        return True

    except Exception as e:
        print(f"❌ Error loading channel posts: {e}")
        print("💡 Make sure the channel exists and you have access to it")
        return False

async def setup_auto_forwarding():
    import json
    import time
    def debug_log(message, data=None):
        with open(r"c:\Users\555\.cursor\debug.log", "a", encoding="utf-8", errors="replace") as f:
            entry = {
                "id": f"log_{int(time.time()*1000)}_setup",
                "timestamp": int(time.time()*1000),
                "location": "telegram_bot.py:setup_auto_forwarding",
                "message": message,
                "data": data or {},
                "sessionId": "debug-session",
                "runId": "run1",
                "hypothesisId": "B,C"
            }
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")

    global forwarding_active
    try:
        debug_log("Starting auto-forwarding setup")
        print("🔄 Setting up auto-forwarding...")

        debug_log("Getting target channel entity", {"target_channel": TARGET_CHANNEL})
        target_channel = await telethon_client.get_entity(TARGET_CHANNEL)
        debug_log("Target channel entity obtained successfully")
        print(f"✅ Target channel: {TARGET_CHANNEL}")

        for source_channel in SOURCE_CHANNELS:
            try:
                debug_log("Testing access to source channel", {"source_channel": source_channel})
                channel_entity = await telethon_client.get_entity(source_channel)
                debug_log("Source channel entity obtained", {"source_channel": source_channel})
                messages = await telethon_client.get_messages(channel_entity, limit=1)
                if messages:
                    last_message_ids[source_channel] = messages[0].id
                    debug_log("Latest message ID obtained", {"source_channel": source_channel, "latest_id": messages[0].id})
                else:
                    last_message_ids[source_channel] = 0
                    debug_log("No messages found in source channel", {"source_channel": source_channel})
                print(f"✅ Source channel accessible: {source_channel}")
            except Exception as e:
                debug_log("Failed to access source channel", {"source_channel": source_channel, "error": str(e)})
                print(f"⚠️ Could not access source channel {source_channel}: {e}")
                last_message_ids[source_channel] = 0

        forwarding_active = True
        debug_log("Setting forwarding_active to True", {"forwarding_active": forwarding_active})
        print("🔄 Setting up real-time event handlers...")
        debug_log("Setting up instant event handlers")

        @telethon_client.on(events.NewMessage(chats=SOURCE_CHANNELS))
        async def instant_forward_handler(event):
            import json
            import time
            def debug_log(message, data=None):
                with open(r"c:\Users\555\.cursor\debug.log", "a", encoding="utf-8") as f:
                    entry = {
                        "id": f"log_{int(time.time()*1000)}_event",
                        "timestamp": int(time.time()*1000),
                        "location": "telegram_bot.py:instant_forward_handler",
                        "message": message,
                        "data": data or {},
                        "sessionId": "debug-session",
                        "runId": "run1",
                        "hypothesisId": "A"
                    }
                    f.write(json.dumps(entry) + "\n")

            try:
                debug_log("New message event received", {"chat_id": event.chat_id, "message_id": event.message.id})

                if not event.message.text and not event.message.media:
                    debug_log("Skipping message without content")
                    return

                await telethon_client.forward_messages(
                    entity=target_channel,
                    messages=event.message,
                    from_peer=event.chat_id
                )

                source_name = "Unknown"
                try:
                    chat = await telethon_client.get_entity(event.chat_id)
                    source_name = getattr(chat, 'title', getattr(chat, 'username', str(event.chat_id)))
                except:
                    pass

                debug_log("Message forwarded successfully", {"source": source_name, "target": TARGET_CHANNEL})
                print(f"📤 [INSTANT] Forwarded message from {source_name} to {TARGET_CHANNEL}")

            except Exception as e:
                debug_log("Error forwarding message", {"error": str(e)})
                print(f"❌ Error in instant forwarding: {e}")

        forwarding_active = True
        print("✅ Instant auto-forwarding setup complete!")
        print(f"📡 Monitoring: {', '.join(SOURCE_CHANNELS)}")
        print(f"🎯 Forwarding to: {TARGET_CHANNEL}")
        print("⚡ Mode: INSTANT (event-driven)")
        debug_log("Instant forwarding setup complete")

    except Exception as e:
        debug_log("Error in setup_auto_forwarding", {"error": str(e)})
        print(f"❌ Error setting up auto-forwarding: {e}")

async def periodic_forwarding_check():
    import json
    import time
    def debug_log(message, data=None):
        with open(r"c:\Users\555\.cursor\debug.log", "a", encoding="utf-8", errors="replace") as f:
            entry = {
                "id": f"log_{int(time.time()*1000)}_forwarding",
                "timestamp": int(time.time()*1000),
                "location": "telegram_bot.py:periodic_forwarding_check",
                "message": message,
                "data": data or {},
                "sessionId": "debug-session",
                "runId": "run1",
                "hypothesisId": "A"
            }
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")

    debug_log("Periodic forwarding check started", {"forwarding_active": forwarding_active})
    while forwarding_active:
        debug_log("Periodic check iteration", {"forwarding_active": forwarding_active})
        try:
            debug_log("Calling check_and_forward_new_messages")
            await check_and_forward_new_messages()
            debug_log("check_and_forward_new_messages completed successfully")
        except Exception as e:
            debug_log("Error in periodic forwarding check", {"error": str(e)})
            print(f"❌ Error in periodic forwarding check: {e}")

        debug_log("Sleeping for 5 seconds")
        await asyncio.sleep(5)

async def check_and_forward_new_messages():
    import json
    import time
    def debug_log(message, data=None):
        with open(r"c:\Users\555\.cursor\debug.log", "a", encoding="utf-8", errors="replace") as f:
            entry = {
                "id": f"log_{int(time.time()*1000)}_check",
                "timestamp": int(time.time()*1000),
                "location": "telegram_bot.py:check_and_forward_new_messages",
                "message": message,
                "data": data or {},
                "sessionId": "debug-session",
                "runId": "run1",
                "hypothesisId": "D,E"
            }
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")

    try:
        debug_log("Starting message check")
        target_channel = await telethon_client.get_entity(TARGET_CHANNEL)
        debug_log("Target channel entity obtained")

        for source_channel in SOURCE_CHANNELS:
            try:
                debug_log("Processing source channel", {"source_channel": source_channel})
                channel_entity = await telethon_client.get_entity(source_channel)
                debug_log("Source channel entity obtained", {"source_channel": source_channel})

                debug_log("Getting latest messages", {"source_channel": source_channel, "limit": 5})
                messages = await telethon_client.get_messages(channel_entity, limit=5)
                debug_log("Messages retrieved", {"source_channel": source_channel, "message_count": len(messages)})

                current_last_id = last_message_ids.get(source_channel, 0)
                debug_log("Current last message ID", {"source_channel": source_channel, "last_id": current_last_id})

                for message in reversed(messages):
                    debug_log("Checking message", {"message_id": message.id, "last_id": current_last_id})
                    if message.id > current_last_id:
                        debug_log("Found new message to forward", {"message_id": message.id, "source_channel": source_channel})
                        try:
                            debug_log("Attempting to forward message")
                            await telethon_client.forward_messages(
                                entity=target_channel,
                                messages=message,
                                from_peer=channel_entity
                            )

                            debug_log("Message forwarded successfully")
                            source_name = getattr(channel_entity, 'title', getattr(channel_entity, 'username', source_channel))
                            print(f"📤 Forwarded message from {source_name} to {TARGET_CHANNEL}")

                        except Exception as forward_error:
                            debug_log("Error forwarding message", {"error": str(forward_error)})
                            print(f"❌ Error forwarding message from {source_channel}: {forward_error}")

                        last_message_ids[source_channel] = max(last_message_ids.get(source_channel, 0), message.id)
                        debug_log("Updated last message ID", {"source_channel": source_channel, "new_last_id": last_message_ids[source_channel]})

            except Exception as channel_error:
                debug_log("Error checking channel", {"source_channel": source_channel, "error": str(channel_error)})
                print(f"⚠️ Error checking channel {source_channel}: {channel_error}")

    except Exception as e:
        debug_log("Error in forwarding check", {"error": str(e)})
        print(f"❌ Error in forwarding check: {e}")

def search_channel_posts(place_name):
    try:
        for message_data in reversed(channel_messages):
            text = message_data['text']
            game_name = extract_game_name(text)
            if game_name and fuzzy_match_game_name(place_name, game_name):
                lua_script = extract_lua_script(text)
                if lua_script:
                    return lua_script, game_name

        return None, None

    except Exception as e:
        print(f"Error searching channel posts: {e}")
        return None, None

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    welcome_text = """
🤖 Welcome to the Roblox Script Bot!

📋 **Public Chat Mode:**
Use commands like `/Blade Ball` to search for Roblox scripts.
The bot will analyze channel posts and find matching scripts.

📝 **Personal Messages Mode:**
Send me direct messages for private script requests.

🔄 **Auto-Forwarding:**
Automatically forwards new posts from monitored channels to @HybridScripts.

⚠️ Make sure the bot is added to the channel with read permissions.
"""
    bot.reply_to(message, welcome_text, parse_mode='Markdown')

@bot.message_handler(commands=['forwarding'])
def handle_forwarding_status(message):
    global forwarding_active

    status_text = f"""
🔄 **Auto-Forwarding Status:**

📡 **Monitored Channels:**
{chr(10).join(f"• {channel}" for channel in SOURCE_CHANNELS)}

🎯 **Target Channel:** {TARGET_CHANNEL}

📊 **Status:** {'✅ Active' if forwarding_active else '❌ Inactive'}

⚡ **Mode:** INSTANT (event-driven)
"""

    if message.chat.type == 'private' or message.from_user.id in [123456789]:
        status_text += "\n\n**Admin Commands:**\n• `/forwarding` - Show status"

    bot.reply_to(message, status_text, parse_mode='Markdown')

@bot.message_handler(func=lambda message: message.text and message.text.startswith('/'))
def handle_public_commands(message):
    command_text = message.text[1:].strip()

    if not command_text:
        bot.reply_to(message, "Please provide a place name after the '/' (e.g., /Blade Ball)")
        return

    bot.reply_to(message, f"🔍 Searching for '{command_text}' script...")

    lua_script, found_game = search_channel_posts(command_text)

    if lua_script:
        response = f"✅ Found script for: {found_game}\n\n```lua\n{lua_script}\n```"
        bot.reply_to(message, response, parse_mode='Markdown')
    else:
        bot.reply_to(message, f"❌ No script found for '{command_text}'. Try a different name or check spelling.")

@bot.message_handler(func=lambda message: message.chat.type == 'private')
def handle_private_messages(message):
    bot.reply_to(message, "Personal messages mode is not yet implemented. Please use commands in public chats for now.")

async def initialize_telethon():
    import json
    import time
    def debug_log(message, data=None):
        with open(r"c:\Users\555\.cursor\debug.log", "a", encoding="utf-8", errors="replace") as f:
            entry = {
                "id": f"log_{int(time.time()*1000)}_init",
                "timestamp": int(time.time()*1000),
                "location": "telegram_bot.py:initialize_telethon",
                "message": message,
                "data": data or {},
                "sessionId": "debug-session",
                "runId": "run1",
                "hypothesisId": "B"
            }
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")

    debug_log("Starting Telethon initialization")
    print("🔄 Initializing Telethon client...")
    success = await load_channel_posts()
    debug_log("load_channel_posts completed", {"success": success})
    if success:
        print("✅ Channel posts loaded successfully!")
        print("✅ Auto-forwarding setup complete!")
    else:
        print("⚠️ Failed to load channel posts, but bot will continue...")
    debug_log("initialize_telethon completed", {"success": success})
    return success

def test_network_connection():
    try:
        import requests
        print("🌐 Testing network connection...")
        response = requests.get("https://api.telegram.org/bot123456:test/getMe", timeout=10)
        print("✅ Network connection OK")
        return True
    except Exception as e:
        print(f"❌ Network connection failed: {e}")
        return False

def main():
    import json
    import time
    def debug_log(message, data=None):
        with open(r"c:\Users\555\.cursor\debug.log", "a", encoding="utf-8", errors="replace") as f:
            entry = {
                "id": f"log_{int(time.time()*1000)}_main",
                "timestamp": int(time.time()*1000),
                "location": "telegram_bot.py:main",
                "message": message,
                "data": data or {},
                "sessionId": "debug-session",
                "runId": "run1",
                "hypothesisId": "A"
            }
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")

    debug_log("Bot starting")
    print("Bot is starting...")

    if not BOT_TOKEN:
        debug_log("BOT_TOKEN not found")
        print("❌ BOT_TOKEN not found")
        return

    if not CHANNEL_USERNAME:
        debug_log("CHANNEL_USERNAME not found")
        print("❌ CHANNEL_USERNAME not found")
        return

    debug_log("Configuration loaded successfully")
    print("✅ Configuration loaded successfully")

    if not test_network_connection():
        debug_log("Network connection test failed")
        print("💡 Check your internet connection and try again")
        return

    debug_log("Initializing Telethon")
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    success = loop.run_until_complete(initialize_telethon())

    if success:
        debug_log("Channel posts loaded successfully")
        print("✅ Channel posts loaded successfully!")
    else:
        debug_log("Failed to load channel posts")
        print("⚠️ Failed to load channel posts, but bot will continue...")

    debug_log("Starting bot polling")
    print("🚀 Starting bot polling...")
    max_retries = 3
    retry_count = 0

    while retry_count < max_retries:
        try:
            debug_log("Attempting bot polling", {"attempt": retry_count + 1})
            bot.polling(none_stop=True, timeout=30, long_polling_timeout=30)
            debug_log("Bot polling succeeded")
            break
        except Exception as e:
            debug_log("Bot polling error", {"attempt": retry_count + 1, "error": str(e)})
            retry_count += 1
            print(f"❌ Bot polling error (attempt {retry_count}/{max_retries}): {e}")

            if retry_count < max_retries:
                debug_log("Retrying in 5 seconds")
                print("🔄 Retrying in 5 seconds...")
                time.sleep(5)
            else:
                debug_log("Max retries reached, giving up")
                print("💡 Try checking your internet connection or firewall settings")
                return

if __name__ == '__main__':
    main()