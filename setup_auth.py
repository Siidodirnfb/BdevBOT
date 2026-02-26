#!/usr/bin/env python3

import asyncio
from telethon import TelegramClient

API_ID = 30753680
API_HASH = 'c238c9c45ed3243c173058b2b64ef1fe'
SESSION_NAME = 'BdevSearch_session'

async def setup_authentication():
    print("Setting up Telegram authentication...")
    print("This will create a session file for future use.")
    print()

    client = TelegramClient(SESSION_NAME, API_ID, API_HASH)

    try:
        await client.start()

        me = await client.get_me()
        print(f"\nAuthenticated as: {me.first_name} (@{me.username})")
        print("Authentication successful!")

        try:
            channel = await client.get_entity('@BdevHub')
            print(f"Found channel: {channel.title}")

            messages = await client.get_messages(channel, limit=1)
            if messages:
                print("Channel access confirmed!")
            else:
                print("Warning: Could not read messages from channel")

        except Exception as e:
            print(f"Warning: Could not access channel @BdevHub: {e}")
            print("The bot may not work properly until channel access is resolved")

        print("\nSetup complete! You can now run the bot.")
        print("Run: python telegram_bot.py")

    except Exception as e:
        print(f"Setup failed: {e}")
        return False

    finally:
        await client.disconnect()

    return True

if __name__ == "__main__":
    print("=== Telegram Bot Authentication Setup ===\n")

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    success = loop.run_until_complete(setup_authentication())

    if success:
        print("\n=== Setup Complete ===")
    else:
        print("\n=== Setup Failed ===")
        print("Please check your API credentials and try again.")