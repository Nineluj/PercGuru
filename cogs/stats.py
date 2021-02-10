import matplotlib
from discord.ext import commands


class StatsCog(commands.Cog):
    def __init__(self, dao, **other):
        self.dao = dao
        super().__init__(**other)

    # @commands.command(name="bar-chart")
    # async def bar_chart(self):
    #     pass
    #
    # @commands.command()
    pass
