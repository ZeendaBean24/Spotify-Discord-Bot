from discord.ext import commands
import random

bot = commands.Bot(command_prefix='/')

@bot.event 
async def on_ready():
    print(f'Logged in as {bot.user.name}')

@bot.command()
async def greet(ctx):
    responses = ['Hello, hope you have a great day!', 'Hi there, welcome!', 'Greetings!']
    await ctx.send(random.choice(responses))

bot.run('Bot Token')
