import os
import lyricsgenius as lg
import langid
import pandas as pd
from dotenv import load_dotenv
import os
from concurrent.futures import ThreadPoolExecutor
import numpy as np
import re
from util import sanatize,findLanguage
from file_paths import songs_list_df_path,status_df_path,raw_lyrics_path

load_dotenv()
genius_api_key=os.getenv('GENIUS_API_KEY')

geniusClient = lg.Genius(genius_api_key,sleep_time=1,verbose=False,timeout=20,retries=2)
# not_found_count=0

def retrieveLyrics(genius_client, song_title, artist_name):
    """
    Retrieves the lyrics of a specified song using the Genius API client.

    Args:
        genius_client (Genius): An instance of the Genius API client used to search for songs.
        song_title (str): The title of the song whose lyrics are to be retrieved.
        artist_name (str): The name of the artist of the song.

    Returns:
        str or None: The lyrics of the song if found, or None if the song does not exist.

    The function performs the following steps:
    1. Searches for the song using the given title and artist name.
    2. If the song is found, it extracts the lyrics and modifies them by removing the first line.
    3. If the modified lyrics end with 'Embed', it removes that text.
    4. Returns the cleaned lyrics, or None if the song is not found.
    """
    
    # Search for the song and get the lyrics
    song = genius_client.search_song(song_title, artist_name)

    if song:
        # print("Lyrics for "+ song_title + " by " + artist_name)
        lyrics=song.lyrics
        lines=lyrics.split('\n')
        modified_lyrics = '\n'.join(lines[1:])
        if modified_lyrics[-5:]=='Embed':
            return modified_lyrics[:-5]
        return modified_lyrics
    
    else:
        return None
              


def save_lyrics(row):

    """
    Retrieves song lyrics for a given row of data and saves them to a directory.

    Args:
        row (dict): A dictionary containing the following keys:
            - 'year': The year the song was released.
            - 'country': The country of the artist.
            - 'song_title': The title of the song.
            - 'artist': The name of the artist or a list of artist names (comma-separated).

    Process:
        - The function constructs a list of artist names from the 'artist' field (split by commas).
        - For each artist name, it attempts to retrieve the lyrics using the retrieveLyrics function.
        - If lyrics are found, they are saved to a directory path in the format:
          "src/lyrics/raw_lyrics/<country>/<year>/" with the filename being the song title.
        - If lyrics are not found for any of the artist names, the function prints a failure message.

    Returns:
        str: 'Retrieved' if lyrics were found and saved, otherwise 'Not Retrieved'.
    """

    year = str(row['year'])
    country = str(row['country'])
    song_title = row['song_title']
    artist = row['artist']
    
    name_list=[]
    name_list.append(artist.strip())
    for name in artist.split(","):
        name_list.append(name)
    
    for name in name_list:
        lyrics = retrieveLyrics(geniusClient, song_title, name)
        if lyrics is not None:
            # Create the directory structure
            print(f'lyrics found for {song_title},{artist} 😀')
            dir_path = os.path.join(raw_lyrics_path, country, year)
            os.makedirs(dir_path, exist_ok=True)
            
            # File path to save the lyrics
            sanitized_title = re.sub(r'[\/:*?"<>|]', '', song_title)
            file_path = os.path.join(dir_path, f"{sanitized_title}.txt")
            
            # Save the lyrics to the file
            with open(file_path, 'w', encoding='utf-8') as file:
                file.write(lyrics)
            return 'Retrieved'
    
    # not_found_count+=1
    print(f'not found ❌')
    return 'Not Retrieved'
    
    

def make_status_df():
    """
    Creates a status DataFrame from a CSV file containing song information and adds new columns 
    to track retrieval and translation status. The updated DataFrame is then saved to a new CSV file.

    Args:
        input_csv (str): The file path of the input CSV file containing the list of songs.
        output_csv (str): The file path where the updated status DataFrame will be saved.

    Returns:
        pd.DataFrame: The updated DataFrame with new columns added.

    The function performs the following steps:
    1. Reads the input CSV file.
    2. Adds three new columns to the DataFrame:
       - 'retrieved': Initially set to None, to track whether the song's data has been retrieved.
       - 'language': Initially set to None, to track the language of the song.
       - 'translated': Initially set to 'No', to track whether the song has been translated.
    3. Saves the updated DataFrame to the specified output CSV file.
    """
    
    songs_list_df=pd.read_csv(songs_list_df_path)
    
    songs_list_df['retrieved']=None
    songs_list_df['language']=None
    songs_list_df['translated']='No'
    songs_list_df['song_title']=songs_list_df['song_title'].apply(lambda x: sanatize(x))
    songs_list_df.to_csv(status_df_path)

def main_lyrics_retriever():
    retrieved=pd.read_csv(status_df_path)
    try:
        for index,row in retrieved.iterrows():
            if (pd.isnull(row['song_title'])) or (pd.isnull(row['artist'])):
                continue
            if pd.isnull(row['retrieved']):
                output=save_lyrics(row)
                retrieved.at[index, 'retrieved'] = output
        retrieved=findLanguage(retrieved,raw_lyrics_path)
        retrieved.to_csv(status_df_path,index=False)
        
    except Exception as e:
        print('Error while retrieving the lyrics: ',e)
        retrieved=findLanguage(retrieved,raw_lyrics_path)
        retrieved.to_csv(status_df_path,index=False)        



    

