import discord
import asyncio
import random
import re
import sys, linecache
from discord.ext import commands
from mods.cog import Cog
from utils import checks


class Markov(Cog):
    def __init__(self, bot):
        super().__init__(bot)
        self.cursor = bot.mysql.cursor
        self.cache = {}
        self.files_path = bot.path.files
        self.guilds = [110373943822540800]
        self.users = {
            130070621034905600: 110373943822540800,
        }

    async def add_markov(self, path, txt):
        split = re.split('\\s+', txt)
        for s in split:
            if len(s) >= 200:
                split.remove(s)
        msg = ' '.join(split).replace('`', '').replace("'", "\\'").replace(':', '').replace('\\', '\\\\').replace(
            '{', '\\{').replace('}', '\\}')
        learn_code = 'markov.learn(`{0}`);'.format(msg)
        code = "var markov_ultra = require('markov-ultra');var markov = new markov_ultra['default']('{0}', 6000000000);{1}".format(
            path, learn_code)
        await self.bot.run_process(['node', '-e', code])

    async def on_message(self, message):
        if isinstance(channel, discord.abc.PrivateChannel):
            return
        elif message.author.bot or message.content.startswith(('!', '.', '!!', '`', '-', '=', ',', '/', '?')):
            return
        if message.guild.id in self.guilds:
            path = self.files_path('markov/{0}/'.format(message.guild.id))
            await self.add_markov(path, message.content)
        if (message.author.id in self.users.keys()) and (self.users[message.author.id] == message.guild.id):
            path = self.files_path('markov/{0}_{1}/'.format(message.author.id, message.guild.id))
            await self.add_markov(path, message.content)

    @commands.group(aliases=['mark', 'm'], no_pm=True, invoke_without_command=True)
    async def markov(self, ctx, *, text: str = None):
        for m in ctx.message.mentions:
            user = m
            text = text.replace(user.mention, '')
            break
        else:
            user = False
        if user:
            if user.id not in self.users.keys():
                return
            elif self.users[user.id] != ctx.guild.id:
                return
        if ctx.guild.id not in self.guilds:
            return
        path = self.files_path(
            'markov/{0}/'.format('{0}_{1}'.format(ctx.author.id, ctx.guild.id) if user else ctx.guild.id))
        code = "var markov_ultra = require('markov-ultra');var markov = new markov_ultra['default']('{0}', 6000000000);console.log(markov.generate(2, 2000{1}))".format(
            path, ', `{0}`'.format(text) if text else '')
        result = await self.bot.run_process(['node', '-e', code], True)
        if result and (result != '') and (result != '\n'):
            await ctx.send(
                str(result).replace('http//', 'http://').replace('https//', 'https://').replace('\\\\', '\\'))
        else:
            await ctx.send(':warning: **Markov Failed**.')

    @markov.command(name='generate')
    @checks.is_owner()
    async def markov_generate(self, ctx, user: str = None):
        try:
            _x = await ctx.channel.send('ok, this ~~might~~ will take a while')
            if user:
                user = self.bot.funcs.find_member(ctx.guild, user, 2)
                if (not user):
                    await ctx.send('Invalid User.')
                    return
            markov_path = self.files_path(
                'markov/{0}/'.format('{0}_{1}'.format(ctx.author.id, ctx.guild.id) if user else ctx.guild.id))
            if user:
                code_path = self.files_path('markov/generated/{0}.js'.format(user.name.lower()))
                sql = 'SELECT * FROM `messages` WHERE server={0} AND user_id={1} LIMIT 60000'.format(
                    ctx.guild.id, user.id)
            else:
                code_path = self.files_path('markov/generated/{0}.js'.format(ctx.guild.name.lower()))
                sql = 'SELECT * FROM `messages` WHERE server={0} LIMIT 400000'.format(ctx.guild.id)
            await _x.edit(content='Fetching messages.')
            result = self.cursor.execute(sql).fetchall()
            await _x.edit(content='Generating code.')
            msgs = []
            for x in result:
                if x['message'].startswith(('!', '.', '!!', '`', '-', '=', ',', '/', '?')):
                    continue
                user = ctx.guild.get_member(x['user_id'])
                if user and user.bot:
                    continue
                msgs.append(x['message'])
            learn_code = []
            for msg in msgs:
                if msg == '':
                    continue
                split = re.split('\\s+', msg)
                for s in split:
                    if len(s) >= 200:
                        split.remove(s)
                msg = ' '.join(split).replace('`', '').replace("'", "\\'").replace(':',
                                                                                   '').replace('\\', '\\\\').replace(
                                                                                       '{', '\\{').replace('}', '\\}')
                learn_code.append('markov.learn(`{0}`);'.format(msg))
            code = "'use strict';\nvar markov_ultra = require('markov-ultra');\nvar markov = new markov_ultra['default']('{0}', 6000000000);\n{1}\n".format(
                markov_path, '\n'.join(learn_code))
            await _x.edit(content='Code generated, saving.')
            f = open(code_path, 'w')
            f.write(code)
            f.close()
            await _x.edit(content=':white_check_mark: Done, `{0}`'.format(code_path))
        except:
            (exc_type, exc_obj, tb) = sys.exc_info()
            f = tb.tb_frame
            lineno = tb.tb_lineno
            filename = f.f_code.co_filename
            linecache.checkcache(filename)
            line = linecache.getline(filename, lineno, f.f_globals)
            await ctx.send('EXCEPTION IN ({}, LINE {} "{}"): {}'.format(filename, lineno, line.strip(), exc_obj))


def setup(bot):
    bot.add_cog(Markov(bot))