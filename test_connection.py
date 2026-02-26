#!/usr/bin/env python3

import telebot
import requests
import time

BOT_TOKEN = '8527923791:AAHAkZMPfeVHdL-dFC40JwcTFlxdoTuvS5w'

def test_basic_connection():
    print("Testing basic HTTPS connection...")
    try:
        response = requests.get("https://api.telegram.org/bot123456:test/getMe", timeout=10)
        print(f"HTTPS connection OK (status: {response.status_code})")
        return True
    except Exception as e:
        print(f"HTTPS connection failed: {e}")
        return False

def test_bot_token():
    print("Testing bot token...")
    try:
        bot = telebot.TeleBot(BOT_TOKEN)
        bot_info = bot.get_me()
        print(f"Bot connected: @{bot_info.username} (ID: {bot_info.id})")
        return True
    except Exception as e:
        print(f"Bot token invalid: {e}")
        return False

def test_bot_polling():
    print("Testing bot polling (10 seconds)...")
    try:
        bot = telebot.TeleBot(BOT_TOKEN)

        @bot.message_handler(commands=['test'])
        def handle_test(message):
            bot.reply_to(message, "Connection test successful!")

        import threading
        import time as time_module

        def stop_polling():
            time_module.sleep(10)
            print("Stopping test polling...")
            bot.stop_polling()

        stop_thread = threading.Thread(target=stop_polling)
        stop_thread.start()

        bot.polling(none_stop=False, timeout=5, long_polling_timeout=5)
        print("Bot polling test completed")
        return True

    except Exception as e:
        print(f"Bot polling failed: {e}")
        return False

def main():
    print("=== Telegram Bot Connection Test ===\n")

    tests = [
        ("Basic HTTPS", test_basic_connection),
        ("Bot Token", test_bot_token),
        ("Bot Polling", test_bot_polling)
    ]

    results = []
    for test_name, test_func in tests:
        print(f"\n--- {test_name} ---")
        result = test_func()
        results.append((test_name, result))

    print("\n=== Results ===")
    all_passed = True
    for test_name, result in results:
        status = "PASS" if result else "FAIL"
        print(f"{status}: {test_name}")
        if not result:
            all_passed = False

    if all_passed:
        print("\nAll tests passed! Your bot should work.")
        print("Run: python telegram_bot.py")
    else:
        print("\nSome tests failed. Check your network and token.")

if __name__ == "__main__":
    main()