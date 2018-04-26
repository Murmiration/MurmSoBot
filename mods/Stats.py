import discord
import time
import requests
import io
from discord.ext import commands
from utils import checks
from mods.cog import Cog
cool = '```xl\n{0}\n```'


class Stats(Cog):
    def __init__(self, bot):
        super().__init__(bot)
        self.cursor = bot.mysql.cursor
        self.queue_message = bot.queue_message
        self.discord_path = bot.path.discord
        self.files_path = bot.path.files

    async def get_largest_guild(self):
        guild_count = [len(i.members) for i in self.bot.guilds]
        max_ = max(guild_count)
        max_index = guild_count.index(max_)
        guilds = [i for i in self.bot.guilds]
        max_guild = guilds[max_index]
        thing = '{0}\n{1}'.format(max_guild.name, max_)
        return (max_guild.name, max_)

    async def get_channels(self):
        text_channels = 0
        voice_channels = 0
        for guild in self.bot.guilds:
            for channel in guild.channels:
                if channel.type == discord.ChannelType.text:
                    text_channels += 1
                if channel.type == discord.ChannelType.voice:
                    voice_channels += 1
        return (text_channels, voice_channels)

    async def update_stats(self):
        sql = 'REPLACE INTO `stats` (`shard`, `servers`, `largest_member_server`, `largest_member_server_name`, `users`, `unique_users`, `text_channels`, `voice_channels`) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)'
        guilds = len(self.bot.guilds)
        largest = await self.get_largest_guild()
        largest_member_guild = largest[1]
        largest_member_guild_name = largest[0]
        users_array = [x for x in self.bot.get_all_members()]
        users = len(users_array)
        unique_users = len(set(users_array))
        channels = await self.get_channels()
        text_channels = channels[0]
        voice_channels = channels[1]
        self.cursor.execute(sql, (self.bot.shard_id, guilds, largest_member_guild, largest_member_guild_name, users,
                                  unique_users, text_channels, voice_channels))
        self.cursor.commit()

    @commands.command()
    @checks.is_owner()
    async def updatestats(self, ctx):
        await self.update_stats()
        await self.carbon()
        await self.discord_pw()
        await ctx.send(':white_check_mark: Upated Stats.')

    async def guild_count(self):
        sql = 'SELECT * FROM `stats`'
        result = self.cursor.execute(sql).fetchall()
        count = 0
        for shard in result:
            count += int(shard['servers'])
        return count

    sent = 0
    key = ''
    API = 'https://www.carbonitex.net/discord/data/botdata.php'

    async def carbon(self):
        guild_count = await self.guild_count()
        data = {
            'key': self.key,
            'servercount': guild_count,
            'botname': self.bot.user.name,
            'botid': self.bot.user.id,
            'logoid': self.bot.user.avatar_url[60:].replace('.jpg', ''),
            'ownerid': 130070621034905600,
            'ownername': 'NotSoSuper',
        }
        try:
            timestamp = time.strftime('%H:%M:%S')
            r = requests.post(self.API, json=data)
            self.sent += 1
            s_data = data
            s_data['key'] = 'no'
            msg = 'Carbon Payload #{1} returned {0.status_code} {0.reason} for {2}\n '.format(r, str(self.sent), s_data)
            await self.queue_message(178313681786896384, '`[{0}]`\n'.format(timestamp) + cool.format(msg))
        except Exception as e:
            msg = (
                '/!\\=================/!\\==/!\\=================/!\\\nERROR: An error occurred while fetching statistics: '
                + str(e)) + '\n/!\\=================/!\\==/!\\=================/!\\'
            await self.queue_message(178313681786896384, cool.format(msg))

    pw_sent = 0
    pw_key = ''

    async def discord_pw(self):
        API = 'https://bots.discord.pw/api/bots/{0}/stats'.format(self.bot.user.id)
        data = {
            'shard_id': self.bot.shard_id,
            'shard_count': self.bot.shard_count,
            'server_count': len(self.bot.guilds),
        }
        headers = {
            'Authorization': self.pw_key,
        }
        try:
            timestamp = time.strftime('%H:%M:%S')
            r = requests.post(API, json=data, headers=headers)
            self.pw_sent += 1
            msg = 'Discord.pw Payload #{1} {0.status_code} {0.reason} for {2}\n '.format(r, str(self.pw_sent), data)
            await self.queue_message(178313681786896384, '`[{0}]`\n'.format(timestamp) + cool.format(msg))
        except Exception as e:
            await self.queue_message(178313681786896384, cool.format(msg))

    async def on_guild_join(self, guild):
        await self.update_stats()
        await self.carbon()
        await self.discord_pw()

    async def on_guild_leave(self, guild):
        await self.update_stats()
        await self.carbon()
        await self.discord_pw()

    async def on_ready(self):
        await self.update_stats()
        await self.carbon()
        await self.discord_pw()


def setup(bot):
    bot.add_cog(Stats(bot))