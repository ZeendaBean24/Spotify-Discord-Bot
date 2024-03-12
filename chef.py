import discord
import os
import random
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from discord.ext import commands
from dotenv import load_dotenv
import urllib.parse
import asyncio

async def fetch_artist_info(artist_id):
    return await asyncio.to_thread(sp.artist, artist_id)

intents = discord.Intents.all()
client = discord.Client(intents=intents)

# Load environment variables from .env file
load_dotenv()

# Get your Spotify API credentials from environment variables
client_id = os.getenv("SPOTIPY_CLIENT_ID")
client_secret = os.getenv("SPOTIPY_CLIENT_SECRET")
redirect_uri = os.getenv("SPOTIPY_REDIRECT_URI")

sp = spotipy.Spotify(auth_manager=SpotifyOAuth(scope="user-read-recently-played"))

bot = commands.Bot(command_prefix='!', intents=intents)

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
    embed.add_field(name=channel, value='Field Value', inline=True)
    
    await ctx.send(channel, embed=embed)

@bot.command()
async def recent(ctx):
    # Get the user's recently played tracks
    results = sp.current_user_recently_played(limit=1)

    # Check if there are any recently played tracks
    if results["items"]:
        item = results["items"][0]
        track_info = item['track']
        
        # Get artists' names
        artists = ', '.join([artist['name'] for artist in track_info['artists']])
        song_name = track_info['name']
        
        # Check if the track is part of a playlist
        if item["context"] and item["context"]["type"] == "playlist":
            # If the most recent item is a playlist, display the playlist information
            playlist_info = sp.playlist(item["context"]["uri"])
            embed = discord.Embed(
                title="Most Recent Song",
                description=f"**{song_name}** by {artists}",
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
                description=f"**{song_name}** by {artists}",
                color=discord.Color.blue()
            )
            embed.add_field(name="Album", value=f"[{album_info['name']}]({album_info['external_urls']['spotify']})", inline=False)
            if album_info['images']:
                embed.set_thumbnail(url=album_info['images'][0]['url'])
        
        await ctx.send(embed=embed)
    else:
        await ctx.send("No recently played tracks found.")

class PlaylistSelect(discord.ui.Select):
    def __init__(self, playlists, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.playlists = playlists  # Store playlists for use in the class
        
        # Setup options based on the playlists provided
        self.options = [
            discord.SelectOption(label=playlist['name'], value=playlist['id']) for playlist in playlists
        ]
    
    async def callback(self, interaction: discord.Interaction):
        # Acknowledge the interaction immediately but indicate a response will be delayed
        await interaction.response.defer()

        # Fetch the selected playlist ID
        playlist_id = self.values[0]
        tracks = sp.playlist_tracks(playlist_id, limit=100)['items']  # You might need to paginate through tracks if there are more than 100

        # Initialize a dictionary to count genres
        genre_count = {}

        for track in tracks:
            # Get artist(s) for each track
            artists = track['track']['artists']
            for artist in artists:
                artist_id = artist['id']
                artist_info = await fetch_artist_info(artist_id)
                
                # Get genres for the artist and update the genre_count dictionary
                for genre in artist_info['genres']:
                    if genre in genre_count:
                        genre_count[genre] += 1
                    else:
                        genre_count[genre] = 1

        # Sort genres by frequency
        sorted_genres = sorted(genre_count.items(), key=lambda x: x[1], reverse=True)

        # Prepare the message content with top 20 genres
        genres_message = "\n".join([f"{i+1}. {genre[0]} - {genre[1]} songs" for i, genre in enumerate(sorted_genres[:20])])

        # Construct a new view to include in the edited message
        new_view = PlaylistView(playlists=self.playlists)
        
        # Edit the original message with the genres, keeping the dropdown for further selections
        await interaction.followup.send(content=f"**Top genres in the selected playlist:**\n{genres_message}", view=new_view)

class PlaylistView(discord.ui.View):
    def __init__(self, playlists, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Correctly pass the playlists parameter to PlaylistSelect
        self.add_item(PlaylistSelect(playlists=playlists, placeholder="Choose a playlist", options=[
            discord.SelectOption(label=playlist['name'], value=playlist['id']) for playlist in playlists
        ]))
        
@bot.command()
async def playlist(ctx):
    current_user = sp.current_user()
    user_id = current_user['id']  # Fetch the current user's Spotify ID
    
    playlists = sp.current_user_playlists(limit=50)['items']  # Increase limit if necessary
    own_playlists = [playlist for playlist in playlists if playlist['owner']['id'] == user_id]  # Filter for user's own playlists
    
    if not own_playlists:
        await ctx.send("You don't have any playlists.")
        return
    
    await ctx.send("Select one of your playlists:", view=PlaylistView(playlists=own_playlists))

def generate_oauth_link(client_id, redirect_uri, scope):
    params = {
        "client_id": client_id,
        "response_type": "code",
        "redirect_uri": redirect_uri,
        "scope": scope,
        "show_dialog": "true",  # Forces the dialog to show every time (useful for testing)
    }
    auth_url = "https://accounts.spotify.com/authorize?" + urllib.parse.urlencode(params)
    return auth_url

@bot.command(name='authenticate')
async def authenticate(ctx):
    scope = "playlist-read-private"  # Add other scopes as needed
    oauth_link = generate_oauth_link(client_id, redirect_uri, scope)
    
    # Create an embed with the OAuth link
    embed = discord.Embed(title="Authenticate with Spotify",
                          description="Click the link below to authenticate your Spotify account with this bot.",
                          color=0x1DB954)  # Spotify green
    embed.add_field(name="Authentication Link", value=f"[Authorize here]({oauth_link})", inline=False)
    
    await ctx.send(embed=embed)

bot.run(os.getenv("DISCORD_TOKEN"))