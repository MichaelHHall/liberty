import discord
from discord.ext import commands
import os

from handlers.audio import AudioHandler
from utils.general import StrUtils, EmbedUtils
from utils.constants import _AUDIO_DIR

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


    @commands.command(name='save', help='Saves the selected song to the assets directory')
    async def save_song(self, context, name, queue_position=None):
        audio_handler = self._audio_handlers[context.guild.id]
        if queue_position:
            try:
                queue_position = int(queue_position)
            except:
                # Probably should do some error reporting here, but.....
                return
        await audio_handler.save_song(name, queue_position)


    @commands.command(name='availablesongs', help='Lists the available songs in the audio assets directory')
    async def available_songs(self, context):
        # Somehow get list of files in the audio dir
        files = os.listdir(_AUDIO_DIR)
        # Create an empty embed
        embeds = [EmbedUtils.get_list_embed_base(title='Liberty Prime Available Audio Files', description='This is a list of the semi-persistent songs saved in the Liberty Prime audio directory')]
        for file in files:
            if len(embeds[-1].fields) >= 25:
                embeds.append(EmbedUtils.get_list_embed_continuation(len(embeds), title='Liberty Prime Available Audio Files'))
            EmbedUtils.add_available_song_field(embeds[-1], file)
        if not embeds[0].fields:
            EmbedUtils.add_empty_list_field(embeds[-1])
        for embed in embeds:
            await context.send(embed=embed)


    @commands.command(name='playlist', help='Lists songs in the queue')
    async def list_queue(self, context):
        # TODO add more info per song including deepfried/regular, length, thumbnail
        audio_handler = self._audio_handlers[context.guild.id]
        # Create an empty embed
        embeds = [EmbedUtils.get_list_embed_base(title='Liberty Prime Audio Queue', description='These are all of the songs waiting to be played by Liberty Prime')]
        # Add Now Playing Song
        if audio_handler.playing:
            EmbedUtils.add_now_playing_field(embeds[-1], audio_handler.playing)
        # Iterate over current queue
        q = audio_handler.get_queue()
        for song in q._queue:
            if len(embeds[-1].fields) >= 25:
                embeds.append(EmbedUtils.get_list_embed_continuation(len(embeds), title='Liberty Prime Audio Queue'))
            EmbedUtils.add_queued_song_field(embeds[-1], song)
        if not embeds[0].fields:
            EmbedUtils.add_empty_list_field(embeds[-1])
        for embed in embeds:
            await context.send(embed=embed)
