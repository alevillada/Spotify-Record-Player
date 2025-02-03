from dotenv import load_dotenv # type: ignore
import os
import RPi.GPIO as GPIO # type: ignore
from dataframe import RecordPlayer_DataFrame
from rfid import RFID_Card
from utils import spotify_authenticator, spotify_playback

def main():
    """
        Houses the Main Logic for Modern Record Player
    """

    # Loading in the .env
    load_dotenv()

    # Create path for the database 
    db_path = os.getenv("DB_PATH")

    # Initialize the RFID and DataFrame
    rfid_c = RFID_Card()
 
    print("Remember to Log into Spotify")
    # Infinite Loop for the logic of the Record Player
    while True:
        try:
            sp = spotify_authenticator()
            df = RecordPlayer_DataFrame(db_path)
        # Create an infinite loop for the functionality of the record player
            while True:
                
                # Request the RFID data
                rfid = rfid_c.read_rfid()

                # Check if the RFIDS data is in the database 
                # if it is not, add it to the database
                rfid_data = df.check_entry(rfid)
                
                if rfid_data is None:
                    continue

                # playback function for the Spotify API
                spotify_playback(sp, rfid_data)
                
        except Exception as e:
            print(f"Error: {e}")
            pass

        finally:
            print("Cleaning up...")
            GPIO.cleanup()



if __name__ == '__main__':
    main()