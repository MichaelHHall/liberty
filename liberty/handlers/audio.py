import discord
import asyncio
from pathlib import Path

from utils.downloader import PytubeDownloader, YouTubeVideo
from utils.constants import _AUDIO_DIR, _DEEP_FRIED_FFMPEG_OPTIONS
from utils.general import FSUtils

manipulations = {
    'deepfry' : _DEEP_FRIED_FFMPEG_OPTIONS,
}

# A file to handle audio queueing and other disasters
class AudioHandler:
    def __init__(self, guild):
        print('initing Audio system')
        self.queue = asyncio.Queue()
        self.guild = guild
        self.playing = None
        self._voice_client = None
        self._prev_source = None
        self.loop = asyncio.get_event_loop()


    async def connect_to_voice(self, channel):
        if not channel:
            # Probably throw an error here?
            print('No channel provided')
            return False
        self._voice_client = await channel.connect()
        return True


    async def disconnect_from_voice(self):
        await self._voice_client.disconnect()
        self._voice_client = None


    async def download_and_add_song(self, url, channel_id=None, manipulation=None, added_by=None):
        video = PytubeDownloader.download(url)
        await self.add_song(video.path, channel_id, manipulation, video.title, source='Downloaded Youtube Audio', added_by=added_by)


    async def add_song(self, song, channel_id=None, manipulation=None, name=None, source='Local Song', added_by=None):
        # TODO accept local songs or youtube URLS??
        # TODO flesh out song object and audio reporting stuff
        opts = manipulations[manipulation] if manipulation else None
        if not name:
            name = song
        await self.queue.put(self.Song(self.guild, name, song, source, added_by, channel_id, opts))
        if not self.playing:
            #start playing
            await self.play_next()


    async def skip_song(self):
        if self.playing and self._voice_client:
            # Stop playing, which apparently calls the stream's 'after' callback
            self._voice_client.stop()


    async def kill_music(self):
        # Loop through the queue and skip songs until empty
        # Skip once more to clear the currently playing song
        # This forces it to go through the proper cleanup process for each song
        # Including deleting tmp files
        while not self.queue.empty():
            await self.skip_song()
            # This is necessary to hand control over to the voice client callback
            # Otherwise this loop continuously executes without actually processing the queue
            # A more elegant solution to yielding control here is welcomed.
            await asyncio.sleep(0.1)
        await self.skip_song()


    async def play_next(self):
        # Plays the next song in the queue
        # Get next song from queue
        try:
            self.playing = self.queue.get_nowait()
        except asyncio.QueueEmpty:
            # Nothing in queue, no need to play next
            self.playing = None
            await self.disconnect_from_voice()
            return
        if not self._voice_client:
            connected = await self.connect_to_voice(self.playing.channel)
        elif self._voice_client.channel != self.playing.channel:
            # Switch channel to new one
            await self.disconnect_from_voice()
            connected = await self.connect_to_voice(self.playing.channel)
        else:
            # Already connected to old channel
            connected = True
        # Create audio stream, then play it on voice client
        if connected:
            stream = discord.FFmpegOpusAudio(self.playing.path, options=self.playing.ffmpegopts)
            self._voice_client.play(stream, after=self.song_ended)
        else:
            # Couldn't play song, so treat as if song has ended
            self.song_ended()


    async def regex_audio(self, path):
        if self.playing:
            await self.regex_interrupt(path)
        else:
            await self.add_song(path)


    async def regex_interrupt(self, path):
        # Pause current stream, store it, play regex
        # TODO turn self._prev_source into a stack so that multiple regexes don't kill each other
        # and regex_recover can complete them all recursively before returning to the queue
        # This system is bad but I declare victory since I made a feature that terminus can't do
        self._voice_client.pause()
        self._prev_source = self._voice_client.source
        new_source = discord.FFmpegOpusAudio(_AUDIO_DIR + path)
        self._voice_client.source = new_source
        self._voice_client.resume()


    async def regex_recover(self):
        cur_source = self._prev_source
        self._prev_source = None
        self._voice_client.play(cur_source, after=self.song_ended)


    def song_ended(self, error=None):
        # If there is a _prev_source from a regex interrupt, recover.
        # If there is an item in the queue, play next. Else, disconnect
        if self._prev_source:
            future = asyncio.run_coroutine_threadsafe(self.regex_recover(), self.loop)
        else:
            if FSUtils.isTmpDir(self.playing.path):
                # Song is in tmp dir, we should delete it
                Path(self.playing.path).unlink(missing_ok=True)
            self.playing = None
            future = asyncio.run_coroutine_threadsafe(self.play_next(), self.loop)
        try:
            future.result()
        except Exception as e:
            print(e)


    def get_queue(self):
        return self.queue


    class Song:
        # TODO add some type of TOSTRING for this class
        # TODO include native verification that the song is real and playable in this class
        def __init__(self, guild, name, path, source, added_by, channel_id, ffmpegopts=None):
            self.guild = guild
            self.name = name
            self.source = source
            self.added_by = added_by
            # Check if path is a full path
            # if not, add the audio_dir to it
            if Path(path).exists():
                self.path = path
            else:
                self.path = _AUDIO_DIR + path
            if channel_id:
                self.channel = self._get_channel_from_id(channel_id)
            else:
                # Use first voice channel as default
                self.channel = self.guild.voice_channels[0]
            self.ffmpegopts=ffmpegopts


        def __str__(self):
            return(self.name)


        def _get_channel_from_id(self, channel_id):
            # TODO verify this is a voice channel, do some error handling that will destroy the song object if the channel is invalid
            # TODO figure out why this always gets nothing and always returns voice_channels[0]
            channel = self.guild.get_channel(channel_id)
            print(channel)
            return self.guild.get_channel(channel_id) or self.guild.voice_channels[0]
