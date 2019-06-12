import sys
import json
import re

from spotify import Spotify
from youtube import YouTube

# Parameters
spotify_playlist = "Quickify" # Set to None to sync all tracks
youtube_playlist = "Quickify"

# read config file
with open('config.json','r') as myfile:
    data=myfile.read()

# parse config file
config_data = json.loads(data)

spotify = Spotify(config_data['spotify_username'], config_data['spotify_client_id'], config_data['spotify_client_secret'])

# Grab all tracks from saved tracks or specified playlist
if spotify_playlist is None:
    tracks = spotify.get_saved_tracks()
else:
    tracks = spotify.get_playlist_tracks(spotify_playlist)
    
if not tracks:
    print("Spotify playlist does not exist")
    exit()


# Sync playlists
print(f"Spotify playlist contains {len(tracks)} tracks")
youtube = YouTube(youtube_playlist)
print(f"YouTube playlist contains {len(youtube.videos)} videos")
youtube.sync_playlist(tracks,youtube.playlist)