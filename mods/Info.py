import asyncio
import time
import steam
import steamapi
import discord
import datetime
import texttable
import wolframalpha
import copy
import random
import aiohttp
from discord.ext import commands
from utils import checks
from steam.steamid import SteamId
from steam.steamprofile import SteamProfile
from steam.steamaccountuniverse import SteamAccountUniverse
from steam.steamaccounttype import SteamAccountType
from mods.cog import Cog
cool = '```xl\n{0}\n```'
code = '```py\n{0}\n```'
diff = '```diff\n{0}\n```'
start_time = time.time()
wa = wolframalpha.Client('')

class Info(Cog):
    def __init__(self, bot):
        super().__init__(bot)
        self.cursor = bot.mysql.cursor
        self.discord_path = bot.path.discord
        self.files_path = bot.path.files
        self.bytes_download = bot.bytes_download
        self.truncate = bot.truncate
        self.get_json = bot.get_json

    @commands.command()
    async def help(self, ctx, *, cmd: str = None):
        'help'
        try:
            if cmd and (cmd in self.bot.commands):
                nctx = copy.copy(ctx)
                nctx.command = self.bot.commands[cmd]
                await self.bot.command_help(nctx)
            else:
                await ctx.message.channel.send(
                    'Please Note: The Following Documentation is NOT complete. I am still adding commands and these are just the commands for the "Fun" module'
                )
                await ctx.message.channel.send(
                    '{0}: https://gist.github.com/Murmiration/0a4e6b83322a7b22878fba608eba705a#file-murmsobot-md'.format(
                        ctx.author.mention))
        except Exception as e:
            print(e)

    @commands.command(aliases=['server'])
    async def guild(self, ctx):
        'server info'
        if isinstance(ctx.channel, discord.abc.PrivateChannel):
            await ctx.send('This is a DM convo, idiot.')
            return
        try:
            guild = ctx.guild
            embed = discord.Embed()
            online = str(
                sum((1 for member in guild.members
                     if (member.status == discord.Status.online) or (member.status == discord.Status.idle))))
            embed.title = ':desktop: **{0}** Information:\n'.format(guild)
            msg = ':id:: `{0}`\n'.format(guild.id)
            msg += ':map: Region: __{0}__\n'.format(str(guild.region))
            msg += ':busts_in_silhouette: Users: **{0}**/{1}\n'.format(online, len(guild.members))
            msg += ':calendar_spiral: Created: `{0}`\n'.format(str(guild.created_at.strftime('%m/%d/%Y %H:%M:%S')))
            msg += ':bust_in_silhouette: Owner: `{0}`\n'.format(guild.owner)
            if guild.verification_level:
                msg += ':exclamation: Verification Level: **{0}**\n'.format(str(guild.verification_level).upper())
            if ctx.guild.afk_channel:
                msg += ':telephone_receiver: AFK Channel: {0}\n'.format(ctx.guild.afk_channel.mention)
                msg += ':keyboard: AFK Timeout: {0} minutes\n'.format(str(int(int(ctx.guild.afk_timeout) / 60)))
            voice = 0
            text = 0
            for channel in guild.channels:
                if isinstance(channel, discord.TextChannel):
                    text += 1
                elif isinstance(channel, discord.VoiceChannel):
                    voice += 1
            msg += ':arrow_forward: Channels: `{0}` Text | `{1}` Voice | **{2}** Total\n'.format(
                text, voice, str(len(guild.channels)))
            msg += ':arrow_forward: Roles: `{0}`\n'.format(str(len(guild.roles)))
            if len(guild.emojis) != 0:
                emotes = ''
                for emote in guild.emojis:
                    if not emote.animated:
                        emotes += '<:{0}:{1}>'.format(emote.name, emote.id)
                msg += ':arrow_forward: Emotes: {0}\n'.format(emotes)
            embed.description = msg
            embed.set_thumbnail(url=guild.icon_url)
            embed.color = discord.Color.blue()
            await ctx.send(embed=embed)
        except Exception as e:
            await ctx.send(e)

    @commands.command()
    async def invite(self, ctx):
        'returns invite link for bot'
        msg = diff.format('+ Invite me to your server with this url')
        msg += '[INVITES ARE CURRENTLY PRIVATE WHILE BOT IS IN BETA, SORRY!]'
        msg += diff.format('- Uncheck Administrator permission if you do not need Admin/Moderation commands.')
        await ctx.message.channel.send(msg)

    @commands.command(aliases=['userinfo', 'user', 'uinfo'])
    async def info(self, ctx, *users: discord.User):
        'Returns inputed users info.'
        try:
            if len(users) == 0:
                users = [ctx.author]
            guild = ctx.guild
            for user in users:
                embed = discord.Embed()
                seen_on_self = True if user == self.bot.user else False
                seen_on = set([
                    member.guild.name for member in self.bot.get_all_members()
                    if (member == user) and (member.guild != guild)
                ]) if user != self.bot.user else 'ALL OF THEM'
                embed.description = ':id:: `{1}`\n:robot: Bot: {2}\n:inbox_tray: Server Join Date: __{3}__\n:globe_with_meridians: Discord Join Date: __{4}__\n:information_source: Status: **{5}**{6}{7}\n:eyes: Seen On (*Shard #{8}*): **{9}** servers **=>** `{10}`\n:shield: Roles: `{11}`\n'.format(
                    '', user.id, 'Yes' if user.bot else 'No', user.joined_at.strftime('%m/%d/%Y %H:%M:%S'),
                    user.created_at.strftime('%m/%d/%Y %H:%M:%S'),
                    str(user.status).upper(), '\n:joystick: Playing: "{0}"'.format(user.game)
                    if user.game else '', '', self.bot.shard_id,
                    len(seen_on) if (not seen_on_self) else '999999999...', ', '.join(seen_on)
                    if (len(seen_on) >= 1) and (not seen_on_self) else 'none other than here ;-;' if (not seen_on_self)
                    else 'discord mainframe', ', '.join([role.name for role in user.roles]))
                embed.title = '**{0}**'.format(user)
                embed.set_thumbnail(url=user.avatar_url)
                await ctx.send(embed=embed)
        except Exception as e:
            await ctx.message.channel.send(str(e))

    @commands.command()
    async def avatar(self, ctx, *users: discord.User):
        'Returns the input users avatar.'
        if len(users) == 0:
            users = [ctx.author]
        for user in users:
            await ctx.message.channel.send("`{0}`'s avatar is: {1}".format(user, user.avatar_url))

    @commands.command(name='time')
    async def _time(self, ctx):
        'Returns bots date and time.'
        await ctx.message.channel.send('Date is: **{0}**\nTime is: **{1}**'.format(
            time.strftime('%A, %B %d, %Y'), time.strftime('%I:%M:%S %p')))

    @commands.command()
    async def uptime(self, ctx):
        'How long have I been up/online?'
        seconds = time.time() - start_time
        (m, s) = divmod(seconds, 60)
        (h, m) = divmod(m, 60)
        (d, h) = divmod(h, 24)
        (w, d) = divmod(d, 7)
        if s != 0:
            msg = '**{0}** seconds{1}.'.format(int(s), ' :frowning:' if m == 0 else '')
        if m != 0:
            e = ' :slight_frown:.' if h == 0 else '.'
            msg = (' : **{0}** minutes : '.format(int(m)) + msg.replace('.', '')) + e
        if h != 0:
            e = ' :slight_smile:.' if d == 0 else '.'
            msg = (' : **{0}** hours'.format(int(h)) + msg.replace('.', '')) + e
        if d != 0:
            e = ' :smiley:.' if w == 0 else '.'
            msg = (' : **{0}** days'.format(int(d)) + msg.replace('.', '').replace(':slight_smile:', '')) + e
        if w != 0:
            msg = (' : **{0}** weeks {1}'.format(int(w)) +
                   msg.replace('.', '')) + ' :joy: :joy: :joy: :joy: :joy: :joy: :joy: :joy: :joy: :joy:.'
        if m == 0:
            msg = ' ' + msg
        else:
            msg = msg[2:]
        await ctx.message.channel.send(':clock4: Online for{0}'.format(msg))

    steamapi.core.APIConnection(api_key='')

    @commands.command()
    async def steam(self, ctx, stem: str):
        'Returns Steam information of inputed SteamID/Custom URL/Etc'
        try:
            steamId = None
            steamProfile = None
            if steamId is None:
                steamId = SteamId.fromSteamId('{0}'.format(stem))
            if steamId is None:
                steamId = SteamId.fromSteamId3(stem)
            if steamId is None:
                steamId = SteamId.fromSteamId64(stem)
            if steamId is None:
                steamId = SteamId.fromProfileUrl(stem)
            if steamId is None:
                steamProfile = SteamProfile.fromCustomProfileUrl(stem)
                if steamProfile is None:
                    await ctx.message.channel.send('bad steam id')
                    return
                steamId = steamProfile.steamId
            else:
                steamProfile = SteamProfile.fromSteamId(steamId)
            msg = ''
            if (steamProfile is not None) and (steamProfile.displayName is not None):
                msg += ('Username: ' + steamProfile.displayName) + '\n'
            steam_user = steamapi.user.SteamUser(steamId.steamId64)
            if steam_user.state == 0:
                msg += 'Status: Offline\n'
            elif steam_user.state == 1:
                msg += 'Status: Online\n'
            elif steam_user.state == 2:
                msg += 'Status: Busy\n'
            elif steam_user.state == 3:
                msg += 'Status: Away\n'
            elif steam_user.state == 4:
                msg += 'Status: Snooze\n'
            elif steam_user.state == 5:
                msg += 'Status: Looking to Trade\n'
            elif steam_user.state == 6:
                msg += 'Status: Looking to Play\n'
            msg += 'Avatar: "{0}"\n'.format(str(steam_user.avatar_full))
            if steam_user.level != None:
                msg += 'Level: {0}\n'.format(str(steam_user.level))
            if steam_user.currently_playing != None:
                msg += 'Currently Playing: {0}\n'.format(str(steam_user.currently_playing))
            elif steam_user.recently_played != []:
                msg += 'Recently Played: {0}\n'.format(
                    str(steam_user.recently_played).replace('<SteamApp ', '').replace('>', '').replace('[', '').replace(
                        ']', ''))
            msg += 'Created: {0}\n'.format(str(steam_user.time_created))
            msg += ('Steam ID: ' + steamId.steamId) + '\n'
            msg += ('Steam ID 64: ' + str(steamId.steamId64)) + '\n'
            msg += ('Permanent Link: "' + steamId.profileUrl) + '"\n'
            if (steamProfile != None) and (steamProfile.customProfileUrl != None):
                msg += ('Link: "' + steamProfile.customProfileUrl) + '"\n'
            msg = msg.replace("'", '′')
            await ctx.message.channel.send(cool.format(msg))
        except Exception as e:
            await ctx.message.channel.send(code.format((type(e).__name__ + ': ') + str(e)))

    @commands.command()
    async def cinfo(self, ctx):
        'Return Channel Information'
        msg = 'Channel Name: {0}\n'.format(ctx.channel.name)
        msg += 'Channel ID: {0}\n'.format(ctx.channel.id)
        msg += 'Channel Created: {0}\n'.format(ctx.channel.created_at)
        await ctx.message.channel.send(cool.format(msg))

    @commands.command(alias='binfo')
    async def botinfo(self, ctx):
        'Bot Information'
        msg = 'MurmSoBot\n'
        msg += 'Original Creator: NotSoSuper\n'
        msg += 'Current Maintainer: Murm\n'
        msg += 'Library: Discord.py\n'
        msg += 'Original Code: https://github.com/NotSoSuper/NotSoBot\n'
        await ctx.message.channel.send(cool.format(msg))

    @commands.command(aliases=['esearch'])
    async def emotesearch(self, ctx, text: str):
        try:
            processmsg = await ctx.channel.send('Please wait...')
            emotelist = []
            for guild in self.bot.guilds:
                for emote in guild.emojis:
                    if text.lower() in emote.name.lower():
                        if not emote.animated:
                            emotelist = emotelist + [emote]
            if emotelist == []:
                await processmsg.delete()
                await ctx.message.channel.send('No Results.')
            else:
                random.shuffle(emotelist)
                emcontent = ''
                for emote in emotelist:
                    emcontent = emcontent + '<:{0}:{1}> '.format(emote.name, emote.id)
                em = discord.Embed(description=emcontent)
                em.set_author(name='Results for {}'.format(text), icon_url=self.bot.user.avatar_url)
                em.set_footer(text='rclick > open link for download')
                await processmsg.delete()
                results = await ctx.channel.send(embed=em)
        except Exception as e:
            await processmsg.delete()
            await ctx.message.channel.send(e)

    @commands.command()
    @commands.cooldown(1, 120, commands.BucketType.guild)
    async def stats(self, ctx):
        try:
            sql = 'SELECT `messages_id` FROM `messages` WHERE action=0 ORDER BY `messages_id` DESC LIMIT 1'
            message_count = self.cursor.execute(sql).fetchall()[0]['messages_id']
            sql = 'SELECT COUNT(`action`) FROM `messages` WHERE action=1'
            message_delete_count = self.cursor.execute(sql).fetchall()[0]['COUNT(`action`)']
            sql = 'SELECT COUNT(`action`) FROM `messages` WHERE action=2'
            message_edit_count = self.cursor.execute(sql).fetchall()[0]['COUNT(`action`)']
            sql = 'SELECT COUNT(`command`) FROM `command_logs`'
            command_count = self.cursor.execute(sql).fetchall()[0]['COUNT(`command`)']
            sql = 'SELECT COUNT(`command`) FROM `command_logs` WHERE server={0}'.format(ctx.guild.id)
            guild_command_count = self.cursor.execute(sql).fetchall()[0]['COUNT(`command`)']
            sql = 'SELECT `command`, COUNT(`command`) AS magnitude FROM `command_logs` GROUP BY `command` ORDER BY magnitude DESC LIMIT 6'
            command_magnitude = self.cursor.execute(sql).fetchall()
            sql = 'SELECT `server`, `server_name`, COUNT(`command`) AS magnitude FROM `command_logs` GROUP BY `server` ORDER BY magnitude DESC LIMIT 5'
            guild_magnitude = self.cursor.execute(sql).fetchall()
            sql = 'SELECT * FROM `stats`'
            results = self.cursor.execute(sql).fetchall()
            guild_list = []
            for shard in results:
                guild_list.append([shard['largest_member_server_name'], shard['largest_member_server']])
            count = 0
            counts = []
            for x in guild_list:
                count = int(x[1])
                counts.append(count)
            max_ = int(max(counts))
            max_index = int(counts.index(max_))
            biggest_guild_name = guild_list[max_index][0]
            biggest_guild_count = guild_list[max_index][1]
            magnitude_table = texttable.Texttable(max_width=90)
            for x in guild_magnitude:
                magnitude_table.add_rows([['Server', 'Commands'], [x['server_name'][:25], x['magnitude']]])
            magnitude_msg = magnitude_table.draw()
            command_table = texttable.Texttable(max_width=90)
            for x in command_magnitude:
                command_table.add_rows([['Command', 'Count'], [x['command'], x['magnitude']]])
            command_msg = command_table.draw()
            command_stats_msg = (magnitude_msg + '\n\n') + command_msg
            text_channels = 0
            voice_channels = 0
            for shard in results:
                text_channels += int(shard['text_channels'])
                voice_channels += int(shard['voice_channels'])
            user_count = 0
            unique_users = 0
            guild_count = 0
            for shard in results:
                guild_count += int(shard['servers'])
                user_count += int(shard['users'])
                unique_users += int(shard['unique_users'])
            seconds = time.time() - start_time
            (m, s) = divmod(seconds, 60)
            (h, m) = divmod(m, 60)
            (d, h) = divmod(h, 24)
            (w, d) = divmod(d, 7)
            if s != 0:
                uptime = '**{0}** seconds.'.format(int(s))
            if m != 0:
                uptime = ' : **{0}** minutes : '.format(int(m)) + uptime
            if h != 0:
                uptime = ' : **{0}** hours'.format(int(h)) + uptime
            if d != 0:
                uptime = ' : **{0}** days'.format(int(d)) + uptime
            if w != 0:
                uptime = ' : **{0}** weeks {1}'.format(int(w)) + uptime
            if m == 0:
                uptime = ' ' + uptime
            else:
                uptime = uptime[2:]
            msg = ':bar_chart: **User/Bot Statistics**\n'
            msg += ('> Uptime: ' + uptime) + '\n'
            msg += '> On **{0}** Servers\n'.format(guild_count)
            msg += '> **{0}** Text channels | **{1}** Voice\n'.format(text_channels, voice_channels)
            msg += '> Serving **{0}** Users\n'.format(user_count)
            msg += '> Unique Users: **{0}**\n'.format(unique_users)
            msg += "> Who've messaged **{0}** times ".format(message_count)
            msg += 'where **{0}** of them have been edited '.format(message_edit_count)
            msg += 'and **{0}** deleted.\n'.format(message_delete_count)
            msg += '> In total **{0}** commands have been called, __{1}__ from this server.\n'.format(
                command_count, guild_command_count)
            msg += ':keyboard: **Command Statistics**\n'
            msg += '```\n{0}```'.format(command_stats_msg)
            msg += ':desktop: **Server Statistics**\n'
            msg += '> Largest Server: **{0}** (Users: **{1}**)\n'.format(biggest_guild_name, biggest_guild_count)
            msg += '> Most used on: **{0}** (Commands: **{1}**/{2})\n'.format(
                guild_magnitude[0]['server_name'], guild_magnitude[0]['magnitude'], command_count)
            await ctx.message.channel.send(msg)
        except Exception as e:
            print(e)

    @commands.command(aliases=['so', 'stack', 'csearch', 'stacko', 'stackoverflow'])
    async def sof(self, ctx, *, text: str):
        try:
            api = 'https://api.stackexchange.com/2.2/search?order=desc&sort=votes&site=stackoverflow&intitle={0}'.format(
                text)
            r = await self.get_json(api)
            q_c = len(r['items'])
            if q_c == 0:
                api = 'https://api.stackexchange.com/2.2/similar?order=desc&sort=votes&site=stackoverflow&title={0}'.format(
                    text)
                r = await self.get_json(api)
                q_c = len(r['items'])
            if q_c == 0:
                api = 'https://api.stackexchange.com/2.2/search/excerpts?order=desc&sort=votes&site=stackoverflow&q={0}'.format(
                    text)
                r = await self.get_json(api)
                q_c = len(r['items'])
            if q_c == 0:
                api = 'https://api.stackexchange.com/2.2/search/advanced?order=desc&sort=votes&site=stackoverflow&q={0}'.format(
                    text)
                r = await self.get_json(api)
                q_c = len(r['items'])
            if q_c == 0:
                await ctx.message.channel.send(':warning: `No results found on` <https://stackoverflow.com>')
                return
            if q_c > 5:
                msg = '**First 5 Results For: `{0}`**\n'.format(text)
            else:
                msg = '**First {0} Results For: `{1}`**\n'.format(str(q_c), text)
            count = 0
            for s in r['items']:
                if q_c > 5:
                    if count == 5:
                        break
                elif count == q_c:
                    break
                epoch = int(s['creation_date'])
                date = str(datetime.datetime.fromtimestamp(epoch).strftime('%m-%d-%Y'))
                msg += '```xl\nTitle: {0}\nLink: {1}\nCreation Date: {2}\nScore: {3}\nViews: {4}\nIs-Answered: {5}\nAnswer Count: {6}```'.format(
                    s['title'], s['link'].replace('http://', '').replace('https://', '').replace('www.', ''), date,
                    s['score'], s['view_count'], s['is_answered'], s['answer_count'])
                count += 1
            await ctx.message.channel.send(msg)
        except Exception as e:
            await ctx.message.channel.send(code.format(e))

    @commands.command(aliases=['wa', 'alpha', 'walpha'])
    @commands.cooldown(1, 5)
    async def wolframalpha(self, ctx, *, q: str):
        result = wa.query(q)
        if result['@success'] == 'false':
            await ctx.message.channel.send(':warning: `No results found on` <https://wolframalpha.com>')
        else:
            msg = ''
            for pod in result.pods:
                if int(pod['@numsubpods']) > 1:
                    for sub in pod['subpod']:
                        subpod_text = sub['plaintext']
                        if subpod_text is None:
                            continue
                        msg += '**{0}**: `{1}`\n'.format(pod['@title'], subpod_text)
                else:
                    subpod_text = pod['subpod']['plaintext']
                    if subpod_text is None:
                        continue
                    msg += '**{0}**: `{1}`\n'.format(pod['@title'], subpod_text)
            await ctx.message.channel.send(msg)


def setup(bot):
    bot.add_cog(Info(bot))