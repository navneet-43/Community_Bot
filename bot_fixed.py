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

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RuskMediaBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        intents.members = True
        intents.guilds = True
        intents.presences = False  # Disable presence intent
        
        super().__init__(command_prefix='!', intents=intents)
        
        self.db = DatabaseManager(DATABASE_PATH)
        self.screening_logic = ScreeningLogic()
        self.active_screenings = {}  # Store active screening sessions
    
    async def setup_hook(self):
        """Called when the bot is starting up"""
        try:
            # Sync commands to the specific guild for faster deployment
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
        logger.info(f'{self.user} has connected to Discord!')
        logger.info(f'Bot is in {len(self.guilds)} guild(s)')
        
        # Initialize default campaigns
        await self.initialize_campaigns()
        
        # Create default roles and channels
        await self.setup_guild()
    
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
    
    async def setup_guild(self):
        """Set up roles and channels for the guild"""
        if not GUILD_ID:
            logger.warning("GUILD_ID not set, skipping guild setup")
            return
        
        guild = self.get_guild(GUILD_ID)
        if not guild:
            logger.warning(f"Guild with ID {GUILD_ID} not found. Bot will work when added to the server.")
            logger.info("To add bot to your server:")
            logger.info("1. Go to Discord Developer Portal")
            logger.info("2. OAuth2 → URL Generator")
            logger.info("3. Select 'bot' and 'applications.commands' scopes")
            logger.info("4. Select required permissions")
            logger.info("5. Use the generated URL to add bot to your server")
            return
        
        # Create roles
        role_names = [
            "Screened User",
            "Scripted Viewers", 
            "Unscripted Viewers",
            "Anime Fans",
            "Tier-1 Cities",
            "Tier-2 Cities", 
            "Tier-3 Cities",
            "Admin"
        ]
        
        for role_name in role_names:
            if not discord.utils.get(guild.roles, name=role_name):
                try:
                    await guild.create_role(name=role_name)
                    logger.info(f"Created role: {role_name}")
                except Exception as e:
                    logger.error(f"Failed to create role {role_name}: {e}")
        
        # Create channels
        channel_names = [
            "scripted-content",
            "unscripted-content", 
            "anime-content",
            "general-screened",
            "admin-commands"
        ]
        
        for channel_name in channel_names:
            if not discord.utils.get(guild.channels, name=channel_name):
                try:
                    await guild.create_text_channel(channel_name)
                    logger.info(f"Created channel: {channel_name}")
                except Exception as e:
                    logger.error(f"Failed to create channel {channel_name}: {e}")
    
    async def on_member_join(self, member):
        """Called when a member joins the server"""
        logger.info(f"Member {member} joined the server")
        
        # Add user to database
        self.db.add_user(
            user_id=member.id,
            username=member.name,
            display_name=member.display_name
        )
        
        # Send welcome message
        embed = discord.Embed(
            title="Welcome to Rusk Media Community! 🎬",
            description="Thank you for joining our community! To get started, please complete our quick screening process.",
            color=0x00ff00
        )
        embed.add_field(
            name="What's Next?",
            value="Use `/start_screening` to begin the screening process and get access to relevant content channels.",
            inline=False
        )
        embed.set_footer(text="This helps us match you with the right content and communities!")
        
        try:
            await member.send(embed=embed)
        except discord.Forbidden:
            # User has DMs disabled, send to general channel
            general_channel = discord.utils.get(member.guild.channels, name="general-screened")
            if general_channel:
                await general_channel.send(f"{member.mention}", embed=embed)
    
    @app_commands.command(name="start_screening", description="Start the screening process")
    async def start_screening(self, interaction: discord.Interaction, campaign: str = "DISCOVERY_2025"):
        """Start the screening process for a user"""
        user_id = interaction.user.id
        
        # Check if user already completed screening
        user_data = self.db.get_user(user_id)
        if user_data and user_data.get('screening_completed'):
            embed = discord.Embed(
                title="Screening Already Completed ✅",
                description="You have already completed the screening process!",
                color=0x00ff00
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        # Start new screening session
        session_id = self.db.start_screening_session(user_id, campaign)
        if not session_id:
            await interaction.response.send_message("Failed to start screening session. Please try again.", ephemeral=True)
            return
        
        # Store active screening
        self.active_screenings[user_id] = {
            'session_id': session_id,
            'current_question': 'show_types',
            'answers': {}
        }
        
        # Send first question
        await self.send_screening_question(interaction, 'show_types')
    
    async def send_screening_question(self, interaction: discord.Interaction, question_key: str):
        """Send a screening question to the user"""
        question_data = self.screening_logic.questions.get(question_key)
        if not question_data:
            await interaction.response.send_message("Invalid question. Please try again.", ephemeral=True)
            return
        
        embed = discord.Embed(
            title=f"Question {self.get_question_number(question_key)}/7",
            description=question_data['question'],
            color=0x0099ff
        )
        
        # Create select menu
        options = []
        for option in question_data['options']:
            label = option['label']
            if 'emoji' in option:
                label = f"{option['emoji']} {label}"
            
            options.append(discord.SelectOption(
                label=label,
                value=option['value'],
                description=option.get('description', '')
            ))
        
        # Handle multi-select for show_types and genres
        if question_key in ['show_types', 'genres']:
            select = discord.ui.Select(
                placeholder="Select all that apply...",
                options=options,
                max_values=len(options)
            )
        else:
            select = discord.ui.Select(
                placeholder="Choose one option...",
                options=options,
                max_values=1
            )
        
        select.callback = lambda i: self.handle_screening_answer(i, question_key)
        
        view = discord.ui.View()
        view.add_item(select)
        
        if interaction.response.is_done():
            await interaction.followup.send(embed=embed, view=view, ephemeral=True)
        else:
            await interaction.response.send_message(embed=embed, view=view, ephemeral=True)
    
    async def handle_screening_answer(self, interaction: discord.Interaction, question_key: str):
        """Handle user's answer to a screening question"""
        user_id = interaction.user.id
        
        if user_id not in self.active_screenings:
            await interaction.response.send_message("No active screening session found. Please start again with `/start_screening`.", ephemeral=True)
            return
        
        # Get selected values
        selected_values = interaction.data['values']
        
        # Store answer
        self.active_screenings[user_id]['answers'][question_key] = selected_values
        self.db.update_screening_session(user_id, question_key, selected_values)
        
        # Get next question
        next_question = self.screening_logic.get_next_question(question_key)
        
        if next_question:
            # Continue with next question
            self.active_screenings[user_id]['current_question'] = next_question
            await self.send_screening_question(interaction, next_question)
        else:
            # Screening complete
            await self.complete_screening(interaction, user_id)
    
    async def complete_screening(self, interaction: discord.Interaction, user_id: int):
        """Complete the screening process and assign roles"""
        screening_data = self.active_screenings[user_id]['answers']
        
        # Validate screening data
        if not self.screening_logic.validate_screening_data(screening_data):
            await interaction.response.send_message("Screening incomplete. Please start again with `/start_screening`.", ephemeral=True)
            return
        
        # Determine roles to assign
        roles_to_assign = self.screening_logic.determine_roles(screening_data)
        
        # Get user segments
        user_segments = self.screening_logic.get_user_segments(screening_data)
        
        # Update database
        self.db.update_user_screening(user_id, screening_data, roles_to_assign)
        
        # Assign roles
        guild = interaction.guild
        member = guild.get_member(user_id)
        
        assigned_roles = []
        for role_name in roles_to_assign:
            role = discord.utils.get(guild.roles, name=role_name)
            if role and role not in member.roles:
                try:
                    await member.add_roles(role)
                    assigned_roles.append(role_name)
                except Exception as e:
                    logger.error(f"Failed to assign role {role_name}: {e}")
        
        # Send completion message
        embed = discord.Embed(
            title="Screening Complete! 🎉",
            description="Thank you for completing the screening process. You now have access to relevant content channels!",
            color=0x00ff00
        )
        
        # Add screening summary
        summary = self.screening_logic.get_screening_summary(screening_data)
        embed.add_field(name="Your Profile", value=summary, inline=False)
        
        # Add assigned roles
        if assigned_roles:
            embed.add_field(name="Assigned Roles", value="\n".join([f"✅ {role}" for role in assigned_roles]), inline=False)
        
        # Add next steps
        embed.add_field(
            name="What's Next?",
            value="You now have access to content channels based on your preferences. Check out the relevant channels in the server!",
            inline=False
        )
        
        await interaction.response.send_message(embed=embed, ephemeral=True)
        
        # Clean up active screening
        del self.active_screenings[user_id]
        
        # Send welcome message to appropriate channels
        await self.send_welcome_to_channels(member, user_segments)
    
    async def send_welcome_to_channels(self, member: discord.Member, user_segments: Dict):
        """Send welcome message to relevant channels based on user segments"""
        guild = member.guild
        
        # Send to primary content channel
        primary_cohort = user_segments.get('primary_cohort', 'mixed')
        if primary_cohort != 'mixed':
            channel_name = f"{primary_cohort}-content"
            channel = discord.utils.get(guild.channels, name=channel_name)
            if channel:
                embed = discord.Embed(
                    title="New Community Member! 🎉",
                    description=f"Welcome {member.mention} to our {primary_cohort} community!",
                    color=0x0099ff
                )
                await channel.send(embed=embed)
        
        # Send to general channel
        general_channel = discord.utils.get(guild.channels, name="general-screened")
        if general_channel:
            embed = discord.Embed(
                title="New Screened Member! 🎬",
                description=f"Welcome {member.mention} to the Rusk Media community!",
                color=0x00ff00
            )
            await general_channel.send(embed=embed)
    
    def get_question_number(self, question_key: str) -> int:
        """Get the question number for display"""
        question_order = [
            'show_types', 'city', 'age_group', 'gender', 
            'genres', 'viewing_platform', 'education'
        ]
        try:
            return question_order.index(question_key) + 1
        except ValueError:
            return 1
    
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
    
    @app_commands.command(name="admin_reset_user", description="Reset a user's screening data (Admin only)")
    @app_commands.default_permissions(administrator=True)
    async def admin_reset_user(self, interaction: discord.Interaction, user: discord.Member):
        """Reset a user's screening data"""
        # This would require additional database methods
        await interaction.response.send_message(f"Reset functionality for {user.mention} would be implemented here.", ephemeral=True)

# Bot instance
bot = RuskMediaBot()

if __name__ == "__main__":
    if not DISCORD_TOKEN:
        logger.error("DISCORD_TOKEN not found in environment variables")
        exit(1)
    
    bot.run(DISCORD_TOKEN)

