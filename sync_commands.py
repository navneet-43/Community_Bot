#!/usr/bin/env python3
"""
Force sync slash commands to Discord server
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

class CommandSyncBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        intents.members = True
        intents.guilds = True
        intents.presences = False
        
        super().__init__(command_prefix='!', intents=intents)
    
    async def setup_hook(self):
        """Force sync commands"""
        print("🔄 Starting command sync...")
        
        # Register commands first
        @app_commands.command(name="start_screening", description="Start the screening process")
        async def start_screening(interaction: discord.Interaction, campaign: str = "DISCOVERY_2025"):
            await interaction.response.send_message(f"✅ Screening started for campaign: {campaign}", ephemeral=True)
        
        @app_commands.command(name="admin_stats", description="Get screening statistics (Admin only)")
        async def admin_stats(interaction: discord.Interaction):
            await interaction.response.send_message("✅ Stats command works!", ephemeral=True)
        
        # Add commands to tree
        self.tree.add_command(start_screening)
        self.tree.add_command(admin_stats)
        
        try:
            if GUILD_ID:
                guild = discord.Object(id=GUILD_ID)
                
                # Clear existing commands first
                self.tree.clear_commands(guild=guild)
                print("🗑️  Cleared existing commands")
                
                # Copy commands to guild
                self.tree.copy_global_to(guild=guild)
                
                # Sync to guild
                synced = await self.tree.sync(guild=guild)
                print(f"✅ Synced {len(synced)} command(s) to guild {GUILD_ID}")
                
                for cmd in synced:
                    print(f"   - /{cmd.name}: {cmd.description}")
            else:
                synced = await self.tree.sync()
                print(f"✅ Synced {len(synced)} command(s) globally")
                
        except Exception as e:
            print(f"❌ Failed to sync commands: {e}")
    
    async def on_ready(self):
        print(f"✅ {self.user} is ready!")
        print(f"✅ Bot is in {len(self.guilds)} guild(s)")
        
        for guild in self.guilds:
            print(f"   - {guild.name} (ID: {guild.id})")
        
        print("\n✅ Commands synced! You can now use /start_screening in your Discord server")
        print("🛑 Press Ctrl+C to stop this bot and run the main bot")
        
        # Keep running for 10 seconds to ensure sync completes
        await asyncio.sleep(10)
        await self.close()

async def main():
    bot = CommandSyncBot()
    try:
        print("🚀 Starting command sync bot...")
        await bot.start(DISCORD_TOKEN)
    except KeyboardInterrupt:
        print("\n🛑 Sync stopped")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    asyncio.run(main())
