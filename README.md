# Roblox Script Telegram Bot

A Telegram bot that searches for Roblox scripts based on channel posts.

## Features

- **Public Chat Mode**: Search for scripts using `/place_name` commands
- **Personal Messages Mode**: Private script requests (not yet implemented)
- **Auto-Forwarding**: Automatically forwards posts from monitored channels to @HybridScripts
- **Fuzzy Matching**: Handles variations in game names (e.g., "Blade Ball" vs "blAde Ball")
- **Automatic Script Extraction**: Finds and extracts Lua code from channel posts

## Setup

1. **Get Telegram API Credentials** (if not already done):
   - Go to https://my.telegram.org/auth
   - Log in with your phone number
   - Go to "API development tools"
   - Create a new application
   - Copy your `api_id` and `api_hash`

2. **Bot is configured** with:
   - Bot Token: `8527923791:AAHAkZMPfeVHdL-dFC40JwcTFlxdoTuvS5w`
   - Channel: `@BdevHub`
   - API ID: `30753680`
   - API Hash: `c238c9c45ed3243c173058b2b64ef1fe`

3. **First-time setup** (run once):
   ```bash
   python setup_auth.py
   ```
   Follow the prompts to authenticate with your phone number.

3. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Add Bot to Channels**:
   - **For Script Search**: Add bot to @BdevHub as administrator (read permissions)
   - **For Auto-Forwarding**: Add bot to @HybridScripts as administrator (post permissions)
   - **Source Channels**: Bot needs access to @ArceusXCommunity, @beconscript, @scripttigraann (read permissions)
   - Posts should follow format:
     ```
     Игра: Game Name
     ```lua
     -- Your Lua script here
     ```

## Usage

### Public Chat Commands
- `/Blade Ball` - Search for Blade Ball script
- `/Phantom Forces` - Search for Phantom Forces script
- `/forwarding` - Check auto-forwarding status
- Any game name after `/`

### How It Works
1. **Auto-Forwarding**: Monitors @ArceusXCommunity, @beconscript, @scripttigraann for new posts
2. **Forwarding**: Automatically forwards new messages to @HybridScripts INSTANTLY (event-driven)
3. **Script Search**: Loads the last 1000 posts from @BdevHub channel at startup
4. **Command Processing**: When `/game_name` received, analyzes stored posts
5. **Pattern Matching**: Looks for "Игра:" or "Game:" patterns
6. **Fuzzy Matching**: Uses intelligent matching to find similar game names
7. **Script Extraction**: Extracts Lua code from matching posts (loadstring or code blocks)
8. **Response**: Returns the found script to the user

## Channel Post Format
Posts in the channel should follow one of these formats:

**Format 1 - Code blocks:**
```
Игра: Blade Ball

```lua
local player = game.Players.LocalPlayer
-- Your script code here
```

**Format 2 - Loadstring (current format):**
```
Игра: Mine a Brainrot
Функции: На фото
Ключ: ❌
loadstring(game:HttpGet("https://raw.githubusercontent.com/gumanba/Scripts/main/MineaBrainrot"))()
```

The bot automatically extracts Lua scripts from both ```lua code blocks and loadstring() calls.
```

## Important Notes

- **No admin permissions needed** - Uses Telegram API to read channel posts directly
- Bot loads the last 1000 posts from @BdevHub at startup
- Channel posts must contain "Игра:" or "Game:" followed by the game name
- Lua code should be in code blocks (```lua) or loadstring() calls
- Fuzzy matching handles spelling variations and case differences
- If no posts are found, check that the channel username is correct

## Running the Bot

First, set up authentication (one-time setup):
```bash
python setup_auth.py
```

Test the setup:
```bash
python test_bot.py
```

Then run the bot:
```bash
python telegram_bot.py
```

## Dependencies

- pyTelegramBotAPI: Telegram bot API wrapper
- telethon: Telegram API client for reading channels
- rapidfuzz: Fast fuzzy string matching
- python-dotenv: Environment variable management