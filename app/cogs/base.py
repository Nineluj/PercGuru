import asyncio
import discord
from discord.ext import commands
from state.state import AppState


ACK_REACTION = "🆗"
ACK_TIME_S = 1.5


class BaseCog(commands.Cog):
    def __init__(self, state: AppState, bot: discord.ext.commands.bot, **other):
        self.state = state
        self.bot = bot
        super().__init__(**other)

    def is_bot(self, id: int):
        return id == self.bot.user.id

    async def ack(self, message: discord.Message):
        asyncio.create_task(self.__ack(message))

    async def __ack(self, message: discord.Message):
        await message.add_reaction(ACK_REACTION)
        await asyncio.sleep(ACK_TIME_S)
        await message.remove_reaction(ACK_REACTION, self.bot.user)
