import discord
from dotenv import load_dotenv
import os

load_dotenv()

TOKEN = os.getenv('BOT_TOKEN')

intents = discord.Intents.default()
intents.message_content = True

bot = discord.Client(intents=intents)

@bot.event
async def on_ready():
    print(f'Logged on as {bot.user}!')
    
    initial_extensions = ['cogs.other', 'cogs.test']
    #initial_extensions = ['cogs.event','cogs.music','cogs.other','cogs.playlist']
    for extension in initial_extensions:
        bot.load_extension(extension)
        print(f'{extension} has been loaded')
@bot.event
async def on_message(message):
    if message.author == bot.user:
        return
    if message.content.startswith('$hello'):
        await message.channel.send('Hello!')
        

    
bot.run(TOKEN)



# from discord import Embed
# from discord import Intents





# bot = commands.Bot(command_prefix=os.getenv('PREFIX'))


# @bot.event
#async def on_ready():
   

# async def on_message(self, message):
#         print(f'Message from {message.author}: {message.content}')

# @bot.event
# async def on_command_error(ctx, error):
#     if isinstance(error, commands.CommandNotFound):
#         await ctx.send(embed=Embed(title='Command not found.'))
#         return
#     elif isinstance(error, commands.MissingRequiredArgument):
#         await ctx.send(embed=Embed(title='Command needs an Argument.'))
#         return
#     elif isinstance(error, commands.CommandInvokeError):
#         await ctx.send(embed=Embed(title=f'{error.original}'))
#         return
#     elif isinstance(error, commands.MissingPermissions):
#         await ctx.send(embed=Embed(title="You don't have the permission to use this command."))
#         return

#     raise error