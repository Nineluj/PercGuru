from discord.ext import commands
import logging
from app.models.core import Fight, Player, Team
from tortoise.exceptions import DoesNotExist

from app.cogs.base import BaseCog

log = logging.getLogger(__name__)


class FightRegistrationCog(BaseCog):
    @commands.Cog.listener()
    async def on_raw_message_delete(self, payload):
        if self.is_bot(payload.member.id):
            return

        if not self.state.is_whitelisted_channel(payload.guild_id, payload.channel_id):
            return

        # TODO Implement logic here: find if fight was recorded and delete info about
        # it if it was
        raise Exception("not implemented")

        # if not then do nothing
        # if it is then need to remove the data from it
        message_id = payload.message_id

        try:
            fight = await Fight.get(id=payload.message_id)
            raise Exception("not implemented")
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
            await self.ack(message)

    async def process_backlog(self):
        pass
