import discord
from discord import slash_command
from discord.ext import commands
from dotenv import load_dotenv
import os

load_dotenv()

TOKEN = os.getenv('BOT_TOKEN')

intents = discord.Intents.default()
intents.message_content = True

bot = discord.Bot(debug_guilds=[592340235354898433], intents=intents, command_prefix=os.getenv('PREFIX'))

initial_extensions = ['cogs.other', 'cogs.test', 'cogs.music']
#initial_extensions = 'cogs.event','cogs.playlist''

@bot.event
async def on_ready():
    for extension in initial_extensions:
        try:
            bot.load_extension(extension)
            print(f'{extension} has been loaded')
        except Exception as e:
            print(e)

    print(f'Logged on as {bot.user} (ID:{bot.user.id})')
    await bot.change_presence(status=discord.Status.online, activity=discord.Game(name="Music"))

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return
    if message.content.startswith('$hello'):
        await message.channel.send('Hello!')



bot.run(TOKEN)