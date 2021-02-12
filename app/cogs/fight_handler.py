from discord.ext import commands
import logging
from app.models.core import Fight, Player, Guild
from tortoise.exceptions import DoesNotExist

from app.cogs.base import BaseCog

log = logging.getLogger(__name__)


class FightRegistrationCog(BaseCog):
    @commands.Cog.listener()
    async def on_raw_message_delete(self, payload):
        if self.is_bot(payload.member.id):
            return

        # TODO: look up if the message deleted was kept in the store
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
        # TODO: check channel

        if len(message.attachments) == 1 and message.attachments[0].filename.endswith(".png"):
            await Fight.create(id=message.id, recorded=message.created_at)
            await self.ack(message)

        # TODO: check that its on a whitelisted channel and that it includes an image
        # raise Exception("not implemented")

    async def process_backlog(self):
        pass
