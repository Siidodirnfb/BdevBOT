#!/usr/bin/env python3

import asyncio
from telethon import TelegramClient

API_ID = 30753680
API_HASH = 'c238c9c45ed3243c173058b2b64ef1fe'

async def test_basic_connection():
    print("Testing basic Telethon connection...")

    client = TelegramClient(None, API_ID, API_HASH)

    try:
        await client.connect()
        print("Connected to Telegram servers")

        authorized = await client.is_user_authorized()
        print(f"Authorization status: {authorized}")

        if not authorized:
            print("Not authorized - need phone authentication")
            print("This is normal - we need to authenticate with your phone")
            return False
        else:
            print("Already authorized!")
            return True

    except Exception as e:
        print(f"Connection failed: {e}")
        return False
    finally:
        await client.disconnect()

async def test_with_session():
    print("\nTesting with session file...")

    client = TelegramClient('BdevSearch_session', API_ID, API_HASH)

    try:
        await client.connect()
        authorized = await client.is_user_authorized()
        print(f"Session authorization status: {authorized}")

        if authorized:
            me = await client.get_me()
            print(f"Authenticated as: {me.first_name} (@{me.username})")
            return True
        else:
            print("Session not authorized")
            return False

    except Exception as e:
        print(f"Session test failed: {e}")
        return False
    finally:
        await client.disconnect()

if __name__ == "__main__":
    print("=== Telethon Authentication Test ===\n")

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    basic_ok = loop.run_until_complete(test_basic_connection())

    if not basic_ok:
        print("\nNeed to authenticate with phone number")
        print("Run: python setup_auth.py")
        print("(Make sure you're in an interactive terminal)")
    else:
        session_ok = loop.run_until_complete(test_with_session())

        if session_ok:
            print("\nAuthentication is working!")
            print("Your bot can now access channels and forward messages.")
        else:
            print("\nBasic connection works but session has issues")