#!/usr/bin/env python3
"""
Debug bot to test member join functionality
"""

import discord
from discord.ext import commands
import asyncio
import logging
from datetime import datetime

from config import *

# Set up detailed logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class DebugBot(commands.Bot):
    def __init__(self):
        # Configure intents
        intents = discord.Intents.default()
        intents.message_content = True
        intents.members = True  # CRITICAL for member join events
        intents.guilds = True
        intents.presences = False
        
        logger.info(f"🔧 Intents configured:")
        logger.info(f"   - members: {intents.members}")
        logger.info(f"   - guilds: {intents.guilds}")
        logger.info(f"   - message_content: {intents.message_content}")
        
        super().__init__(command_prefix='!', intents=intents)
    
    async def on_ready(self):
        """Called when the bot is ready"""
        logger.info(f'🤖 Debug Bot Ready: {self.user}')
        logger.info(f'📊 Connected to {len(self.guilds)} guild(s)')
        
        # Check guild connection
        guild = self.get_guild(GUILD_ID)
        if guild:
            logger.info(f'✅ Connected to guild: {guild.name} (ID: {guild.id})')
            logger.info(f'👥 Guild has {guild.member_count} members')
            logger.info(f'🔍 Bot permissions in guild: {guild.me.guild_permissions}')
            
            # Check if bot can see members
            members = guild.members
            logger.info(f'👥 Bot can see {len(members)} members')
            
            # List recent members
            recent_members = sorted(members, key=lambda m: m.joined_at, reverse=True)[:5]
            logger.info("📋 Recent members:")
            for member in recent_members:
                logger.info(f"   - {member.display_name} (joined: {member.joined_at})")
        else:
            logger.error(f'❌ Guild with ID {GUILD_ID} not found!')
    
    async def on_member_join(self, member):
        """Called when a member joins the server"""
        logger.info(f"🎉 MEMBER JOIN EVENT TRIGGERED!")
        logger.info(f"   - Member: {member} (ID: {member.id})")
        logger.info(f"   - Guild: {member.guild.name}")
        logger.info(f"   - Joined at: {datetime.now()}")
        
        # Test sending DM
        try:
            embed = discord.Embed(
                title="🎉 Welcome to Rusk Media!",
                description="Testing auto-welcome message...",
                color=0x00ff00
            )
            await member.send(embed=embed)
            logger.info(f"✅ Successfully sent welcome DM to {member}")
        except discord.Forbidden:
            logger.warning(f"❌ Cannot send DM to {member} - DMs disabled")
        except Exception as e:
            logger.error(f"❌ Error sending DM to {member}: {e}")
    
    async def on_error(self, event, *args, **kwargs):
        """Handle errors"""
        logger.error(f"❌ Error in event {event}: {args} {kwargs}")
    
    async def on_command_error(self, ctx, error):
        """Handle command errors"""
        logger.error(f"❌ Command error: {error}")

async def main():
    if not DISCORD_TOKEN:
        logger.error("❌ DISCORD_TOKEN not found")
        return
    
    logger.info("🚀 Starting debug bot...")
    bot = DebugBot()
    
    try:
        await bot.start(DISCORD_TOKEN)
    except Exception as e:
        logger.error(f"❌ Bot error: {e}")

if __name__ == "__main__":
    asyncio.run(main())
