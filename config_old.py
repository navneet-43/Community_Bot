import os
from dotenv import load_dotenv

load_dotenv()

# Discord Bot Configuration
DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
GUILD_ID = int(os.getenv('GUILD_ID', 0))  # Your Discord server ID

# Database Configuration
DATABASE_PATH = 'rusk_media_bot.db'

# Campaign Configuration
DEFAULT_CAMPAIGNS = [
    "DISCOVERY_2025",
    "FGD_SCRIPTED_SEPT24",
    "FGD_UNSCRIPTED_SEPT24",
    "FGD_ANIME_SEPT24"
]

# Screening Questions Configuration
SCREENING_QUESTIONS = {
    "show_types": {
        "question": "Which of the following types of shows do you enjoy watching? (Select all that apply)",
        "options": [
            {"label": "Scripted series (fiction/web dramas)", "value": "scripted", "emoji": "🎬"},
            {"label": "Unscripted reality/competition shows", "value": "unscripted", "emoji": "📺"},
            {"label": "Anime/animated series", "value": "anime", "emoji": "🎌"}
        ]
    },
    "city": {
        "question": "Which city/town do you live in?",
        "options": [
            {"label": "Delhi", "value": "delhi", "tier": "tier1"},
            {"label": "Mumbai", "value": "mumbai", "tier": "tier1"},
            {"label": "Bangalore", "value": "bangalore", "tier": "tier1"},
            {"label": "Chennai", "value": "chennai", "tier": "tier1"},
            {"label": "Kolkata", "value": "kolkata", "tier": "tier1"},
            {"label": "Hyderabad", "value": "hyderabad", "tier": "tier1"},
            {"label": "Pune", "value": "pune", "tier": "tier1"},
            {"label": "Ahmedabad", "value": "ahmedabad", "tier": "tier1"},
            {"label": "Other Tier-1 City", "value": "other_tier1", "tier": "tier1"},
            {"label": "Tier-2 City", "value": "tier2", "tier": "tier2"},
            {"label": "Tier-3 City", "value": "tier3", "tier": "tier3"}
        ]
    },
    "age_group": {
        "question": "What is your age group?",
        "options": [
            {"label": "Under 18", "value": "under_18", "emoji": "👶"},
            {"label": "18-24", "value": "18_24", "emoji": "🧑"},
            {"label": "25-34", "value": "25_34", "emoji": "👨"},
            {"label": "35-45", "value": "35_45", "emoji": "👩"},
            {"label": "45+", "value": "45_plus", "emoji": "👴"}
        ]
    },
    "gender": {
        "question": "What is your gender?",
        "options": [
            {"label": "Male", "value": "male", "emoji": "👨"},
            {"label": "Female", "value": "female", "emoji": "👩"},
            {"label": "Non-binary", "value": "non_binary", "emoji": "🧑"},
            {"label": "Prefer not to say", "value": "prefer_not_say", "emoji": "🤐"}
        ]
    },
    "genres": {
        "question": "Which of these shows or genres do you enjoy? (Select all that apply)",
        "options": [
            {"label": "Romance/Drama", "value": "romance_drama", "emoji": "💕"},
            {"label": "Comedy", "value": "comedy", "emoji": "😂"},
            {"label": "Reality Competition", "value": "reality_competition", "emoji": "🏆"},
            {"label": "Dating Shows", "value": "dating_shows", "emoji": "💘"},
            {"label": "Anime", "value": "anime", "emoji": "🎌"},
            {"label": "Thriller/Mystery", "value": "thriller", "emoji": "🔍"},
            {"label": "Action", "value": "action", "emoji": "⚔️"},
            {"label": "Sci-Fi/Fantasy", "value": "scifi_fantasy", "emoji": "🚀"}
        ]
    },
    "viewing_platform": {
        "question": "How do you usually watch our content?",
        "options": [
            {"label": "App User", "value": "app_user", "emoji": "📱"},
            {"label": "YouTube", "value": "youtube", "emoji": "📺"},
            {"label": "TV", "value": "tv", "emoji": "📺"},
            {"label": "Other Platform", "value": "other", "emoji": "🌐"}
        ]
    },
    "education": {
        "question": "What is your highest education level? (NCCS proxy)",
        "options": [
            {"label": "High School or Below", "value": "high_school", "nccs": "C2"},
            {"label": "Some College/Diploma", "value": "some_college", "nccs": "C1"},
            {"label": "Bachelor's Degree", "value": "bachelors", "nccs": "B2"},
            {"label": "Master's Degree or Higher", "value": "masters_plus", "nccs": "B1"}
        ]
    }
}

# Role Configuration
ROLE_MAPPING = {
    "scripted": "Scripted Viewers",
    "unscripted": "Unscripted Viewers", 
    "anime": "Anime Fans",
    "tier1": "Tier-1 Cities",
    "tier2": "Tier-2 Cities",
    "tier3": "Tier-3 Cities"
}

# Channel Configuration
CHANNEL_MAPPING = {
    "scripted": "scripted-content",
    "unscripted": "unscripted-content",
    "anime": "anime-content"
}

