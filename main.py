# Discord libraries
import discord
from discord.ext import commands

# Other utils
import os

# Initilize the bot
bot = commands.Bot(command_prefix = '/')

@bot.event
async def on_ready():
    print('Logged in as {0.user}'.format(bot))

# Load cogs
cogs = ['cogs.chess', 'cogs.dice']
for cog in cogs:
    try:
        bot.load_extension(cog)
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
