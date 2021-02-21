from discord.ext import commands
import discord
import logging
from app.models.core import Fight
from tortoise.exceptions import DoesNotExist

from app.cogs.base import BaseCog

log = logging.getLogger(__name__)


class FightRegistrationCog(
    BaseCog,
    name="Fights"
):
    def __init__(self, *args, react_handler=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.react_handler = react_handler

    @commands.command("sync")
    async def sync_data(self, ctx, *args):
        """
        Syncs the fight data on this channel
        """
        await ctx.send("Sync in progress, likely to take a while. "
                       "Don't register any new fights or participation "
                       "lest you want to have to run this again...")

        await self.process_backlog(ctx.channel, full=len(args) == 1 and args[0] == 'full')
        await ctx.send("Done with sync")

    @commands.Cog.listener()
    async def on_raw_message_delete(self, payload):
        # message = await self.bot.get_channel(payload.channel_id).fetch_message(payload.message_id)
        # if self.is_bot(payload.member.id):
        #     return

        if not await self.state.is_whitelisted_channel(payload.guild_id, payload.channel_id):
            return

        message_id = payload.message_id
        channel = self.bot.get_channel(payload.channel_id)

        try:
            fight = await Fight.get(id=payload.message_id)
            await fight.delete()
            await channel.send("Deleted information about fight")
        except DoesNotExist:
            log.info(f"Message with id {message_id} deleted but not stored as fight. Ignoring.")

    @commands.Cog.listener()
    async def on_message(self, message, ack=True):
        if message.author.bot:
            return
        if not await self.state.is_whitelisted_channel(message.guild.id, message.channel.id):
            return

        if len(message.attachments) == 1 and message.attachments[0].filename.endswith(".png"):
            if not await Fight.exists(id=message.id):
                await Fight.create(id=message.id, recorded=message.created_at)
                log.info(f"Created fight uploaded by {message.author.nick or message.author.name}")

            if len(message.reactions) != 0:
                log.info("Processed message already has reacts, checking those")
                for react in message.reactions:
                    emoji = react.emoji

                    if hasattr(emoji, 'name'):
                        emoji_str = emoji.name
                    else:
                        emoji_str = emoji

                    async for member in react.users():
                        await self.react_handler(emoji_str, member, message.channel.id, message.id, ack=False)

            if ack:
                await self.ack(message)

    async def process_backlog(self, channel: discord.TextChannel, full=False):
        last_fight = await Fight.all().order_by('-recorded').first()

        if full or not last_fight:
            start_at = None
        else:
            start_at = last_fight.recorded.replace(tzinfo=None)

        async for message in channel.history(after=start_at, limit=None):
            await self.on_message(message, ack=False)
