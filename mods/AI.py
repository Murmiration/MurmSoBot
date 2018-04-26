import discord
import asyncio
import re
from cleverbot import Cleverbot
from discord.ext import commands
from chatterbot import ChatBot
from mods.cog import Cog
from utils import checks
chatbot = ChatBot(
    'NotSoBot',
    trainer='chatterbot.trainers.ChatterBotCorpusTrainer',
    storage_adapter='chatterbot.storage.MongoDatabaseAdapter',
    output_adapter='chatterbot.output.OutputFormatAdapter',
    output_format='text',
    database='chatterbot-database',
    database_uri='mongodb://localhost:27017/')
cb = Cleverbot()


class AI(Cog):
    def __init__(self, bot):
        super().__init__(bot)
        self.ai_target = {}

    @commands.command(aliases=['cb'])
    async def cleverbot(self, ctx, *, question: str):
        await ctx.send(':speech_balloon: ' + cb.ask(question)[:2000])

    @commands.group(aliases=['artificialinteligence', 'talk'], invoke_without_command=True)
    async def ai(self, ctx, *, msg: str = None):
        'Toggle AI Targeted Responses'
        if msg != None:
            await ctx.channel.trigger_typing()
            ask_msg = ctx.message.content[:899]
            await ctx.send('**{0}**\n'.format(ctx.author.name) + str(chatbot.get_response(ask_msg)))
            return
        if any([ctx.author.id == x for x in self.ai_target]) == False:
            await ctx.send('ok, AI targetting user `{0}`\n'.format(ctx.author.name))
            self.ai_target.update({
                ctx.author.id: ctx.channel.id,
            })
        else:
            await ctx.send('ok, removed AI target `{0}`'.format(ctx.author.name))
            del self.ai_target[ctx.author.id]

    @ai.command(name='remove', aliases=['forceremove'])
    @checks.mod_or_perm(manage_server=True)
    async def ai_remove(self, ctx, *users: discord.User):
        for user in users:
            if user.id in self.ai_target.keys():
                del self.ai_target[user.id]
                await ctx.send(':white_check_mark: Removed `{0}` from AI Target.'.format(user))
            else:
                await ctx.send(':warning: `{0}` is not in the AI Target!'.format(user))

    async def on_message(self, message):
        if (not (message.author.id in self.ai_target.keys())):
            return
        elif self.ai_target[message.author.id] != message.channel.id:
            return
        if message.author == self.bot.user:
            return
        if message.content.startswith('.'):
            return
        check = await self.bot.funcs.command_check(message, 'off')
        if check:
            del self.ai_target[message.author.id]
            return
        ask_msg = message.clean_content[:899]
        ask_msg = re.sub('[^0-9a-zA-Z]+', ' ', ask_msg)
        ask_msg = ask_msg.replace('`', '')
        if len(message.mentions) != 0:
            for s in message.mentions:
                ask_msg = ask_msg.replace(s.mention, s.name)
        try:
            await message.channel.trigger_typing()
            msg = '**{0}**\n'.format(message.author.name) + str(chatbot.get_response(ask_msg))
            if len(msg) != 0:
                await message.channel.send(msg)
        except:
            del self.ai_target[message.author.id]
            return
        asyncio.sleep(1)


def setup(bot):
    bot.add_cog(AI(bot))