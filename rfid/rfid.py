import RPi.GPIO as GPIO
from mfrc522 import SimpleMFRC522
import sys
sys.path.append('../')

class RFID_Card:
    """
        Creates an RFID_Card object that contains the functions used for the interaction for the RFID Card
        
        Library Dependencies:
            import pandas as pd
            import RPi.GPIO as GPIO
            from mfrc522 import SimpleMFRC522
    """
    
    def __init__(self):
        """
            initializes the RFID_Card object
        """
        
        
    def read_rfid(self):
        """
            This function reads the RFID card and returns the value
            This value will be used as the primary key used in our database.
        """
        reader = SimpleMFRC522() # initializes the reader
        
        # Loop until a valid RFID entry is read or "O" is pressed
        while True:
            try:  # tries to read the rfid card
                print("Scan RFID Card:")
                id = reader.read()[0]
                
                # check if the RFID is a valid entry - int or "O"
                if isinstance(id, int): # if the id is an integer
                    print(f"RFID Card: {id}")
                    return id
                
                else: # if the id is not an integer or "O"
                    print("Invalid entry, try again.")
                    continue
            
            except Exception as e: # if there is an error reading the RFID
                print(f"Error reading RFID: {e}")
            
            finally:
                GPIO.cleanup()

    
    