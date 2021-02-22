import discord
import discord.ext.commands


async def send_embed(ctx, title, body):
    e = discord.Embed(color=discord.Color.blurple(), title=title, description=body)
    await ctx.send(embed=e)


async def send_stats_embed(ctx, title, fields):
    e = discord.Embed(color=discord.Color.blurple(), title=title)
    for name, value in fields:
        e.add_field(name=name, value=value, inline=True)
    await ctx.send(embed=e)


fail = discord.ext.commands.check(lambda ctx: False)
