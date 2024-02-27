import discord
from discord.ext import commands
import random
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from dotenv import load_dotenv
import os
import json

intents = discord.Intents.all()
client = discord.Client(intents=intents)

# Load environment variables from .env file
load_dotenv()

# Get your Spotify API credentials from environment variables
# client_id = os.getenv("SPOTIPY_CLIENT_ID")
# client_secret = os.getenv("SPOTIPY_CLIENT_SECRET")
# redirect_uri = os.getenv("SPOTIPY_REDIRECT_URI")

# Initialize
bot = commands.Bot(command_prefix='cook ', intents=intents)

# Database to store user access tokens (this is just for demonstration)
DATABASE_FILE = "user_tokens.json"

# Helper function to load user tokens from the database
def load_user_tokens():
    if os.path.exists(DATABASE_FILE):
        with open(DATABASE_FILE, "r") as file:
            return json.load(file)
    else:
        return {}
    
# Helper function to save user tokens to the database
def save_user_tokens(tokens):
    with open(DATABASE_FILE, "w") as file:
        json.dump(tokens, file)

@bot.event
async def on_ready():
    print(f'Successful! Logged in as {bot.user.name}')

# Dictionary to keep track of users in the process of authentication
awaiting_authentication = {}

# Load user tokens from the database
user_tokens = load_user_tokens()

# Event listener to handle response after user authentication
@bot.event
async def on_message(message):
    if message.author.bot:
        return
    if message.content.startswith("!authenticate"):
        # Extract user's Discord ID
        user_id = message.author.id
        # Check if user is in the process of authenticating
        if user_id in awaiting_authentication:
            # Parse access token from message content (this is just for demonstration)
            access_token = message.content.split()[-1]
            # Store user's access token
            user_tokens[user_id] = access_token
            save_user_tokens(user_tokens)
            # Inform user that authentication was successful
            await message.channel.send("Authentication successful!")
            # Remove user from awaiting_authentication
            del awaiting_authentication[user_id]
    await bot.process_commands(message)

# Function to authenticate users with Spotify
@bot.command()
async def authenticate(ctx):
    # Get user's Discord ID
    user_id = ctx.author.id
    # Redirect user to Spotify authentication URL
    auth_url = spotipy.SpotifyOAuth(scope="user-read-recently-played",
                                    client_id=os.getenv("SPOTIPY_CLIENT_ID"),
                                    client_secret=os.getenv("SPOTIPY_CLIENT_SECRET"),
                                    redirect_uri=os.getenv("SPOTIPY_REDIRECT_URI")                      
                                    ).get_authorize_url()
    await ctx.send(f"Authorize the bot to access your Spotify account: {auth_url}")
    # Store the Discord ID to associate it with the access token later
    awaiting_authentication[user_id] = True

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
    embed.add_field(name=channel, value='Field Value', inline=True)
    
    await ctx.send(channel, embed=embed)

# Function to handle the recent command
@bot.command()
async def recent(ctx):
    # Get user's Discord ID
    user_id = ctx.author.id
    # Check if user is authenticated
    if user_id not in user_tokens:
        await ctx.send("You need to authenticate first using the !authenticate command.")
        return
    # Fetch user's access token
    access_token = user_tokens[user_id]
    # Create Spotify client with user's access token
    sp = spotipy.Spotify(auth=access_token)
    # Get user's recent tracks
    results = sp.current_user_recently_played(limit=1)
    # Display recent track
    if results["items"]:
        track_info = results["items"][0]["track"]
        # Check if the track is part of a playlist
        if results["items"][0]["context"] and results["items"][0]["context"]["type"] == "playlist":
            # If the most recent item is a playlist, display the playlist information
            playlist_info = sp.playlist(results["items"][0]["context"]["uri"])
            embed = discord.Embed(
                title="Most Recent Song",
                description=f"**{track_info['name']}** by {', '.join([artist['name'] for artist in track_info['artists']])}",
                color=discord.Color.blue()
            )
            embed.add_field(name="Playlist", value=f"[{playlist_info['name']}]({playlist_info['external_urls']['spotify']})", inline=False)
            if playlist_info['images']:
                embed.set_thumbnail(url=playlist_info['images'][0]['url'])
        else:
            # If the most recent item is not a playlist, display the album information
            album_info = sp.album(track_info['album']['external_urls']['spotify'])
            embed = discord.Embed(
                title="Most Recent Song",
                description=f"**{track_info['name']}** by {', '.join([artist['name'] for artist in track_info['artists']])}",
                color=discord.Color.blue()
            )
            embed.add_field(name="Album", value=f"[{album_info['name']}]({album_info['external_urls']['spotify']})", inline=False)
            if album_info['images']:
                embed.set_thumbnail(url=album_info['images'][0]['url'])
        
        await ctx.send(embed=embed)
    else:
        await ctx.send("No recent tracks found.")

bot.run(os.getenv("DISCORD_TOKEN"))
