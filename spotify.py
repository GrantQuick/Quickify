import spotipy
import spotipy.util as util
from spotipy.oauth2 import SpotifyOAuth

from textify import clean_string


class Spotify:
    
    __redirect_uri = 'https://localhost/'
    __scope = 'user-library-read'

    def __init__(self, username, client_id, client_secret):
        self.username = username
        self.__sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=client_id,client_secret=client_secret,scope=self.__scope,username=self.username,redirect_uri=self.__redirect_uri))
        
    # Get all the saved tracks in the current user's library
    def get_saved_tracks(self):
        tracks = []
        results = self.__sp.current_user_saved_tracks()

        for item in results['items']:
            clean_artist = clean_string(item['track']['artists'][0]['name'])
            clean_track = clean_string(item['track']['name'])
            tracks.append([clean_artist,clean_track,''])

        while results['next']:
            results = self.__sp.next(results)
            for item in results['items']:
                clean_artist = clean_string(item['track']['artists'][0]['name'])
                clean_track = clean_string(item['track']['name'])
                tracks.append([clean_artist,clean_track,''])
        return tracks

    # Get all playlists for user, if the supplied playlist exists get
    # all tracks in that playlist
    def get_playlist_tracks(self, playlist_name):
        tracks = []
        playlists = []
        
        # Get list of all playlists
        results = self.__sp.current_user_playlists()

        for item in results['items']:
            playlists.append([item['name'],item['id']])

        while results['next']:
            results = self.__sp.next(results)
            for item in results['items']:
                playlists.append([item['name'],item['id']])


        # If the provided playlist name matches one of the playlists,
        # grab all the tracks from that playlist
        for title_id in playlists:

            if playlist_name.lower() in title_id[0].lower():
                results = self.__sp.user_playlist_tracks(self.username,title_id[1])
                
                for item in results['items']:
                    clean_artist = clean_string(item['track']['artists'][0]['name'])
                    clean_track = clean_string(item['track']['name'])
                    tracks.append([clean_artist,clean_track,''])
                
                while results['next']:
                    results = self.__sp.next(results)
                    for item in results['items']:
                        clean_artist = clean_string(item['track']['artists'][0]['name'])
                        clean_track = clean_string(item['track']['name'])
                        tracks.append([clean_artist,clean_track,''])
                return tracks
