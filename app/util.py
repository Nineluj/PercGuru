import discord
import discord.ext.commands


async def send_embed(ctx, title, body, image=None):
    e = discord.Embed(color=discord.Color.blurple(), title=title, description=body)
    if image is not None:
        e.add_field(name="Image", value=image)
        e.set_image()
    await ctx.send(embed=e)

fail = discord.ext.commands.check(lambda ctx: False)
