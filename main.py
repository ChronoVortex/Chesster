# Discord libraries
import discord
from discord.ext import commands

# Other utils
import os
from random import randrange
import re

# Initilize the bot
bot = commands.Bot(command_prefix = '/')

@bot.event
async def on_ready():
	print('Logged in as {0.user}'.format(bot))

# Dice roller
@bot.command()
async def roll(ctx, rollstr: str):
	# Validate roll string
	if not re.compile(r'^\d+d\d+$').match(rollstr):
		await ctx.send('Invalid roll, enter in the format #d#.')
		return
	
	# Get dice values from string
	dice = re.compile(r'\d+').findall(rollstr)
	count = int(dice[0])
	sides = int(dice[1])
	
	# Validate dice values
	if count < 1:
		await ctx.send('Invalid roll, number of dice must be greater than 0.')
		return
	if count > 64:
		await ctx.send('Invalid roll, number of dice must be less than 65.')
		return
	if sides < 2:
		await ctx.send('Invalid roll, number of sides must be greater than 1.')
		return
	if sides > 64:
		await ctx.send('Invalid roll, number of sides must be less than 65.')
		return
	
	# Calculate roll and send results
	if count == 1:
		await ctx.send('Result: {}'.format(randrange(1, sides + 1)))
	else:
		roll_list = [randrange(1, sides + 1) for n in range(count)]
		await ctx.send('Results: {}\nTotal: {}'.format(', '.join(map(str, roll_list)), sum(roll_list)))

# Load cogs
cogs = ['cogs.chess']
for cog in cogs:
	try:
		bot.load_extension(cog)
	except Exception:
		print('Unable to load cog {}'.format(cog))

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