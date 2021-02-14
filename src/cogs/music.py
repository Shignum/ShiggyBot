import asyncio
import math
import re

import lavalink
from discord import Embed
from discord import Intents
from discord.ext import commands

url_rx = re.compile(r'https?://(?:www\.)?.+')

intents = Intents.default()
intents.voice_states = True

class Music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        if not hasattr(bot, 'music'):
            self.bot.music = lavalink.Client(self.bot.user.id)
            self.bot.music.add_node('localhost', 7000, 'Shiggybot', 'eu', 'music-node')
            self.bot.add_listener(self.bot.music.voice_update_handler, 'on_socket_response')

        self.bot.music.add_event_hook(self.track_hook)

    def cog_unload(self):
        self.bot.music._event_hooks.clear()

    async def cog_before_invoke(self, ctx):
        guild_check = ctx.guild is not None
        if guild_check:
            await self.ensure_voice(ctx)
        return guild_check

    async def ensure_voice(self, ctx):
        if ctx.author.voice is None:
            raise commands.CommandInvokeError('You need to be in a voicechannel.')
        else:
            player = ctx.bot.music.player_manager.get(ctx.guild.id)
            if player is not None:
                should_connect = ctx.command.name in ('play', 'search', 'join', 'playtop',)
                if not player.is_connected:
                    if not should_connect:
                        raise commands.CommandInvokeError('Not connected.')

                    permissions = ctx.author.voice.channel.permissions_for(ctx.me)
                    if not permissions.connect or not permissions.speak:
                        raise commands.CommandInvokeError('I need the connect and speak permission.')

                    player.store('channel', ctx.channel.id)
                    await self.connect_to(ctx.guild.id, str(ctx.author.voice.channel.id))
                else:
                    if int(player.channel_id) != int(ctx.author.voice.channel.id):
                        raise commands.CommandInvokeError('You need to be in my voicechannel.')
            else:
                player = self.bot.music.player_manager.create(ctx.guild.id, endpoint=str(ctx.guild.region))
                await player.set_volume(20)
                await self.ensure_voice(ctx)

    async def track_hook(self, event):
        if isinstance(event, lavalink.events.QueueEndEvent):
            guild_id = int(event.player.guild_id)
            await self.connect_to(guild_id, None)

    async def connect_to(self, guild_id: int, channel_id: str):
        ws = self.bot._connection._get_websocket(guild_id)
        await ws.voice_state(str(guild_id), channel_id)

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, prev, cur):
        if prev.channel is None:
            return
        if self.bot.user in prev.channel.members and len(prev.channel.members) == 1:
            player = self.bot.music.player_manager.get(prev.channel.guild.id)
            player.queue.clear()
            await player.stop()
            await self.connect_to(prev.channel.guild.id, None)

    @commands.command(aliases=['j'])
    async def join(self, ctx):
        """Joins the voice channel.(not useful)"""

    @commands.command(aliases=['s'])
    async def search(self, ctx, *, query):
        """(short:'s')Searches on youtube and let's you choose the song."""
        try:
            player = self.bot.music.player_manager.get(ctx.guild.id)
            query = f'ytsearch:{query}'
            results = await player.node.get_tracks(query)
            tracks = results['tracks'][0:10]
            i = 0
            query_result = ''
            for track in tracks:
                i = i + 1
                query_result = query_result + f'{i}) [{track["info"]["title"]}]({track["info"]["uri"]})\n'
            embed = Embed()
            embed.description = query_result
            embed.title = 'Please choose the number of the song you want to play.'

            await ctx.channel.send(embed=embed)

            def check(m):
                return m.author.id == ctx.author.id

            response = await self.bot.wait_for('message', check=check, timeout=60)
            track = tracks[int(response.content) - 1]
            embed = Embed()
            embed.title = 'Track queued'
            embed.description = f'[{track["info"]["title"]}]({track["info"]["uri"]})'

            player.add(requester=ctx.author.id, track=track)
            await ctx.send (embed=embed)
            if not player.is_playing:
                await player.play()

        except asyncio.TimeoutError:
            await ctx.send(embed=Embed(title='Timed out.'))

    @commands.command(aliases=['p'])
    async def play(self, ctx, *, query: str):
        """(short:'p') Plays a song/playlist or searches youtube and plays the first. """
        player = self.bot.music.player_manager.get(ctx.guild.id)
        query = query.strip('<>')

        if not url_rx.match(query):
            query = f'ytsearch:{query}'

        results = await player.node.get_tracks(query)

        if not results or not results['tracks']:
            return await ctx.send('Nothing found!')

        # Valid loadTypes are:
        #   TRACK_LOADED    - single video/direct URL)
        #   PLAYLIST_LOADED - direct URL to playlist)
        #   SEARCH_RESULT   - query prefixed with either ytsearch: or scsearch:.
        #   NO_MATCHES      - query yielded no results
        #   LOAD_FAILED     - most likely, the video encountered an exception during loading.

        embed = Embed()

        if results['loadType'] == 'PLAYLIST_LOADED':
            tracks = results['tracks']

            for track in tracks:
                # Add all of the tracks from the playlist to the queue.
                player.add(requester=ctx.author.id, track=track)

            embed.title = 'Playlist queued!'
            embed.description = f'{results["playlistInfo"]["name"]} - {len(tracks)} tracks'
        else:
            track = results['tracks'][0]
            embed.title = 'Track queued'
            embed.description = f'[{track["info"]["title"]}]({track["info"]["uri"]})'

            track = lavalink.models.AudioTrack(track, ctx.author.id, recommended=True)
            player.add(requester=ctx.author.id, track=track)

        await ctx.send(embed=embed)

        if not player.is_playing:
            await player.play()

    @commands.command()
    async def playtop(self, ctx, *, query: str):
        """ Same as play, but queues on top. """
        await ctx.invoke(self.bot.get_command('join'))
        player = self.bot.music.player_manager.get(ctx.guild.id)
        query = query.strip('<>')

        if not url_rx.match(query):
            query = f'ytsearch:{query}'

        results = await player.node.get_tracks(query)

        if not results or not results['tracks']:
            return await ctx.send('Nothing found!')

        embed = Embed()

        if results['loadType'] == 'PLAYLIST_LOADED':
            tracks = results['tracks']

            for track in tracks:
                player.add(requester=ctx.author.id, track=track)

            embed.title = 'Playlist queued!'
            embed.description = f'{results["playlistInfo"]["name"]} - {len(tracks)} tracks'

        else:
            track = results['tracks'][0]
            embed.title = 'Track queued'
            embed.description = f'[{track["info"]["title"]}]({track["info"]["uri"]})'

            track = lavalink.models.AudioTrack(track, ctx.author.id, recommended=True)
            player.add(requester=ctx.author.id, track=track, index=0)

        await ctx.send(embed=embed)

        if not player.is_playing:
            await player.play()

    @commands.command()
    async def leave(self, ctx):
        """Stops music and leaves."""
        guild_id = int(ctx.message.guild.id)
        player = self.bot.music.player_manager.get(ctx.guild.id)
        await player.stop()
        await self.connect_to(guild_id, None)

    @commands.command()
    async def stop(self, ctx):
        """Stops the music, clears the queue and leaves."""
        player = self.bot.music.player_manager.get(ctx.guild.id)
        player.queue.clear()
        await player.stop()
        await self.connect_to(ctx.guild.id, None)

    @commands.command()
    async def clear(self, ctx):
        """clears the queue"""
        player = self.bot.music.player_manager.get(ctx.guild.id)
        player.queue.clear()
        await ctx.send(embed = Embed(title ='Queue cleared.'))

    @commands.command()
    async def pause(self, ctx):
        """pause the music."""
        player = self.bot.music.player_manager.get(ctx.guild.id)
        await player.set_pause(True)
        await ctx.send(embed = Embed(title ='Music paused.'))

    @commands.command()
    async def resume(self, ctx):
        """unpause the music."""
        player = self.bot.music.player_manager.get(ctx.guild.id)
        await player.set_pause(False)
        await ctx.send(embed = Embed(title ='Music playing'))

    @commands.command()
    async def skip(self, ctx):
        """Skips the now playing song."""
        player = self.bot.music.player_manager.get(ctx.guild.id)
        await player.skip()
        await ctx.send(embed = Embed(title ='Song skipped.'))

    @commands.command()
    async def shuffle(self, ctx):
        """toggles shuffle on/off. (".queue" wrong if on)"""
        player = self.bot.music.player_manager.get(ctx.guild.id)
        if not player.shuffle:
            player.shuffle = True
            await ctx.send(embed = Embed(title ='Songs are now playing randomly.'))
        else:
            player.shuffle = False
            await ctx.send(embed = Embed(title ='Songs are no longer playing randomly.'))

    @commands.command(aliases=['loop'])
    async def repeat(self, ctx):
        """toggles queue repeat on/off."""
        player = self.bot.music.player_manager.get(ctx.guild.id)
        player.repeat = not player.repeat
        await ctx.send(embed = Embed(title ='Repeat ' + ('enabled' if player.repeat else 'disabled')))

    @commands.command()
    async def volume(self, ctx):
        """Shows the music volume."""
        player = self.bot.music.player_manager.get(ctx.guild.id)
        await ctx.send(embed = Embed(title =f'Volume is {player.volume}'))

    @commands.command()
    async def setvolume(self, ctx, *, query: int):
        """sets the volume to a new value between 0 and 200."""
        player = self.bot.music.player_manager.get(ctx.guild.id)
        if query <= 200:
            await player.set_volume(query)
            await ctx.send(embed = Embed(title =f'volume set to {player.volume}'))
        else:
            ctx.send(embed = Embed(title ='value to high.'))

    @commands.command(aliases=['np'])
    async def nowplaying(self, ctx):
        """(short:'np') Shows the song playing."""
        player = self.bot.music.player_manager.get(ctx.guild.id)
        if player.is_playing:
            current = player.current.title
            url = f'https://youtube.com/watch?v={player.current.identifier}'
            embed = Embed(title='Now playing', description=f'[{current}]({url})')
            await ctx.send(embed=embed)
        else:
            embed = Embed(title=f'Nothing is playing')
            await ctx.send(embed=embed)

    @commands.command()
    async def queue(self, ctx, page: int = 1):
        """Shows  the next 10 songs in the queue."""
        player = self.bot.music.player_manager.get(ctx.guild.id)

        items_per_page = 10
        pages = math.ceil(len(player.queue) / items_per_page)

        start = (page - 1) * items_per_page
        end = start + items_per_page

        queue_list = ''
        for index, track in enumerate(player.queue[start:end], start=start):
            queue_list += f'`{index + 1}.` [**{track.title}**]({track.uri})\n'

        if player.is_playing:
            current = player.current.title
            url = f'https://youtube.com/watch?v={player.current.identifier}'
            embed = Embed(
                description=f'**{len(player.queue)} tracks**\n\n Now playing: [{current}]({url})\n\n{queue_list}')
        else:
            embed = Embed(description=f'**{len(player.queue)} tracks**\n\n{queue_list}')
        embed.set_footer(text=f'Viewing page {page}/{pages}')
        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(Music(bot))
