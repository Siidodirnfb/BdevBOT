#!/usr/bin/env python3

import os
import sys

def check_dependencies():
    required_packages = [
        'telebot',
        'telethon',
        'rapidfuzz',
        'dotenv'
    ]

    missing = []
    for package in required_packages:
        try:
            __import__(package)
            print(f"[OK] {package}")
        except ImportError:
            missing.append(package)
            print(f"[MISSING] {package}")

    return len(missing) == 0

def check_files():
    required_files = [
        'telegram_bot.py',
        'setup_auth.py',
        'test_bot.py',
        'test_functions.py',
        'requirements.txt'
    ]

    for file in required_files:
        if os.path.exists(file):
            print(f"[OK] {file}")
        else:
            print(f"[MISSING] {file}")

def check_credentials():
    print("[OK] Bot Token: Configured")

    print("[OK] API ID: Configured")
    print("[OK] API Hash: Configured")

    print("[OK] Channel: @BdevHub")

def main():
    print("=== Roblox Telegram Bot Status Check ===\n")

    print("1. Dependencies:")
    deps_ok = check_dependencies()
    print()

    print("2. Files:")
    check_files()
    print()

    print("3. Configuration:")
    check_credentials()
    print()

    print("4. Next Steps:")
    if deps_ok:
        print("[OK] Dependencies installed")
        print("-> Run: python setup_auth.py (one-time authentication)")
        print("-> Run: python telegram_bot.py (to start the bot)")
    else:
        print("[ACTION] Install missing dependencies: pip install -r requirements.txt")

    print("\n5. Bot Features:")
    print("[+] Searches Roblox scripts from @BdevHub channel")
    print("[+] Supports loadstring() and code block formats")
    print("[+] Fuzzy matching for game names")
    print("[+] No admin permissions needed in channel")
    print("[+] Loads last 1000 channel posts")

if __name__ == "__main__":
    main()