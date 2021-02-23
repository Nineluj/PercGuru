# PercGuru

## Requirements
- Python >=3.8
- Sqlite >= 3.30

## Terminology
Guilds: In the discord backend, servers are called `guilds`.

Cog: Classes to organize related commands and listeners.

Team: A group of players that are related by a reaction emoji.
For an alliance discord server these can be the guilds that make
up that alliance but to avoid ambiguity those are called teams.

## Dev setup
These instructions should work for Linux and MacOS. Maybe Windows but you'll likely have to do some more work to
get it to work.

1. Make sure that you have sqlite3 installed. Installation steps will vary based on your machine.
Once you have it installed run
    ```shell
   sqlite3 --version
   ```
   And check that the version is `3.3X`. Other versions may or may not work.


2. (Recommended) Create and activate a Python virtual environment
   ```shell
   python3 -m venv venv
   source venv/bin/activate
   ```

3. Install the python requirements
   ```shell
   pip install -r requirements.txt
   ```

4. Run `bot.py` with the following the `BOT_TOKEN` environment variable set
   ```text
   BOT_TOKEN=<my_secret_bot_token> python bot.py
   ```
