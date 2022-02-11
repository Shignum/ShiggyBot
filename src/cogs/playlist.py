from discord.ext import commands
from discord import Embed
import asyncio
import json
import pycord.wavelink as wavelink
import re
from os import path

url_rx = re.compile(r'https?://(?:www\.)?.+')

class Playlist(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.path = (path.realpath(__file__)).split('src')
        if not hasattr(bot, 'music'):
            self.bot.music = lavalink.Client(self.bot.user.id)
            self.bot.music.add_node('localhost', 7000, 'Shiggybot', 'eu', 'music-node')
            self.bot.add_listener(self.bot.music.voice_update_handler, 'on_socket_response')

    async def cog_before_invoke(self, ctx):
        if not path.isfile(f'{self.path[0]}data/playlists/{ctx.message.guild.id}.json'):
            with open(f'{self.path[0]}data/playlists/{ctx.message.guild.id}.json', 'w') as f:
                data = {}
                json.dump(data, f, indent=4)
        player = ctx.bot.music.player_manager.get(ctx.guild.id)
        if player is None:
            player = self.bot.music.player_manager.create(ctx.guild.id, endpoint=str(ctx.guild.region))
            await player.set_volume(20)

    async def connect_to(self, guild_id: int, channel_id: str):
        ws = self.bot._connection._get_websocket(guild_id)
        await ws.voice_state(str(guild_id), channel_id)

    @commands.command(aliases=['addpl','apl'])
    @commands.has_permissions(administrator=True)
    async def addplaylist(self,ctx,*,query):
        player = self.bot.music.player_manager.get(ctx.guild.id)
        query = query.strip('<>')

        if not url_rx.match(query):
            query = f'ytsearch:{query}'
        results = await player.node.get_tracks(query)
        if not results or not results['tracks']:
            return await ctx.send(embed=Embed(title='Nothing found.'))
        if not results['loadType'] == 'PLAYLIST_LOADED':
            return await ctx.send(embed=Embed(title='Not a playlist.'))
        else:
            tracks = results['tracks']
            name = results["playlistInfo"]["name"]
            tracks = len(tracks)

            with open(f'{self.path[0]}data/playlists/{ctx.message.guild.id}.json', 'r') as f:
                data = json.load(f)
                data[name] = {"tracks": tracks, "url": query}

            with open(f'{self.path[0]}data/playlists/{ctx.message.guild.id}.json', 'w') as f:
                json.dump(data, f, indent=4)
            await ctx.send(embed=Embed(title= f'The playlist {name} ({tracks} tracks) has been added.'))

    @commands.command(aliases= ['playpl', 'ppl'])
    async def playplaylist(self,ctx,*,query):
        if not ctx.author.voice:
            await ctx.send(embed=Embed(title='You need to be in a voicechannel.'))
            return
        with open(f'{self.path[0]}data/playlists/{ctx.message.guild.id}.json', 'r') as f:
            data = json.load(f)
        if query in data:
            pl = data[f"{query}"]["url"]

            player = self.bot.music.player_manager.get(ctx.guild.id)
            if player is not None and not player.is_connected:
                await self.connect_to(ctx.guild.id, str(ctx.author.voice.channel.id))
            await ctx.invoke(self.bot.get_command('play'), query=pl)
        else:
            await ctx.send(embed = Embed(title='No playlist found.'))

    @commands.command(aliases=['deletepl','dpl'])
    @commands.has_permissions(administrator=True)
    async def deleteplaylist(self,ctx,*,query):
        with open(f'{self.path[0]}data/playlists/{ctx.message.guild.id}.json', 'r') as f:
            data = json.load(f)
        if not query in data:
            await ctx.send(embed=Embed(title=f'No playlist found.'))
            return
        else:
            data.pop(query)
            with open(f'{self.path[0]}data/playlists/{ctx.message.guild.id}.json', 'w') as f:
                json.dump(data, f, indent=4)
            await ctx.send(embed=Embed(title=f'Playlist deleted.'))

    @commands.command(aliases=['listpl','lpl'])
    async def listplaylists(self,ctx,page: int = 1):
        with open(f'{self.path[0]}data/playlists/{ctx.message.guild.id}.json', 'r') as f:
            data = json.load(f)
        final_list = []
        pllist = ''
        i=0
        for key in data:
            pllist += f'- {key}\n'
            i = i + 1
            if i % 10 == 0:
                final_list.append(pllist)
                pllist = ''
        if i % 10 != 0:
            final_list.append(pllist)
        try:
            selection = page - 1
            pages = str(len(final_list))
            if int(selection) < 0:
                embed=Embed(description = final_list[0])
                embed.set_footer(text=f'Viewing page 1/{pages}')
            elif int(selection) > len(final_list) - 1:
                embed=Embed(description = final_list[len(final_list)-1])
                embed.set_footer(text=f'Viewing page {str(len(final_list))}/{pages}')
            else:
                embed=Embed(description = final_list[int(selection)])
                embed.set_footer(text=f'Viewing page {page}/{pages}')
            await ctx.send(embed=embed)
        except commands.CommandInvokeError:
            await ctx.channel.send(embed=Embed(title='Something went wrong.'))

    @commands.command(aliases=['cpl','changepl'])
    @commands.has_permissions(administrator=True)
    async def changeplaylist(self,ctx,*,query):
        try:
            with open(f'{self.path[0]}data/playlists/{ctx.message.guild.id}.json', 'r') as f:
                data = json.load(f)
            if not query in data:
                await ctx.send(embed=Embed(title=f'No playlist found.'))
                return
            else:
                await ctx.author.send(embed=Embed(title='Please enter the new playlist name'))
                new_name = await self.bot.wait_for('message', timeout=30, check=lambda
                                                    message: message.channel == ctx.author.dm_channel)
                if new_name.content == query:
                    await ctx.author.send(embed=Embed(title='That was the same playlist name'))
                    return
                data[new_name.content] = data[query]
                data.pop(query)
                with open(f'{self.path[0]}data/playlists/{ctx.message.guild.id}.json', 'w') as f:
                    json.dump(data, f, indent=4)
                await ctx.author.send(embed=Embed(title=f'Playlist name changed to {new_name.content}'))
                await ctx.send(embed=Embed(title=f'Playlist name changed to {new_name.content}'))
        except asyncio.TimeoutError:
            await ctx.author.send(embed=Embed(description='timed out'))


def setup(bot):
    bot.add_cog(Playlist(bot))