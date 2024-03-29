import discord
from discord.ext import commands, tasks
from random import choice


from app.cogs.base import BaseCog


lines = [
    "fail their challenge",
    "bully gobballs",
    "die to a perc",
    "not crit three times in a row",
    "wipe on korri",
    "throw their vulbis in the trash",
    "spend $100 on color changes",
    "die against a treasure hunt chest"
]


class MemeCog(BaseCog):
    """
    Cog that sets funny status messages on an interval. Optional.
    """
    @commands.Cog.listener()
    async def on_ready(self):
        await self.set_new_status()

    @tasks.loop(minutes=10)
    async def refresh_status(self):
        await self.set_new_status()

    async def set_new_status(self):
        guilds_no_test = list(filter(lambda guild: not "test" in guild.name.lower(), self.bot.guilds))

        if len(guilds_no_test) == 0:
            return

        guild = choice(guilds_no_test)
        all_no_bots = list(filter(lambda member: not member.bot, guild.members))

        if len(all_no_bots) != 0:
            member = choice(all_no_bots)

            await self.bot.change_presence(activity=discord.Activity(
                type=discord.ActivityType.watching,
                name=f"{member.nick or member.name} {choice(lines)}"
            ))
