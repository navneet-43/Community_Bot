#!/usr/bin/env python3
"""
Setup script for Rusk Media Discord Bot
This script helps you get the bot token and set up the environment
"""

import os
import sys
from dotenv import load_dotenv

def setup_environment():
    """Set up the environment file"""
    print("🚀 Setting up Rusk Media Discord Bot")
    print("=" * 50)
    
    # Check if .env exists
    if os.path.exists('.env'):
        print("✅ .env file already exists")
        load_dotenv()
    else:
        print("📝 Creating .env file...")
        with open('.env', 'w') as f:
            f.write("# Discord Bot Configuration\n")
            f.write("DISCORD_TOKEN=your_bot_token_here\n")
            f.write("GUILD_ID=your_guild_id_here\n\n")
            f.write("# Database Configuration\n")
            f.write("DATABASE_PATH=rusk_media_bot.db\n")
        print("✅ .env file created")
    
    # Check for bot token
    token = os.getenv('DISCORD_TOKEN')
    if not token or token == 'your_bot_token_here':
        print("\n❌ Bot token not configured!")
        print("\n📋 To get your bot token:")
        print("1. Go to https://discord.com/developers/applications")
        print("2. Click 'New Application' and name it 'Rusk Media Bot'")
        print("3. Go to 'Bot' section and click 'Add Bot'")
        print("4. Copy the token and paste it in .env file")
        print("5. Enable these bot permissions:")
        print("   - Send Messages")
        print("   - Use Slash Commands")
        print("   - Manage Roles")
        print("   - Manage Channels")
        print("   - Read Message History")
        return False
    
    # Check for guild ID
    guild_id = os.getenv('GUILD_ID')
    if not guild_id or guild_id == 'your_guild_id_here':
        print("\n❌ Guild ID not configured!")
        print("\n📋 To get your guild ID:")
        print("1. Enable Developer Mode in Discord (User Settings > Advanced > Developer Mode)")
        print("2. Right-click on your server name and select 'Copy ID'")
        print("3. Paste the ID in .env file")
        return False
    
    print("\n✅ Environment configured successfully!")
    return True

def install_dependencies():
    """Install required dependencies"""
    print("\n📦 Installing dependencies...")
    os.system("pip install -r requirements.txt")
    print("✅ Dependencies installed!")

def main():
    """Main setup function"""
    if setup_environment():
        install_dependencies()
        print("\n🎉 Setup complete!")
        print("\n🚀 To run the bot:")
        print("python bot.py")
        print("\n📚 For more information, check the README.md file")
    else:
        print("\n❌ Setup incomplete. Please configure the environment variables first.")
        sys.exit(1)

if __name__ == "__main__":
    main()

