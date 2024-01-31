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

# Retrieve the current user's Spotify ID
user_id = sp.current_user()["id"]

# Retrieve the current user's playlists
user_playlists = sp.current_user_playlists()

# Display playlists and store them in a dictionary with an index
playlist_dict = {}
index = 1
for playlist in user_playlists['items']:
    if playlist['owner']['id'] == user_id:  # Check if the playlist is owned by the user
        playlist_dict[index] = playlist
        print(f"{index}. Playlist Name: {playlist['name']}")
        index += 1

# Prompt the user to select two playlists
print("Please enter the numbers of two (public) playlists you want to select, separated by a comma (e.g., 1,2):")
selected_indexes = input().split(',')

# Convert input to integers and get the selected playlists
selected_playlists = [playlist_dict[int(i)] for i in selected_indexes]

# Display details for the selected playlists
for playlist in selected_playlists:
    print(f"Playlist Name: {playlist['name']}")
    print(f"Playlist ID: {playlist['id']}")
    print(f"Owner: {playlist['owner']['display_name']}")
    print(f"Total Tracks: {playlist['tracks']['total']}")
    print(f"Description: {playlist['description']}")
    print("---")


def get_playlist_genres(playlist_id):
    tracks = sp.playlist_tracks(playlist_id)
    genres = set()

    for track in tracks['items']:
        for artist in track['track']['artists']:
            artist_info = sp.artist(artist['id'])
            for genre in artist_info['genres']:
                genres.add(genre)

    return list(genres)