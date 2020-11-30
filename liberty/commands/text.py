import discord
from discord.ext import commands

# A file for defining basic info commands
class Text(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self._last_member = None

    @commands.command(name='server', help = 'Fetches server information')
    async def fetchServerInfo(self, context):
        guild = context.guild

        await context.send(f'Server Name: {guild.name}')
        await context.send(f'Server Size: {len(guild.members)}')
        await context.send(f'Server ID: {guild.id}')


    @commands.command(name='N', help = 'Start a chain reaction that cannot be stopped')
    async def gamer(self, context):
        await context.send('!I')


    @commands.command(name='echo', help = 'echo a comment')
    async def echo_message(self, context, *msg):
        await context.send(' '.join(msg))
