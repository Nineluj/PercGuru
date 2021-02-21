import matplotlib.pyplot as plt
from discord.ext import commands
from app.cogs.base import BaseCog
from app.models.core import Fight, Team
import discord
import datetime
from app.util import send_embed
import io
import matplotlib as mpl
mpl.use('Agg')


class StatsCog(
    BaseCog,
    name="Stats"
):
    @commands.command(name="count", help="count [number_of_days] [-plot]")
    async def number_defenses(self, ctx, *args):
        if len(args) > 0:
            try:
                number_days = int(args[0])
            except ValueError:
                number_days = 30
        else:
            number_days = 30

        teams = await self.state.list_teams(ctx.guild.id)  #self.get_guild_team_emojis_names(ctx.guild.id)
        # await ctx.send(",".join(teams))

        now = datetime.datetime.now()
        delta = datetime.timedelta(days=number_days)
        min_dt = now - delta

        count = {}
        for t in teams:
            team = await Team.get(name=t)

            participations = 0
            async for member in team.members:
                async for fight in member.fights.filter(recorded__gte=min_dt):
                    participations += 1

            count[t] = participations

        ans = [f"{team.capitalize()}: {how_many}" for team, how_many in count.items()]
        await send_embed(ctx, f"Perc Fight Participation ({number_days} days)", "\n".join(ans))

        if "-plot" in args:
            xs = list(count.keys())
            ys = list(count.values())

            sorted_ys, sorted_xs = (list(t) for t in zip(*sorted(zip(ys, xs), reverse=True)))

            plt.bar(sorted_xs, sorted_ys, color='red', width=0.4)

            with io.BytesIO() as image_binary:
                plt.savefig(image_binary, format='png')
                image_binary.seek(0)

                file = discord.File(fp=image_binary, filename='plot.png')
                await ctx.channel.send(content="Plot", file=file)
