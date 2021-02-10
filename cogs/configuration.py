from discord.ext import commands
import discord


class ConfigurationCog(commands.Cog, name="Configuration"):
    def __init__(self, dao, **other):
        self.dao = dao
        super().__init__(**other)

    """
    Commands for configuring the bot
    """
    @commands.group()
    async def config(self, ctx):
        """
        Commands for managing the bot.
        """
        if ctx.invoked_subcommand is None:
            await ctx.send("Not a full command")
            return False

    @config.command(name="guilds")
    async def configure_alliance_guilds(self, ctx, message_id):
        """
        Sets the guilds for this discord server based on the names of the reacts to the given message
        :param message_id: The ID of the message that has only the reacts of all the guilds
        """

        # TODO: should probably record and watch this message for:
        #  - people that join/leave/change guilds
        #  - guilds that join or leave

        try:
            reacted_message = await ctx.fetch_message(message_id)
        except discord.NotFound:
            await ctx.send("Can't find the message with that ID. Try again.")
            return False
        except discord.Forbidden:
            await ctx.send("Can't access that message.")
            return False
        except discord.HTTPException:
            await ctx.send("Womp womp")
            return False

        print(reacted_message)

        # if we wanted to get the users
        guild_directory = {}
        for react in reacted_message.reactions:
            g_name = react.emoji.name

            guild_members = []
            for user in await react.users().flatten():
                guild_members.append(user)

            guild_directory[g_name] = guild_members

        guild_member_counts = [f"{name} with {len(members)} member{'s' if len(members) == 1 else ''}"
                               for name, members in guild_directory.items()]
        guild_overview = "\n".join(guild_member_counts)
        await ctx.send(f"Configured. ```{guild_overview}```")
