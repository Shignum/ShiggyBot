from discord.ext import commands


class other(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def chatclear(self, ctx, amount=7):
        await ctx.channel.purge(limit=amount)

def setup(bot):
    bot.add_cog(other(bot))