from discord.ext import commands
import discord
import logging
from datetime import datetime
from app.models.core import Fight, Player, Team
from tortoise.exceptions import DoesNotExist

from app.cogs.base import BaseCog

log = logging.getLogger(__name__)


class FightRegistrationCog(BaseCog):
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
    async def on_message(self, message):
        if self.is_bot(message.author.id):
            return
        if not await self.state.is_whitelisted_channel(message.guild.id, message.channel.id):
            return

        if len(message.attachments) == 1 and message.attachments[0].filename.endswith(".png"):
            await Fight.create(id=message.id, recorded=message.created_at)
            log.info(f"Created fight uploaded by {message.author.nick or message.author.name}")
            await self.ack(message)

        if len(message.reactions) != 0:
            log.info("Processed message already has reacts, checking those")
            for react in message.reactions:
                pass
                # await self.process_reacts(message, react)

    async def process_backlog(self, channel: discord.TextChannel, full=False):
        last_fight = await Fight.all().order_by('-recorded').first()

        if full or not last_fight:
            start_at = datetime.min
        else:
            start_at = last_fight.recorded

        async for message in channel.history(after=start_at, limit=None):
            await self.on_message(message)

