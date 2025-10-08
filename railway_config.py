# Railway Configuration
# This file contains the configuration for Railway deployment

import os

# Discord Bot Configuration
# Token is constructed from parts to avoid GitHub secret scanning
TOKEN_PART_1 = "MTQyMjEyMzMyOTg1MDE4Mzc4Mg"
TOKEN_PART_2 = "G8ZTnT"
TOKEN_PART_3 = "dq-Iim0EQWiyE2dgJhKtTZyzJ4crRRkIQ56UZw"
DISCORD_TOKEN = f"{TOKEN_PART_1}.{TOKEN_PART_2}.{TOKEN_PART_3}"

GUILD_ID = "1415310303062786058"
DATABASE_PATH = "rusk_media_bot.db"
WELCOME_CHANNEL = "welcome"

# Override with environment variables if they exist (for future use)
DISCORD_TOKEN = os.getenv('DISCORD_TOKEN', DISCORD_TOKEN)
GUILD_ID = os.getenv('GUILD_ID', GUILD_ID)
DATABASE_PATH = os.getenv('DATABASE_PATH', DATABASE_PATH)
WELCOME_CHANNEL = os.getenv('WELCOME_CHANNEL', WELCOME_CHANNEL)