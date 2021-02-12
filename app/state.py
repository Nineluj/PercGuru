import discord
from typing import Set, List


class GuildState:
    teams: Set[discord.Emoji]
    listen_channels: Set[discord.TextChannel]
    pass


class AppState:
    guilds: List[GuildState]

    def __init__(self):
        pass
