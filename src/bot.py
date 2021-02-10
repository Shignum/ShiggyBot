import os

from discord import Embed
from discord import Intents
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()
intents = Intents.default()
intents.typing = False
intents.presences = False
bot = commands.Bot(command_prefix=os.getenv('PREFIX'))
TOKEN = os.getenv('BOT_TOKEN')


@bot.event
async def on_ready():
    print(f'{bot.user} has logged in.')
    initial_extensions = ['cogs.event','cogs.music']
    for extension in initial_extensions:
        bot.load_extension(extension)

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        await ctx.send(embed=Embed(title='Command not found.'))
        return
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send(embed=Embed(title='Command used wrong.'))
        return

    raise error


bot.run(TOKEN)
