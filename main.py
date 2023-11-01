import subprocess
import sys

#check for packages and install
try: 
  if open('cache.txt', 'r').read() != '1':
    packages = open('requirements.txt', 'r').read().splitlines()
    print("installing dependencies")
    for i in range(len(packages)):
      subprocess.check_call([sys.executable, "-m", "pip", "install", packages[i]])
    with open('cache.txt', 'w') as f:
      f.write('1')
except:
  open('cache.txt', 'w')
  print("created cache file")
  print("installing dependencies")
  packages = open('requirements.txt', 'r').read().splitlines()
  for i in range(len(packages)):
    subprocess.check_call([sys.executable, "-m", "pip", "install", packages[i]])
  with open('cache.txt', 'w') as f:
    f.write('1')

import spotipy
from spotipy import oauth2
import os
from dotenv import load_dotenv
from ytmusicapi import YTMusic
from tqdm import trange

# Returns a list of songs and a list of artists from a given spotify playlist link
def spotify():

  # Load environment variables
  load_dotenv()
  client_id = os.getenv('API_KEY')
  client_secret = os.getenv('API_SECRET')

  #Authorize dev key
  client_credentials_manager = oauth2.SpotifyClientCredentials(client_id=client_id, client_secret=client_secret)
  sp = spotipy.Spotify(client_credentials_manager = client_credentials_manager)

  #Returns dictionary "tracks" and playlist name
  def get_playlist_tracks(username, playlist_id, sp):
    results = sp.user_playlist_tracks(username, playlist_id)
    playlistname = sp.user_playlist(user=None, playlist_id = playlist_id, fields="name")
    playlistname = playlistname['name']
    tracks = results['items']
    while results['next']:
      results = sp.next(results)
      tracks.extend(results['items'])
    return tracks, playlistname

  #Filters dictionary "tracks" to only return "artist name" and "song name" 
  def filter(tracks, sp):
    artist = ['' for x in range(len(tracks))]
    name = ['' for x in range(len(tracks))]
    for i in range(len(tracks)):
      artist[i] = tracks[i]['track']['artists'][0]['name']
      name[i] = tracks[i]['track']['name']
    return artist, name

  print("Please Enter Your Spotify Playlist URL:")
  try: #Extract Playlist ID
    playlist_uri = input().split("/playlist/")[-1].split("?")[0]
  except:
    print("Link Invalid")
    exit()
  tracks, playlistname = get_playlist_tracks('username', playlist_uri, sp)
  artist, name = filter(tracks, sp)
  return(name, artist, playlistname)

def youtube(name, artist, playlistname):

  # Prompt OAUTH
  os.system('.\ytmusicapi oauth')
  ytmusic = YTMusic("oauth.json")

  # Find playlist ID from a given query
  playlist_id = ytmusic.create_playlist(playlistname, "Imported from Spotify")
  if not playlist_id:
    print("Failed to create playlist")
    exit()
  
  # Find song ID from a given query
  song_id = []
  for i in trange(len(name), desc='Importing songs'):
    song_name = str(name[i] + artist[i])
    songs = ytmusic.search(song_name, "songs")
    if songs:
      song_id.append(songs[0]['videoId'])
    else:
      print(f"\n" + f"Song '{str(name[i] + ' by ' + artist[i])}' not found | Song #{i + 1}")

  # Add songs to playlist
  ytmusic.add_playlist_items(playlist_id, song_id, duplicates=True)
  print(f"Added songs to playlist '{playlistname}' (Playlist ID: {playlist_id}).")

# Run the functions
name, artist, playlistname = spotify()
youtube(name, artist, playlistname)