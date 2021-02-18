import matplotlib
from discord.ext import commands
from app.cogs.base import BaseCog


class StatsCog(BaseCog):
    # @commands.command(name="bar-chart")
    # async def bar_chart(self):
    #     pass
    #
    # @commands.command()

    @commands.command(name="count")
    async def number_defenses(self, guild=None, number_days=30):
        pass

