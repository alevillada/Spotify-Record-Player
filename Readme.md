# Spotify Record Player

**Spotify Record Player** is an RFID-enabled music playback system inspired by [this YouTube tutorial](https://www.youtube.com/watch?v=-jGWjFR936o&t=776s). It integrates RFID technology with the Spotify API to allow users to play music (tracks, albums, or playlists) by scanning RFID cards. The project enhances data management for RFID tokens by using a CSV database to store and manage the association between RFID cards and Spotify media links.

> [!Important]
> When the application is run, the user will be asked to "Log into their Spotify Account", users must use a separate device (such as phone or desktop) to manually connect to the Raspberry Pi. This is done by selecting "Connect to a device" in the Spotify UI and selecting raspotify. Failure to do so will result in a playback error.

## Table of Contents

- [Features](#features)
- [Project Structure](#project-structure)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)

## Features

- **RFID Integration:** Uses an MFRC522 RFID reader with Raspberry Pi GPIO to scan RFID cards.
- **Spotify Playback:** Authenticates with Spotify and plays media based on the scanned RFID card.
- **Dynamic Database Management:** Automatically creates and manages a CSV database that maps RFID cards to Spotify media links.
- **Media Metadata Fetching:** Retrieves track, album, or playlist details (such as media name and artist) from the Spotify API.
- **Overwrite Functionality:** Allows users to update an existing RFID card's media entry via an "overwrite" card.

## Project Structure

```
`Modern-Record-Player/
├── main.py
├── dataframe/
	└── dataframe.py          # Manages the RFID to Spotify media mapping CSV database
├── rfid/
	└── rfid.py               # Contains the RFID_Card class for scanning RFID cards
├── utils/
	├── spotify_utils.py      # Handles Spotify authentication and playback functions
	└── custom_errors.py      # Custom exceptions (e.g., URLError) \
├── requirements.txt          # Python package dependencies
└── .env                      # Environment variables file (not included; see below)`
```

> [!Note:]
> Also included is `read.py` which allows to manually read an RFID card individually. This allows users to manually add data into their database using a correct RFID address.

## Installation

### Prerequisites

- **Hardware:** Raspberry Pi (and all that this needs), MFRC522 RFID reader, and compatible RFID cards.
- **Software:** Python 3.7 or higher

### Setting Up the Environment

1. **Clone the Repository:**

   ```
   git clone https://github.com/yourusername/modern-record-player.git
   cd modern-record-player
   ```

2. **Create and Activate a Virtual Environment (Optional but Recommended):**

   ```
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install Dependencies:**

   All required Python packages are listed in the `requirements.txt` file. Install them with:
   `pip install -r requirements.txt`

## Configuration

Before running the application, create a `.env` file in the project root with the following variables:

```
# Path to the CSV database file
DB_PATH=./data/rfid_database.csv

# Spotify API credentials
SPOTIPY_CLIENT_ID=your_spotify_client_id SPOTIPY_CLIENT_SECRET=your_spotify_client_secret

# Cache path for Spotify authentication (ensure the directory exists or will be created)
CACHE_PATH=./.cache-spotify

# Raspberry Pi Device ID registered with Spotify (for playback) RASPI_ID=your_raspi_device_id
```

> [!Note]
> Replace the placeholder values (e.g., `your_spotify_client_id`) with your actual credentials and paths.

## Usage

1. **Log Into Spotify:** When you run the project, you will be prompted to log into Spotify for authentication. Ensure you use the same account that has access to the device specified by `RASPI_ID`.

2. **Run the Application:**

   run `python main.py`

   **The application workflow:**

   - **Startup:** Loads environment variables and initializes the CSV database (creating both a new database and overwrite card if none exist).
   - **RFID Scanning:** Continuously waits for an RFID card scan.
   - **Database Interaction:** Checks if the scanned RFID card is associated with a media entry:
     - If the card is not in the database, you will be prompted to enter a new Spotify link.
     - If the card is recognized (or if it’s an "overwrite" card), the corresponding media entry is retrieved or updated.
   - **Spotify Playback:** Initiates playback of the associated track, album, or playlist on the device specified by `RASPI_ID`.

3. **Adding or Overwriting an Entry:**
   - **New Entry:** Scan a new RFID card and enter a valid Spotify link when prompted.
   - **Overwrite:** Use the designated "overwrite" card to update an existing entry. The system will guide you through scanning a new card to overwrite the previous entry.
