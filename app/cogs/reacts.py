import logging
import discord
import tortoise.exceptions

from discord.ext import commands
from app.cogs.base import BaseCog
from app.models.core import Fight
from app.models.core import Player, Guild


log = logging.getLogger(__name__)
FIGHT_WIN_REACT = "☑️"
ACK_MESSAGE_REACT = "👍"
REFRESH_REACT = "👋"


class ReactsCog(BaseCog):
    def update_guild_list(self, message):
        """
        Uses the reacts on the given message as the guilds available on the server
        :param message:
        :return:
        """
        raise Exception("not implemented")

    @commands.Cog.listener()
    async def on_guild_join(self, guild):
        # TODO handle this, bot is already running and gets added to server
        raise Exception("not implemented")

    @commands.Cog.listener()
    async def on_ready(self):
        guilds = []
        for g in self.bot.guilds:
            guilds.append(str(g))
        log.info("Joined these servers: " + ",".join(guilds))

    async def handle_fight_win(self, message: discord.Message):
        fight = await Fight.get(id=message.id)
        fight.victory = True
        await fight.save()

        await self.ack(message)

    async def handle_other_react(
            self, message: discord.Message, channel: discord.TextChannel, reaction: discord.Emoji
    ):
        if self.guild_emote_list is None:
            # error: guild emote list not set up
            await channel.send(f"You haven't set up the react message. Check the help page.")
            return

        if reaction.name in self.guild_emote_list:
            raise Exception("not implemented")
        else:
            player = None
            try:
                player = await Player.get(name=message.author.name)
            except tortoise.exceptions.DoesNotExist:
                # TODO: catch this?
                guild = await Guild.get()
                player = await Player.create(name=message.author.name)

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        if self.is_bot(payload.member.id):
            return

        # Verify that the react was added by a member of that guild?
        reaction = payload.emoji
        message_id = payload.message_id

        channel = self.bot.get_channel(payload.channel_id)
        message = await channel.fetch_message(message_id)

        if reaction.name == FIGHT_WIN_REACT:
            await self.handle_fight_win(message)
        else:
            await self.handle_other_react(message, channel, reaction)
