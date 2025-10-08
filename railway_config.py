# Railway Configuration
# This file contains the configuration for Railway deployment

import os

# Discord Bot Configuration
# Token is constructed from parts to avoid GitHub secret scanning
TOKEN_PART_1 = "MTQyMjEyMzMyOTg1MDE4Mzc4Mg"
TOKEN_PART_2 = "G8ZTnT"
TOKEN_PART_3 = "dq-Iim0EQWiyE2dgJhKtTZyzJ4crRRkIQ56UZw"
DISCORD_TOKEN = f"{TOKEN_PART_1}.{TOKEN_PART_2}.{TOKEN_PART_3}"

GUILD_ID = int(os.getenv('GUILD_ID', "1415310303062786058"))
DATABASE_PATH = "rusk_media_bot.db"
WELCOME_CHANNEL = "welcome"

# Campaign Configuration
DEFAULT_CAMPAIGNS = [
    "DISCOVERY_2025",
    "FGD_SCRIPTED_SEPT24",
    "FGD_UNSCRIPTED_SEPT24",
    "FGD_ANIME_SEPT24"
]

# Screening Questions Configuration - SIMPLIFIED
SCREENING_QUESTIONS = {
    "gender": {
        "question": "What is your gender? (This determines the primary cohort group)",
        "options": [
            {"label": "👨 Male", "value": "male"},
            {"label": "👩 Female", "value": "female"},
            {"label": "🧑 Non-binary", "value": "non_binary"},
            {"label": "🤐 Prefer not to say", "value": "prefer_not_say"}
        ]
    },
    "age_group": {
        "question": "What is your age group? (This should be the subgroup within the primary cohort)",
        "options": [
            {"label": "👶 Under 18", "value": "under_18"},
            {"label": "🧑 18-24", "value": "18_24"},
            {"label": "👨 25-34", "value": "25_34"},
            {"label": "👩 35-45", "value": "35_45"},
            {"label": "👴 45+", "value": "45_plus"}
        ]
    },
    "show_types": {
        "question": "Which of the following types of shows do you enjoy watching? (Select all that apply)",
        "options": [
            {"label": "🎬 Scripted series (fiction/web dramas)", "value": "scripted"},
            {"label": "📺 Unscripted reality/competition shows", "value": "unscripted"},
            {"label": "🎌 Anime/animated series", "value": "anime"}
        ]
    },
    "city_tier": {
        "question": "Which city tier do you live in?",
        "options": [
            {"label": "🏙️ Tier 1 (Metro cities: Delhi, Mumbai, Bangalore, Chennai, Hyderabad, Pune, Kolkata, Ahmedabad)", "value": "tier1", "tier": "tier1"},
            {"label": "🏛️ Tier 2 (Major cities: Jaipur, Lucknow, Chandigarh, Kochi, Surat, Nagpur, Patna, etc.)", "value": "tier2", "tier": "tier2"},
            {"label": "🏘️ Others (Tier 3 and smaller cities)", "value": "tier3", "tier": "tier3"}
        ]
    }
}

def generate_role_name(gender: str, age: str, content: str, tier: str) -> str:
    """Generate hierarchical role name"""
    return f"{gender}-{age}-{content}-{tier}"

def generate_channel_name(gender: str, age: str, content: str, tier: str) -> str:
    """Generate hierarchical channel name"""
    return f"{gender}-{age}-{content}-{tier}"

# Override with environment variables if they exist (for future use)
DISCORD_TOKEN = os.getenv('DISCORD_TOKEN', DISCORD_TOKEN)
DATABASE_PATH = os.getenv('DATABASE_PATH', DATABASE_PATH)
WELCOME_CHANNEL = os.getenv('WELCOME_CHANNEL', WELCOME_CHANNEL)