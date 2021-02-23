"""
Module for setting up and stopping the connection to the database.
"""
from tortoise import Tortoise
import asyncio
import logging

log = logging.getLogger(__name__)


async def init():
    await Tortoise.init(
        db_url="sqlite://db.sqlite3",
        modules={"models": ["app.models.core"]}
    )
    await Tortoise.generate_schemas()
    log.info("Done making schemas")


def stop():
    async def stop_async():
        await Tortoise.close_connections()

    loop = asyncio.new_event_loop()
    loop.run_until_complete(stop_async())


if __name__ == "__main__":
    from tortoise import run_async
    run_async(init())
