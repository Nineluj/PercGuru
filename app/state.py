"""
Knows how to save and retrieve information related to the configuration to the database
"""
from __future__ import annotations

import discord
from discord.ext.commands import Bot
from typing import Dict, Optional, List, Set
from tortoise.exceptions import DoesNotExist, IntegrityError
import logging

from app.models.core import Guild, WhitelistedChannel


log = logging.getLogger(__name__)


class CachedGuildState:
    """
    Holds information about a guild (discord server) and knows how to talk to the
    database to retrieve and save it as needed
    """

    # Represents whether the bot has been set up for the guild
    is_setup: bool
    __team_names: List[str]
    __whitelisted_channels: Set[int]
    __discord_model: discord.Guild
    __db_model: Guild

    def __init__(self, bot: Bot):
        self.__bot = bot
        self.__team_names = []
        self.__whitelisted_channels = set()

    async def setup(self, guild: discord.Guild):
        exists = await Guild.exists(id=guild.id)

        if exists:
            guild_db_inst = await Guild.get(id=guild.id)
        else:
            guild_db_inst = await Guild.create(id=guild.id)

        is_setup = (exists and
                    (hasattr(guild_db_inst, 'react_message_id') and guild_db_inst.react_message_id is not None) and
                    (hasattr(guild_db_inst, 'react_message_channel_id') and guild_db_inst.react_message_channel_id is not None))

        self.is_setup = is_setup
        self.__db_model = guild_db_inst
        self.__discord_model = guild

        await self.refresh_whitelisted_channels()
        if is_setup:
            await self.refresh_team_names()

    def load_team_names(self):
        raise Exception("not implemented")

    async def refresh_team_names(self):
        channel_id, message_id = self.__db_model.react_message_channel_id, self.__db_model.react_message_id
        reacted_message = await self.__bot.get_channel(channel_id).fetch_message(message_id)

        team_names = [react.emoji.name for react in reacted_message.reactions]
        self.__team_names = team_names

    async def refresh_whitelisted_channels(self):
        self.__whitelisted_channels = set()
        async for channel in self.__db_model.whitelisted_channels:
            self.__whitelisted_channels.add(channel.channel_id)

    async def is_whitelisted_channel(self, channel_id):
        return channel_id in self.__whitelisted_channels

    async def add_channel(self, channel_id):
        self.__whitelisted_channels.add(channel_id)

        try:
            new_relation = await WhitelistedChannel.create(guild=self.__db_model, channel_id=channel_id)
            return new_relation is not None
        except IntegrityError as integrity_e:
            if "UNIQUE" in str(integrity_e):
                return True
            else:
                raise integrity_e

    async def remove_channel(self, channel_id):
        """
        Removes the channel_id from the database and the in-store memory
        """
        try:
            whitelisted_channel = await WhitelistedChannel.get(
                channel_id=channel_id,
                guild=self.__db_model
            )

            await whitelisted_channel.delete()
        except DoesNotExist:
            pass

        try:
            self.__whitelisted_channels.remove(channel_id)
        except ValueError:
            pass

    async def clear_channels(self):
        async for channel in self.__db_model.whitelisted_channels:
            await channel.delete()

        self.__whitelisted_channels = set()
        return True

    async def list_channels(self):
        return list(self.__whitelisted_channels)

    async def set_react_message(self, channel_id, message_id) -> bool:
        self.__db_model.react_message_channel_id = channel_id
        self.__db_model.react_message_id = message_id
        await self.__db_model.save()

        self.is_setup = True
        await self.refresh_team_names()

    async def list_teams(self):
        return self.__team_names[:]


class AppState:
    """
    Contains the entire configuration state for the guilds that this bot is a part of
    """
    __guilds: Dict[int, CachedGuildState]
    __ready: bool

    def __init__(self, bot: Bot):
        self.__bot = bot
        self.__ready = False
        self.__guilds = dict()

    async def load(self, reload=True):
        """
        Called when the state should get loaded. Use database objects to get the needed information.
        Must be called before any other methods are used.
        """
        if reload:
            self.__guilds = dict()

        for guild in self.__bot.guilds:
            guild_state = CachedGuildState(self.__bot)
            await guild_state.setup(guild)
            self.__guilds[guild.id] = guild_state

        self.__ready = True

    def get_guild(self, guild_id):
        return self.__guilds[guild_id]

    def check_has_guild(self, guild_id):
        if guild_id not in self.__guilds:
            log.warning(f"Guild with ID {guild_id} is not in state")
            return False
        return True

    def is_setup(self, guild_id):
        return guild_id in self.__guilds and self.__guilds[guild_id].is_setup

    async def delegate(self, guild_id, fun, *args):
        """
        Runs the given function with the specified args on the GuildState object with the given id.
        Does NOT check if the guild has been set up. Errors from that are clear enough
        and should not occur after the bot has been configured.
        """
        has_guild = self.check_has_guild(guild_id)
        if has_guild:
            guild = self.get_guild(guild_id)
            ret = await fun(guild_id, *args)
            if ret is None:
                return True
            else:
                return ret

        return False

    async def is_whitelisted_channel(self, guild_id, channel_id):
        return await self.delegate(guild_id, CachedGuildState.is_whitelisted_channel, channel_id)

    async def add_channel(self, guild_id, channel_id) -> bool:
        return await self.delegate(guild_id, CachedGuildState.add_channel, channel_id)

    async def remove_channel(self, guild_id, channel_id) -> bool:
        return await self.delegate(guild_id, CachedGuildState.remove_channel, channel_id)

    async def clear_channels(self, guild_id):
        return await self.delegate(guild_id, CachedGuildState.clear_channels)

    async def list_channels(self, guild_id):
        return await self.delegate(guild_id, CachedGuildState.list_channels)

    async def set_react_message(self, guild_id, channel_id, message_id) -> bool:
        return await self.delegate(guild_id, CachedGuildState.set_react_message, channel_id, message_id)

    async def list_teams(self, guild_id):
        return await self.delegate(guild_id, CachedGuildState.list_teams)
