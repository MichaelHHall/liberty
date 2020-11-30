import discord

import asyncio

_AUDIO_DIR = 'assets/audio/'

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
            return False
        self._voice_client = await channel.connect()


    async def disconnect_from_voice(self):
        await self._voice_client.disconnect()
        self._voice_client = None


    async def add_song(self, song):
        # TODO accept local songs or youtube URLS??
        # TODO flesh out song object and audio reporting stuff
        await self.queue.put(self.Song('test', song, None))
        if not self.playing:
            #start playing
            await self.play_next()


    async def skip_song(self):
        if self.playing:
            # Stop playing, then call play_next
            # This actually doesn't work so it's commented out
            #await self._voice_client.stop()
            #await self.play_next()
            pass


    async def play_next(self):
        # Plays the next song in the queue
        # Get next song from queue
        self.playing = await self.queue.get()
        # Use default channel if none is specified
        if not self.playing.channel:
            self.playing.channel = self.guild.voice_channels[0]
        if not self._voice_client:
            await self.connect_to_voice(self.playing.channel)
        elif self._voice_client.channel != self.playing.channel:
            # Switch channel to new one
            await self.disconnect_from_voice()
            await self.connect_to_voice(self.playing.channel)
        # Create audio stream, then play it on voice client
        stream = discord.FFmpegOpusAudio(_AUDIO_DIR + self.playing.path)
        self._voice_client.play(stream, after=self.song_ended)


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


    def song_ended(self, error):
        # If there is a _prev_source from a regex interrupt, recover.
        # If there is an item in the queue, play next. Else, disconnect
        if self._prev_source:
            future = asyncio.run_coroutine_threadsafe(self.regex_recover(), self.loop)
        elif self.queue.empty():
            self.playing = None
            future = asyncio.run_coroutine_threadsafe(self.disconnect_from_voice(), self.loop)
        else:
            self.playing = None
            future = asyncio.run_coroutine_threadsafe(self.play_next(), self.loop)
        try:
            future.result()
        except Exception as e:
            print(e)


    def get_queue(self):
        return self.queue


    class Song:
        #TODO add some type of TOSTRING for this class
        #TODO include native verification that the song is real and playable in this class
        def __init__(self, name, path, channel):
            self.name = name
            self.path = path
            self.channel = channel
