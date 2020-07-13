# Discord libraries
import discord
from discord.ext import commands

# Get initialization settings
import settings

# Other utils
import os
import re
if settings.use_quantum_rng:
	print('Initializing with QRNG')
	import qrng
	qrng.set_backend()
	def randrange(min: int, max: int):
		return qrng.get_random_int(min, max - 1)
else:
	print('Initializing with PRNG')
	from random import randrange

# Initilize the bot
bot = commands.Bot(command_prefix = '/')

@bot.event
async def on_ready():
	print('Logged in as {0.user}'.format(bot))

# Dice roller
@bot.command()
async def roll(ctx, *rollstrs: str):
	rolls = []
	for rollstr in rollstrs:
		# Validate roll string
		if not re.compile(r'^\d+d\d+([+-]\d+)?$').match(rollstr):
			await ctx.send('"{}" is not a valid roll, enter in the format #d# or #d#±#.'.format(rollstr))
			return
		
		# Get roll values from string
		roll = re.compile(r'\d+').findall(rollstr)
		count = int(roll[0])
		sides = int(roll[1])
		mod = 0
		if len(roll) > 2:
			mod = (int(roll[2]) if rollstr[-len(roll[2])-1] == '+' else -int(roll[2]))
		
		# Validate roll values
		if count < 1:
			await ctx.send('"{}" is not a valid roll, number of dice must be greater than 0.'.format(rollstr))
			return
		if count > 100:
			await ctx.send('"{}" is not a valid roll, number of dice must be less than 101.'.format(rollstr))
			return
		if sides < 2:
			await ctx.send('"{}" is not a valid roll, number of sides must be greater than 1.'.format(rollstr))
			return
		if sides > 100:
			await ctx.send('"{}" is not a valid roll, number of sides must be less than 101.'.format(rollstr))
			return
		
		# Add roll to main list
		rolls.append((count, sides, mod))
	
	# Calculate roll(s)
	roll_list = []
	mods = []
	for count, sides, mod in rolls:
		for _ in range(count):
			roll_list.append(randrange(1, sides + 1))
		if not mod == 0:
			mods.append(mod)
	
	# Send results
	if len(roll_list) == 1:
		await ctx.send('Result: {}'.format(roll_list[0] + sum(mods)))
	else:
		to_send = 'Results: {}\n'.format(', '.join(map(str, roll_list)))
		if len(mods) > 0:
			to_send += 'Modifiers: {}\n'.format(', '.join(map(str, mods)))
		await ctx.send('{}Total: {}'.format(to_send, sum(roll_list) + sum(mods)))

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
