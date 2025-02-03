
import pandas as pd # type: ignore
import sys
import os
sys.path.append('../')
from rfid import RFID_Card
from utils import spotify_link_extractor, URLError, spotify_authenticator, spotify_playback
from rfid import RFID_Card
from time import sleep

class RecordPlayer_DataFrame:
    """
        Contains all the methods to interact with the RFID card database.
    """
    def __init__(self, df_path:str):
        """
            Initializes the class
            
            parameters:
                df_path: str - The path to the csv file
        """
        self.df_path = df_path
        
        # first, we need to check if the csv file exists
        # if it does not exist, we will create it
        try:
            self.df = pd.read_csv(self.df_path)

        # * for the first initiation of the DB *
        except FileNotFoundError:
            # Creates a new DataBase for the RFID cards
            print("No database found. Creating a new database.")
            rfid_c = RFID_Card() # creates an RFID card object
            rfid = rfid_c.read_rfid() 

            if not rfid:
                print("No RFID data found.")
                return
            
            # Create a new database
            # note: first entry will be the overcard entry
            self.create_dataframe(rfid)
            # first_entry = self.new_entry(rfid_data)

            # if first_entry:
            #     self.create_dataframe(**first_entry)
           

    def check_entry(self, rfid):
        """
            Checks if the RFID card number and determines what to do next.
            
            1) its in the database - extract the data
            2) its not in the database - create a new entry
            3) overwrite - overwrite the entry in the database
            
            parameters:
                rfid: int or str - The RFID card number or "overwrite"
                
            returns:
                True - if the RFID card number is in the database
                False - if the RFID card number is not in the database
        """
        # If the RFID card number is in the database, extract the data
        if rfid in self.df['RFID'].values:
            print("RFID card found in the database.")
            
            # if the RFID card number is the overwite card - overwrite the entry
            if self.df[self.df["RFID"] ==  rfid]["Item"].values == "overwrite":
                
                # if the lenght of the database is 1, then the overwrite card is the only card in the database
                if len(self.df) == 1:
                    print("No entries to overwrite. Try again.")
                    sleep(1)
                    return None
                        
                # if the length of the database is greater than 1, then the overwrite card is not the only card in the database
                elif len(self.df) > 1:
                    sleep(1)
                    print("\nOverwriting activated.")
                    # takes in the rfid card number to overwrite and requests a new rfid card number
                    rfid = self.overwrite_entry(rfid)
                
        # if the RFID is not found, create a new entry
        else:
            print("RFID not found, create a new entry.")
            new_entry = self.new_entry(rfid)
            if new_entry:
                self.add_entry_to_database(**new_entry)

            else: 
                print("Failed to create a new entry")
                return None
        
        # Extract the data from database
        data = self.extract_data(rfid)
        return data


    def extract_data(self, rfid:int):
        """
            Extracts the data from the database.

            parameters:
                rfid: int - The RFID card number

            returns:
                prints the data from the database
        """
        # Extract the data from the database
        data = self.df[self.df['RFID'] == rfid]
        print(data)
        return data


    def overwrite_entry(self, overwrite_rfid:int):
        """
            Overwrites the entry in the database.
            
            parameters:
                overwrite_rfid: int - The RFID card number to overwrite
        """
        while True:
            rfid_c = RFID_Card()
            rfid = rfid_c.read_rfid()
        
        # Overwrite card cannot be overwritten. Loop until a different RFID card is read
            if overwrite_rfid == rfid:
                print("Overwrite card cannot be overwritten.")
            else:
                break
    
        # Extract the data from the database
        old_entry = self.df[self.df['RFID'] == rfid]
        
        # If the RFID card number is not in the database
        if old_entry.empty:
            print("RFID card not found in the database.")
            return
        
        # Display the data
        print("Entry Deleted:")
        print(old_entry)
        
        # Remove the old entry
        self.df = self.df[self.df['RFID'] != rfid]

        # Save the updated DataFrame
        self.df.to_csv(self.df_path, index=False)

        # Reload the updated database
        self.df = pd.read_csv(self.df_path)

        # Create a new entry
        new_entry = self.new_entry(rfid)
        if new_entry:
            self.add_entry_to_database(**new_entry)
            print("Entry successfully overwritten.")
        else:
            print("Failed to overwrite the entry.")
        
        return new_entry["rfid"]
    
            
    def new_entry(self, rfid_key:int):
        """
            Creates a new entry for the database.
            
            parameters :
                rfid: int - The RFID card number
                
            returns:
                rfid: int - The RFID card number
                media_type: str - The type of media (song, album, playlist)
                item: str - The item to be played (this is deduced from the url)
                media_name: str - The name of the media
                artist_name: str - The name of the artist
        """
        rfid = rfid_key
        
        # Asks for the spotify link, and extracts the media type and item
        url = input("Enter New Spotify Link: ")
        
        # Extract the media type and item from the url
        try:
            media_type, item = spotify_link_extractor(url)
        except URLError as e:
            print(f"Error: {e}")
            return
        
        # Check if the media item already exists in the database
        if os.path.exists(self.df_path):
            # if item already exists, ask for a new item
            if item in self.df['Item'].values:
                print("This Media item already exixts in the database.")
                return self.new_entry(rfid)
        
        # * Web API request to get the media name and artist name *
        # Authenticate the user
        sp = spotify_authenticator()

        # Get the media name and artist name
        media_name = None
        artist_name = None

        # depending on the media type, we will get the media name and artist name
        try:
            if media_type == "track":
                # Request track metadata
                track = sp.track(item)
                media_name = track['name']  # Track name
                artist_name = track['artists'][0]['name']  # Artist name
            elif media_type == "album":
                # Request album metadata
                album = sp.album(item)
                media_name = album['name']  # Album name
                artist_name = album['artists'][0]['name']  # Artist name
            elif media_type == "playlist":
                # Request playlist metadata (note: playlists don’t have a single artist)
                playlist = sp.playlist(item)
                media_name = playlist['name']  # Playlist name
                artist_name = "Various Artists"  # Placeholder for playlists
            else:
                print(f"Unsupported media type: {media_type}")
                return
        
        except Exception as e:
            print(f"Error fetching metadata from Spotify API: {e}")
            return

        # Display the new entry details
        print("New Entry Details:")

        # Create the database entry dictionary
        entry = {
            "rfid": rfid,
            "media_type": media_type,
            "item": item,
            "media_name": media_name,
            "artist_name": artist_name
        }

        # Return the new entry
        return entry


    def add_entry_to_database(self, rfid:int, media_type:str, item:str, media_name:str, artist_name:str, path:str = None):
        """
            Adds a new entry to the database - Allows for manual entry of the RFID card details.
            
            parameters:
                rfid: int - The RFID card number
                media_Type: str - The type of media (song, album, playlist)
                item: str - The item to be played (this is deduced from the url)
                media_name: str - The name of the media
                artist_name: str - The name of the artist
                path: str (defaults to data folder) - The path to save the csv file
        """
        # double check that the RFID card number is not already in the database
        if rfid in self.df['RFID'].values:
            print("RFID card already in the database.")
            return

        if path is None:
            path = self.df_path

        # Create a dictionary with the RFID card number and the song/album/playlist
        data = {
            'RFID': [rfid],
            "Media Type": [media_type],
            'Item': [item],
            'Media Name': [media_name],
            'Artist Name': [artist_name]
        }

        # Create a DataFrame
        df = pd.DataFrame(data)
        
        # Save the DataFrame to a csv file
        df.to_csv(path, mode='a', header=False, index=False)

        self.df = pd.read_csv(self.df_path)

        return 


    def create_dataframe(self, rfid:int, path:str = None):
        """
            Creates a dataframe for the RFID cards.
            
            note: the first entry will be the overcard entry
            
            parameters:
                rfid: int - The RFID card number
                path: str (defaults to data folder) - The path to save the csv file 
                
            returns:
                prints "CSV file created" - if the csv file was created successfully
        """
        if path is None:
            path = self.df_path

        # Create a dictionary with the RFID card number and the song/album/playlist
        data = {
            'RFID': [rfid],
            "Media Type": "overwrite",
            'Item': "overwrite",
            'Media Name': "overwrite",
            'Artist Name': "overwrite"
        }

        # Create a DataFrame
        df = pd.DataFrame(data)
        
        # Save the DataFrame to a csv file
        df.to_csv(path, index=False)
        
        # reload the database.
        self.df = pd.read_csv(self.df_path)
        print("database succesfully created")
        sleep(2)

        # # play the media
        # sp = spotify_authenticator()

        # rfid_data = self.extract_data(rfid)
        # spotify_playback(sp, rfid_data)

        return