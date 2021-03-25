from discord.ext import commands


class Other(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=['cc'])
    @commands.has_permissions(administrator=True)
    async def chatclear(self, ctx, amount=6):
        await ctx.channel.purge(limit=amount+1)

def setup(bot):
    bot.add_cog(Other(bot))