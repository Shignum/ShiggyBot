from discord.ext import commands
from discord import slash_command, Option

class other(commands.Cog):
    def __init__(self,bot):
        self.bot = bot

    @slash_command(name='chatclear', description='deletes chat messages')
    async def chatclear(self, ctx, amount=6):
        amount=int(amount)
        await ctx.channel.purge(amount)
        await ctx.respond(f'deleted {amount} messages')

def setup(bot):
    bot.add_cog(other(bot))