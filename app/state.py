"""
Knows how to save and retrieve information related to the configuration to the database through the objects
in models.config
"""
from __future__ import annotations

import discord
from typing import Tuple, Dict, Optional
import logging

from app.models.config import Guild, WhitelistedChannel


log = logging.getLogger(__name__)


class AppState:
    __guilds: Dict[int, Tuple[bool, Optional[Guild]]]
    __ready: bool

    def __init__(self, client: discord.Client):
        self.__client = client
        self.__ready = False
        self.__guilds = dict()

    async def load(self, reload=True):
        """
        Called when the state should get loaded. Use database objects to get the needed information.
        """
        if reload:
            self.__guilds = dict()

        for guild in self.__client.guilds:
            exists = await Guild.exists(id=guild.id)

            if exists:
                guild_inst = await Guild.get(id=guild.id)
            else:
                guild_inst = await Guild.create(id=guild.id)

            is_setup = exists and \
                (hasattr(guild_inst, 'react_message_id') and hasattr(guild_inst, 'react_message_channel_id'))

            self.__guilds[guild.id] = (is_setup, guild_inst)

        self.__ready = True

    def is_setup(self, guild_id):
        return guild_id in self.__guilds and self.__guilds[guild_id].is_setup

    async def is_whitelisted_channel(self, guild_id, channel_id):
        if guild_id not in self.__guilds:
            log.warning(f"Guild with ID {guild_id} is not in state")
            return False

        guild = self.__guilds[guild_id][1]
        async for chan in guild.whitelisted_channels:
            if chan.channel_id == channel_id:
                return True

        return False

    async def add_channel(self, guild_id, channel_id) -> bool:
        if guild_id not in self.__guilds:
            log.warning(f"Guild with ID {guild_id} is not in state")
            return False

        guild = await Guild.get(id=guild_id)
        new_relation = await WhitelistedChannel.create(guild=guild, channel_id=channel_id)
        return new_relation is not None

    async def remove_channel(self, guild_id, channel_id) -> bool:
        if guild_id not in self.__guilds:
            log.warning(f"Guild with ID {guild_id} is not in state")
            return False

        guild = await Guild.get(id=guild_id)
        whitelisted_channel = await WhitelistedChannel.get(
            channel_id=channel_id,
            guild=guild
        )
        if whitelisted_channel is not None:
            await whitelisted_channel.delete()

        return True

    async def clear_channels(self, guild_id):
        if guild_id not in self.__guilds:
            log.warning(f"Guild with ID {guild_id} is not in state")
            return False

        guild = await Guild.get(id=guild_id)
        async for chan in guild.whitelisted_channels:
            await chan.delete()

        return True

    async def list_channels(self, guild_id):
        if guild_id not in self.__guilds:
            log.warning(f"Guild with ID {guild_id} is not in state")
            return False

        guild = await Guild.get(id=guild_id)
        return [chan for chan in await guild.whitelisted_channels], True

    async def set_react_message(self, guild_id, channel_id, message_id) -> bool:
        if guild_id not in self.__guilds:
            log.warning(f"Guild with ID {guild_id} is not in state")
            return False

        is_setup, guild_inst = self.__guilds[guild_id]
        guild_inst.react_message_channel_id = channel_id
        guild_inst.react_message_id = message_id
        await guild_inst.save()

        self.__guilds[guild_id] = (True, guild_inst)
        return True

    async def get_react_message(self, guild_id):
        """
        :return: Tuple of the channel_id, message_id
        """
        is_setup, guild_inst = self.__guilds[guild_id]
        return guild_inst.react_message_channel_id, guild_inst.react_message_id

