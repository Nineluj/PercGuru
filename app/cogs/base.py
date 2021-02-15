import asyncio
import discord
from discord.ext import commands
from app.state import AppState


ACK_REACTION = "🆗"
ACK_TIME_S = 3


class BaseCog(commands.Cog):
    def __init__(self, state: AppState, bot: discord.ext.commands.bot.Bot, **other):
        self.state = state
        self.bot = bot
        super().__init__(**other)

    def is_bot(self, id: int):
        return id == self.bot.user.id

    async def ack(self, message: discord.Message, keep=False):
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

    @commands.Cog.listener()
    async def on_command_error(self, error, ctx):
        pass
        # self.bot.help_command()

    async def get_guild_team_emojis(self, guild_id):
        # TODO: cache this?
        channel_id, message_id = await self.state.get_react_message(guild_id)
        channel: discord.TextChannel = self.bot.get_channel(channel_id)
        reacted_message = await channel.fetch_message(message_id)

        return [react.emoji.name for react in reacted_message.reactions]
