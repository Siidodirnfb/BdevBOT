import telebot
import re
from rapidfuzz import fuzz
import os
import html
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

channel_messages = []
forwarding_active = False

# --- Логика извлечения данных ---
def extract_game_name(text):
    patterns = [r'Игра:\s*(.+?)(?:\n|$)', r'Game:\s*(.+?)(?:\n|$)']
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return match.group(1).strip()
    return None

def extract_lua_script(text):
    # 1. Сначала ищем готовые блоки кода с синтаксисом ```lua
    markdown_lua = re.search(r'```lua\s*\n(.*?)\n```', text, re.DOTALL | re.IGNORECASE)
    if markdown_lua:
        return markdown_lua.group(1).strip()

    # 2. Ищем блоки кода с простыми бэктиками ```
    markdown_simple = re.search(r'```\s*\n(.*?)\n```', text, re.DOTALL | re.IGNORECASE)
    if markdown_simple:
        return markdown_simple.group(1).strip()

    # 3. Если бэктиков нет, ищем саму строку loadstring
    loadstring_match = re.search(r'loadstring\(game:HttpGet\("([^"]+)"\)\)\(\)', text, re.IGNORECASE)
    if loadstring_match:
        return loadstring_match.group(0).strip() # Возвращаем чистую строку

    return None

def fuzzy_match_game_name(requested_name, found_name):
    if not found_name:
        return False
    
    # Приводим к нижнему регистру для поиска без учета регистра
    req_clean = re.sub(r'[^\w\s]', '', requested_name).lower().strip()
    found_clean = re.sub(r'[^\w\s]', '', found_name).lower().strip()
    
    # Поиск по ключевым словам (вхождение подстроки)
    if req_clean in found_clean or found_clean in req_clean:
        return True
        
    # Нечеткое сравнение (для опечаток)
    return fuzz.token_set_ratio(req_clean, found_clean) > 65

# --- Работа с Telethon ---
async def load_channel_posts():
    global channel_messages
    try:
        await telethon_client.start()
        channel = await telethon_client.get_entity(CHANNEL_USERNAME)
        messages = await telethon_client.get_messages(channel, limit=1000)
        channel_messages = [{'text': m.text, 'id': m.id} for m in messages if m.text]
        print(f"✅ База загружена ({len(channel_messages)} шт.)")
        await setup_auto_forwarding()
    except Exception as e:
        print(f"❌ Ошибка Telethon: {e}")

async def setup_auto_forwarding():
    global forwarding_active
    try:
        target_entity = await telethon_client.get_entity(TARGET_CHANNEL)
        @telethon_client.on(events.NewMessage(chats=SOURCE_CHANNELS))
        async def handler(event):
            try:
                await telethon_client.forward_messages(target_entity, event.message)
            except: pass
        forwarding_active = True
    except: pass

# --- Обработчик команд ---
@bot.message_handler(func=lambda m: m.text and m.text.startswith('!'))
def handle_public_commands(message):
    query = message.text[1:].strip()
    if not query: return

    bot.send_chat_action(message.chat.id, 'typing')
    results = []
    
    for msg in reversed(channel_messages):
        game_name = extract_game_name(msg['text'])
        if game_name and fuzzy_match_game_name(query, game_name):
            script = extract_lua_script(msg['text'])
            if script and not any(r['script'] == script for r in results):
                results.append({'game': game_name, 'script': script})

    if results:
        # Мы всегда оборачиваем результат в <pre><code> для HTML режима Telegram
        # Это гарантирует, что даже "голый" loadstring станет блоком кода с кнопкой копирования
        response = f"✅ <b>Результаты поиска по запросу '{html.escape(query)}':</b>\n\n"
        
        for i, res in enumerate(results, 1):
            g_esc = html.escape(res['game'])
            s_esc = html.escape(res['script']) # Очищаем код от HTML-тегов
            
            # Оформляем как блок кода. В Telegram HTML режиме это <pre><code>
            block = f"<b>{i}. {g_esc}</b>\n<pre><code>{s_esc}</code></pre>\n\n"
            
            if len(response + block) > 4000:
                response += "<i>...часть результатов скрыта...</i>"
                break
            response += block
            
        bot.reply_to(message, response, parse_mode='HTML')
    else:
        bot.reply_to(message, f"❌ По запросу '{html.escape(query)}' ничего не найдено.")

# --- Запуск ---
def run_telethon_loop():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(load_channel_posts())
    loop.run_forever()

if __name__ == '__main__':
    threading.Thread(target=run_telethon_loop, daemon=True).start()
    print("🚀 Бот активен и готов к поиску!")
    bot.infinity_polling()