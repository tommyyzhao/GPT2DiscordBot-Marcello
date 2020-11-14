import discord
import os
from discord.ext import commands

client = commands.Bot(command_prefix = '.')

#loading and unloading the GPT2 model actually doesn't work, don't use
@client.command()
async def load(ctx, extension):
    client.load_extension(f'cogs.{extension}')
    
@client.command()
async def unload(ctx, extension):
    client.unload_extension(f'cogs.{extension}')

for filename in os.listdir('./cogs'):
    if filename.endswith('.py'):
        client.load_extension(f'cogs.{filename[:-3]}')
    
client.run('Nzc2NjE2NDczODg3NTA2NDUy.X63edA.fogKyKzlOKhnp8TJrtsGMceAx54')