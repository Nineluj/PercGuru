from discord.ext import commands
import discord
import logging

from app.cogs.base import BaseCog
from app.models.core import Team
from app.models.config import Guild
from typing import Dict

log = logging.getLogger(__name__)


class ConfigurationCog(
    BaseCog,
    name="Configuration",
    description="""Commands for configuring the bot"""
):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # V Not using this at the moment
        # Maps <id of failed user command> -> <id of bot response to that command>
        # Could clear this periodically but should be ok.
        # Ok to just be here since don't care about persistence between sessions and this is
        # the only cog that consumes text commands
        self.sync = kwargs['sync_fn']
        self.recently_failed: Dict[int, discord.Message] = dict()

    """
    Commands for configuring the bot
    """

    @commands.group(name="config")
    @commands.is_owner()
    async def config(self, ctx):
        pass

    async def channel_leave(self, channel: discord.TextChannel):
        return await self.state.remove_channel(channel.guild.id, channel.id)

    async def channel_join(self, channel: discord.TextChannel):
        return await self.state.add_channel(channel.guild.id, channel.id)

    async def channels_list(self, guild: discord.Guild):
        return await self.state.list_channels(guild.id)

    async def channels_clear(self, guild: discord.Guild):
        return await self.state.clear_channels(guild.id)

    def channels_to_str(self, channels):
        lines = []
        for whitelisted_chan in channels:
            name = self.bot.get_channel(whitelisted_chan.channel_id).name
            lines.append(f"- {name} ({whitelisted_chan.channel_id})")
        return "\n".join(lines)

    @config.command(
        name="channel",
        help="""Adds or removes the listeners for this channel.
        Options are `join` or `leave`. No arguments also joins."""
    )
    @commands.is_owner()
    async def config_listen_channel(self, ctx, *args):
        if len(args) == 0 or args[0] == 'join':
            result = await self.channel_join(ctx.message.channel)
        elif args[0] == 'leave':
            result = await self.channel_leave(ctx.message.channel)
        elif args[0] == 'clear':
            result = await self.channels_clear(ctx.guild)
        elif args[0] == 'list':
            channels, result = await self.channels_list(ctx.guild)
            if len(channels) == 0:
                await ctx.send("Not listening on any channels")
                return
            if result:
                await ctx.send("Currently listening on these:\n" + self.channels_to_str(channels))
                return
        elif args[0] == 'sync':
            await ctx.send("Sync in progress, likely to take a while. "
                           "Don't register any new fights or participation "
                           "lest you want to have to run this again...")
            await self.sync(ctx.channel, full=len(args) == 2 and args[1] == 'full')
            await ctx.send("Done with sync")
            return
        else:
            await self.error(ctx.channel, "Did not understand the command")
            return

        if result:
            await self.ack(ctx.message, keep=True)
        else:
            await self.error(ctx.channel, "Could not complete operation")

    @config.command(name="guilds")
    @commands.is_owner()
    async def configure_guild_teams(self, ctx, *args):
        """
        Sets the guilds for this discord server based on the names of the reacts to the given message
        """

        if len(args) == 0:
            await self.error(ctx.channel, "Missing arguments. Options are (list, set)")
            return
        elif args[0] == 'list':
            emojis = await self.get_guild_team_emojis_names(ctx.guild.id)
            await ctx.send("Registered guilds are:\n" + "\n".join(emojis))
        elif args[0] == 'set':
            await self.configure_set(ctx, *args)
        else:
            await ctx.send("Unknown subcommand")

    async def configure_set(self, ctx, *args):
        if len(args) != 2:
            await self.error(ctx.channel, "Use: set <message_id>")
            return

        message_id = args[1]
        try:
            reacted_message = await ctx.fetch_message(message_id)
        except discord.NotFound:
            await ctx.send("Can't find the message with that ID. Try again.")
            return False
        except discord.Forbidden:
            await ctx.send("Can't access that message.")
            return False
        except discord.HTTPException:
            await ctx.send("Womp womp")
            return False

        result = await self.state.set_react_message(ctx.guild.id, ctx.channel.id, reacted_message.id)
        if result:
            await self.ack(ctx.message, keep=True)
            await ctx.send("Reaction message updated successfully.")
        else:
            await self.error(ctx.channel, "Unable to use that message to configure the teams")

        # Set up the team models if they don't exist
        reacts = await self.get_guild_team_emojis_names(ctx.guild.id)

        for team_name in reacts:
            server_id = ctx.guild.id
            server_inst = await Guild.get(id=server_id)
            team_exists = await Team.exists(name=team_name, server=server_inst)

            if not team_exists:
                created_team = await Team.create(name=team_name, server=server_inst)
                if not created_team:
                    log.warning(f"Wasn't able to create team with name {team_name} for guild {server_id}")
                else:
                    log.info(f"Created team with name {team_name} for guild {server_id}")

        log.info(f"Done initializing teams")
