import discord
from discord.ext import commands

import logging

logger = logging.getLogger('BucketCommands')

# A file for defining commands to interact directly with S3 buckets
# To be used for testing, probably won't be generally available
class Buckets(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self._handler = self.bot.bucket_handler


    @commands.command(name='list_s3_keys')
    async def list_s3_keys(self, context):
        res = await self._handler.list_keys()
        await context.send(res)
