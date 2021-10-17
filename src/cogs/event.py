import asyncio
import json
import os

import dateutil.parser
from discord import Embed
from discord import Intents
from discord.ext import commands

intents = Intents.default()
intents.reactions = True

class Event(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.path = (os.path.realpath(__file__)).split('src')

    async def cog_before_invoke(self, ctx):
        if not os.path.isfile(f'{self.path[0]}data/event/{ctx.message.guild.id}.json'):
            with open(f'{self.path[0]}data/event/{ctx.message.guild.id}.json', 'w') as f:
                data = {}
                json.dump(data, f, indent=4)

    async def embed_edit(self,msg,):
        users0 = set()
        users1 = set()
        users2 = set()
        reactions = msg.reactions[0]
        async for user in reactions.users():
            if user == self.bot.user:
                continue
            users0.add(user)
        nl = '\n'
        react_users0 = chr(173) + '\n' f"{nl.join(user.name for user in users0)}"

        reactions = msg.reactions[1]
        async for user in reactions.users():
            if user == self.bot.user:
                continue
            users1.add(user)
        nl = '\n'
        react_users1 = chr(173) + '\n' f"{nl.join(user.name for user in users1)}"

        reactions = msg.reactions[2]
        async for user in reactions.users():
            if user == self.bot.user:
                continue
            users2.add(user)
        nl = '\n'
        react_users2 = chr(173) + '\n' f"{nl.join(user.name for user in users2)}"
        embed = msg.embeds[0]
        embed.set_field_at(0, name=' 👍\n\n ', value=react_users0, inline=True)
        embed.set_field_at(1, name=' 👎\n\n ', value=react_users1, inline=True)
        embed.set_field_at(2, name=' ❓\n\n ', value=react_users2, inline=True)
        await msg.edit(embed=embed)

    async def msg_edit(self, payload):
        if payload.user_id == self.bot.user.id:
            return
        with open(f'{self.path[0]}data/event/{payload.guild_id}.json', 'r') as f:
            data = json.load(f)
            if str(payload.message_id) in data:
                channel = self.bot.get_channel(payload.channel_id)
                msg = await channel.fetch_message(payload.message_id)

                if payload.emoji.name == "👍":
                    for i in ('👎','❓'):
                        try:
                            await msg.remove_reaction(i, payload.member)
                        except Exception:
                            pass
                    await self.embed_edit(msg)


                elif payload.emoji.name == '👎':
                    for i in ('👍','❓'):
                        try:
                            await msg.remove_reaction(i, payload.member)
                        except Exception:
                            pass
                    await self.embed_edit(msg)

                elif payload.emoji.name == '❓':
                    for i in ('👍','👎'):
                        try:
                            await msg.remove_reaction(i, payload.member)
                        except Exception:
                            pass
                    await self.embed_edit(msg)

                elif payload.emoji.name == '📝':
                    if str(payload.member) != data[f"{payload.message_id}"]['author']:
                        await msg.remove_reaction('📝',payload.member)
                        return
                    embed=Embed(description='What do you want to do? \n '
                                            '1️⃣ change date and time of the event \n '
                                            '2️⃣ change name of the event \n '
                                            '3️⃣ nothing \n '
                                            '❌ delete the event')

                    send_msg = await payload.member.send(embed=embed)
                    reactions =('1️⃣','2️⃣','3️⃣','❌')
                    for i in reactions:
                        await send_msg.add_reaction(emoji=i)
                    await msg.remove_reaction('📝',payload.member)

                    try:
                        def check_reaction(m):
                            return m.channel_id == send_msg.channel.id

                        def check_message(m):
                            return m.channel.id == send_msg.channel.id

                        reaction = await self.bot.wait_for('raw_reaction_add',timeout=30,check=check_reaction)

                        if reaction.emoji.name == '1️⃣':
                            await payload.member.send(embed=Embed(description='Enter new date for the event'))
                            response = await self.bot.wait_for('message',check=check_message,timeout=60)
                            date_parse = dateutil.parser.parse(response.content, fuzzy=True, dayfirst=True)
                            date = date_parse.strftime("%d.%m.%Y %H:%M")
                            embed=msg.embeds[0]
                            embed.title = data[f"{payload.message_id}"]['text']+' '+date
                            await msg.edit(embed=embed)
                            await payload.member.send(embed=Embed(description='event date updated'))
                            data[f"{payload.message_id}"]['date']=date
                            with open(f'{self.path[0]}data/event/{payload.guild_id}.json', 'w') as t:
                                json.dump(data, t, indent=4)

                        elif reaction.emoji.name == '2️⃣':
                            await payload.member.send(embed=Embed(description='Enter new name for the event'))

                            response = await self.bot.wait_for('message',check=check_message,timeout=60)
                            embed=msg.embeds[0]
                            embed.title = response.content+' '+data[f"{payload.message_id}"]['date']
                            await msg.edit(embed=embed)
                            await payload.member.send(embed=Embed(description='event name updated'))
                            data[f"{payload.message_id}"]['text'] = response.content
                            with open(f'{self.path[0]}data/event/{payload.guild_id}.json', 'w') as t:
                                json.dump(data, t, indent=4)
                        elif reaction.emoji.name == '3️⃣':
                            await payload.member.send(embed=Embed(description='did nothing'))
                            return
                        elif reaction.emoji.name == '❌':
                            await msg.delete()
                            data.pop(f'{payload.message_id}')
                            with open(f'{self.path[0]}data/event/{payload.guild_id}.json', 'w') as d:
                                json.dump(data, d, indent=4)
                            await payload.member.send(embed=Embed(description='event deleted'))
                    except asyncio.TimeoutError:
                        await payload.member.send(embed=Embed(description='timed out'))


    @commands.command(brief='creates an event, format: text date time',
                      help="date formats: 01.12.21, 01.12 or 1.12 \ntime format:HH:MM (18:23)")
    async def event(self, ctx, *, content):
        if ctx.author.bot:
            return
        try:
            date_parse = dateutil.parser.parse(content, fuzzy_with_tokens=True, dayfirst=True)
            date = date_parse[0].strftime("%d.%m.%Y %H:%M")
            text = ''.join(date_parse[1])

            embed = Embed(title=text + date)
            embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.avatar_url)
            embed.add_field(name=' 👍\n\n ', value=chr(173), inline=True)
            embed.add_field(name=' 👎\n\n ', value=chr(173), inline=True)
            embed.add_field(name=' ❓\n\n ', value=chr(173), inline=True)
            embed.set_footer(text='react with 👍, 👎 or ❓, 📝 to edit ')
            msg = await ctx.send(embed=embed)
            reactions = ('👍','👎','❓','📝')
            for i in reactions :
                await msg.add_reaction(emoji=i)

            with open(f'{self.path[0]}data/event/{ctx.message.guild.id}.json', 'r') as f:
                data = json.load(f)
                data[msg.id] = {"date": date,"author": str(ctx.author), "text": text}

            with open(f'{self.path[0]}data/event/{ctx.message.guild.id}.json', 'w') as f:
                json.dump(data, f, indent=4)
            await ctx.message.delete()

        except dateutil.parser._parser.ParserError:
            raise commands.CommandInvokeError('Unsupported date/time format.')

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        if payload.emoji.name in ('👍','👎','❓','📝'):

            await self.msg_edit(payload)

    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload):
        if payload.emoji.name in ('👍', '👎', '❓'):
            await self.msg_edit(payload)

def setup(bot):
    bot.add_cog(Event(bot))
