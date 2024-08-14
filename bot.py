from ast import alias
import os
from pydoc import describe
import json
from sys import prefix
from tokenize import Token
import discord
from discord.ext import commands

intents = discord.Intents.all()


# Load dotenv function from the module
from dotenv import load_dotenv

# Load the allowed IDs from the JSON file
with open('allowed_ids.json', 'r') as file:
    data = json.load(file)
    allowed_ids = data['allowed_ids']

# load discord bot token
load_dotenv()
# grabs the token from the .env file 
Token = os.getenv('TOKEN')

# define bot prefix
def get_prefix(bot, message):
    with open('prefixes.json', 'r') as f:
        prefixes = json.load(f)
    return prefixes[str(message.guild.id)]

# establish the bot prefix
client = commands.Bot(command_prefix = get_prefix, intents=intents)
command_prefix = get_prefix

# Improved error event handler
@client.event
async def on_command_error(ctx, error):
    error_messages = {
        commands.CommandNotFound: 'Command not found',
        commands.MissingRequiredArgument: 'Missing required argument',
        commands.MissingPermissions: 'Missing permissions',
        commands.BotMissingPermissions: 'Bot missing permissions',
        commands.CheckFailure: 'Check failure',
        commands.CommandOnCooldown: 'Command on cooldown',
        commands.CommandInvokeError: 'Command invoke error',
        commands.CommandError: 'Command error'
    }

    # Check if the error type is in the dictionary
    if type(error) in error_messages:
        await ctx.send(error_messages[type(error)])
    else:
        # Handle any other unanticipated errors
        print(f"Error in command {ctx.command} - {error}")
        await ctx.send(f"An unexpected error occurred: {error}")

#Previous error handler
'''@client.event
async def on_command_error(ctx, error):
        if isinstance(error, commands.CommandNotFound):
            await ctx.send('Command not found')
        elif isinstance(error, commands.MissingRequiredArgument):
            await ctx.send('Missing required argument')
        elif isinstance(error, commands.MissingPermissions):
            await ctx.send('Missing permissions')
        elif isinstance(error, commands.BotMissingPermissions):
            await ctx.send('Bot missing permissions')
        elif isinstance(error, commands.CheckFailure):
            await ctx.send('Check failure')
        elif isinstance(error, commands.CommandOnCooldown):
            await ctx.send('Command on cooldown')
        elif isinstance(error, commands.CommandInvokeError):
            await ctx.send('Command invoke error')
        elif isinstance(error, commands.CommandError):
            await ctx.send('Command error')'''

@client.event
async def on_ready():
    print(f'{client.user} has connected to Discord!')
    print(f'The prefix is: {get_prefix}')
    await load_extensions()

#Prefix Setter and reader (for the bot)
@client.event
async def on_guild_join(guild):
    with open('prefixes.json', 'r') as f:
        prefixes = json.load(f)
    prefixes[str(guild.id)] = '*'
    with open('prefixes.json', 'w') as f:
        json.dump(prefixes, f, indent=4)

#Removes Prefix Setter and reader
@client.event
async def on_guild_remove(guild):
    with open('prefixes.json', 'r') as f:
        prefixes = json.load(f)
    prefixes.pop(str(guild.id))
    with open('prefixes.json', 'w') as f:
        json.dump(prefixes, f, indent=4)

#set a prefix in the server
@client.command(brief='"New prefix": to change the prefix in the server', describe='changes the prefix', aliases=['Prefix'])
async def prefix(ctx, prefix):
    with open('prefixes.json', 'r') as f:
        prefixes = json.load(f)
    prefixes[str(ctx.guild.id)] = prefix
    with open('prefixes.json', 'w') as f:
        json.dump(prefixes, f, indent=4)
    await ctx.send(f'Prefix set to {prefix}')

#load a new cog
@client.command(brief='"cog name": to load a new cog', describe='Load a new cog', aliases=['Load'])
async def load(ctx, extension):
    if ctx.author.id in allowed_ids:
        await client.load_extension(f'Commands.{extension}')
        print (f'{extension} has been loaded')
        await ctx.send(f'Loaded {extension}')
    else:
        await ctx.send('You do not have authorization')

#unload a cog 
@client.command(brief='"cog name": to unload a cog', describe='Unload a cog', aliases=['Unload'])
async def unload(ctx, extension):
    if ctx.author.id in allowed_ids:
        await client.unload_extension(f'Commands.{extension}')
        print (f'{extension} has been unloaded')
        await ctx.send(f'Unloaded {extension}')
    else:
        await ctx.send('You do not have authorization')


#Reload a cog
@client.command(brief='"cog name": to reload a cog', describe='Reload a cog', aliases=['Reload','rl'])
async def reload(ctx, extension):
    if ctx.author.id in allowed_ids:
        await client.reload_extension(f'Commands.{extension}')
        print (f'{extension} has been reloaded')
        await ctx.send(f'Reloaded {extension}')
    else:
        await ctx.send('You do not have authorization')

#List cogs
@client.command(brief='"list of all cogs', describe='list of cogs', aliases=['List cogs', 'List Cogs', 'list cogs', 'list Cogs'])
async def list(ctx):
    if ctx.author.id in allowed_ids:
        for filename in os.listdir('./Commands'):
            if filename.endswith('.py'):
                print(f'{filename[:-3]} is present and voting')
                await ctx.send(f'{filename[:-3]} is present and voting')
    else:
        await ctx.send('You do not have authorization')

#search and load all cogs
async def load_extensions():
    for filename in os.listdir('./Commands'):
        if filename.endswith('.py'):
            await client.load_extension(f'Commands.{filename[:-3]}')
            print (f'{filename[:-3]} has been loaded')
    
    
client.run(Token)