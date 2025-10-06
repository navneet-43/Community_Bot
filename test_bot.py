#!/usr/bin/env python3
"""
Simple test script to verify bot commands are working
"""

import discord
from discord.ext import commands
from discord import app_commands
import asyncio
import os
from dotenv import load_dotenv

load_dotenv()

DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
GUILD_ID = int(os.getenv('GUILD_ID', 0))

class TestBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        intents.members = True
        intents.guilds = True
        intents.presences = False
        
        super().__init__(command_prefix='!', intents=intents)
    
    async def setup_hook(self):
        """Sync commands to guild"""
        try:
            if GUILD_ID:
                guild = discord.Object(id=GUILD_ID)
                synced = await self.tree.sync(guild=guild)
                print(f"✅ Synced {len(synced)} command(s) to guild {GUILD_ID}")
                for cmd in synced:
                    print(f"   - {cmd.name}: {cmd.description}")
            else:
                synced = await self.tree.sync()
                print(f"✅ Synced {len(synced)} command(s) globally")
        except Exception as e:
            print(f"❌ Failed to sync commands: {e}")
    
    async def on_ready(self):
        print(f"✅ {self.user} is ready!")
        print(f"✅ Bot is in {len(self.guilds)} guild(s)")
        
        # List guilds
        for guild in self.guilds:
            print(f"   - {guild.name} (ID: {guild.id})")
        
        # Test if we can find our target guild
        target_guild = self.get_guild(GUILD_ID)
        if target_guild:
            print(f"✅ Found target guild: {target_guild.name}")
        else:
            print(f"❌ Target guild {GUILD_ID} not found")
    
    @app_commands.command(name="test", description="Test command to verify bot is working")
    async def test_command(self, interaction: discord.Interaction):
        await interaction.response.send_message("✅ Test command works! Bot is responding correctly.", ephemeral=True)
    
    @app_commands.command(name="start_screening", description="Start the screening process")
    async def start_screening(self, interaction: discord.Interaction, campaign: str = "DISCOVERY_2025"):
        await interaction.response.send_message(f"✅ Screening command works! Campaign: {campaign}", ephemeral=True)

async def main():
    bot = TestBot()
    try:
        print("🚀 Starting test bot...")
        await bot.start(DISCORD_TOKEN)
    except KeyboardInterrupt:
        print("\n🛑 Bot stopped by user")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    asyncio.run(main())

