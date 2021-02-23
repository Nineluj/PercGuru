from discord.ext import commands
import discord
import logging

from app.util import send_embed
from app.permissions import is_top_privilege
from app.cogs.base import BaseCog
from app.models.core import Team, Guild

log = logging.getLogger(__name__)


class ConfigurationCog(
    BaseCog,
    name="Configuration",
    description="""Commands for configuring the bot"""
):
    """
    Commands for configuring the teams for a given guild (server)
    """
    @commands.group(
        name="guilds",
        invoke_without_command=True
    )
    @commands.guild_only()
    @is_top_privilege()
    async def configure_guild_teams(self, ctx):
        await ctx.invoke(self.configure_list)

    @configure_guild_teams.command(name="list")
    @commands.guild_only()
    @is_top_privilege()
    async def configure_list(self, ctx):
        emojis = await self.state.list_teams(ctx.guild.id)  # await self.get_guild_team_emojis_names(ctx.guild.id)
        await send_embed(ctx.channel, "Guilds", "\n".join(emojis))

    @configure_guild_teams.command(name="set")
    @commands.guild_only()
    @is_top_privilege()
    async def configure_set(self, ctx, *args):
        if len(args) != 1:
            await self.error(ctx.channel, "Use: set <message_id>")
            return False

        message_id = args[0]
        try:
            reacted_message = await ctx.fetch_message(message_id)
        except discord.NotFound:
            await ctx.send("Can't find the message with that ID. Try again.")
            return False
        except discord.Forbidden:
            await ctx.send("Can't access that message.")
            return False
        except discord.HTTPException:
            await ctx.send("Womp womp")
            return False

        result = await self.state.set_react_message(ctx.guild.id, ctx.channel.id, reacted_message.id)

        try:
            if result:
                await self.ack(ctx.message, keep=True)
                await ctx.send("Reaction message updated successfully.")
            else:
                await self.error(ctx.channel, "Unable to use that message to configure the teams")
        except discord.Forbidden:
            log.warning("Unable to post confirmation of guilds set")

        await self.create_teams(ctx)
        log.info(f"Done initializing teams")

    async def create_teams(self, ctx):
        reacts = await self.state.list_teams(ctx.guild.id)

        for team_name in reacts:
            server_id = ctx.guild.id
            server_inst = await Guild.get(id=server_id)
            team_exists = await Team.exists(name=team_name, server=server_inst)

            if not team_exists:
                created_team = await Team.create(name=team_name, server=server_inst)
                if not created_team:
                    log.warning(f"Wasn't able to create team with name {team_name} for guild {server_id}")
                else:
                    log.info(f"Created team with name {team_name} for guild {server_id}")

