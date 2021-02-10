import asyncpg
import asyncio
from contextlib import suppress
import logging

log = logging.getLogger(__name__)


class Dao:
    def __init__(self, conf):
        # Lock is for the db object which needs to be set in start before it can be used
        self.lock = asyncio.Lock()
        self.db = None
        self.conf = conf

    async def start(self):
        await self.lock.acquire()
        self.db = await Database.create(*self.conf)
        self.lock.release()

    async def ensure_initialized(self):
        while True:
            await self.lock.acquire()

            if self.db is None:
                self.lock.release()
                break
            else:
                self.lock.release()
            await asyncio.sleep(1)

        return None

    async def save(self):
        await self.ensure_initialized()
        pass


class Database:
    conn: asyncpg.Connection

    def __init__(self):
        raise RuntimeError("Cannot create database through constructor")

    @classmethod
    async def __postgres_create_db(cls, username, password, new_database_name):
        try:
            conn = await asyncpg.connect(
                user=username,
                password=password,
                database="postgres",
                host="127.0.0.1"
            )

            await conn.execute(f'''
                CREATE DATABASE {new_database_name}
            ''')
        except:
            raise Exception("Failed to create database with the given name")

    @classmethod
    async def create(cls, username, password, database, second_try=False):
        try:
            conn = await asyncpg.connect(
                user=username,
                password=password,
                database=database,
                host="127.0.0.1"
            )
        except asyncpg.InvalidCatalogNameError:
            if second_try:
                raise Exception("Failed to connect to newly created database")

            log.warning("No database set up with the given name, creating it...")
            await Database.__postgres_create_db(username, password, database)
            return Database.create(username, password, database, second_try=True)

        with suppress(asyncpg.DuplicateTableError):
            log.info("Creating tables")
            await conn.execute('''
                CREATE TABLE fights(
                    id INT PRIMARY KEY,
                    uploaded date,
                    defense bit
                );
                
                CREATE TABLE fight_participants(
                    
                );
                
                CREATE TABLE fighters(
                    
                );
            ''')

        log.info("Done initializing the database")

        obj = cls.__new__(cls)
        obj.conn = conn
        return obj

    async def get_last_write_timestamp(self) -> int:
        # return self.
        return 0


if __name__ == "__main__":
    import sys

    loop = asyncio.get_event_loop()
    loop.run_until_complete(Database.create(*sys.argv[1:]))
