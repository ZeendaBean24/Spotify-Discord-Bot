import spotipy
from spotipy.oauth2 import SpotifyOAuth
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Get your Spotify API credentials from environment variables
client_id = os.getenv("SPOTIPY_CLIENT_ID")
client_secret = os.getenv("SPOTIPY_CLIENT_SECRET")
redirect_uri = os.getenv("SPOTIPY_REDIRECT_URI")

# Initialize the Spotipy client with your credentials and required scope
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=client_id,
                                               client_secret=client_secret,
                                               redirect_uri=redirect_uri,
                                               scope='playlist-read-private'))


# Retrieve the current user's playlists
user_playlists = sp.current_user_playlists()

# Iterate through the playlists and print out their details
for playlist in user_playlists['items']:
    print(f"Playlist Name: {playlist['name']}")
    print(f"Playlist ID: {playlist['id']}")
    print(f"Owner: {playlist['owner']['display_name']}")
    print(f"Total Tracks: {playlist['tracks']['total']}")
    print(f"Description: {playlist['description']}")
    print("---")


