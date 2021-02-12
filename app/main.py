import discord
from discord.ext import commands
from os import getenv
from collections import namedtuple
from sys import stdout
import logging

from state.state import AppState
from data import db
from help_command import MyHelpCommand
from cogs.configuration import ConfigurationCog
from cogs.stats import StatsCog
from cogs.reacts import ReactsCog
from cogs.fight_handler import FightRegistrationCog
from cogs.memes import MemeCog

TOKEN = getenv("BOT_TOKEN")
LOG_FILE = getenv("LOG_FILE", "perc.log")

Job = namedtuple("Job", [])

# Almighty bot object
intents = discord.Intents.default()
intents.messages = True
intents.members = True
intents.reactions = True
bot = commands.Bot(command_prefix="$", help_command=MyHelpCommand(), intents=intents)

# Set up the log
logging.basicConfig(level=getenv("LOGLEVEL", "INFO"), filename=LOG_FILE)
logging.getLogger().addHandler(logging.StreamHandler(stream=stdout))
log = logging.getLogger(__name__)


# Add the cogs (components of the bots, grouped into categories in help)
state = AppState()
cog_args = (state, bot)
for cog in [ConfigurationCog, StatsCog, FightRegistrationCog, ReactsCog, MemeCog]:
    bot.add_cog(cog(*cog_args))


@bot.event
async def on_connect():
    log.info("Starting database connection")
    await db.init()


@bot.event
async def on_ready():
    log.info('Connected! Username: {0.name}, ID: {0.id}'.format(bot.user))


def run():
    log.info("Starting the bot")
    bot.run(TOKEN)
    log.info("Stopping")
    log.info("Closing DB connection")
    db.stop()
    log.info("Bye")

    exit(0)
