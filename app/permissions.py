from discord.ext import commands


class MissingPrivilegeException(commands.CommandError):
    pass


PRIVILEGED_ROLES = ['leadership', 'council', 'officer']
HIGHEST_PRIVILEGE = ['leadership']


def fail():
    """
    Dumb check that always fails
    """
    async def predicate(ctx):
        raise MissingPrivilegeException('You do not have top-level privileges to manage this bot.')

    return commands.check(predicate)


def is_top_privilege():
    """A :func:`.check` that checks if the person invoking this command is privileged (bot author or top privileged role)
    """
    async def predicate(ctx):
        if await ctx.bot.is_owner(ctx.author):
            return True

        for role in ctx.author.roles:
            if role.name.lower() in HIGHEST_PRIVILEGE:
                return True

        raise MissingPrivilegeException('You do not have top-level privileges to manage this bot.')

    return commands.check(predicate)


def is_privileged():
    """A :func:`.check` that checks if the person invoking this command is privileged (bot author or privileged role)
    """
    async def predicate(ctx):
        if await ctx.bot.is_owner(ctx.author):
            return True

        for role in ctx.author.roles:
            if role.name.lower() in PRIVILEGED_ROLES:
                return True

        raise MissingPrivilegeException('You do not have the privileges to use this bot.')

    return commands.check(predicate)
