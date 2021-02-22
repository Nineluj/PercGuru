import discord
from discord.ext import commands
from os import getenv
from collections import namedtuple
from sys import stdout
import logging
import traceback

from app.state import AppState
from app.data import db
from app.help_format import MyHelpCommand
from app.cogs.configuration import ConfigurationCog
from app.cogs.stats import StatsCog
from app.cogs.reacts import ReactsCog
from app.cogs.channels import ChannelsCog
from app.cogs.fight_handler import FightRegistrationCog
from app.cogs.memes import MemeCog

TOKEN = getenv("BOT_TOKEN")
LOG_FILE = getenv("LOG_FILE", "perc.log")
TEST_GUILD_ID = 808797581547012146

Job = namedtuple("Job", [])

# Almighty bot object
intents = discord.Intents.default()
intents.messages = True
intents.members = True
intents.reactions = True
bot = commands.Bot(command_prefix="pg ", help_command=MyHelpCommand(), intents=intents)

# Set up the log
logging.basicConfig(
    format="%(asctime)s %(name)-30s %(levelname)-8s %(message)s",
    level=getenv("LOGLEVEL", "INFO"),
    filename=LOG_FILE
)
logging.getLogger().addHandler(logging.StreamHandler(stream=stdout))
log = logging.getLogger(__name__)


# Add the cogs (components of the bots, grouped into categories in help)
state = AppState(bot)
cog_args = (state, bot)

# Need to extract sync from this cog
react_cog = ReactsCog(*cog_args)
bot.add_cog(react_cog)
fight_cog = FightRegistrationCog(*cog_args, process_reacts=react_cog.process_message_reacts)
bot.add_cog(fight_cog)

for cog in [ConfigurationCog, StatsCog, ChannelsCog, MemeCog]:
    bot.add_cog(cog(*cog_args))


@bot.event
async def on_connect():
    log.info("Starting database connection")
    await db.init()


@bot.event
async def on_ready():
    await state.load()
    log.info('Connected! Username: {0.name}, ID: {0.id}'.format(bot.user))


@bot.event
async def on_command_error(ctx, error):
    if ctx.guild.id == TEST_GUILD_ID:
        traceback.print_exception(type(error), error, error.__traceback__)
    else:
        log.error(str(error))

    await ctx.send(f"Could not complete command. Reason: {str(error)}")


def run():
    log.info("Starting the bot")
    bot.run(TOKEN)
    log.info("Stopping")
    log.info("Closing DB connection")
    db.stop()
    log.info("Bye")

    exit(0)
