import discord
from discord.ext.commands import Bot

import commands.text
import commands.audio
import responses.process

from importlib import reload
import sys
import ctypes.util
import yaml

discord.opus.load_opus(ctypes.util.find_library('opus'))

with open('secrets.yml') as stream:
    try:
        secrets = yaml.safe_load(stream)
    except yaml.YAMLError as exc:
        print(exc)


# Make a new bot class
class BetterBot( Bot ):
    async def process_commands(self, message):
        ctx = await self.get_context(message)
        await self.invoke(ctx)

bot = BetterBot(command_prefix='$')
TOKEN = secrets['BOT_TOKEN']

def define_cogs():
    return {
        'Text': (commands.text.Text, 'commands.text'),
        'Audio': (commands.audio.Audio, 'commands.audio'),
        'Processor': (responses.process.Processor, 'responses.process'),
    }

_DISABLED_COGS = []
_COGS = define_cogs()

@bot.event
async def on_ready():
    print(_COGS)
    for name, cog in _COGS.items():
        bot.add_cog(cog[0](bot))
    print(f'Bot connected as {bot.user}')
    print(f'Bot is living in {bot.guilds}')


@bot.command(name='reload', help='Reloads a cog. If no arg is provided, reloads all cogs')
async def reload_cogs(context, cog=None):
    reloaded = []
    global _COGS
    if cog and cog in _COGS.keys():
        # Reload single cog
        bot.remove_cog(cog)
        reload(sys.modules[_COGS[cog][1]])
        _COGS = define_cogs()
        if cog not in _DISABLED_COGS:
            bot.add_cog(_COGS[cog][0](bot))
            reloaded.append(cog.upper())
    else:
        # Reload all cogs
        for name, cog in _COGS.items():
            bot.remove_cog(name)
            print(cog)
            reload(sys.modules[cog[1]])
        _COGS = define_cogs()
        for name, cog in _COGS.items():
            if name not in _DISABLED_COGS:
                bot.add_cog(cog[0](bot))
                reloaded.append(name.upper())
    await context.send(f'RELOAD OF {reloaded} SECURED. AMERICAN VICTORY IS ASSURED.')


@bot.command(name='disable', help='disables a cog')
async def disable_cog(context, cog):
    if cog and cog in _COGS.keys():
        _DISABLED_COGS.append(cog)
        await reload_cogs(context, cog)
        await context.send(f'{cog.upper()} COG DISABLED. LIKELIHOOD OF CHINESE COMMUNIST DESTRUCTION WITHOUT {cog.upper()}: 100%')
    else:
        await context.send('PLEASE PROVIDE A VALID COG NAME TO DISABLE, PATRIOT')


@bot.command(name='enable', help='enables a cog')
async def enable_cog(context, cog):
    if cog and cog in _COGS.keys():
        if cog in _DISABLED_COGS:
            _DISABLED_COGS.remove(cog)
            await reload_cogs(context, cog)
            await context.send(f'{cog.upper()} COG ENABLED. LIKELIHOOD OF CHINESE COMMUNIST DESTRUCTION WITH {cog.upper()}: 100%')
        else:
            await context.send('THIS COG IS ALREADY ENABLED. USE IT WISELY')
    else:
        await context.send('PLEASE PROVIDE A VALID COG NAME TO ENABLE, PATRIOT')


bot.run(TOKEN)
