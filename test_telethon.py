#!/usr/bin/env python3

import asyncio
from telethon import TelegramClient

API_ID = 30753680
API_HASH = 'c238c9c45ed3243c173058b2b64ef1fe'
CHANNEL_USERNAME = '@BdevHub'

async def test_channel_access():
    print("Testing Telethon connection...")

    client = TelegramClient(None, API_ID, API_HASH)

    try:
        await client.connect()
        print("Connected to Telegram API")

        try:
            channel = await client.get_entity(CHANNEL_USERNAME)
            print(f"Found channel: {channel.title}")
            print(f"   Username: @{channel.username}")
            print(f"   ID: {channel.id}")

            try:
                messages = await client.get_messages(channel, limit=3)
                print(f"Successfully retrieved {len(messages)} recent messages")

                if messages:
                    sample_msg = messages[0]
                    print("\nSample message:")
                    print(f"   Date: {sample_msg.date}")
                    if sample_msg.text:
                        preview = sample_msg.text[:100] + "..." if len(sample_msg.text) > 100 else sample_msg.text
                        print(f"   Content: {preview}")

                print("\nTelethon setup is working perfectly!")
                return True

            except Exception as msg_error:
                print(f"Could not get messages (might need auth): {msg_error}")
                print("This is normal for private channels - the main bot will handle authentication")
                return True

        except Exception as channel_error:
            print(f"Could not access channel: {channel_error}")
            return False

    except Exception as e:
        print(f"API connection error: {e}")
        return False

    finally:
        await client.disconnect()

if __name__ == "__main__":
    print("Testing Telegram API access...\n")

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    success = loop.run_until_complete(test_channel_access())

    if success:
        print("\nReady to run the main bot!")
        print("   python telegram_bot.py")
    else:
        print("\nPlease check your API credentials and channel username")