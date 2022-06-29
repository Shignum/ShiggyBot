import discord
from discord import slash_command
from discord.ext import commands
from dotenv import load_dotenv
import os

load_dotenv()

TOKEN = os.getenv('BOT_TOKEN')

intents = discord.Intents.default()
intents.message_content = True

client = discord.Bot() #debug_guilds=[592340235354898433], intents=intents, command_prefix=os.getenv('PREFIX')

initial_extensions = ['cogs.other', 'cogs.test']
#initial_extensions = ['cogs.event','cogs.music','cogs.other','cogs.playlist']

if __name__ == '__main__':

    for extension in initial_extensions:
        try:
            client.load_extension(extension)
            print(f'{extension} has been loaded')
        except Exception as e:
            print(e)

@client.event
async def on_ready():
    print(f'Logged on as {client.user}!')
    await client.change_presence(status=discord.Status.online, activity=discord.Game(name="Music"))

@client.event
async def on_message(message):
    if message.author == client.user:
        return
    if message.content.startswith('$hello'):
        await message.channel.send('Hello!')



client.run(TOKEN)