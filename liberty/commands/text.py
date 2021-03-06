import discord
from discord.ext import commands

import asyncio

# A file for defining basic info commands
class Text(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self._last_member = None


    async def get_prev_message(self, context, message_limit=25):
        """Search through previous messages until you find one that contains text"""
        for message in (await context.channel.history(limit=message_limit).flatten())[1:]:
            if message.content:
                resp = message.content
                return resp
        return None


    @commands.command(name='echo', help = 'echo a comment')
    async def echo_message(self, context, *msg):
        if not msg:
            msg = []
            msg.append(await self.get_prev_message(context))
        await context.send(' '.join(msg))


    @commands.command(name='nuke', help='Send a tactical nuke at another member of the server')
    async def nuke_friend(self, context):
        # Get all members mentioned in the command
        targets = context.message.mentions
        if not targets:
            await context.send('Please designate a communist scoundrel to target!')
            return

        for i in range(0,15):
            for target in targets:
                await context.send(target.mention)
                await asyncio.sleep(0.5)


    @commands.command(name='carpetbomb', help='Assault a member of the server with a blanket of attacks')
    async def carpetbomb(self, context):
        # Get mentions in command
        targets = context.message.mentions
        if not targets:
            await context.send('Please designate a communist scoundrel to target!')
            return

        # Loop over all text channels in guild
        channels = context.guild.text_channels
        for channel in channels:
            for target in targets:
                # Ensure target is mentionable in channel
                if target.mention in [member.mention for member in channel.members]:
                    if channel.permissions_for(context.guild.me).send_messages:
                        await channel.send(target.mention)
                        await asyncio.sleep(0.5)
