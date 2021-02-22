from discord.ext import commands


class MissingPrivilegeException(commands.CommandError):
    pass


PRIVILEGED_ROLES = ['Leadership', 'Council', 'Officer']
HIGHEST_PRIVILEGE = ['Leadership']


def fail():
    """
    Dumb check that always fails
    """
    async def predicate(ctx):
        raise MissingPrivilegeException('You do not have top-level privileges to manage this bot.')

    return commands.check(predicate)


def is_top_privilege():
    """A :func:`.check` that checks if the person invoking this command is privileged (bot author or privileged role)
    """
    async def predicate(ctx):
        if not await ctx.bot.is_owner(ctx.author) and not any(e in HIGHEST_PRIVILEGE for e in ctx.author.roles):
            raise MissingPrivilegeException('You do not have top-level privileges to manage this bot.')
        return True

    return commands.check(predicate)


def is_privileged():
    """A :func:`.check` that checks if the person invoking this command is privileged (bot author or privileged role)
    """
    async def predicate(ctx):
        if not await ctx.bot.is_owner(ctx.author) and not any(e in PRIVILEGED_ROLES for e in ctx.author.roles):
            raise MissingPrivilegeException('You do not have the privileges to use this bot.')
        return True

    return commands.check(predicate)
