import discord, os, random, spotipy, asyncio, locale, time, json, re, lyricsgenius
from spotipy.oauth2 import SpotifyOAuth
from discord.ext import commands
from dotenv import load_dotenv
# import urllib.parse

# Load the Opus library
opus_path = '/opt/homebrew/lib/libopus.dylib'  # apk add --no-cache opus-dev
discord.opus.load_opus(opus_path)

if discord.opus.is_loaded():
    print("Opus successfully loaded.")
else:
    print("Failed to load Opus.")

# Set the locale to the user's default setting (for number formatting)
locale.setlocale(locale.LC_ALL, '')

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
genius_api_token = os.getenv("GENIUS_ACCESS_TOKEN")
file_path = os.getenv('FILE_PATH')

sp = spotipy.Spotify(auth_manager=SpotifyOAuth(scope="user-read-recently-played"))
bot = commands.Bot(command_prefix='!', intents=intents)

def load_user_scores():
    with open(file_path, "r") as file:
        return json.load(file)

# Function to save user scores to JSON file
def save_user_scores(user_scores):
    with open(file_path, "w") as file:
        json.dump(user_scores, file)
        
def update_user_stats(user):
    user_id = str(user.id)
    user_scores = load_user_scores()

    if user_id not in user_scores:
        user_scores[user_id] = {
            "username": user.name,
            "pp": 0,  # Placeholder for points, adjust as needed
            "uses": 0
        }

    user_scores[user_id]['uses'] += 1
    save_user_scores(user_scores)

#TODO: REMOVE DUPLICATES IN RANDOM 3, ADD MIXES? (Except for Pop mix - already added)
# Define a dictionary mapping genre codes to specific playlist URIs
playlist_uris_by_genre = {
    0: ["spotify:playlist:37i9dQZF1DWZoDfksyokHA", "spotify:playlist:37i9dQZF1DX9Z3vMB2b8im", "spotify:playlist:37i9dQZF1DX4WYpdgoIcn6", "spotify:playlist:37i9dQZF1DWTKdpN2FAbcN", "spotify:playlist:37i9dQZF1DX4mWCZw6qYIw", "spotify:playlist:37i9dQZF1DX4mWCZw6qYIw", "spotify:playlist:37i9dQZF1DXdPec7aLTmlC", "spotify:playlist:37i9dQZF1DX889U0CL85jj", "spotify:playlist:37i9dQZF1DX5D8j6p4CXZT", "spotify:playlist:37i9dQZF1DXaK0O81Xtkis", "spotify:playlist:37i9dQZF1DX3rxVfibe1L0", "spotify:playlist:37i9dQZF1DXdl6IPOySdX4", "spotify:playlist:37i9dQZF1DXcbAIldMQMIs", "spotify:playlist:37i9dQZF1DX8OR0U4UGusN", "spotify:playlist:37i9dQZF1DX4OzrY981I1W", "spotify:playlist:37i9dQZF1DX3YSRoSdA634", "spotify:playlist:37i9dQZF1DXbEm2sKzgoJ8", "spotify:playlist:37i9dQZF1DX2DKrE9X6Abv", "spotify:playlist:37i9dQZF1DWWVULl5wUsL9", "spotify:playlist:37i9dQZF1DXcBWIGoYBM5M", "spotify:playlist:37i9dQZF1DX5Vy6DFOcx00"], # Special Series (Multiple)
    1: ["spotify:playlist:37i9dQZF1DXcOFePJj4Rgb", "spotify:playlist:37i9dQZF1EQncLwOalG3K7", "spotify:playlist:1udqwx26htiKljZx4HwVxs", "spotify:playlist:5cAz3DR6eFPhxH4ozTKQcx", "spotify:playlist:37i9dQZF1DXcxvFzl58uP7", "spotify:playlist:6sLKqrUF3TEfcMkcS6P3gu", "spotify:playlist:37i9dQZF1DWWvvyNmW9V9a", "spotify:playlist:37i9dQZF1DWWqNV5cS50j6", "spotify:playlist:37i9dQZF1DX5y8xoSWyhcz", "spotify:playlist:4GZT3MbZ4IwjtIxKuYerfu", "spotify:playlist:6mtYuOxzl58vSGnEDtZ9uB", "spotify:playlist:37i9dQZF1DX4o1oenSJRJd"],  # Pop
    2: ["spotify:playlist:37i9dQZF1DX9oh43oAzkyx", "spotify:playlist:37i9dQZF1DWWY64wDtewQt", "spotify:playlist:37i9dQZF1DWUVpAXiEPK8P", "spotify:playlist:37i9dQZF1DX0XUsuxWHRQd", "spotify:playlist:37i9dQZF1DX76Wlfdnj7AP"],  # Rap/Hip-Hop/Phonk
    3: ["spotify:playlist:37i9dQZF1DWVV27DiNWxkR", "spotify:playlist:37i9dQZF1DWXRqgorJj26U", "spotify:playlist:37i9dQZF1DX4mWCZw6qYIw", "spotify:playlist:37i9dQZF1DWVsh2vXzlKFb", "spotify:playlist:37i9dQZF1DX5y8xoSWyhcz", "spotify:playlist:37i9dQZF1DWT6zAeOrK0H1", "spotify:playlist:37i9dQZF1DX0E9XMGembJo", "spotify:playlist:37i9dQZF1DX8uc99HoZBLU", "spotify:playlist:37i9dQZF1DX26DKvjp0s9M", "spotify:playlist:37i9dQZF1DXb9izPIc0SCS", "spotify:playlist:37i9dQZF1DX2sUQwD7tbmL", "spotify:playlist:37i9dQZF1DX4OzrY981I1W", "spotify:playlist:37i9dQZF1DX0CIO5EOSHeD", "spotify:playlist:37i9dQZF1DX9crXQ0wuuXE", "spotify:playlist:37i9dQZF1DXad2sxzzYX1N"],  # Indie/Rock
    4: ["spotify:playlist:37i9dQZF1DX1jtMPFVTOER", "spotify:playlist:37i9dQZF1DWWQRwui0ExPn", "spotify:playlist:37i9dQZF1DX0CIO5EOSHeD", "spotify:playlist:37i9dQZF1DWWEJlAGA9gs0", "spotify:playlist:37i9dQZF1DX8Sz1gsYZdwj", "spotify:playlist:37i9dQZF1DWV7EzJMK2FUI"],  # Classical/Lofi/Jazz
    5: ["spotify:playlist:37i9dQZF1DXbrUpGvoi3TS", "spotify:playlist:37i9dQZF1DX7qK8ma5wgG1", "spotify:playlist:37i9dQZF1DWVV27DiNWxkR", "spotify:playlist:37i9dQZF1DWXxauMBOQPxX", "spotify:playlist:37i9dQZF1DWW2hj3ZtMbuO", "spotify:playlist:37i9dQZF1DX6xZZEgC9Ubl", "spotify:playlist:37i9dQZF1DX15JKV0q7shD", "spotify:playlist:37i9dQZF1DX1vEe0OWx8Fn"] # Sad
}

# Function to fetch random playlists based on genre code
def fetch_playlists_by_genre(genre_code=None):
    playlists = []

    if genre_code in playlist_uris_by_genre:
        playlist_uris = playlist_uris_by_genre[genre_code]
        selected_uris = random.sample(playlist_uris, min(len(playlist_uris), 3))
        playlists = [sp.playlist(uri) for uri in selected_uris]
    else:
        # Flatten all playlist URIs into a single list
        all_uris = [uri for uris in playlist_uris_by_genre.values() for uri in uris]
        selected_uris = random.sample(all_uris, min(len(all_uris), 3))
        playlists = [sp.playlist(uri) for uri in selected_uris]

    return playlists

@bot.event
async def on_command_completion(ctx):
    update_user_stats(ctx.author)

# Global dictionary to track ongoing games by channel
ongoing_game = {}

@bot.event
async def on_ready():
    print(f'Successful! Logged in as {bot.user.name}')

@bot.command()
# greet command
async def greet(ctx):
    greetings = [
        ("Hello", "English"),
        ("Hola", "Spanish"),
        ("Bonjour", "French"),
        ("Hallo", "German"),
        ("Ciao", "Italian"),
        ("Привет", "Russian"),
        ("こんにちは", "Japanese"),
        ("你好", "Chinese"),
        ("안녕하세요", "Korean"),
        ("Merhaba", "Turkish"),
        ("Salam", "Arabic"),
        ("नमस्ते", "Hindi"),
        ("Shalom", "Hebrew"),
        ("Olá", "Portuguese"),
        ("Zdravstvuyte", "Russian"),
        ("Sawubona", "Zulu"),
        ("Jambo", "Swahili"),
        ("Hej", "Swedish"),
        ("Hei", "Finnish"),
        ("Szia", "Hungarian"),
        ("Goddag", "Danish"),
        ("Halló", "Icelandic"),
        ("Kumusta", "Filipino"),
        ("Sawasdee", "Thai"),
        ("Xin chào", "Vietnamese"),
        ("Selamat siang", "Indonesian"),
        ("Namaskar", "Nepali"),
        ("Tere", "Estonian"),
        ("Sveiki", "Latvian"),
        ("Labas", "Lithuanian"),
        ("Barev", "Armenian"),
        ("Salam", "Persian"),
        ("Yassas", "Greek"),
        ("Dobry den", "Czech"),
        ("Szervusz", "Hungarian"),
        ("Buna", "Romanian"),
        ("Zdravo", "Serbian"),
        ("Pryvit", "Ukrainian"),
        ("Sveikas", "Lithuanian"),
    ]
    msg = random.choice(greetings)
    await ctx.send(f"## {msg[0]}! ({msg[1]})")

@bot.command()
async def luckynumber(ctx):
    number = random.randint(1, 100)  # Random number between 1 and 100
    await ctx.send(f"Your lucky number today is: {number}")

@bot.command()
async def cmds(ctx):
    commands_list = [
        '\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*',
        '## Overview',
        '',
        '**`!cmds` - Lists all available commands**',
        '**`!info` - Provides info about the bot**',
        '## Basic Commands',
        '',
        '`!greet` - Greet you with a random message',
        '`!luckynumber` - Tells you a random lucky number',
        '## Music Commands',
        '',
        '**`!recent` - Displays the most recent Spotify track played**',
        '**`!genres` - Shows the top genres in a Spotify playlist**',
        '**`!popularity` - Analyzes the popularity of a Spotify playlist**',
        '**`!randomsong` - Picks a random song from a Spotify playlist**',
        '**`!guess` - Guessing game based on an album cover**',
        '**`!preview` - Guessing game based on a song audio snippet (Voice call required)**',
        '',
        '\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*',
    ]
    await ctx.send('\n'.join(commands_list))


@bot.command()
async def info(ctx):
    description = (
        "## @zeendabean24 & @ntcie Present: *Spotify Chef Bot*\n\n"
        "I will be your music buddy here on Discord!\n" 
        "I have many cool commands to connect you and your pals through music.\n\n"
        "**Use the prefix **`!`** and **`!cmds`** to start!**"
    )
    await ctx.send(description)

# @bot.command()
# async def test(ctx):
#     channel = ctx.message.channel
#     embed = discord.Embed(
#         title = 'Title',
#         description = 'This is description.',
#         colour = discord.Colour.blue()
#     )

#     embed.set_footer(text='This is a footer')
#     embed.set_image(url='https://archive.org/download/discordprofilepictures//discordblue.png')
#     embed.set_thumbnail(url='https://archive.org/download/discordprofilepictures//discordblue.png')
#     embed.set_author(name='Zeen Liu', icon_url='https://archive.org/download/discordprofilepictures//discordblue.png')
#     embed.add_field(name='Field Name', value='Field Value', inline=False)
#     embed.add_field(name='Field Name', value='Field Value', inline=True)
#     embed.add_field(name='Field Name', value='Field Value', inline=True)
#     embed.add_field(name=channel, value='Field Value', inline=True)
    
#     await ctx.send(channel, embed=embed)

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
        selected_playlist = next((p for p in self.playlists if p['id'] == playlist_id), None)

        if selected_playlist:
            tracks = await fetch_all_playlist_tracks(playlist_id)

            # Basic playlist information
            total_tracks = len(tracks)
            total_duration_ms = sum(track['track']['duration_ms'] for track in tracks if track['track'])
            total_seconds = total_duration_ms // 1000
            hours, remainder = divmod(total_seconds, 3600)
            minutes, seconds = divmod(remainder, 60)

            # Initialize a dictionary to count genres
            genre_count = {}
            artist_genres_cache = {}

            async def get_artist_genres(artist_id):
                if artist_id not in artist_genres_cache:
                    artist_info = await asyncio.to_thread(sp.artist, artist_id)
                    artist_genres_cache[artist_id] = artist_info['genres']
                return artist_genres_cache[artist_id]

            for track in tracks:
                track_genres = set()
                artists = track['track']['artists']
                for artist in artists:
                    genres = await get_artist_genres(artist['id'])
                    track_genres.update(genres)
                for genre in track_genres:
                    genre_count[genre] = genre_count.get(genre, 0) + 1

            sorted_genres = sorted(genre_count.items(), key=lambda x: x[1], reverse=True)[:5]
            genres_message = "\n".join(f"{i+1}. {genre} - {count} songs ({(count / total_tracks) * 100:.2f}%)" for i, (genre, count) in enumerate(sorted_genres))

            overview_message = (f"**{selected_playlist['name']} - Playlist Overview:**\n"
                                f"Total Tracks: {total_tracks}\n"
                                f"Total Duration: {hours}h {minutes}m {seconds}s\n\n"
                                f"**Top Genres:**\n{genres_message}")

            await interaction.followup.send(overview_message)

class GenrePlaylistView(discord.ui.View):
    def __init__(self, playlists, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.add_item(PlaylistSelect(playlists=playlists, placeholder="Choose a playlist"))

@bot.command()
async def genres(ctx):
    current_user = sp.current_user()
    user_id = current_user['id']
    
    playlists = sp.current_user_playlists(limit=50)['items']
    own_playlists = [playlist for playlist in playlists if playlist['owner']['id'] == user_id]
    
    if not own_playlists:
        await ctx.send("You don't have any playlists.")
        return
    
    await ctx.send("Select one of your playlists:", view=GenrePlaylistView(playlists=own_playlists))

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

def estimate_streams(popularity, max_streams=100000000, min_streams=10000):
    return int(min_streams + (popularity / 100) * (max_streams - min_streams))

class PopularitySelect(discord.ui.Select):
    def __init__(self, playlists, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.playlists = playlists
        self.options = [discord.SelectOption(label=playlist['name'], value=playlist['id']) for playlist in playlists]

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer()
        playlist_id = self.values[0]
        selected_playlist = next((p for p in self.playlists if p['id'] == playlist_id), None)

        if selected_playlist:
            tracks = await fetch_all_playlist_tracks(playlist_id)
            total_popularity = sum(track['track']['popularity'] for track in tracks if track['track'])
            average_popularity = total_popularity / len(tracks) if tracks else 0

            total_estimated_streams = estimate_streams(total_popularity)
            average_estimated_streams = estimate_streams(average_popularity)

            top_tracks = sorted(tracks, key=lambda t: t['track']['popularity'], reverse=True)[:5]
            top_tracks_message = "\n".join(
                [f"{i+1}. {track['track']['name']} - Popularity: {track['track']['popularity']}"
                 for i, track in enumerate(top_tracks)]
            )

            message = (f"**Playlist: {selected_playlist['name']}**\n"
                       f"**Total Popularity**: {locale.format_string('%d', total_popularity, grouping=True)}\n"
                       f"**Total Estimated Streams**: {locale.format_string('%d', total_estimated_streams, grouping=True)}\n"
                       f"**Average Popularity**: {locale.format_string('%.2f', average_popularity, grouping=True)}\n"
                       f"**Average Estimated Streams per Song**: {locale.format_string('%d', average_estimated_streams, grouping=True)}\n\n"    
                       f"**Top 5 Most Popular Tracks:**\n{top_tracks_message}")

            await interaction.followup.send(message)

class PopularityView(discord.ui.View):
    def __init__(self, playlists, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.add_item(PopularitySelect(playlists=playlists, placeholder="Choose a playlist"))

@bot.command()
async def popularity(ctx, genre_code: int = None):

    playlists = fetch_playlists_by_genre(genre_code)

    # current_user = sp.current_user()
    # user_id = current_user['id']
    # playlists = sp.current_user_playlists(limit=50)['items']
    # own_playlists = [playlist for playlist in playlists if playlist['owner']['id'] == user_id]

    if not playlists:
        await ctx.send("Fetch didn't work. Try again.")
        return

    await ctx.send("Select a Spotify playlist to analyze popularity:", view=PopularityView(playlists=playlists))

@bot.command()
async def randomsong(ctx, genre_code: int = None):
    playlists = fetch_playlists_by_genre(genre_code)

    # user_id = sp.current_user()['id']
    # playlists = sp.current_user_playlists(limit=50)['items']
    # own_playlists = [playlist for playlist in playlists if playlist['owner']['id'] == user_id]

    if not playlists:
        await ctx.send("Fetch didn't work. Try again.")
        return

    await ctx.send("Select a Spotify playlist:", view=SongPlaylistView(playlists=playlists))

class RandomSongSelect(discord.ui.Select):
    def __init__(self, playlists, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.playlists = playlists
        self.options = [discord.SelectOption(label=playlist['name'], value=playlist['id']) for playlist in playlists]
    
    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer()
        playlist_id = self.values[0]
        tracks = await fetch_all_playlist_tracks(playlist_id)

        if not tracks:
            await interaction.followup.send("The selected playlist is empty.")
            return

        # Select a random song
        selected_track = random.choice(tracks)['track']
        song_name = selected_track['name']
        album_cover_url = selected_track['album']['images'][0]['url']

        # Send the album cover image along with the song name and artist
        artists = ', '.join([artist['name'] for artist in selected_track['artists']])
        embed = discord.Embed(
            title=f"Random Song: {song_name}",
            description=f"Artist(s): {artists}",
            color=discord.Color.blue()
        )
        embed.set_image(url=album_cover_url)

        await interaction.followup.send(embed=embed)

class SongPlaylistView(discord.ui.View):
    def __init__(self, playlists, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.add_item(RandomSongSelect(playlists=playlists, placeholder="Choose a playlist"))

@bot.command()
async def guess(ctx, genre_code: int = None):
    # Check if the command is being used in a DM channel
    if not isinstance(ctx.channel, discord.DMChannel):
        await ctx.send("You need to be in DMs to execute this command.")
        return
    
    playlists = fetch_playlists_by_genre(genre_code)
    
    # user_id = sp.current_user()['id']
    # playlists = sp.current_user_playlists(limit=50)['items']
    # own_playlists = [playlist for playlist in playlists if playlist['owner']['id'] == user_id]

    if not playlists:
        await ctx.send("Fetch didn't work. Try again.")
        return

    await ctx.send("Select a Spotify playlist:", view=GuessPlaylistView(playlists=playlists))

class GuessGameSelect(discord.ui.Select):
    def __init__(self, playlists, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.playlists = playlists
        self.options = [discord.SelectOption(label=playlist['name'], value=playlist['id']) for playlist in playlists]

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer()
        playlist_id = self.values[0]
        tracks = await fetch_all_playlist_tracks(playlist_id)

        if not tracks:
            await interaction.followup.send("The selected playlist is empty.")
            return

        # Select a random song
        selected_track = random.choice(tracks)['track']
        album_name = selected_track['album']['name']
        album_cover_url = selected_track['album']['images'][0]['url']
        artist_names = [artist['name'] for artist in selected_track['artists']]

        # Store game data
        ongoing_game[interaction.channel_id] = {
            "game_type": "guess",
            "album_name": album_name.lower(),
            "artist_names": [artist.lower() for artist in artist_names],
            "attempts": 0
        }

        embed = discord.Embed(
            title="Guess the Album and Artist!",
            description="Type your guess in the format `[Album name] / [Artist]`. **You get 10 attempts!** *Hints will be progressively provided as you guess incorrectly.* Type `exit` to end the game at any point.",
            color=discord.Color.blue()
        )
        embed.set_image(url=album_cover_url)

        await interaction.followup.send(embed=embed)

class GuessPlaylistView(discord.ui.View):
    def __init__(self, playlists, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.add_item(GuessGameSelect(playlists=playlists, placeholder="Choose a playlist"))

# Global dictionary to track ongoing game by channel
ongoing_game = {}

@bot.command()
async def preview(ctx, genre_code: int = None):
    
    playlists = fetch_playlists_by_genre(genre_code)
    
    # user_id = sp.current_user()['id']
    # playlists = sp.current_user_playlists(limit=50)['items']
    # own_playlists = [playlist for playlist in playlists if playlist['owner']['id'] == user_id]

    if not playlists:
        await ctx.send("Fetch didn't work. Try again.")
        return

    select = discord.ui.Select(placeholder="Choose your playlist",
                               options=[discord.SelectOption(label=playlist['name'], value=playlist['id'])
                                        for playlist in playlists])

    async def select_callback(interaction):
        await interaction.response.defer()
        playlist_id = select.values[0]
        tracks = await fetch_all_playlist_tracks(playlist_id)

        if not tracks:
            await interaction.followup.send("The selected playlist is empty.")
            return

        selected_track = random.choice(tracks)['track']
        track_name = selected_track['name']  # Extract the name of the track
        track_name = re.sub(r"\[.*?\]|\(.*?\)", "", track_name).strip()  # Clean the track name

        preview_url = selected_track['preview_url']

        if preview_url is None:
            await interaction.followup.send("Preview not available for the selected track.")
            return
        
        # Check if the author is in a guild (server)
        if ctx.guild is None:
            await ctx.send("You must use this command in a voice channel in a server!")
            return
    
        if ctx.author.voice and ctx.author.voice.channel:
            channel = ctx.author.voice.channel
            voice_client = discord.utils.get(bot.voice_clients, guild=ctx.guild)

            ffmpeg_options = {
                'options': '-t 30'  # Play for 30 seconds
            }

            if voice_client and voice_client.is_connected():
                await voice_client.move_to(channel)
            else:
                voice_client = await channel.connect()

            audio_source = discord.FFmpegPCMAudio(preview_url, **ffmpeg_options)
            volume_adjusted_source = discord.PCMVolumeTransformer(audio_source, volume=0.25)  # 25% volume
            voice_client.play(volume_adjusted_source, after=lambda e: bot.loop.create_task(voice_client.disconnect()))

            start_time = time.time()
            ongoing_game[ctx.channel.id] = {
                "game_type": "preview",
                "track_name": selected_track['name'].lower(),
                "artist_names": [artist['name'].lower() for artist in selected_track['artists']],
                "start_time": start_time,
                "guild": ctx.guild,
                "channel": ctx.channel
            }

            # Start a timer to end the game after 1 minute
            bot.loop.create_task(end_game_after_timeout(ctx.channel.id, 60))  # 60 seconds timeout

            await interaction.followup.send("Guess the song and artist! Type your answer in the format `[Track name] / [Artist]`.")
        else:
            await interaction.followup.send("You are not connected to a voice channel.")

    select.callback = select_callback

    view = discord.ui.View()
    view.add_item(select)
    await ctx.send("Select a Spotify playlist:", view=view)

async def end_game_after_timeout(channel_id, timeout):
    await asyncio.sleep(timeout)
    game_data = ongoing_game.pop(channel_id, None)
    if game_data:
        guild = game_data['guild']
        channel = game_data['channel']  # Get the stored channel object
        voice_client = discord.utils.get(bot.voice_clients, guild=guild)
        if voice_client and voice_client.is_connected():
            await voice_client.disconnect()
        await channel.send("Timed Out: Game Ended.")

@bot.event
async def on_message(message):
    await bot.process_commands(message)

    if message.author == bot.user:
        return

    # Check if there's an ongoing game in this channel
    game_data = ongoing_game.get(message.channel.id)

    user = message.author
    channel_id = message.channel.id
    current_user = sp.current_user()
    user_id = str(user.id)
    username = user.name

    if game_data:
        voice_client = discord.utils.get(bot.voice_clients, guild=message.guild)

        if message.content.startswith('!'):
            if voice_client and voice_client.is_connected():
                await voice_client.disconnect()
            await message.channel.send("Game ended because a new command was entered.")
            ongoing_game.pop(message.channel.id, None)
            return

        game_type = game_data.get('game_type')
        
        if game_type == 'preview':
            guess = message.content.lower().strip()
            track_name, artist_names = game_data['track_name'], game_data['artist_names']
            guessed_track, guessed_artist = (guess.split(' / ') + ["", ""])[:2]

            end_time = time.time()
            time_taken = end_time - game_data['start_time']
            time_taken_ms = int((time_taken % 1) * 1000)
            max_time = 30  # Max time in seconds to earn points
            max_points = 15  # Maximum points possible
            min_points = 3  # Minimum points
            points_awarded = max(int(max_points - (time_taken / max_time * max_points)), min_points)

            ongoing_game.pop(message.channel.id, None)  # End the game after one guess

            if guessed_track == track_name and guessed_artist in artist_names:
                if voice_client and voice_client.is_connected():
                    await voice_client.disconnect()
                user_scores = load_user_scores()
                if not user_id in user_scores.keys():
                    user_scores[user_id] = {
                        "username": username,
                        "pp": 0,
                        "uses": 0,
                    }
                user_scores[user_id]['pp'] += points_awarded
                save_user_scores(user_scores)
                await message.channel.send(f"{message.author.display_name} got the correct answer `{guessed_track} / {guessed_artist}` in {int(time_taken)} seconds and {time_taken_ms} milliseconds ({points_awarded} coins). \nYou currently have **{user_scores[user_id]['pp']}** coins.")
            else:
                if voice_client and voice_client.is_connected():
                    await voice_client.disconnect()
                correct_artist = artist_names[0]
                await message.channel.send(f"Incorrect guess! The correct answer was `{track_name} / {correct_artist}`. You took {int(time_taken)} seconds and {time_taken_ms} milliseconds.")

        # Handling for the album guessing game
        elif game_type == 'guess':
            guess = message.content.lower().strip()

            album_name, artist_names = game_data['album_name'], game_data['artist_names']
            album_name = re.sub(r"\[.*?\]|\(.*?\)", "", album_name).strip()

            guessed_album, guessed_artist = (guess.split(' / ') + ["", ""])[:2]
            
            if guess == 'exit':
                await message.channel.send("Game ended. Thanks for playing!")
                await message.channel.send(f"\nThe correct answer was `{album_name} / {', '.join(artist_names)}`.")
                ongoing_game.pop(message.channel.id, None)
                return

            # Logic for checking guesses, providing hints, etc.
            # Update this part with the specific logic for the album guessing game
            # Similar to how you have it in your current `on_message` handling for the `guess` game

            # Increment the number of attempts
            game_data['attempts'] += 1
            attempts = game_data['attempts']

            album_match = guessed_album == album_name.lower()
            artist_match = any(guessed_artist == artist.lower() for artist in artist_names)

            # Generate hints based on the number of attempts
            def reveal_characters(name, indices):
                return ' '.join('_' if i not in indices and c != ' ' else c for i, c in enumerate(name))

            def get_first_indices(name):
                return [0] + [i+1 for i, c in enumerate(name[:-1]) if c == ' ']

            def get_last_indices(name):
                return [i-1 for i, c in enumerate(name[1:], 1) if c == ' '] + [len(name)-1]

            hint_artist = artist_names[0]  # Use the first artist for hints
            other_artists_count = len(artist_names) - 1
            hint_album = ''
            if attempts >= 9:
                hint_album = reveal_characters(album_name, get_first_indices(album_name) + get_last_indices(album_name))
                hint_artist = reveal_characters(hint_artist, get_first_indices(hint_artist) + get_last_indices(hint_artist))
            elif attempts >= 7:
                hint_album = reveal_characters(album_name, get_first_indices(album_name))
                hint_artist = reveal_characters(hint_artist, get_first_indices(hint_artist))
            elif attempts >= 5:
                hint_album = reveal_characters(album_name, [0]) 
                hint_artist = reveal_characters(hint_artist, [0])
            elif attempts >= 3:
                hint_album = reveal_characters(album_name, [])
                hint_artist = reveal_characters(hint_artist, [])

            response_message = ""

            # Start forming the response message early to avoid sending an empty message
            if attempts == 10:
                response_message += f"**Too many attempts!** The correct answer was `{album_name} / {', '.join(artist_names)}`."
                ongoing_game.pop(message.channel.id, None)  # End the game after a correct guess
            else:
                response_message += f"Attempt {attempts} *({10 - attempts} attempt(s) left)*: "

                if album_match and artist_match:
                    username = user.name
                    user_scores = load_user_scores()
                    if not user_id in user_scores.keys():
                        user_scores[user_id] = {
                            "username": username,
                            "pp": 0,
                            "uses": 0
                        }
                    user_scores[user_id]['pp'] += 10-attempts
                    save_user_scores(user_scores)
                    response_message += f"\nCongratulations, **{username}**! You guessed both correctly in **{attempts} attempt(s)!**"
                    response_message += f"\nThe correct answer was `{album_name} / {', '.join(artist_names)}`."
                    response_message += f"\nYou received **{10-attempts} coins**! *(10 - {attempts} attempts)*"
                    response_message += f"\nYou currently have **{user_scores[user_id]['pp']}** coins."
                    ongoing_game.pop(message.channel.id, None)  # End the game after a correct guess
                else:
                    if album_match:
                        response_message += "\n**You got the album name correct!**"
                    elif artist_match:
                        if len(artist_names) == 1:
                            response_message += "\n**You got the artist correct!**"
                        else:
                            response_message += "\n**You got one of the artists correct!**"
                    else:
                        response_message += "\n**Both the album name and artist are incorrect.**"

                    # Add hints to the response
                    if hint_album and hint_artist:
                        additional_artist_hint = f" and {other_artists_count} other artist(s)" if other_artists_count > 0 else ""
                        response_message += f"\nHint: `{hint_album} / {hint_artist}{additional_artist_hint}`"

                    response_message += "\nTry again, or type `exit` to end the game."
                await message.channel.send(response_message)

        elif game_data['game_type'] == 'lyrics':
                end_time = time.time()
                time_taken = end_time - game_data['start_time']
                time_taken_ms = int((time_taken % 1) * 1000)
                max_time = 30  # Max time in seconds to earn points
                max_points = 15  # Maximum points possible
                min_points = 3  # Minimum points
                points_awarded = max(int(max_points - (time_taken / max_time * max_points)), min_points)

                # User is trying to guess the song based on lyrics provided
                guess = message.content.lower().strip()
                correct_song = game_data['song_name'].lower()
                correct_artists = [artist.lower() for artist in game_data['artist_names']]

                # Checking user's guess against correct song and artist
                if correct_song in guess and any(artist in guess for artist in correct_artists):
                    # Correct guess
                    user_scores = load_user_scores()
                    if not user_id in user_scores.keys():
                        user_scores[user_id] = {
                            "username": username,
                            "pp": 0,
                            "uses": 0,
                        }
                    else:
                        user_scores[user_id]['pp'] += points_awarded
                    save_user_scores(user_scores)
                    await message.channel.send(f"{message.author.display_name} got the correct answer `{guessed_track} / {guessed_artist}` in {int(time_taken)} seconds and {time_taken_ms} milliseconds ({points_awarded} coins). \nYou currently have **{user_scores[user_id]['pp']}** coins.")

                    ongoing_game.pop(message.channel.id)  # End the game for this channel
                else:
                    # Incorrect guess
                    game_data['attempts'] += 1
                    if game_data['attempts'] >= 2:
                        # Too many incorrect guesses
                        await message.channel.send(f"Incorrect! The correct answer was '{correct_song}' by '{', '.join(game_data['artist_names'])}'.")
                        ongoing_game.pop(message.channel.id)  # Remove game state
                    else:
                        # Provide another chance
                        await message.channel.send("Incorrect guess! Try again. Remember, format your answer as `[Song name] / [Artist]`.")
@bot.command()
async def blend(ctx):
    current_user = sp.current_user()
    uid = current_user['id'] 
    playlists = sp.current_user_playlists(limit=50)['items']  # Increase limit if necessary
    own_playlists = [playlist for playlist in playlists if playlist['owner']['id'] == uid]  # Filter for user's own playlists

    if not own_playlists:
        await ctx.send("You don't have any public playlists.")
        return

    all_tracks = []
    for playlist in own_playlists:
        tracks = await fetch_all_playlist_tracks(playlist['id'])
        all_tracks.extend(tracks)

    if not all_tracks:
        await ctx.send("Your playlists don't have any tracks.")
        return

    # Initialize message
    msg = "**Your 50-track blend:**\n>>> "
    message_character_limit = 2000

    for i in range(1, 51):
        if not all_tracks:  # Check if there are no more tracks to list
            break

        track = random.choice(all_tracks)
        track_info = f"{i}. **{track['track']['name']}** by **{track['track']['artists'][0]['name']}**\n"
        if len(msg) + len(track_info) > message_character_limit:
            await ctx.send(msg)
            msg = ">>> "  # Start a new message
        msg += track_info
        all_tracks.remove(track)

    # Send any remaining message content
    if msg.strip():
        await ctx.send(msg)

    await ctx.send("(More features coming soon!)")

@bot.command()
async def top(ctx):
    user_scores = load_user_scores()
    scores = []
    msg = "**Top 10 users (globally), by coins**"
    for uid in user_scores:
        scores.append([user_scores[uid]["pp"], user_scores[uid]["username"]])
    scores.sort(reverse=True)
    for i in range(min(10, len(scores))):
        msg += f"\n{i+1}. **{scores[i][1]}**: {scores[i][0]} coins"
    await ctx.send(msg)

@bot.command()
async def uses(ctx):
    user_scores = load_user_scores()
    scores = []
    msg = "**Top 10 users (globally), by command uses**"
    for uid in user_scores:
        scores.append([user_scores[uid]["uses"], user_scores[uid]["username"]])
    scores.sort(reverse=True)
    for i in range(min(10, len(scores))):
        msg += f"\n{i+1}. **{scores[i][1]}**: {scores[i][0]} command uses"
    await ctx.send(msg)

class LyricsGameSelect(discord.ui.Select):
    def __init__(self, playlists, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.playlists = playlists
        self.placeholder = 'Select a Spotify playlist'
        self.options = [
            discord.SelectOption(label=playlist['name'], value=playlist['id'])
            for playlist in playlists
        ]

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer()

        playlist_id = self.values[0]
        tracks = await fetch_all_playlist_tracks(playlist_id)

        if not tracks:
            await interaction.response.send_message("The selected playlist is empty.")
            return

        # Choose a random track
        random_track = random.choice(tracks)['track']
        track_name = re.sub(r"\[.*?\]|\(.*?\)", "", random_track['name']).strip()
        genius = lyricsgenius.Genius(genius_api_token)
        song = genius.search_song(track_name, random_track['artists'][0]['name'])

        if not song:
            await interaction.response.send_message("Failed to fetch lyrics. Try another track.")
            return

        # Set up the ongoing game data
        start_time = time.time()
        ongoing_game[interaction.channel_id] = {
            "game_type": "lyrics",
            "song_name": song.title,
            "artist_names": [artist['name'] for artist in random_track['artists']],
            "start_time": start_time,
            "lyrics": song.lyrics,
            "attempts": 0
        }

        lyrics = song.lyrics.split('\n')
        line_counts = {}
        for line in lyrics[1:][:-1]:
            if line.strip():
                if not '[' in line and not ']' in line and not '(' in line and not ')' in line:
                    if track_name in line:
                        line_counts[line] = line_counts.get(line, 0) + 2
                    else:
                        line_counts[line] = line_counts.get(line, 0) + 1
        best_line = max(line_counts, key=line_counts.get)
        await interaction.followup.send(f"**30 Seconds! Guess the song name and artist of this verse!**\nType your guess in this format: `[Song name] / [Artist]`!\n\n>>> ## {best_line}")
        
        # Start waiting for guesses with a timeout
        asyncio.create_task(wait_for_guess(interaction.channel_id))

async def wait_for_guess(channel_id, timeout=30):
    await asyncio.sleep(timeout)  # Simply wait for the timeout period
    if channel_id in ongoing_game:
        channel = bot.get_channel(channel_id)
        await channel.send("Time's up! Better luck next time.")
        ongoing_game.pop(channel_id, None)  # Remove the game state after timeout


class LyricsGameView(discord.ui.View):
    def __init__(self, playlists, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.add_item(LyricsGameSelect(playlists=playlists))

@bot.command()
async def lyrics(ctx, genre_code: int = None):
    playlists = fetch_playlists_by_genre(genre_code)
    if not playlists:
        await ctx.send("No suitable playlists found.")
        return

    await ctx.send("Select a playlist for the lyrics game:", view=LyricsGameView(playlists=playlists))

bot.run(os.getenv("DISCORD_TOKEN"))