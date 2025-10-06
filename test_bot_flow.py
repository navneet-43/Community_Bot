#!/usr/bin/env python3
"""
Test script to verify the complete bot flow
"""

import discord
from discord.ext import commands
import asyncio
import logging
from datetime import datetime

from config import *
from database import DatabaseManager
from screening_logic import ScreeningLogic

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TestBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        intents.members = True
        intents.guilds = True
        intents.presences = False
        
        super().__init__(command_prefix='!', intents=intents)
        
        self.db = DatabaseManager(DATABASE_PATH)
        self.screening_logic = ScreeningLogic()
    
    async def on_ready(self):
        """Called when the bot is ready"""
        logger.info(f'🤖 Test Bot Ready: {self.user}')
        logger.info(f'📊 Connected to {len(self.guilds)} guild(s)')
        
        # Test guild connection
        guild = self.get_guild(GUILD_ID)
        if guild:
            logger.info(f'✅ Connected to guild: {guild.name} (ID: {guild.id})')
            logger.info(f'👥 Guild has {guild.member_count} members')
            
            # Test member join simulation
            await self.test_member_join_flow()
        else:
            logger.error(f'❌ Guild with ID {GUILD_ID} not found!')
        
        await self.close()
    
    async def test_member_join_flow(self):
        """Test the complete member join flow"""
        logger.info("🧪 Testing complete member join flow...")
        
        # Test 1: Check database connection
        try:
            stats = self.db.get_user_stats()
            logger.info(f"✅ Database working - {stats.get('total_users', 0)} users")
        except Exception as e:
            logger.error(f"❌ Database error: {e}")
            return
        
        # Test 2: Check screening logic
        try:
            questions = list(self.screening_logic.questions.keys())
            logger.info(f"✅ Screening logic working - {len(questions)} questions: {questions}")
        except Exception as e:
            logger.error(f"❌ Screening logic error: {e}")
            return
        
        # Test 3: Check question flow
        try:
            next_q = self.screening_logic.get_next_question('gender')
            logger.info(f"✅ Question flow working - next after gender: {next_q}")
        except Exception as e:
            logger.error(f"❌ Question flow error: {e}")
            return
        
        # Test 4: Check role determination
        try:
            test_data = {
                'gender': ['male'],
                'age_group': ['18_24'],
                'show_types': ['scripted', 'anime'],
                'city_tier': ['tier1']
            }
            roles = self.screening_logic.determine_roles(test_data)
            logger.info(f"✅ Role determination working - would create roles: {roles}")
        except Exception as e:
            logger.error(f"❌ Role determination error: {e}")
            return
        
        logger.info("🎉 All tests passed! Bot flow is working correctly.")
        logger.info("📋 To test with a real user:")
        logger.info("   1. Send invite link to someone")
        logger.info("   2. They join the server")
        logger.info("   3. Bot should auto-send welcome + questions")
        logger.info("   4. After 4 questions, they get roles + channels")

async def main():
    if not DISCORD_TOKEN:
        logger.error("❌ DISCORD_TOKEN not found")
        return
    
    bot = TestBot()
    await bot.start(DISCORD_TOKEN)

if __name__ == "__main__":
    asyncio.run(main())
