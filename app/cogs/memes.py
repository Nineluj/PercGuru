import discord
from discord.ext import commands, tasks
from random import choice


from cogs.base import BaseCog


lines = [
    "fail their challenge",
    "bully gobballs",
    "focus the perc",
    "not crit three times in a row",
    "wipe on korri"
]


class MemeCog(BaseCog):
    @commands.Cog.listener()
    async def on_ready(self):
        await self.set_new_status()

    @tasks.loop(minutes=10)
    async def refresh_status(self):
        await self.set_new_status()

    async def set_new_status(self):
        guild = choice(self.bot.guilds)
        member = choice(guild.members)

        await self.bot.change_presence(activity=discord.Activity(
            type=discord.ActivityType.watching,
            name=f"{member.nick if member.nick is not None else member.name} {choice(lines)}"
        ))
