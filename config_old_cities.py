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

# Tier 1 Cities (8 cities)
TIER_1_CITIES = {
    'bangalore', 'bengaluru', 'delhi', 'new delhi', 'ncr', 'chennai', 
    'hyderabad', 'mumbai', 'pune', 'kolkata', 'calcutta', 'ahmedabad'
}

# Tier 2 Cities (20 cities)
TIER_2_CITIES = {
    'amritsar', 'bhopal', 'bhubaneswar', 'chandigarh', 'faridabad', 
    'ghaziabad', 'jamshedpur', 'jaipur', 'kochi', 'cochin', 'lucknow', 
    'nagpur', 'patna', 'raipur', 'surat', 'visakhapatnam', 'vizag',
    'agra', 'ajmer', 'kanpur', 'mysuru', 'mysore', 'srinagar'
}

# City Normalization Map (handle common variations)
CITY_NORMALIZATION = {
    'new delhi': 'Delhi',
    'ncr': 'Delhi',
    'bengaluru': 'Bangalore',
    'calcutta': 'Kolkata',
    'cochin': 'Kochi',
    'vizag': 'Visakhapatnam',
    'mysore': 'Mysuru'
}

# Screening Questions Configuration - NEW ORDER
SCREENING_QUESTIONS = {
    "gender": {
        "question": "What is your gender? (This determines the primary cohort group)",
        "options": [
            {"label": "Male", "value": "male", "emoji": "👨"},
            {"label": "Female", "value": "female", "emoji": "👩"},
            {"label": "Non-binary", "value": "non_binary", "emoji": "🧑"},
            {"label": "Prefer not to say", "value": "prefer_not_say", "emoji": "🤐"}
        ]
    },
    "age_group": {
        "question": "What is your age group? (This should be the subgroup within the primary cohort)",
        "options": [
            {"label": "Under 18", "value": "under_18", "emoji": "👶"},
            {"label": "18-24", "value": "18_24", "emoji": "🧑"},
            {"label": "25-34", "value": "25_34", "emoji": "👨"},
            {"label": "35-45", "value": "35_45", "emoji": "👩"},
            {"label": "45+", "value": "45_plus", "emoji": "👴"}
        ]
    },
    "show_types": {
        "question": "Which of the following types of shows do you enjoy watching? (Select all that apply) - Next subgroup within age",
        "options": [
            {"label": "Scripted series (fiction/web dramas)", "value": "scripted", "emoji": "🎬"},
            {"label": "Unscripted reality/competition shows", "value": "unscripted", "emoji": "📺"},
            {"label": "Anime/animated series", "value": "anime", "emoji": "🎌"}
        ]
    },
    "city": {
        "question": "Which city/town do you live in? (Next subgroup within content group)",
        "options": [
            # Tier 1 Cities
            {"label": "Bangalore", "value": "bangalore", "tier": "tier1"},
            {"label": "Delhi/NCR", "value": "delhi", "tier": "tier1"},
            {"label": "Chennai", "value": "chennai", "tier": "tier1"},
            {"label": "Hyderabad", "value": "hyderabad", "tier": "tier1"},
            {"label": "Mumbai", "value": "mumbai", "tier": "tier1"},
            {"label": "Pune", "value": "pune", "tier": "tier1"},
            {"label": "Kolkata", "value": "kolkata", "tier": "tier1"},
            {"label": "Ahmedabad", "value": "ahmedabad", "tier": "tier1"},
            
            # Tier 2 Cities
            {"label": "Amritsar", "value": "amritsar", "tier": "tier2"},
            {"label": "Bhopal", "value": "bhopal", "tier": "tier2"},
            {"label": "Bhubaneswar", "value": "bhubaneswar", "tier": "tier2"},
            {"label": "Chandigarh", "value": "chandigarh", "tier": "tier2"},
            {"label": "Faridabad", "value": "faridabad", "tier": "tier2"},
            {"label": "Ghaziabad", "value": "ghaziabad", "tier": "tier2"},
            {"label": "Jamshedpur", "value": "jamshedpur", "tier": "tier2"},
            {"label": "Jaipur", "value": "jaipur", "tier": "tier2"},
            {"label": "Kochi", "value": "kochi", "tier": "tier2"},
            {"label": "Lucknow", "value": "lucknow", "tier": "tier2"},
            {"label": "Nagpur", "value": "nagpur", "tier": "tier2"},
            {"label": "Patna", "value": "patna", "tier": "tier2"},
            {"label": "Raipur", "value": "raipur", "tier": "tier2"},
            {"label": "Surat", "value": "surat", "tier": "tier2"},
            {"label": "Visakhapatnam", "value": "visakhapatnam", "tier": "tier2"},
            {"label": "Agra", "value": "agra", "tier": "tier2"},
            {"label": "Ajmer", "value": "ajmer", "tier": "tier2"},
            {"label": "Kanpur", "value": "kanpur", "tier": "tier2"},
            {"label": "Mysuru", "value": "mysuru", "tier": "tier2"},
            {"label": "Srinagar", "value": "srinagar", "tier": "tier2"},
            
            # Tier 3
            {"label": "Other City (Tier 3)", "value": "other_tier3", "tier": "tier3"}
        ]
    }
}

def normalize_city(city_input: str) -> tuple:
    """
    Normalize city input and determine tier
    Returns: (normalized_city_name, tier)
    """
    city_lower = city_input.lower().strip()
    
    # Check normalization map first
    if city_lower in CITY_NORMALIZATION:
        normalized = CITY_NORMALIZATION[city_lower]
        city_lower = normalized.lower()
    
    # Check Tier 1
    if city_lower in TIER_1_CITIES:
        # Capitalize properly
        for city in TIER_1_CITIES:
            if city == city_lower:
                return (city.capitalize(), 'tier1')
    
    # Check Tier 2
    if city_lower in TIER_2_CITIES:
        for city in TIER_2_CITIES:
            if city == city_lower:
                return (city.capitalize(), 'tier2')
    
    # Default to Tier 3
    return (city_input.capitalize(), 'tier3')

# Role/Channel naming pattern: gender-age-content-tier
# Example: female-18_24-scripted-tier1
def generate_role_name(gender: str, age: str, content: str, tier: str) -> str:
    """Generate hierarchical role name"""
    return f"{gender}-{age}-{content}-{tier}"

def generate_channel_name(gender: str, age: str, content: str, tier: str) -> str:
    """Generate hierarchical channel name"""
    return f"{gender}-{age}-{content}-{tier}"
