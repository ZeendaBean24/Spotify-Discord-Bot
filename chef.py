import discord
import os
import random
from discord.ext import commands
from dotenv import load_dotenv

intents = discord.Intents.all()
client = discord.Client(intents=intents)
bot = commands.Bot(command_prefix='cook ', intents=intents)

@bot.event
async def on_ready():
    print(f'Successful! Logged in as {bot.user.name}')

@bot.command()
async def greet(ctx):
    responses = ['Hello, hope you have a great day!', 'Hi there, welcome!', 'Greetings!']
    await ctx.send(random.choice(responses))

@bot.command()
async def luckynumber(ctx):
    number = random.randint(1, 100)  # Random number between 1 and 100
    await ctx.send(f"Your lucky number today is: {number}")

@bot.command()
async def cmds(ctx):
    commands_list = [
        'cook cmds - Lists all available commands',
        'cook greet - Greet you with a random message',
        'cook luckynumber - Tells you a random lucky number',
        'cook info - Provides info about the bot',
    ]
    await ctx.send('You can use the following commands: \n' + '\n'.join(commands_list))

@bot.command()
async def info(ctx):
    await ctx.send('This bot is created by @zeendabean24. It offers fun and utility commands.')


load_dotenv()
bot.run(os.getenv("DISCORD_TOKEN"))