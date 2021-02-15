from discord.ext import commands
import discord

from app.cogs.base import BaseCog
from typing import Dict


class ConfigurationCog(
    BaseCog,
    name="Configuration",
    description="""Commands for configuring the bot"""
):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Maps <id of failed user command> -> <id of bot response to that command>
        # Could clear this periodically but should be ok.
        # Ok to just be here since don't care about persistence between sessions and this is
        # the only cog that consumes text commands
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
            await self.error(ctx.channel, "Missing arguments")
            return
        elif args[0] == 'list':
            emojis = await self.get_guild_team_emojis(ctx.guild.id)
            await ctx.send("Registered guilds are:\n" + "\n".join(emojis))
        elif args[0] == 'set':
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
