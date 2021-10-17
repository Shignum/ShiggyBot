import os

from discord import Embed
from discord import Intents
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()
intents = Intents.default()

bot = commands.Bot(command_prefix=os.getenv('PREFIX'))
TOKEN = os.getenv('BOT_TOKEN')

@bot.event
async def on_ready():
    print(f'{bot.user} has logged in.')
    initial_extensions = ['cogs.event','cogs.music','cogs.other','cogs.playlist']
    for extension in initial_extensions:
        bot.load_extension(extension)

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        await ctx.send(embed=Embed(title='Command not found.'))
        return
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send(embed=Embed(title='Command needs an Argument.'))
        return
    elif isinstance(error, commands.CommandInvokeError):
        await ctx.send(embed=Embed(title=f'{error.original}'))
        return
    elif isinstance(error, commands.MissingPermissions):
        await ctx.send(embed=Embed(title="You don't have the permission to use this command."))
        return

    raise error


bot.run(TOKEN)
