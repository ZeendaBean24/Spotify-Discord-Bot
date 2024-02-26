import discord
import os
import random
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from discord.ext import commands
from dotenv import load_dotenv

intents = discord.Intents.all()
client = discord.Client(intents=intents)

# Load environment variables from .env file
load_dotenv()

# Get your Spotify API credentials from environment variables
client_id = os.getenv("SPOTIPY_CLIENT_ID")
client_secret = os.getenv("SPOTIPY_CLIENT_SECRET")
redirect_uri = os.getenv("SPOTIPY_REDIRECT_URI")

sp = spotipy.Spotify(auth_manager=SpotifyOAuth(scope="user-read-recently-played"))

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

@bot.command()
async def test(ctx):
    channel = ctx.message.channel
    embed = discord.Embed(
        title = 'Title',
        description = 'This is description.', 
        colour = discord.Colour.blue()
    )

    embed.set_footer(text='This is a footer')
    embed.set_image(url='https://archive.org/download/discordprofilepictures//discordblue.png')
    embed.set_thumbnail(url='https://archive.org/download/discordprofilepictures//discordblue.png')
    embed.set_author(name='Zeen Liu', icon_url='https://archive.org/download/discordprofilepictures//discordblue.png')
    embed.add_field(name='Field Name', value='Field Value', inline=False)
    embed.add_field(name='Field Name', value='Field Value', inline=True)
    embed.add_field(name='Field Name', value='Field Value', inline=True)
    
    await ctx.send(channel, embed=embed)

@bot.command()
async def recent(ctx):
    # Get the user's recently played tracks
    results = sp.current_user_recently_played(limit=50)

    # Filter out the last 3 playlists
    playlist_info_list = []
    for item in results["items"]:
        if item["context"] and item["context"]["type"] == "playlist":
            playlist_info = sp.playlist(item["context"]["uri"])
            playlist_info_list.append(playlist_info)

        if len(playlist_info_list) >= 3:
            break

    # Create and send the embed
    if playlist_info_list:
        embed = discord.Embed(
            title="Last 3 Played Playlists",
            color=discord.Color.blue()
        )
        for playlist_info in playlist_info_list:
            embed.add_field(
                name=playlist_info['name'],
                value=f"[Open Playlist]({playlist_info['external_urls']['spotify']})",
                inline=False
            )
            if playlist_info['images']:
                embed.set_thumbnail(url=playlist_info['images'][0]['url'])
        await ctx.send(embed=embed)
    else:
        await ctx.send("No playlists found in recently played tracks.")

bot.run(os.getenv("DISCORD_TOKEN"))