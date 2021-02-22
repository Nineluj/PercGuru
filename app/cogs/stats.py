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

        teams = await self.state.list_teams(ctx.guild.id)

        now = datetime.datetime.now()
        delta = datetime.timedelta(days=number_days)
        min_dt = now - delta

        team_participation_count = {}
        fights = set()
        for t in teams:
            team = await Team.get(name=t)

            participations = 0
            async for fight in team.fights.filter(recorded__gte=min_dt):
                fights.add(fight)
                participations += 1

            team_participation_count[t] = participations

        fight_count = len(fights)

        ans = [f"{team.capitalize()}: {how_many} ({100 * how_many / fight_count:.1f}%)"
               for team, how_many in team_participation_count.items()]
        await send_embed(ctx, f"Perc Fight Participation ({number_days} days)", "\n".join(ans))

        if "-plot" in args:
            xs = list(team_participation_count.keys())
            ys = list(team_participation_count.values())

            sorted_ys, sorted_xs = (list(t) for t in zip(*sorted(zip(ys, xs), reverse=True)))

            plt.bar(sorted_xs, sorted_ys, color='red', width=0.4)

            with io.BytesIO() as image_binary:
                plt.savefig(image_binary, format='png')
                image_binary.seek(0)

                file = discord.File(fp=image_binary, filename='plot.png')
                await ctx.channel.send(content="Plot", file=file)
