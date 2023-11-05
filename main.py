import discord
from discord.ext import commands
import os
from settings import *

# Initilize the bot
bot = commands.Bot(command_prefix=PREFIX, intents=discord.Intents.all())

# Load cogs
@bot.event
async def on_ready():
    print('Logged in as {0.user}'.format(bot))
    cogs = ['cogs.chess', 'cogs.dice']
    for cog in cogs:
        try:
            await bot.load_extension(cog)
        except Exception as e:
            print('Unable to load {}: {}'.format(cog, e))

# Run bot
token = ''
if os.path.isfile('./token'):
    with open('token', 'r') as f:
        token = f.readline()
else:
    token = str(input('Enter bot token: '))
    with open('token', 'w') as f:
        f.write(token)
bot.run(token)
