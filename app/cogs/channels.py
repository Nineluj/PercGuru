from discord.ext import commands
import logging

from app.util import send_embed
from app.cogs.base import BaseCog

log = logging.getLogger(__name__)


class ChannelsCog(
    BaseCog,
    name="Channels",
    description="""Commands for managing channel listening"""
):
    @commands.group(
        name="channel",
        help="Manage the channels that the bot listens on",
        invoke_without_command=True
    )
    @commands.is_owner()
    async def config_guild_channels(self, ctx):
        await ctx.invoke(self.config_guild_channels_list)

    @config_guild_channels.command(name="join")
    async def config_guild_channels_join(self, ctx):
        """
        Joins the channel in which this message was sent
        """
        channel = ctx.message.channel
        result = await self.state.add_channel(channel.guild.id, channel.id)

        if result:
            await self.ack(ctx.message, keep=True)

    @config_guild_channels.command(name="leave")
    async def config_guild_channels_leave(self, ctx):
        """
        Leaves the channel in which this message was sent
        """
        channel = ctx.message.channel
        result = await self.state.remove_channel(channel.guild.id, channel.id)

        if result:
            await self.ack(ctx.message, keep=True)

    @config_guild_channels.command(name="list")
    async def config_guild_channels_list(self, ctx):
        """
        Lists the channels that the bot is listening on in this server
        """
        channels = await self.state.list_channels(ctx.guild.id)

        if len(channels) == 0:
            await ctx.send("Not listening on any channels")
        else:
            await send_embed(ctx, "Channels", self.channels_to_str(channels))

    @config_guild_channels.command(name="clear")
    async def config_guild_channels_clear(self, ctx):
        """
        Stops listening on all channels for this server
        """
        result = await self.state.clear_channels(ctx.guild.id)
        if result:
            await self.ack(ctx.message, keep=True)
        else:
            await self.error(ctx.channel, "Unable to clear the channels")

    def channels_to_str(self, channels):
        lines = []
        for whitelisted_channel_id in channels:
            name = self.bot.get_channel(whitelisted_channel_id).name
            lines.append(f"- {name} ({whitelisted_channel_id})")
        return "\n".join(lines)
