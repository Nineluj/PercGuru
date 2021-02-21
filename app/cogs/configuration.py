from discord.ext import commands
from typing import Dict
import discord
import logging

from app.util import send_embed
from app.cogs.base import BaseCog
from app.models.core import Team
from app.models.config import Guild

log = logging.getLogger(__name__)


class ConfigurationCog(
    BaseCog,
    name="Configuration",
    description="""Commands for configuring the bot"""
):
    """
    Commands for configuring the bot
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # V Not using this at the moment
        # Maps <id of failed user command> -> <id of bot response to that command>
        # Could clear this periodically but should be ok.
        # Ok to just be here since don't care about persistence between sessions and this is
        # the only cog that consumes text commands
        self.recently_failed: Dict[int, discord.Message] = dict()

    @commands.group(
        name="guilds",
        invoke_without_command=True
    )
    @commands.is_owner()
    async def configure_guild_teams(self, ctx):
        await ctx.invoke(self.configure_list)

    @configure_guild_teams.command(name="list")
    async def configure_list(self, ctx):
        emojis = await self.state.list_teams(ctx.guild.id)  # await self.get_guild_team_emojis_names(ctx.guild.id)
        await send_embed(ctx.channel, "Guilds", "\n".join(emojis))

    @configure_guild_teams.command(name="set")
    async def configure_set(self, ctx, *args):
        if len(args) != 1:
            await self.error(ctx.channel, "Use: set <message_id>")
            return

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
        if result:
            await self.ack(ctx.message, keep=True)
            await ctx.send("Reaction message updated successfully.")
        else:
            await self.error(ctx.channel, "Unable to use that message to configure the teams")

        # Set up the team models if they don't exist
        reacts = await self.state.list_teams(ctx.guild.id)  # self.get_guild_team_emojis_names(ctx.guild.id)

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

        log.info(f"Done initializing teams")

    # @config.command(name="clear")
    # @discord.ext.commands.is_owner()
    # async def clear_recent(self, ctx, *args):
    #     # Only want to do this on the test server
    #     if ctx.guild.id == 808797581547012146:
    #         left = 10
    #
    #         if len(args) == 1:
    #             left = int(args[0])
    #
    #         all_msgs = []
    #
    #         async for message in ctx.channel.history():
    #             all_msgs.append(message)
    #             left -= 1
    #
    #             if left == 0:
    #                 break
    #
    #         await ctx.channel.delete_messages(all_msgs)
