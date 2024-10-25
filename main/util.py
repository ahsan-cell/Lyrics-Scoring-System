
import pandas as pd
import re
import os
import langid
from file_paths import country_csv_path, country_year_to_be_retrieved_path, songs_list_df_path, status_df_path, raw_lyrics_path

def detect_language(text):
    
    # Classify the text to get the language and confidence score
    lang, confidence = langid.classify(text)
    if lang =='en':
        return 'English'
    return 'Not English'

def create_country_year(countries, min_year,max_year):
    """
    Creates a DataFrame combining a list of countries with a range of years.

    Args:
        countries (list): A list of country names.
        min_year (int): The minimum year to include in the DataFrame.
        max_year (int): The maximum year to include in the DataFrame.

    Returns:
        pd.DataFrame: A DataFrame with two columns: 'country' and 'year', 
                       containing all combinations of countries and years.

    The function performs the following steps:
    1. Generates a list of years from min_year to max_year.
    2. Creates DataFrames for the list of countries and the generated years.
    3. Merges the two DataFrames using a cross join to create all combinations.
    """
    years = list(range(min_year, max_year+1))
    countries = pd.DataFrame(countries, columns=['country'])
    years_df = pd.DataFrame(years, columns=['year'])
    final_df = countries.merge(years_df, how='cross')
    return final_df


def make_country_year_to_retrieved(minYear,maxYear):
    """
    Creates a CSV file mapping countries to a range of years for which 
    lyrics are to be retrieved.

    This function performs the following steps:
    1. Reads a CSV file containing country names.
    2. Converts the country names into a list.
    3. Calls the `create_country_year` function to generate a DataFrame 
       for the years 2010 to 2024.
    4. Saves the resulting DataFrame to a CSV file named 
       'country_year_to_be_retrieved.csv'.
    """
    countries=pd.read_csv(country_csv_path)
    countries=countries['Country'].to_list()
    df=create_country_year(countries,minYear,maxYear)
    df.to_csv(country_year_to_be_retrieved_path,index=False)

def sanatize(name):
    sanatized= re.sub(r'[\/:*?"<>|"]', '', name)
    return sanatized

    

def read_file(file_path):
    try:
        # Open the file in read mode
        with open(file_path, 'r') as file:
            content = file.read()
            
            # Check if file is empty
            if len(content) == 0:
                print(f"The file '{file_path}' is empty.")
                return None
            else:
                return content
    except FileNotFoundError:
        print(f"File '{file_path}' not found.")
        return None
    except Exception as e:
        print(f"An error occurred: {e}")
        return None
    


def scan_directory_with_metadata(directory):
    """
    Scans a specified directory to retrieve metadata of song files.

    Args:
        directory (str): The path to the directory to be scanned.

    Returns:
        list of dict: A list of dictionaries, each containing metadata for 
                       a song file, including:
                       - 'country': The country extracted from the directory path.
                       - 'year': The year extracted from the directory path.
                       - 'song_title': The title of the song (filename without extension).
                       - 'file_path': The full path to the song file.

    The function traverses the directory structure, looking for files 
    and extracting relevant metadata based on the expected directory layout.
    It specifically looks for paths formatted as `.../country/year/song_title.txt`.
    """
    files_data = []
    print('scanning')
    for root, _, files in os.walk(directory):
        
        for file in files:
            # Create full file path
            file_path = os.path.join(root, file)
            
            # Split the path to extract country, year, and song title
            path_parts = file_path.split(os.sep)
            if len(path_parts) == 7:
                # Extract country, year, and song title (filename without extension)
                country = path_parts[-3]
                year = path_parts[-2]
                song_title = os.path.splitext(file)[0]  # Remove the .txt extension
                
                # Append as a dictionary
                files_data.append({
                    'country': country,
                    'year': year,
                    'song_title': song_title,
                    'file_path': file_path
                })
    return files_data

def findLanguage(df,raw_lyrics_path):
    """
    Detects the language of the lyrics for songs marked as 'Retrieved' in the DataFrame.

    Args:
        df (pd.DataFrame): A DataFrame containing song metadata with a 'retrieved' column.
        raw_lyrics_path (str): The path to the directory containing raw lyrics files.

    Returns:
        pd.DataFrame: The updated DataFrame with a new 'language' column populated 
                       for songs where the lyrics were retrieved.

    The function iterates over the DataFrame, checking each song's lyrics file. 
    If the song's lyrics have been retrieved, it reads the lyrics and detects 
    the language using a language detection function, updating the DataFrame accordingly.
    """
    for index,row in df.iterrows():
        if row['retrieved']=='Retrieved':
            path=os.path.join(raw_lyrics_path,row['country'],str(row['year']),row['song_title']+'.txt')
            with open(path, 'r', encoding='utf-8') as file:
                content = file.read()
                language=detect_language(content)
                df.at[index, 'language'] = language
                
    return df


def update_status_df():
    """
    Updates the status DataFrame by checking for new songs in the specified 
    directory and adding their metadata.

    Using:
        status_df_path (str): The file path of the current status DataFrame CSV.
        raw_lyrics_path (str): The path to the directory containing raw lyrics files.

    Returns:
        None: The function updates the existing status DataFrame and saves it 
              back to the specified CSV file.

    The function performs the following steps:
    1. Scans the raw lyrics directory for song files and retrieves their metadata.
    2. Reads the existing status DataFrame from the CSV file.
    3. Merges the retrieved metadata with the existing DataFrame to identify new songs.
    4. If new songs are found, it initializes additional metadata fields (e.g., language).
    5. Calls `findLanguage` to detect the language of the new songs based on their lyrics.
    6. Concatenates the new songs' metadata with the existing DataFrame and saves the updated 
       DataFrame back to the CSV file.
    """
    print('Checking directory structure to detect any changes.....')
    file_data=scan_directory_with_metadata(raw_lyrics_path)
    file_data=pd.DataFrame(file_data)
    
    retrieved_df=pd.read_csv(status_df_path)

    retrieved_df['year']=retrieved_df['year'].astype(str)
    new_songs=pd.merge(retrieved_df,file_data,on=['country','year','song_title'],how='right',indicator=True)
    new_songs = new_songs[new_songs['_merge'] == 'right_only'].drop('_merge', axis=1)
    
    
    if not new_songs.empty:
        print('New songs found')
        new_songs['language']=None
        new_songs['retrieved']='Retrieved'
        print('Checking the language of new songs...')
        new_songs=findLanguage(new_songs,raw_lyrics_path)
        new_df=pd.DataFrame({
            'song_title':new_songs['song_title'].to_list(),
            'country':new_songs['country'].to_list(),
            'year':new_songs['year'].to_list(),
            'artist':['not present' for i in range(len(new_songs))],
            'rank':[-1 for i in range(len(new_songs))],
            'retrieved':['Retrieved' for i in range(len(new_songs))],
            'language':new_songs['language'].to_list(),
            'translated':['No' for i in range(len(new_songs))]
        })
        update=pd.concat([retrieved_df,new_df])
        update.to_csv(status_df_path,index=False)
        print('New changes adjusted in status_df')
    else:
        print('No new songs found')
    
