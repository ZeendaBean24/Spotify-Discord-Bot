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
        'cook test - Test command with an embedded message',
        'cook recent - Displays the most recent Spotify track played',
        'cook playlist - Select and view information about your Spotify playlists',
    ]
    await ctx.send('You can use the following commands: \n' + '\n'.join(commands_list))

@bot.command()
async def info(ctx):
    description = (
        "Hey there! I'm Chef Bot, your music buddy here on Discord, lovingly crafted by **@zeendabean24** and **@ntcie**. "
        "My main gig? Bringing folks together through the magic of music! I've got all sorts of cool tricks "
        "up my sleeve to help you and your pals groove along together. From checking out what's been playing lately "
        "to digging into the nitty-gritty of your favorite playlists, I'm all about making your music journey a blast. "
        "But hey, I'm not just about tunes! I've got plenty of other fun stuff tucked away too, so whether you're "
        "looking to chill out with some tunes or just have a good time, I'm your go-to guy. Ready to rock? Let's jam!"
    )
    await ctx.send(description)

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

async def fetch_all_playlist_tracks(playlist_id):
        tracks = []
        offset = 0
        while True:
            # Fetch a page of tracks
            response = await asyncio.to_thread(sp.playlist_tracks, playlist_id, limit=100, offset=offset)
            tracks.extend(response['items'])

            # If this page is less than the maximum limit, we've reached the end
            if len(response['items']) < 100:
                break

            # Prepare to fetch the next page
            offset += 100
        
        return tracks

class PlaylistSelect(discord.ui.Select):
    def __init__(self, playlists, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.playlists = playlists  # Store playlists for use in the class
        
        # Setup options based on the playlists provided
        self.options = [
            discord.SelectOption(label=playlist['name'], value=playlist['id']) for playlist in playlists
        ]
    
    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer()

        playlist_id = self.values[0]  # The selected playlist ID
        tracks = await fetch_all_playlist_tracks(playlist_id)

        # Basic playlist information
        total_tracks = len(tracks)
        # Assuming each track has a duration_ms attribute, sum them up and convert to hours, minutes, and seconds
        total_duration_ms = sum(track['track']['duration_ms'] for track in tracks if track['track'])
        total_seconds = total_duration_ms // 1000
        hours, remainder = divmod(total_seconds, 3600)
        minutes, seconds = divmod(remainder, 60)

        # Initialize a dictionary to count genres
        genre_count = {}

        # Initialize a cache for artist genres
        artist_genres_cache = {}

        async def get_artist_genres(artist_id):
            if artist_id not in artist_genres_cache:
                artist_info = await asyncio.to_thread(sp.artist, artist_id)
                artist_genres_cache[artist_id] = artist_info['genres']
            return artist_genres_cache[artist_id]

        for track in tracks:
            track_genres = set()  # A set to store unique genres for this track
            artists = track['track']['artists']
            for artist in artists:
                genres = await get_artist_genres(artist['id'])
                track_genres.update(genres)  # Add genres to the set, duplicates are automatically handled
            # Now update the genre counts based on this track's unique genres
            for genre in track_genres:
                genre_count[genre] = genre_count.get(genre, 0) + 1

        # Sort genres by frequency and select the top 10
        sorted_genres = sorted(genre_count.items(), key=lambda x: x[1], reverse=True)[:10]

        # Prepare the messages
        basic_info_message = f"**Playlist Overview:**\nTotal Tracks: {total_tracks}\nTotal Duration: {hours}h {minutes}m {seconds}s\n"
        genres_message = "\n".join([f"{i+1}. {genre[0]} - {genre[1]} songs" for i, genre in enumerate(sorted_genres)])

        # Combine messages
        overview_message = basic_info_message + "**Top Genres:**\n" + genres_message

        # Send the follow-up message with the results
        await interaction.followup.send(overview_message)

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

# def generate_oauth_link(client_id, redirect_uri, scope):
#     params = {
#         "client_id": client_id,
#         "response_type": "code",
#         "redirect_uri": redirect_uri,
#         "scope": scope,
#         "show_dialog": "true",  # Forces the dialog to show every time (useful for testing)
#     }
#     auth_url = "https://accounts.spotify.com/authorize?" + urllib.parse.urlencode(params)
#     return auth_url

# @bot.command(name='authenticate')
# async def authenticate(ctx):
#     scope = "playlist-read-private"  # Add other scopes as needed
#     oauth_link = generate_oauth_link(client_id, redirect_uri, scope)
    
#     # Create an embed with the OAuth link
#     embed = discord.Embed(title="Authenticate with Spotify",
#                           description="Click the link below to authenticate your Spotify account with this bot.",
#                           color=0x1DB954)  # Spotify green
#     embed.add_field(name="Authentication Link", value=f"[Authorize here]({oauth_link})", inline=False)
    
#     await ctx.send(embed=embed)

bot.run(os.getenv("DISCORD_TOKEN"))