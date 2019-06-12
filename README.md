# Quickify
A Python script for syncing a Spotify playlist to YouTube.

## Getting Started
You will need to create and register an application with Spotify. Once an application has been created, you will need the **client_id** of the application, the **client_secret** of your application, and the username associated with your Spotify account.

You will also need to create and register a project with YouTube.

### Creating a Spotify Application
Follow the instructions at https://developer.spotify.com/documentation/web-api/quick-start/ to create a new Spotify application and acquire your **client_id** and **client_secret**. You can use https://localhost/ as a redirect URL.

### Creating a YouTube Application
Follow the instructions at https://developers.google.com/youtube/v3/getting-started. Your application will need to use the YouTube Data API. Once you have set up a project, you will need to create and download OAuth 2.0 credentials for your project. To do this:
1. Visit the [Google Developers Console](https://console.developers.google.com/)
2. Select your newly-created project
3. Click Credentials
4. Click Create Credentials
5. Choose OAuth client ID
6. Choose Web application
7. Give the credential a name
8. Click Create
9. Download the JSON file for your new credential
10. Rename this file client_secret.json

### Using the Script
1. Clone or download the script
2. Install the requirements
3. Add your Spotify username, client_id and client_secret to the config.json file
4. Place the YouTube OAuth 2.0 json file you created into the Quickify project folder
5. Open quickify.py and set the value of spotify_playlist to be the name of the Spotify playlist you would like to sync. If you would like to sync all saved tracks, set this value to None
6. Still in quickify.py, set the value of youtube_playlist to be the name of the YouTube playlist you would like to sync the Spotify songs to. The script will ask you if you would like to create a new playlist if the one specified does not already exist.
7. Run quickify.py
8. On the initial run, you will be prompted to visit Spotify and YouTube links as part of the OAuth 2.0 authorisation steps. Follow the instructions to authorise the script to connect to your accounts. This only needs to be performed once.
9. The script will loop through the tracks in your Spotify playlist and add the first YouTube video that correspond to search of the track's Artist and Title. The script will also remove ay tracks from the specified YouTube playlist that no longer exist in your Spotify playlist.

## Known Issues
Google only allow a relatively small number of API calls in one 24 hour period. If you have a large playlist, it may not be possible to sync all tracks in one day. If this is the case, you can re-sync the following day and the script will add the missing tracks, or as many as it can until the API call quota is hit again.

The script matches songs based on the artist name and song title. It will pick the first result of a YouTube search using those search terms. As such, the video it retunrs may not always be the "official" music video.

The script may remove videos from the playlist in error. This may occur in instances where the title of the video only contains the name of the track and omits the artist. This would result in a false positive and cause the script to remove the video as it cannot be matched to a track.

## Authors
* **Grant Quick** - *Initial work* - [GrantQuick](https://github.com/GrantQuick)
