# Railway Configuration
# This file contains the configuration for Railway deployment

import os

# Discord Bot Configuration
# Replace YOUR_DISCORD_TOKEN_HERE with your actual Discord bot token
DISCORD_TOKEN = "YOUR_DISCORD_TOKEN_HERE"
GUILD_ID = "1415310303062786058"
DATABASE_PATH = "rusk_media_bot.db"
WELCOME_CHANNEL = "welcome"

# Override with environment variables if they exist
DISCORD_TOKEN = os.getenv('DISCORD_TOKEN', DISCORD_TOKEN)
GUILD_ID = os.getenv('GUILD_ID', GUILD_ID)
DATABASE_PATH = os.getenv('DATABASE_PATH', DATABASE_PATH)
WELCOME_CHANNEL = os.getenv('WELCOME_CHANNEL', WELCOME_CHANNEL)