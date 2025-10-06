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
        intents.presences = False
        
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
        logger.info(f'{self.user} has connected to Discord!')
        logger.info(f'Bot is in {len(self.guilds)} guild(s)')
        
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
    
    async def create_role_if_not_exists(self, guild: discord.Guild, role_name: str) -> Optional[discord.Role]:
        """Create a role if it doesn't exist"""
        role = discord.utils.get(guild.roles, name=role_name)
        if not role:
            try:
                role = await guild.create_role(name=role_name)
                logger.info(f"Created role: {role_name}")
            except Exception as e:
                logger.error(f"Failed to create role {role_name}: {e}")
        return role
    
    async def create_channel_if_not_exists(self, guild: discord.Guild, channel_name: str, role: discord.Role = None) -> Optional[discord.TextChannel]:
        """Create a private channel if it doesn't exist"""
        channel = discord.utils.get(guild.channels, name=channel_name)
        if not channel:
            try:
                # Create private channel - only visible to users with the specific role
                overwrites = {
                    guild.default_role: discord.PermissionOverwrite(read_messages=False),
                    guild.me: discord.PermissionOverwrite(read_messages=True)
                }
                
                if role:
                    overwrites[role] = discord.PermissionOverwrite(read_messages=True)
                
                channel = await guild.create_text_channel(channel_name, overwrites=overwrites)
                logger.info(f"Created channel: {channel_name}")
            except Exception as e:
                logger.error(f"Failed to create channel {channel_name}: {e}")
        return channel
    
    async def on_member_join(self, member):
        """Called when a member joins the server - AUTOMATICALLY START SCREENING"""
        logger.info(f"Member {member} joined the server - Auto-starting screening")
        
        # Check if user already completed screening
        user_data = self.db.get_user(member.id)
        if user_data and user_data.get('screening_completed'):
            logger.info(f"User {member} already completed screening")
            return
        
        # Add user to database
        self.db.add_user(
            user_id=member.id,
            username=member.name,
            display_name=member.display_name,
            campaign="AUTO_JOIN"
        )
        
        # Start screening session
        session_id = self.db.start_screening_session(member.id, "AUTO_JOIN")
        if not session_id:
            logger.error(f"Failed to start screening session for {member}")
            return
        
        # Store active screening
        self.active_screenings[member.id] = {
            'session_id': session_id,
            'current_question': 'gender',  # NEW: Start with gender
            'answers': {}
        }
        
        # Send welcome message with first question automatically
        embed = discord.Embed(
            title="Welcome to Rusk Media Community! 🎬",
            description="Thank you for joining! Please complete this quick 4-question screening to get access to your personalized content channels.",
            color=0x00ff00
        )
        embed.set_footer(text="This helps us match you with the right content and communities!")
        
        try:
            await member.send(embed=embed)
            await asyncio.sleep(1)
            await self.send_screening_question_dm(member, 'gender')
        except discord.Forbidden:
            logger.warning(f"Could not send DM to {member}, user has DMs disabled")
            general_channel = discord.utils.get(member.guild.channels, name="general")
            if general_channel:
                await general_channel.send(
                    f"{member.mention} Welcome! Please enable DMs to complete the screening process."
                )
    
    async def send_screening_question_dm(self, member: discord.Member, question_key: str):
        """Send a screening question via DM"""
        question_data = self.screening_logic.questions.get(question_key)
        if not question_data:
            logger.error(f"Invalid question key: {question_key}")
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
            if 'emoji' in option:
                label = f"{option['emoji']} {label}"
            
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
        except discord.Forbidden:
            logger.error(f"Cannot send DM to {member}")
    
    async def handle_screening_answer_dm(self, interaction: discord.Interaction, question_key: str, member: discord.Member):
        """Handle user's answer to a screening question in DM"""
        user_id = member.id
        
        if user_id not in self.active_screenings:
            await interaction.response.send_message("No active screening session found. Please rejoin the server to restart.", ephemeral=True)
            return
        
        # Get selected values
        selected_values = interaction.data['values']
        
        # Store answer
        self.active_screenings[user_id]['answers'][question_key] = selected_values
        self.db.update_screening_session(user_id, question_key, selected_values)
        
        # Send acknowledgment
        await interaction.response.send_message(f"✅ Answer recorded!", ephemeral=True)
        
        # Get next question
        next_question = self.screening_logic.get_next_question(question_key)
        
        if next_question:
            # Continue with next question
            self.active_screenings[user_id]['current_question'] = next_question
            await asyncio.sleep(0.5)
            await self.send_screening_question_dm(member, next_question)
        else:
            # Screening complete
            await self.complete_screening_dm(member, user_id)
    
    async def complete_screening_dm(self, member: discord.Member, user_id: int):
        """Complete the screening process and assign roles"""
        screening_data = self.active_screenings[user_id]['answers']
        
        # Validate screening data
        if not self.screening_logic.validate_screening_data(screening_data):
            await member.send("❌ Screening incomplete. Please rejoin the server to restart.")
            return
        
        # Determine roles and channels to create
        role_channel_data = self.screening_logic.determine_roles_and_channels(screening_data)
        roles_to_create = role_channel_data['roles']
        channels_to_create = role_channel_data['channels']
        
        # Get user segments
        user_segments = self.screening_logic.get_user_segments(screening_data)
        
        # Update database
        self.db.update_user_screening(user_id, screening_data, roles_to_create)
        
        # Create and assign roles/channels
        guild = member.guild
        assigned_roles = []
        created_channels = []
        
        for i, role_name in enumerate(roles_to_create):
            # Create role if doesn't exist
            role = await self.create_role_if_not_exists(guild, role_name)
            
            if role:
                # Assign role to user
                if role not in member.roles:
                    try:
                        await member.add_roles(role)
                        assigned_roles.append(role_name)
                        logger.info(f"Assigned role {role_name} to {member}")
                    except Exception as e:
                        logger.error(f"Failed to assign role {role_name}: {e}")
                
                # Create corresponding channel if doesn't exist
                if i < len(channels_to_create):
                    channel_name = channels_to_create[i]
                    channel = await self.create_channel_if_not_exists(guild, channel_name, role)
                    if channel:
                        created_channels.append(channel_name)
        
        # Send completion message
        embed = discord.Embed(
            title="Screening Complete! 🎉",
            description="Thank you for completing the screening process. You now have access to your personalized content channels!",
            color=0x00ff00
        )
        
        # Add screening summary
        summary = self.screening_logic.get_screening_summary(screening_data)
        embed.add_field(name="Your Profile", value=summary, inline=False)
        
        # Add assigned roles
        if assigned_roles:
            embed.add_field(name="Your Groups", value="\n".join([f"✅ {role}" for role in assigned_roles]), inline=False)
        
        # Add channels
        if created_channels:
            embed.add_field(name="Your Channels", value="\n".join([f"📺 #{channel}" for channel in created_channels]), inline=False)
        
        # Add next steps
        embed.add_field(
            name="What's Next?",
            value="Head back to the Rusk Media server! You now have access to your personalized channels.",
            inline=False
        )
        
        await member.send(embed=embed)
        
        # Clean up active screening
        del self.active_screenings[user_id]
        
        # Send welcome message to channels
        for channel_name in created_channels:
            channel = discord.utils.get(guild.channels, name=channel_name)
            if channel:
                embed = discord.Embed(
                    title="New Member! 🎉",
                    description=f"Welcome {member.mention} to this group!",
                    color=0x0099ff
                )
                try:
                    await channel.send(embed=embed)
                except:
                    pass
    
    def get_question_number(self, question_key: str) -> int:
        """Get the question number for display"""
        question_order = ['gender', 'age_group', 'show_types', 'city']
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

# Bot instance
bot = RuskMediaBot()

if __name__ == "__main__":
    if not DISCORD_TOKEN:
        logger.error("DISCORD_TOKEN not found in environment variables")
        exit(1)
    
    bot.run(DISCORD_TOKEN)
