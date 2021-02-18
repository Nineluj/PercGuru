import logging
import discord
import tortoise.exceptions

from discord.ext import commands
from app.cogs.base import BaseCog
from app.models.core import Fight
from app.models.core import Player, Team


log = logging.getLogger(__name__)
FIGHT_WIN_REACT = "☑️"
ACK_MESSAGE_REACT = "👍"
REFRESH_REACT = "👋"


class ReactsCog(BaseCog):
    @commands.Cog.listener()
    async def on_ready(self):
        guilds = []
        for g in self.bot.guilds:
            guilds.append(str(g))
        log.info("Joined these servers: " + ",".join(guilds))

    async def handle_fight_win(self, fight, message: discord.Message, ack=False):
        # Not adding a way to unmark this, better not enter it incorrectly
        fight.victory = True
        await fight.save()
        if ack:
            await self.ack(message)

    async def handle_other_react(
            self,
            fight: Fight,
            user: discord.Member,
            reaction: str,
            message: discord.Message,
            channel: discord.TextChannel,
            ack=False
    ):
        teams = await self.get_guild_team_emojis_names(message.guild.id)

        if len(teams) == 0:
            await channel.send(f"You haven't set up the react message. Check the help page.")
            return

        username = user.nick or user.name

        if reaction in teams:
            try:
                player = await Player.get(id=user.id)
            except tortoise.exceptions.DoesNotExist:
                # Should never get us a NotFound bc of the earlier check
                team = await Team.get(name=reaction)
                player = await Player.create(id=user.id, team=team)

            # Will not count as twice, will only override if already present
            await fight.participants.add(player)
            log.info(f"Added player {username} as participant for fight {message.id}")
            if ack:
                await self.ack(message)
        else:
            log.warning(f"Non team react '{reaction}' posted by {username} on message {message.id}")

    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload):
        raise Exception("not implemented")

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        """
        Constraints:
        - You only react for yourself, don't react for some other player
            - !!! Don't react for another guild
        - You don't mark lost fights as wins since they cannot be unmarked
        """
        if self.is_bot(payload.member.id):
            return
        if not await self.state.is_whitelisted_channel(payload.guild_id, payload.channel_id):
            return

        reaction = payload.emoji
        user = payload.member

        await self.handle_react(reaction.name, user, payload.channel_id, payload.message_id)

    async def handle_react(self, reaction: str, user: discord.Member, channel_id: int, message_id: int, ack=True):
        fight = await Fight.get(id=message_id)

        channel = self.bot.get_channel(channel_id)
        message = await channel.fetch_message(message_id)

        if reaction == FIGHT_WIN_REACT:
            await self.handle_fight_win(fight, message, ack=ack)
        else:
            await self.handle_other_react(fight, user, reaction, message, channel, ack=ack)
