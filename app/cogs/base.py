import asyncio
import logging
import discord
from discord.ext import commands

from app.state import AppState


log = logging.getLogger(__name__)


ACK_REACTION = "🆗"
ACK_TIME_S = 2


class BaseCog(commands.Cog):
    """
    Abstract class which provides utility methods for working with the app state
    and interacting with discord text channels
    """
    def __init__(self, state: AppState, bot: discord.ext.commands.bot.Bot, **other):
        self.state = state
        self.bot = bot
        super().__init__()
        self.__handled_error_message_ids = set()

    def is_own_bot(self, user_id: int):
        return user_id == self.bot.user.id

    async def ack(self, message: discord.Message, keep=False):
        """
        Uses the ACK react to show that some action related to the message
        has been processed. Keeps the ACK only for a limited amount of time by default.
        :param message: The message to ACK
        :param keep: If true, the ACK react remains on the message
        """
        asyncio.create_task(self.__ack(message, keep))

    async def __ack(self, message: discord.Message, keep=False):
        await message.add_reaction(ACK_REACTION)
        if not keep:
            await asyncio.sleep(ACK_TIME_S)
            await message.remove_reaction(ACK_REACTION, self.bot.user)

    @staticmethod
    async def error(channel: discord.TextChannel, response_text: str):
        sent = await channel.send(response_text)
        return sent
