import discord
from discord.ext import commands

from handlers.audio import AudioHandler

import yaml
import re
import logging

logger = logging.getLogger('RegexProcessor')

# A file for processing regexes and sending responses to their respective handlers
class Processor(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self._last_member = None
        try:
            self._audio_handlers = self.bot.get_cog('Audio')._audio_handlers
        except:
            self._audio_handlers = None
            logger.error('Audio system broke')
        # Probably want to import my yaml here
        with open("responses/regexes.yml") as stream:
            try:
                self.regexes = yaml.safe_load(stream)
            except yaml.YAMLError as exc:
                logger.error(exc)

    
    @commands.Cog.listener()
    async def on_message(self, message):
        # Don't process regexes in commands or messages from liberty
        if message.author == self.bot.user:
            return
        if message.content.startswith(self.bot.command_prefix):
            return
        #check if a regex matches
        for reg in self.regexes:
            try:
                if re.search(reg['regex'], message.content):
                    # Process responses
                    for key in reg.keys():
                        method = getattr(self, key)
                        if type(reg[key]) is str:
                            resp = [reg[key]]
                        else:
                            resp = reg[key]
                        await method(message, resp)
            except KeyError as e:
                logger.error(e)
                continue
    

    async def regex(self, message, response):
        return


    async def text_response(self, message, response):
        for resp in response:
            await message.channel.send(resp)


    async def reaction_response(self, message, response):
        for resp in response:
            for emoji in self.bot.emojis:
                if emoji.name == resp:
                    resp = emoji
                    break
            await message.add_reaction(resp)


    async def audio_response(self, message, response):
        if self._audio_handlers:
            # We can do audio stuff
            _audio_handler = self._audio_handlers[message.guild.id]
            # response is a list, I should make this handle bigger lists eventually
            await _audio_handler.regex_audio(response[0], added_by=message.author)
        else:
            logger.warning('Audio responses disabled because Audio cog is not here')
