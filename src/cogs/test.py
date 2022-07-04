from discord.commands import slash_command 
from discord.ext import commands

class test(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @slash_command(name='hello', description='says hi')
    async def hello(self, ctx):
        await ctx.respond("Hi, this is a slash command from a cog!")
        
def setup(bot):
    bot.add_cog(test(bot))