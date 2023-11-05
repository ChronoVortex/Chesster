import discord
from discord.ext import commands

import re
from random import randrange, getrandbits

class dice(commands.Cog):
    # Dice roller
    @commands.command(
        aliases=['dice', 'diceroll', 'rolldice'],
        help='Roll dice using #d# or #d#±#, will take multiple')
    async def roll(self, ctx, *rollstrs: str):
        if not rollstrs:
            await ctx.send('Rolling nothing...\nResults: nothing. Big suprise.')
            return
        
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
    
    # Coin flipper
    @commands.command(
        aliases=['coinflip', 'flip', 'coin'],
        help='Flip a coin')
    async def flipcoin(self, ctx):
        await ctx.send(file=discord.File('res/heads.png' if getrandbits(1) else 'res/tails.png'))

async def setup(bot):
    await bot.add_cog(dice(bot))
