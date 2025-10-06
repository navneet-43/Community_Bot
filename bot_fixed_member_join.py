import discord
from discord.ext import commands
from discord import app_commands
import asyncio
import logging
from datetime import datetime
from typing import Optional, Dict, List, Any

from config import *
from database import DatabaseManager
from screening_logic import ScreeningLogic

# Set up detailed logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class RuskMediaBot(commands.Bot):
    def __init__(self):
        # Configure intents with detailed logging
        intents = discord.Intents.default()
        intents.message_content = True
        intents.members = True  # CRITICAL for member join events
        intents.guilds = True
        intents.presences = False
        
        logger.info(f"🔧 Bot intents configured:")
        logger.info(f"   - members: {intents.members}")
        logger.info(f"   - guilds: {intents.guilds}")
        logger.info(f"   - message_content: {intents.message_content}")
        
        super().__init__(command_prefix='!', intents=intents)
        
        self.db = DatabaseManager(DATABASE_PATH)
        self.screening_logic = ScreeningLogic()
        self.active_screenings = {}
    
    async def setup_hook(self):
        """Called when the bot is starting up"""
        try:
            if GUILD_ID:
                synced = await self.tree.sync(guild=discord.Object(id=GUILD_ID))
                logger.info(f"Synced {len(synced)} command(s) to guild {GUILD_ID}")
            else:
                synced = await self.tree.sync()
                logger.info(f"Synced {len(synced)} command(s) globally")
        except Exception as e:
            logger.error(f"Failed to sync commands: {e}")
    
    async def on_ready(self):
        """Called when the bot is ready"""
        logger.info(f'🤖 {self.user} has connected to Discord!')
        logger.info(f'📊 Bot is in {len(self.guilds)} guild(s)')
        
        # Check guild connection and permissions
        guild = self.get_guild(GUILD_ID)
        if guild:
            logger.info(f'✅ Connected to guild: {guild.name} (ID: {guild.id})')
            logger.info(f'👥 Guild has {guild.member_count} members')
            logger.info(f'🔍 Bot permissions: {guild.me.guild_permissions}')
            
            # Check if we can see members
            members = guild.members
            logger.info(f'👥 Bot can see {len(members)} members')
        else:
            logger.error(f'❌ Guild with ID {GUILD_ID} not found!')
        
        # Initialize default campaigns
        await self.initialize_campaigns()
    
    async def initialize_campaigns(self):
        """Initialize default campaigns in the database"""
        for campaign_name in DEFAULT_CAMPAIGNS:
            existing_campaigns = self.db.get_campaigns()
            if not any(c['name'] == campaign_name for c in existing_campaigns):
                self.db.add_campaign(
                    name=campaign_name,
                    description=f"Campaign for {campaign_name}",
                    invite_link=f"https://discord.gg/{campaign_name.lower()}"
                )
                logger.info(f"Initialized campaign: {campaign_name}")
    
    async def on_member_join(self, member):
        """Called when a member joins the server - AUTOMATICALLY START SCREENING"""
        logger.info(f"🎉 MEMBER JOIN EVENT TRIGGERED!")
        logger.info(f"   - Member: {member} (ID: {member.id})")
        logger.info(f"   - Username: {member.name}")
        logger.info(f"   - Display Name: {member.display_name}")
        logger.info(f"   - Guild: {member.guild.name}")
        logger.info(f"   - Joined at: {datetime.now()}")
        
        try:
            # Check if user already completed screening
            user_data = self.db.get_user(member.id)
            if user_data and user_data.get('screening_completed'):
                logger.info(f"✅ User {member} already completed screening")
                return
            
            # Add user to database
            logger.info(f"📝 Adding user {member} to database...")
            self.db.add_user(
                user_id=member.id,
                username=member.name,
                display_name=member.display_name,
                campaign="AUTO_JOIN"
            )
            
            # Start screening session
            logger.info(f"🎯 Starting screening session for {member}...")
            session_id = self.db.start_screening_session(member.id, "AUTO_JOIN")
            if not session_id:
                logger.error(f"❌ Failed to start screening session for {member}")
                return
            
            # Store active screening
            self.active_screenings[member.id] = {
                'session_id': session_id,
                'current_question': 'gender',
                'answers': {}
            }
            
            # Send welcome message with first question automatically
            logger.info(f"📤 Sending welcome message to {member}...")
            embed = discord.Embed(
                title="Welcome to Rusk Media Community! 🎬",
                description="Thank you for joining! Please complete this quick 4-question screening to get access to your personalized content channels.",
                color=0x00ff00
            )
            embed.set_footer(text="This helps us match you with the right content and communities!")
            
            try:
                await member.send(embed=embed)
                logger.info(f"✅ Welcome message sent to {member}")
                
                await asyncio.sleep(1)
                logger.info(f"📋 Sending first question to {member}...")
                await self.send_screening_question_dm(member, 'gender')
                logger.info(f"✅ First question sent to {member}")
                
            except discord.Forbidden:
                logger.warning(f"❌ Could not send DM to {member}, user has DMs disabled")
                general_channel = discord.utils.get(member.guild.channels, name="general")
                if general_channel:
                    await general_channel.send(
                        f"{member.mention} Welcome! Please enable DMs to complete the screening process."
                    )
                    logger.info(f"✅ Sent welcome message to general channel for {member}")
            except Exception as e:
                logger.error(f"❌ Error sending message to {member}: {e}")
                
        except Exception as e:
            logger.error(f"❌ Error in on_member_join for {member}: {e}")
    
    async def send_screening_question_dm(self, member: discord.Member, question_key: str):
        """Send a screening question via DM"""
        logger.info(f"📋 Sending question '{question_key}' to {member}")
        
        question_data = self.screening_logic.questions.get(question_key)
        if not question_data:
            logger.error(f"❌ Invalid question key: {question_key}")
            return
        
        embed = discord.Embed(
            title=f"Question {self.get_question_number(question_key)}/4 📋",
            description=question_data['question'],
            color=0x0099ff
        )
        
        # Create select menu
        options = []
        for option in question_data['options']:
            label = option['label']
            
            # Limit label length to 100 characters (Discord limit)
            if len(label) > 100:
                label = label[:97] + "..."
            
            options.append(discord.SelectOption(
                label=label,
                value=option['value']
            ))
        
        # Handle multi-select for show_types
        if question_key in ['show_types']:
            select = discord.ui.Select(
                placeholder="Select all that apply...",
                options=options,
                max_values=len(options),
                custom_id=f"screening_{question_key}"
            )
        else:
            select = discord.ui.Select(
                placeholder="Choose one option...",
                options=options,
                max_values=1,
                custom_id=f"screening_{question_key}"
            )
        
        select.callback = lambda i: self.handle_screening_answer_dm(i, question_key, member)
        
        view = discord.ui.View(timeout=None)
        view.add_item(select)
        
        try:
            await member.send(embed=embed, view=view)
            logger.info(f"✅ Question '{question_key}' sent to {member}")
        except discord.Forbidden:
            logger.error(f"❌ Cannot send DM to {member}")
        except Exception as e:
            logger.error(f"❌ Error sending question to {member}: {e}")
    
    async def handle_screening_answer_dm(self, interaction: discord.Interaction, question_key: str, member: discord.Member):
        """Handle user's answer to a screening question in DM"""
        logger.info(f"📝 Received answer for '{question_key}' from {member}")
        
        user_id = member.id
        
        if user_id not in self.active_screenings:
            logger.error(f"❌ No active screening session found for {member}")
            await interaction.response.send_message("No active screening session found. Please rejoin the server to restart.", ephemeral=True)
            return
        
        # Get selected values
        selected_values = interaction.data['values']
        logger.info(f"📝 {member} selected: {selected_values}")
        
        # Store answer
        self.active_screenings[user_id]['answers'][question_key] = selected_values
        self.db.update_screening_session(user_id, question_key, selected_values)
        
        # Send acknowledgment
        await interaction.response.send_message(f"✅ Answer recorded!", ephemeral=True)
        
        # Get next question
        next_question = self.screening_logic.get_next_question(question_key)
        logger.info(f"➡️ Next question for {member}: {next_question}")
        
        if next_question:
            # Continue with next question
            self.active_screenings[user_id]['current_question'] = next_question
            await asyncio.sleep(0.5)
            await self.send_screening_question_dm(member, next_question)
        else:
            # Screening complete
            logger.info(f"🎉 Screening complete for {member}!")
            await self.complete_screening_dm(member, user_id)
    
    async def complete_screening_dm(self, member: discord.Member, user_id: int):
        """Complete the screening process and assign roles"""
        logger.info(f"🏁 Completing screening for {member}")
        
        screening_data = self.active_screenings[user_id]['answers']
        
        # Validate screening data
        if not self.screening_logic.validate_screening_data(screening_data):
            logger.error(f"❌ Screening incomplete for {member}")
            await member.send("❌ Screening incomplete. Please rejoin the server to restart.")
            return
        
        # Determine roles to assign
        roles_to_assign = self.screening_logic.determine_roles(screening_data)
        logger.info(f"🎭 Roles to assign to {member}: {roles_to_assign}")
        
        # Get user segments
        user_segments = self.screening_logic.get_user_segments(screening_data)
        
        # Update database
        self.db.update_user_screening(user_id, screening_data, roles_to_assign)
        
        # Assign roles and create channels
        guild = member.guild
        assigned_roles = []
        
        for role_name in roles_to_assign:
            # Check if role exists, if not, create it
            role = discord.utils.get(guild.roles, name=role_name)
            if not role:
                try:
                    role = await guild.create_role(name=role_name)
                    logger.info(f"✅ Created role: {role_name}")
                except Exception as e:
                    logger.error(f"❌ Failed to create role {role_name}: {e}")
                    continue
            
            if role and role not in member.roles:
                try:
                    await member.add_roles(role)
                    assigned_roles.append(role_name)
                    logger.info(f"✅ Assigned role {role_name} to {member}")
                except Exception as e:
                    logger.error(f"❌ Failed to assign role {role_name}: {e}")
        
        # Create private channels for each assigned hierarchical role
        for role_name in assigned_roles:
            if not role_name.startswith('Screened User'):  # Skip base role
                channel_name = role_name.lower()
                category = discord.utils.get(guild.categories, name="Screened Channels")
                if not category:
                    category = await guild.create_category("Screened Channels")
                    logger.info("✅ Created category: Screened Channels")

                if not discord.utils.get(guild.channels, name=channel_name):
                    try:
                        # Overwrites to make channel private to this role
                        overwrites = {
                            guild.default_role: discord.PermissionOverwrite(read_messages=False),
                            role: discord.PermissionOverwrite(read_messages=True, send_messages=True)
                        }
                        await guild.create_text_channel(channel_name, category=category, overwrites=overwrites)
                        logger.info(f"✅ Created private channel: #{channel_name} for role {role_name}")
                    except Exception as e:
                        logger.error(f"❌ Failed to create channel {channel_name}: {e}")

        # Send completion message
        embed = discord.Embed(
            title="Screening Complete! 🎉",
            description="Thank you for completing the screening process. You now have access to your personalized content channels in the server!",
            color=0x00ff00
        )
        
        # Add screening summary
        summary = self.screening_logic.get_screening_summary(screening_data)
        embed.add_field(name="Your Profile", value=summary, inline=False)
        
        # Add assigned roles
        if assigned_roles:
            embed.add_field(name="Assigned Groups", value="\n".join([f"✅ {role}" for role in assigned_roles]), inline=False)
        
        # Add next steps
        embed.add_field(
            name="What's Next?",
            value="Check out the new private channels that have appeared in the server based on your preferences!",
            inline=False
        )
        
        await member.send(embed=embed)
        
        # Clean up active screening
        del self.active_screenings[user_id]
        
        # Send welcome message to appropriate channels
        general_screened_channel = discord.utils.get(guild.channels, name="general-screened")
        if general_screened_channel:
            welcome_embed = discord.Embed(
                title="New Screened Member! 🎬",
                description=f"Welcome {member.mention} to the Rusk Media community! They've completed screening and joined their personalized groups.",
                color=0x00ff00
            )
            await general_screened_channel.send(embed=welcome_embed)
        
        logger.info(f"🎉 Screening process completed successfully for {member}")
    
    def get_question_number(self, question_key: str) -> int:
        """Get the question number for display"""
        question_order = ['gender', 'age_group', 'show_types', 'city_tier']
        try:
            return question_order.index(question_key) + 1
        except ValueError:
            return 1
    
    async def on_error(self, event, *args, **kwargs):
        """Handle errors"""
        logger.error(f"❌ Error in event {event}: {args} {kwargs}")
    
    @app_commands.command(name="admin_stats", description="Get screening statistics (Admin only)")
    @app_commands.default_permissions(administrator=True)
    async def admin_stats(self, interaction: discord.Interaction):
        """Get screening statistics for admins"""
        stats = self.db.get_user_stats()
        
        embed = discord.Embed(
            title="Screening Statistics 📊",
            color=0x0099ff
        )
        
        embed.add_field(name="Total Users", value=str(stats.get('total_users', 0)), inline=True)
        embed.add_field(name="Completed Screenings", value=str(stats.get('completed_screenings', 0)), inline=True)
        
        campaign_stats = stats.get('campaign_stats', {})
        if campaign_stats:
            campaign_text = "\n".join([f"{campaign}: {count}" for campaign, count in campaign_stats.items()])
            embed.add_field(name="Users by Campaign", value=campaign_text, inline=False)
        
        await interaction.response.send_message(embed=embed, ephemeral=True)

# Bot instance
bot = RuskMediaBot()

if __name__ == "__main__":
    if not DISCORD_TOKEN:
        logger.error("❌ DISCORD_TOKEN not found in environment variables")
        exit(1)
    
    logger.info("🚀 Starting Rusk Media Bot...")
    bot.run(DISCORD_TOKEN)
