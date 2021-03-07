import discord
from discord.ext import commands

from handlers.audio import AudioHandler
from utils.general import StrUtils, EmbedUtils

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
        added_by=context.author
        if StrUtils.isURL(song):
            res = await audio_handler.download_and_add_song(song, channel_id, added_by=added_by)
        else:
            res = await audio_handler.add_song(song, channel_id, added_by=added_by)
        if not res:
            await context.send('This audio file could not be played')


    @commands.command(name='deepfry', help='Adds a song to the queue to be played with the deepfry audio distortion')
    async def deepfry_song(self, context, song, channel_id=None):
        audio_handler = self._audio_handlers[context.guild.id]
        added_by=context.author
        if StrUtils.isURL(song):
            res = await audio_handler.download_and_add_song(song, channel_id, 'deepfry', added_by=added_by)
        else:
            res = await audio_handler.add_song(song, channel_id, 'deepfry', added_by=added_by)
        if not res:
            await context.send('This audio file could not be played')


    @commands.command(name='next', help='Plays the next song in the queue')
    async def play_next(self, context):
        audio_handler = self._audio_handlers[context.guild.id]
        await audio_handler.skip_song()


    @commands.command(name='killmusic', help='deletes the queue and ends the current song')
    async def kill_music(self, context):
        audio_handler = self._audio_handlers[context.guild.id]
        await audio_handler.kill_music()


    @commands.command(name='list', help='Lists songs in the queue')
    async def list_queue(self, context):
        # TODO handle long queues by splitting embeds based on character limit
        # TODO add more info per song including deepfried/regular, length, thumbnail
        # TODO include creating the embed field in the Song class, it looks gross here
        audio_handler = self._audio_handlers[context.guild.id]
        # Create an empty embed
        embed = EmbedUtils.get_list_embed_base()
        # Add Now Playing Song
        if audio_handler.playing:
            EmbedUtils.add_now_playing_field(embed, audio_handler.playing)
        # Iterate over current queue
        q = audio_handler.get_queue()
        for song in q._queue:
            EmbedUtils.add_queued_song_field(embed, song)
        if not embed.fields:
            EmbedUtils.add_empty_list_field(embed)
        await context.send(embed=embed)
