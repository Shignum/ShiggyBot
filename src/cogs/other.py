from discord.ext import commands
from discord import slash_command, Option

class other(commands.Cog):
    def __init__(self,client):
        self.client = client

    @commands.command(aliases=['cc'])
    @commands.has_permissions(administrator=True)
    async def chatclear(self, ctx, amount=6):
        amount=int(amount)
        await ctx.channel.purge(amount)
        await ctx.respond(f'deleted {amount} messages')

def setup(client):
    client.add_cog(other(client))