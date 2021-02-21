import logging
import discord
import tortoise.exceptions

from discord.ext import commands
from app.cogs.base import BaseCog
from app.models.core import Fight
from app.models.core import Team

log = logging.getLogger(__name__)
# FIGHT_WIN_REACT = "☑️"
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
        teams = await self.state.list_teams(message.guild.id)

        if len(teams) == 0:
            await channel.send(f"You haven't set up the react message. Check the help page.")
            return

        if reaction in teams:
            team = await Team.get(name=reaction)
            # Add is idempotent
            await fight.participants.add(team)
            log.info(f"Recorded team {reaction} as participant for fight {message.id}")

            if ack:
                await self.ack(message)
        else:
            log.warning(f"Non team react '{reaction}' posted by {user} on message {message.id}")

    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload):
        # Need to allow people fix mis-inputs (wrong alliance reaction)
        if self.is_own_bot(payload.user_id):
            return
        if not await self.state.is_whitelisted_channel(payload.guild_id, payload.channel_id):
            return

        if not hasattr(payload, 'emoji') or not hasattr(payload.emoji, 'name'):
            return

        removed = payload.emoji.name

        if removed not in await self.state.list_teams(payload.guild_id):
            return

        message_id = payload.message_id

        try:
            fight = await Fight.get(id=message_id)
            await fight.participants.clear()

            message = await self.bot.get_channel(payload.channel_id).fetch_message(payload.message_id)
            await self.process_message_reacts(message)
            await self.ack(message)

        except tortoise.exceptions.DoesNotExist:
            pass

    async def process_message_reacts(self, message: discord.Message):
        for react in message.reactions:
            emoji = react.emoji

            if hasattr(emoji, 'name'):
                emoji_str = emoji.name
            else:
                emoji_str = emoji

            async for member in react.users():
                await self.handle_react(emoji_str, member, message.channel.id, message.id, ack=False)

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        """
        Constraints:
        - You only react for yourself, don't react for some other player
            - !!! Don't react for another guild
        - You don't mark lost fights as wins since they cannot be unmarked
        """
        if self.is_own_bot(payload.member.id):
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

        # if reaction == FIGHT_WIN_REACT:
        #     await self.handle_fight_win(fight, message, ack=ack)
        # else:
        await self.handle_other_react(fight, user, reaction, message, channel, ack=ack)
