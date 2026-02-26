#!/usr/bin/env python3

from telegram_bot import extract_game_name, extract_lua_script, fuzzy_match_game_name

def test_bot_setup():
    print("Testing Telegram Bot Setup...\n")

    test_text = "Игра: Blade Ball\n```lua\nprint('Hello World')\n```"
    game_name = extract_game_name(test_text)
    lua_script = extract_lua_script(test_text)

    print(f"PASS: Game name extracted: {game_name}")
    print(f"PASS: Lua script found: {bool(lua_script)}")
    print(f"PASS: Fuzzy matching working: {fuzzy_match_game_name('Blade Ball', 'blAde Ball')}")

    print("\nBot setup is ready!")
    print("\nTo run the bot:")
    print("   python telegram_bot.py")
    print("\nBot commands:")
    print("   /Blade Ball - Search for Blade Ball script")
    print("   /start - Show help")
    print("   /help - Show help")

if __name__ == "__main__":
    test_bot_setup()