import discord
from discord.ext import commands
import asyncio
from os import getenv
from collections import namedtuple
import logging

from help_command import MyHelpCommand
from data.dao import Dao
from cogs.configuration import ConfigurationCog
from cogs.stats import StatsCog
from cogs.reacts import ReactsCog

TOKEN = getenv("BOT_TOKEN")
DB_USERNAME = getenv("DB_USERNAME")
DB_PASSWORD = getenv("DB_PASSWORD")
DB_NAME = getenv("DB_NAME", "percguru")
DB_HOST = getenv("DB_HOST", "127.0.0.1")
db_config = (DB_USERNAME, DB_PASSWORD, DB_NAME, DB_HOST)

Job = namedtuple("Job", [])

# Almighty bot object
bot = commands.Bot(command_prefix="!", help_command=MyHelpCommand())

# Set up the log
logging.basicConfig(level=getenv("LOGLEVEL", "INFO"))
log = logging.getLogger(__name__)

# Create the dao object
dao = Dao(db_config)

# Add the cogs (components of the bots, grouped into categories in help)
bot.add_cog(ConfigurationCog(dao))
bot.add_cog(StatsCog(dao))
bot.add_cog(ReactsCog(dao))
# bot.add_cog()


@bot.event
async def on_ready():
    asyncio.create_task(dao.start())
    log.info('Connected! Username: {0.name}, ID: {0.id}'.format(bot.user))


if __name__ == "__main__":
    intents = discord.Intents.default()
    intents.reactions = True

    print("Starting the bot")
    bot.run(TOKEN)
    print("Combat is over. Ending remaining tasks.")

    print("Done. Shutdown.")
    exit(0)
