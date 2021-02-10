from discord.ext import commands
import discord
from data.dao import Dao


class ReactsCog(commands.Cog):
    def __init__(self, dao, **other):
        self.dao = dao
        super().__init__(**other)

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        d_guild_name = payload.emoji.name
        message_id = payload.message.id

        await self.job_queue.put(Job())
