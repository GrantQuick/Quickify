import os.path
import sys
import pickle
import googleapiclient.errors

from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from google.auth.transport.requests import Request
from difflib import SequenceMatcher
from textify import clean_string

class YouTube:

    # Disable OAuthlib's HTTPS verification when running locally.
    # *DO NOT* leave this option enabled in production.
    os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

    def __init__(self, playlist_name):
        client_secrets_file = "client_secret.json"
        scopes = ["https://www.googleapis.com/auth/youtube.force-ssl"]
        api_service_name = "youtube"
        api_version = "v3"

        self.playlist = []
        self.videos = []
        self.videos_added = 0
        self.videos_removed = 0

        # Get credentials and create an API client
        creds = None
        if os.path.exists('token.pickle'):
            with open('token.pickle', 'rb') as __token:
                creds = pickle.load(__token)
        # If there are no (valid) credentials available, let the user log in.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    client_secrets_file, scopes)
                creds = flow.run_local_server()
            # Save the credentials for the next run
            with open('token.pickle', 'wb') as __token:
                pickle.dump(creds, __token)
        self.youtube = build(api_service_name, api_version, credentials=creds)

        self.get_playlist(playlist_name)
        if not self.playlist:
            # print("YouTube playlist does not exist")
            create_playlist =  self.ask_user()
            if not create_playlist:
                print("Sync cancelled")
                exit(0)
            else:
               self.new_playlist(playlist_name)
        self.get_playlist_videos()

    # Search for a video
    def find_video(self, search_term_list):
        search_term = ' '.join([str(elem) for elem in search_term_list])
        request = self.youtube.search().list(
            part="snippet",
            maxResults=1,
            q=search_term,
            type="video",
            fields="items(snippet(title),id(videoId))"
        )
        response = request.execute()

        return [response['items'][0]['snippet']['title'],response['items'][0]['id']['videoId']]

    # Get a playlist
    def get_playlist(self,playlist_name):
        
        playlists = []
        
        request = self.youtube.playlists().list(
            part="snippet",
            mine=True,
            fields="items(id,snippet(title)),nextPageToken",
            maxResults=50
        )
        
        response = request.execute()
        items = response['items']
        
        for item in items:
            playlists.append([item['id'],[item][0]['snippet']['title']])

        while 'nextPageToken' in response:
            request = self.youtube.playlists().list(
                part="snippet",
                mine=True,
                fields="items(id,snippet(title)),nextPageToken",
                maxResults=50,
                pageToken=response['nextPageToken']
            )
            response = request.execute()
            items = response['items']
            for item in items:
                playlists.append([item['id'],[item][0]['snippet']['title']])

        for title_id in playlists:
            if playlist_name in title_id:
                self.playlist = title_id
    
    # Get all the videos in a playlist
    # Grab the videoId, title and playlistVideoId
    def get_playlist_videos(self):
        request = self.youtube.playlistItems().list(
            part="snippet",
            fields="items(snippet(resourceId(videoId)),snippet(title),id),nextPageToken",
            playlistId=self.playlist[0],
            maxResults=50
        )
        response = request.execute()
        for item in response['items']:
            clean_video_title = clean_string(item['snippet']['title'])
            self.videos.append([item['snippet']['resourceId']['videoId'],clean_video_title,item['id']])

        while 'nextPageToken' in response:
            request = self.youtube.playlistItems().list(
                part="snippet",
                fields="items(snippet(resourceId(videoId)),snippet(title),id),nextPageToken",
                playlistId=self.playlist[0],
                pageToken=response['nextPageToken'],
                maxResults=50
            )

            response = request.execute()
            for item in response['items']:
                clean_video_title = clean_string(item['snippet']['title'])
                self.videos.append([item['snippet']['resourceId']['videoId'],clean_video_title,item['id']])
    
    def sync_playlist(self, spotify_tracks, youtube_playlist):
        
        in_video_playlist = False

        # Add new videos
        for track in spotify_tracks:
            spot_words = track[0] + track[1]
                        
            # Check if the track's artist and title already exist in a video within the YouTube playlist
            for video in self.videos:
                                
                in_video_playlist = False

                if all(word in video[1] for word in spot_words):
                    in_video_playlist = True
                    break

            # If artist and title can't be found in a video, search for YouTube for it
            if not in_video_playlist:
                print(f"Searching for: {spot_words}")
                found_video = self.find_video(spot_words)
                # Check if the found video's id already exists in a video within the YouTube playlist
                # i.e. don't add duplicates
                for video in self.videos:
                    if found_video[1] in video[0]:
                        in_video_playlist = True
                        print(f"Already in playlist: {spot_words}. Video: {video[1]}")
                        # Add the video id to the spotify track
                        track[2] = found_video[1]
                        break
            if not in_video_playlist:
                self.add_video(found_video[1])
                self.videos_added += 1
                print("Added: " + found_video[0])

        # Remove videos not in playlist
        for video in self.videos:
            in_spotify_playlist = False
            for track in spotify_tracks:
                rem_spot_words = track[0] + track[1]
                if all(word in video[1] for word in rem_spot_words):
                    in_spotify_playlist = True
                    break
            
            # make sure
            for track in spotify_tracks:
                if track[2] == video[0]:
                    in_spotify_playlist = True
                    print("Not removing: " + ' '.join([str(elem) for elem in video[1]]))
                    break

            if not in_spotify_playlist:
                self.find_video(rem_spot_words)
                print("Removed: " + ' '.join([str(elem) for elem in video[1]]))
                self.remove_video(video[2])
                self.videos_removed += 1
        
        print(f"Sync complete, {self.videos_added} video(s) added, {self.videos_removed} video(s) removed")
        

    def add_video(self,video_id):
        request = self.youtube.playlistItems().insert(
            part="snippet",
            body={
                'snippet': {
                    'playlistId': self.playlist[0],
                    'position': 1,
                    'resourceId': {
                        'kind': 'youtube#video',
                        'videoId': video_id
                    }
                }
            }
        )
        request.execute()
        
    def remove_video(self, video_playlist_id):
        request = self.youtube.playlistItems().delete(
                id=video_playlist_id
            ).execute()

    def ask_user(self):
        check = str(input("YouTube playlist does not exist. Would you like to create it? (Y/N): ")).lower().strip()
        try:
            if check[0] == 'y':
                return True
            elif check[0] == 'n':
                return False
            else:
                print('Please press Y or N')
                return self.ask_user()
        except Exception as error:
            print("Please enter valid inputs")
            print(error)
            return self.ask_user()
        return check

    def new_playlist(self,playlist_name):
        request = self.youtube.playlists().insert(
            part="snippet",
            body={
                "snippet": {
                "title": playlist_name
                }
            },
            fields="id"
        )
        response = request.execute()
        print(f"{playlist_name} playlist created")
        self.playlist = [response['id'],playlist_name]