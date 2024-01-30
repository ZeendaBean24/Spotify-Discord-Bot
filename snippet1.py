import spotipy
from spotipy.oauth2 import SpotifyOAuth

sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id='id',
                                               client_secret='secret',
                                               redirect_uri='uri',
                                               scope='playlist-read-private'))

user_playlists = sp.current_user_playlists()

