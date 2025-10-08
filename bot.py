import discord
from discord.ext import commands
from discord import app_commands
import asyncio
import logging
from datetime import datetime
from typing import Optional, Dict, List, Any
import os

# Try to load from railway_config first, then fall back to config
try:
    from railway_config import *
    print("Using Railway configuration")
except ImportError:
    from config import *
    print("Using local configuration")
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

    async def start_screening_flow(self, member: discord.Member, campaign_label: str) -> bool:
        """Create DB records and attempt to DM the user the first question.
        Returns True if a DM was successfully sent, False if DM failed.
        """
        # Prevent duplicate screening sessions
        if member.id in self.active_screenings:
            logger.info(f"User {member} already has an active screening session, skipping")
            return True
            
        # Ensure DB user exists
        self.db.add_user(
            user_id=member.id,
            username=member.name,
            display_name=member.display_name,
            campaign=campaign_label
        )

        # Start screening session
        session_id = self.db.start_screening_session(member.id, campaign_label)
        if not session_id:
            logger.error(f"Failed to start screening session for {member}")
            return False

        # Track active screening in-memory
        self.active_screenings[member.id] = {
            'session_id': session_id,
            'current_question': 'gender',
            'answers': {}
        }

        # Send first question directly (no separate welcome message)
        try:
            # Add small delay to prevent rate limiting when multiple users join quickly
            await asyncio.sleep(1)
            await self.send_screening_question_dm(member, 'gender')
            return True
        except discord.Forbidden:
            logger.warning(f"Could not DM {member}. DMs likely disabled.")
            return False
        except discord.HTTPException as e:
            if e.status == 400 and e.code == 40003:
                logger.warning(f"Rate limited when DMing {member}. Will retry later.")
                # Could implement retry logic here if needed
                return False
            else:
                logger.error(f"HTTP error when DMing {member}: {e}")
                return False
    
    async def setup_hook(self):
        """Called when the bot is starting up"""
        try:
            # Ensure application commands are added to the command tree
            try:
                # Register admin_stats if present
                if hasattr(self, 'admin_stats'):
                    if GUILD_ID:
                        self.tree.add_command(self.admin_stats, guild=discord.Object(id=GUILD_ID))
                    else:
                        self.tree.add_command(self.admin_stats)
                # Register start_screening if present
                if hasattr(self, 'start_screening'):
                    if GUILD_ID:
                        self.tree.add_command(self.start_screening, guild=discord.Object(id=GUILD_ID))
                    else:
                        self.tree.add_command(self.start_screening)
            except Exception as e:
                logger.error(f"Failed to add app commands: {e}")

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
        
        # CRITICAL: Fix all channel permissions on startup to ensure security
        for guild in self.guilds:
            try:
                await self.fix_channel_permissions(guild)
                logger.info(f"Fixed channel permissions for guild: {guild.name}")
            except Exception as e:
                logger.error(f"Failed to fix channel permissions for {guild.name}: {e}")
    
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
        """Create a private channel if it doesn't exist, or fix permissions if it does"""
        channel = discord.utils.get(guild.channels, name=channel_name)
        
        # Define secure permissions
        overwrites = {
            guild.default_role: discord.PermissionOverwrite(read_messages=False),  # Everyone can't see
            guild.me: discord.PermissionOverwrite(read_messages=True, send_messages=True)  # Bot can see and send
        }
        
        if role:
            overwrites[role] = discord.PermissionOverwrite(read_messages=True, send_messages=True)  # Role can see and send
        
        if not channel:
            # Create new channel with secure permissions
            try:
                channel = await guild.create_text_channel(channel_name, overwrites=overwrites)
                logger.info(f"Created secure channel: {channel_name}")
            except Exception as e:
                logger.error(f"Failed to create channel {channel_name}: {e}")
        else:
            # Channel exists - Apply secure permissions directly
            try:
                await channel.edit(overwrites=overwrites)
                logger.info(f"SECURED: Applied secure permissions to existing channel: {channel_name}")
            except Exception as e:
                logger.error(f"Failed to fix permissions for channel {channel_name}: {e}")
        
        return channel
    
    async def fix_channel_permissions(self, guild: discord.Guild):
        """Fix permissions for all hierarchical channels to ensure proper access control"""
        logger.info("Checking and fixing channel permissions...")
        
        # Find all hierarchical channels (channels with 3+ hyphens)
        hierarchical_channels = []
        for channel in guild.channels:
            if isinstance(channel, discord.TextChannel) and channel.name.count('-') >= 3:
                hierarchical_channels.append(channel)
        
        # Also find channels that might be user-specific (contain gender-age-content-tier pattern)
        user_specific_channels = []
        for channel in guild.channels:
            if isinstance(channel, discord.TextChannel):
                # Check if channel name matches pattern: gender-age-content-tier
                parts = channel.name.split('-')
                if len(parts) >= 4:
                    # Check if it looks like a user-specific channel
                    if parts[0] in ['male', 'female', 'non_binary'] and parts[3] in ['tier1', 'tier2', 'tier3']:
                        user_specific_channels.append(channel)
        
        # Combine and deduplicate
        all_channels_to_fix = list(set(hierarchical_channels + user_specific_channels))
        
        for channel in all_channels_to_fix:
            try:
                # Get the role that should have access to this channel
                channel_role = discord.utils.get(guild.roles, name=channel.name)
                
                # Debug: Log current permissions
                logger.info(f"Channel: {channel.name}")
                logger.info(f"  - Category: {channel.category.name if channel.category else 'None'}")
                logger.info(f"  - Current overwrites: {len(channel.overwrites)}")
                for target, overwrite in channel.overwrites.items():
                    logger.info(f"    - {target}: read={overwrite.read_messages}, send={overwrite.send_messages}")
                
                if channel_role:
                    # CRITICAL FIX: Set permissions in one step to avoid making channels public
                    overwrites = {
                        guild.default_role: discord.PermissionOverwrite(
                            read_messages=False, 
                            send_messages=False,
                            view_channel=False,
                            connect=False,
                            speak=False
                        ),  # Everyone explicitly denied everything
                        guild.me: discord.PermissionOverwrite(
                            read_messages=True, 
                            send_messages=True,
                            view_channel=True,
                            manage_channels=True,
                            manage_permissions=True
                        ),  # Bot has full access
                        channel_role: discord.PermissionOverwrite(
                            read_messages=True, 
                            send_messages=True,
                            view_channel=True
                        )  # Only this specific role can access
                    }
                    
                    await channel.edit(overwrites=overwrites)
                    logger.info(f"SECURED: Channel {channel.name} now ONLY accessible to {channel_role.name}")
                else:
                    logger.warning(f"Could not find role for channel: {channel.name} - securing channel anyway")
                    # Even if no role exists, secure the channel so no one can see it
                    overwrites = {
                        guild.default_role: discord.PermissionOverwrite(
                            read_messages=False, 
                            send_messages=False,
                            view_channel=False
                        ),
                        guild.me: discord.PermissionOverwrite(
                            read_messages=True, 
                            send_messages=True,
                            view_channel=True
                        )
                    }
                    await channel.edit(overwrites=overwrites)
                    logger.info(f"Secured channel without role: {channel.name} - NO ONE can access")
                    
            except Exception as e:
                logger.error(f"Failed to fix permissions for channel {channel.name}: {e}")
        
        logger.info(f"Completed permission fix for {len(all_channels_to_fix)} channels")
    
    async def on_member_join(self, member):
        """Called when a member joins the server - AUTOMATICALLY START SCREENING"""
        logger.info(f"Member {member} joined the server - Auto-starting screening")
        
        # Check if user already completed screening
        user_data = self.db.get_user(member.id)
        if user_data and user_data.get('screening_completed'):
            logger.info(f"User {member} already completed screening")
            return
        # Attempt DM-based flow
        dm_ok = await self.start_screening_flow(member, "AUTO_JOIN")
        if not dm_ok:
            logger.warning(f"Could not send DM to {member}, user has DMs disabled")
            # Prefer an explicitly configured welcome channel if provided
            welcome_channel_name = os.getenv('WELCOME_CHANNEL', '').strip()
            channel_to_use = None
            if welcome_channel_name:
                channel_to_use = discord.utils.get(member.guild.text_channels, name=welcome_channel_name)
            # Fallback to system channel if available
            if not channel_to_use:
                channel_to_use = member.guild.system_channel
            # Final fallback to a channel named "general" if present
            if not channel_to_use:
                channel_to_use = discord.utils.get(member.guild.text_channels, name="general")
            if channel_to_use:
                view = StartScreeningView(self)
                await channel_to_use.send(
                    f"{member.mention} Welcome! Your DMs seem disabled. Enable DMs for this server and press the button to begin.",
                    view=view
                )
    
    async def send_screening_question_dm(self, member: discord.Member, question_key: str):
        """Send a screening question via DM"""
        question_data = self.screening_logic.questions.get(question_key)
        if not question_data:
            logger.error(f"Invalid question key: {question_key}")
            return
        
        # For the first question, include welcome message
        if question_key == 'gender':
            embed = discord.Embed(
                title="Welcome to Rusk Media Community! 🎬",
                description="Thank you for joining! Please complete this quick 4-question screening to get access to your personalized content channels.\n\n**Question 1/4:** " + question_data['question'],
                color=0x00ff00
            )
            embed.set_footer(text="This helps us match you with the right content and communities!")
        else:
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
        
        # Debug: Log what the user selected
        logger.info(f"User {member} selected for {question_key}: {selected_values}")
        
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
        
        # Debug: Log the user's screening data
        logger.info(f"Screening data for {member}: {screening_data}")
        logger.info(f"Roles to create for {member}: {roles_to_create}")
        
        # Debug: Log what the user currently has
        current_roles = [role.name for role in member.roles]
        logger.info(f"Current roles for {member} before assignment: {current_roles}")
        
        # Get user segments
        user_segments = self.screening_logic.get_user_segments(screening_data)
        
        # Update database
        self.db.update_user_screening(user_id, screening_data, roles_to_create)
        
        # Create and assign roles/channels
        guild = member.guild
        assigned_roles = []
        created_channels = []
        
        # First, remove any old hierarchical roles that don't match the user's current gender
        user_gender = screening_data.get('gender', ['unknown'])[0]
        old_roles_to_remove = []
        for role in member.roles:
            role_name = role.name
            # Check if this is a hierarchical role (contains hyphens and is not "Screened User")
            if role_name != "Screened User" and role_name.count('-') >= 2:
                # Remove if:
                # 1. It's not in our new roles list, OR
                # 2. It's a role for a different gender than the user's current gender
                role_gender = role_name.split('-')[0]  # Get the gender part of the role name
                should_remove = (
                    role_name not in roles_to_create or 
                    (role_gender != user_gender and role_gender in ['male', 'female', 'non_binary'])
                )
                
                if should_remove:
                    old_roles_to_remove.append(role)
                    logger.info(f"Will remove old role: {role_name} from {member} (reason: {'not in new roles' if role_name not in roles_to_create else 'wrong gender'})")
        
        # Remove old roles
        if old_roles_to_remove:
            try:
                await member.remove_roles(*old_roles_to_remove)
                logger.info(f"Removed {len(old_roles_to_remove)} old roles from {member}")
            except Exception as e:
                logger.error(f"Failed to remove old roles: {e}")
        
        for i, role_name in enumerate(roles_to_create):
            # CRITICAL CHECK: Ensure this role is actually in our roles_to_create list
            if role_name not in roles_to_create:
                logger.error(f"CRITICAL ERROR: Role {role_name} not in roles_to_create list!")
                continue
            
            # Safety check: Ensure role gender matches user gender
            if role_name != "Screened User" and role_name.count('-') >= 2:
                role_gender = role_name.split('-')[0]
                if role_gender != user_gender:
                    logger.error(f"CRITICAL ERROR: Attempted to assign {role_name} (gender: {role_gender}) to user {member} (gender: {user_gender})")
                    continue  # Skip this role assignment
            
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
                else:
                    logger.info(f"User {member} already has role {role_name}")
                
                # Create corresponding channel if doesn't exist
                if i < len(channels_to_create):
                    channel_name = channels_to_create[i]
                    channel = await self.create_channel_if_not_exists(guild, channel_name, role)
                    if channel:
                        created_channels.append(channel_name)
        
        # Debug: Log final roles after assignment
        final_roles = [role.name for role in member.roles]
        logger.info(f"Final roles for {member} after assignment: {final_roles}")
        
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
        logger.info(f"Cleaned up screening session for {member}")
        
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
        question_order = ['gender', 'age_group', 'show_types', 'city_tier']
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

    @app_commands.command(name="start_screening", description="Start the onboarding screening via DM")
    async def start_screening(self, interaction: discord.Interaction):
        """Lets a user manually start the screening if they didn't receive a DM on join"""
        member = interaction.user
        dm_ok = await self.start_screening_flow(member, "MANUAL_START")
        if dm_ok:
            await interaction.response.send_message("📩 Check your DMs for the screening questions!", ephemeral=True)
        else:
            await interaction.response.send_message("❗ I couldn't DM you. Please enable DMs for this server and run /start_screening again.", ephemeral=True)
    
    @app_commands.command(name="fix_permissions", description="Fix channel permissions (Admin only)")
    async def fix_permissions(self, interaction: discord.Interaction):
        """Fix permissions for all hierarchical channels"""
        # Check if user is admin
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message("❌ You need administrator permissions to use this command.", ephemeral=True)
            return
        
        await interaction.response.defer(ephemeral=True)
        
        try:
            await self.fix_channel_permissions(interaction.guild)
            await interaction.followup.send("✅ Channel permissions have been fixed!", ephemeral=True)
        except Exception as e:
            logger.error(f"Failed to fix permissions: {e}")
            await interaction.followup.send(f"❌ Failed to fix permissions: {str(e)}", ephemeral=True)
    
    @app_commands.command(name="check_user_channels", description="Check what channels a user can see (Admin only)")
    async def check_user_channels(self, interaction: discord.Interaction, user: discord.Member):
        """Check what channels a specific user can see"""
        # Check if user is admin
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message("❌ You need administrator permissions to use this command.", ephemeral=True)
            return
        
        await interaction.response.defer(ephemeral=True)
        
        try:
            # Get all hierarchical channels
            hierarchical_channels = []
            for channel in interaction.guild.channels:
                if isinstance(channel, discord.TextChannel) and channel.name.count('-') >= 3:
                    hierarchical_channels.append(channel)
            
            # Check which channels the user can see
            visible_channels = []
            for channel in hierarchical_channels:
                if channel.permissions_for(user).read_messages:
                    visible_channels.append(channel.name)
            
            # Get user's roles
            user_roles = [role.name for role in user.roles if role.name != "@everyone"]
            
            embed = discord.Embed(
                title=f"Channel Access for {user.display_name}",
                color=0x0099ff
            )
            embed.add_field(
                name="User's Roles", 
                value="\n".join(user_roles) if user_roles else "No roles", 
                inline=False
            )
            embed.add_field(
                name="Visible Channels", 
                value="\n".join(visible_channels) if visible_channels else "No channels visible", 
                inline=False
            )
            embed.add_field(
                name="Total Hierarchical Channels", 
                value=str(len(hierarchical_channels)), 
                inline=True
            )
            
            await interaction.followup.send(embed=embed, ephemeral=True)
            
        except Exception as e:
            logger.error(f"Failed to check user channels: {e}")
            await interaction.followup.send(f"❌ Failed to check channels: {str(e)}", ephemeral=True)

# Bot instance
bot = RuskMediaBot()

if __name__ == "__main__":
    # Debug: Print all environment variables
    logger.info("Environment variables:")
    for key, value in os.environ.items():
        if 'DISCORD' in key or 'GUILD' in key or 'DATABASE' in key or 'WELCOME' in key:
            logger.info(f"{key}: {'*' * len(value) if value else 'NOT SET'}")
    
    if not DISCORD_TOKEN:
        logger.error("DISCORD_TOKEN not found in environment variables")
        logger.error(f"Available env vars: {list(os.environ.keys())}")
        exit(1)
    
    logger.info("Starting Discord bot...")
    bot.run(DISCORD_TOKEN)


class StartScreeningView(discord.ui.View):
    """View with a button that retries starting the screening via DM."""
    def __init__(self, bot: RuskMediaBot):
        super().__init__(timeout=300)
        self.bot_ref = bot

    @discord.ui.button(label="Start Screening", style=discord.ButtonStyle.primary)
    async def start(self, interaction: discord.Interaction, button: discord.ui.Button):
        member = interaction.user
        dm_ok = await self.bot_ref.start_screening_flow(member, "BUTTON_START")
        if dm_ok:
            await interaction.response.send_message("📩 Sent! Please check your DMs to begin.", ephemeral=True)
        else:
            await interaction.response.send_message("❗ I couldn't DM you. Enable DMs for this server and press the button again.", ephemeral=True)
