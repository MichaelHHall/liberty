import discord
from pathlib import Path
import validators
import datetime

from utils.constants import _TMP_DIR

class FSUtils():
    @staticmethod
    def isTmpDir(path):
        # Return true if this file is anywhere in the tmp dir
        # This will be used to tell the program if it is safe to delete a file
        tmpdir = Path(_TMP_DIR).resolve()
        testpath = Path(path).resolve()
        return tmpdir in [testpath] + [p for p in testpath.parents]


class StrUtils():
    @staticmethod
    def isURL(string):
        return validators.url(string)


    @staticmethod
    def generateFilename(basename='liberty'):
        timestamp = int(datetime.datetime.now().timestamp()*1000)
        return basename+'-'+str(timestamp)


class EmbedUtils():
    @staticmethod
    def get_list_embed_base():
        return discord.Embed(title='Liberty Prime Audio Queue', url='https://patriots.win/', color=0x500000, description='These are all of the songs waiting to be played by Liberty Prime')


    @staticmethod
    def get_list_embed_continuation(pagenum):
        if pagenum%3 == 0:
            # Red (Aggie Maroon, Gig 'em!)
            color = 0x500000
        elif pagenum%3 == 1:
            # White
            color = 0xffffff
        else:
            # Blue
            color = 0x0000ff
        return discord.Embed(title='Liberty Prime Audio Queue Page ' + str(pagenum+1), url='https://patriots.win/', color=color)


    @staticmethod
    def add_empty_list_field(embed):
        embed.add_field(name='This list is empty. You can help by expanding it!', value='Use the $play or $deepfry command to add your favorite YouTube videos to the queue!', inline=False)


    @staticmethod
    def add_now_playing_field(embed, song):
        embed.add_field(name='Now Playing: ' + song.name, value=song.source + ' Added By: ' + song.added_by.display_name, inline=False)


    @staticmethod
    def add_queued_song_field(embed, song):
        embed.add_field(name=song.name, value=song.source + ' Added By: ' + song.added_by.display_name, inline=False)
