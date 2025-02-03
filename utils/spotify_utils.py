import re
from .custom_errors import URLError
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import os
from dotenv import load_dotenv
from time import sleep

def spotify_authenticator():
    """
        Authenticates the user with the Spotify API
    """
    # set up load_dotenv
    load_dotenv()

    # get the client id and secret from the environment variables
    client_id = os.getenv("SPOTIPY_CLIENT_ID")
    client_secret = os.getenv("SPOTIPY_CLIENT_SECRET")
    cache_path = os.getenv("CACHE_PATH")

    # if the client id and secret are not found in the environment variables
    if not client_id or not client_secret:
        raise URLError("Client ID or Client Secret not found in the environment variables.")
    if not cache_path:
        raise URLError("Cache path not found in the environment variables.")

    # Ensure the directory exists
    os.makedirs(os.path.dirname(cache_path), exist_ok=True)

    # authenticate the user
    sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
                    client_secret=client_secret, 
                    redirect_uri="http://localhost:8080", 
                    scope="user-read-playback-state user-modify-playback-state",
                    cache_path= cache_path))
    
    return sp


def spotify_playback(sp: spotipy.Spotify, rfid_data):
    """
        Initiates the playback process for the Spotify API

        params:
            sp: spotipy.Spotify - the authenticated Spotify object
            device_id: str - the device id of the device to play the media
            rfid data: the data linked to the RFID card
    """
    # Import enviromental variables
    load_dotenv()

    # Get environmental variables
    device_id = os.getenv("RASPI_ID")
    if not device_id:
        raise ValueError("Device ID (RASPI_ID) not found in environment variables.")

    # extract uri and media type from rfid_data
    uri = rfid_data["Item"].values[0]
    media_type = rfid_data["Media Type"].values[0]

    # if an album or playlist - uses context_uri
    if media_type in ['album', 'playlist']:
        sp.start_playback(device_id= device_id, context_uri=uri)
        print("Playing!\n")

    # if it is a track - uses uris
    elif media_type == 'track':
        sp.start_playback(device_id= device_id, uris=[uri])
        print("Playing!\n")

    else:
        raise ValueError(f"Media Type '{media_type}' not recognized.\n")

    sleep(2)

    return


def spotify_link_extractor(url:str):

    """
        In order to properly use the uri, we need to extract the proper item from the uri

        this function cleans the uri and returns the proper item
    """
    
    if not url.startswith("https://open.spotify.com/"):
        raise URLError("Invalid Spotify URL format.")
    
    # note: all proper links start the same
    # trim the beginning of the url 
    trimmed_url = re.search(r"https://open.spotify.com/(.+)", url)

    # error handling 
    if not trimmed_url:
        raise URLError("The URL does not match the expected pattern.")

    # return the media type (album, track or playlist)
    item_type = re.search(r"^[^/]+", trimmed_url.group(1))
    
    # returns the needed actionable uri
    item = re.search(r"/([^?]+)", trimmed_url.group(1))
    
    # item is extracted but must be reformatted correctly for our code
    item = f"spotify:{item_type.group(0)}:{item.group(1)}"

    # if both items are correctly found
    if item_type and item:
        return  item_type.group(0), item # returns the type (album, track or playlist) and the needed uri

    # else did not find the expected match
    # note: again, must be a spotify link.
    else: 
        raise URLError("The URL does not match the expected pattern.")
    
    