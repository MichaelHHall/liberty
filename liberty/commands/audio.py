import discord
from discord.ext import commands

from handlers.audio import AudioHandler

# A file for defining audio commands
class Audio(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self._last_member = None
        self._audio_handlers = {}
        for guild in bot.guilds:
            self.init_handler(guild)


    def init_handler(self, guild):
        print('init handler for guild ', guild.id)
        if guild.id not in self._audio_handlers.keys():
            self._audio_handlers[guild.id] = AudioHandler(guild)


    @commands.command(name='play', help='Adds a song to the queue')
    async def play_song(self, context, song, channel_id=None):
        audio_handler = self._audio_handlers[context.guild.id]
        await audio_handler.add_song(song)


    @commands.command(name='next', help='Plays the next song in the queue')
    async def play_next(self, context):
        audio_handler = self._audio_handlers[context.guild.id]
        await audio_handler.skip_song()


    @commands.command(name='list', help='Lists songs in the queue')
    async def list_queue(self, context):
        audio_handler = self._audio_handlers[context.guild.id]
        await context.send(audio_handler.get_queue())
