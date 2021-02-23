from app.cogs.base import BaseCog
from app.models.core import Team, Guild
from app.permissions import is_privileged
from app.util import send_stats_embed

import matplotlib.pyplot as plt
from discord.ext import commands
import discord
import io
import logging
from datetime import datetime, timedelta
import matplotlib as mpl
mpl.use('Agg')

log = logging.getLogger(__name__)


class StatsCog(
    BaseCog,
    name="Stats"
):
    @commands.command(name="count", help="count [number_of_days] [-plot]")
    @commands.guild_only()
    @is_privileged()
    async def number_defenses(self, ctx, *args):
        if len(args) > 0:
            try:
                number_days = int(args[0])
            except ValueError:
                number_days = 7
        else:
            number_days = 7

        log.info(f"Getting stats for the past {number_days} days for server {ctx.guild.name}")

        teams = await self.state.list_teams(ctx.guild.id)
        min_dt = datetime.utcnow() - timedelta(days=number_days)

        team_participation_count = {}
        fights = set()
        for t in teams:
            server = await Guild.get(id=ctx.guild.id)
            team = await Team.get(name=t, server=server)

            participations = 0

            async for fight in team.fights.filter(recorded__gte=min_dt):
                fights.add(fight)
                participations += 1

            team_participation_count[t] = participations

        fight_count = len(fights)

        xs = list(team_participation_count.keys())
        ys = list(team_participation_count.values())

        sorted_ys, sorted_xs = (list(t) for t in zip(*sorted(zip(ys, xs), reverse=True)))

        ans = [(f"{team.capitalize()}", f"{how_many} ({100 * how_many / fight_count:.1f}%)")
               for team, how_many in zip(sorted_xs, sorted_ys)]
        await send_stats_embed(ctx, f"Perc Fight Participation ({number_days} days)", ans)

        if "-plot" in args:
            plt.xticks(rotation='vertical')
            plt.gcf().subplots_adjust(bottom=0.25)
            plt.bar(sorted_xs, sorted_ys, color='red', width=0.4)

            with io.BytesIO() as image_binary:
                plt.savefig(image_binary, format='png')
                image_binary.seek(0)

                file = discord.File(fp=image_binary, filename='plot.png')
                await ctx.channel.send(content="Plot", file=file)

            plt.clf()
