
# Project Documentation: Lyrics Scoring System

 
## Project Overview:

This project aims to rank the top 25 songs from various countries for each year, starting from 2010. The lyrics are fetched, translated into English if necessary, and scored based on a customizable prompt, using ChatGPT for both translation and scoring.

  

## Directory Structure:

Here is the structure of the project's directory:

  
```bash
main/

├── CSV_Files/
 ├── country.csv # List of countries.
 ├── country_year_to_be_retrieved.csv # Countries and years for which data needs to be retrieved.
 ├── status.csv # Tracks the status of retrieved and translated lyrics.
 ├── top_n_country_year_multi_threading.csv # Stores the top songs fetched for each country-year combination.

├── src/
  ├── lyrics/
    ├── raw_lyrics/ # Stores raw song lyrics retrieved for each country and year.
    ├── translated_lyrics/ # Stores translated lyrics in English.
  ├── notations/
    ├── Notation_1.csv # Stores the song scores with country, year, rank, and score.
    
├── complete_flow.py
├── detect_changes.py # Detects changes in retrieved songs and updates the status.
├── file_paths.py # Contains file paths used throughout the project.
├── gather_data.py # Gather top songs data for specified countries and years.
├── get_top_songs.py # Fetches top songs for each country and year from Spotify.
├── lyrics_retriever.py # Retrieves song lyrics from Genius API.
├── openai_functions.py # Handles OpenAI API for translations and scoring.
├── score.py # Scores songs based on provided lyrics.
├── scoring_prompt.txt # Scoring prompt used by ChatGPT.
├── translating_and_scoring_functions.py # Functions for translating and scoring lyrics.
├── translation_prompt.txt # Translation prompt used by ChatGPT.
├── util.py # Utility functions for handling file operations and metadata.
├── .gitignore # Ignored files by git.
├── requirements.txt # Dependencies for the project.
├── 
```
<div style="page-break-after: always"></div>

## Flow of Execution


### Overall Flow:

1. Country and Year Mapping: We define the countries and years of interest (from 2010 to 2024). These are stored in `country_year_to_be_retrieved.csv` (created by `util.py`).

2. Fetching Top Songs: Using the Spotify API, the top 25 songs for each country-year combination are fetched and stored in the CSV file `top_n_country_year_multi_threading.csv` (handled by `get_top_songs.py` and `gather_data.py`).

3. Lyrics Retrieval: Lyrics for all the top 25 songs across all countries and years have been retrieved using the Genius API. They are saved in the `raw_lyrics` folder, and the status of each song is updated in `status.csv`.

4. Translation and Scoring (Top 20 Countries): Only the songs from the top 20 countries (as defined by the list) have been translated into English using ChatGPT and scored. The translated songs are saved in the `translated_lyrics` folder, and their status is updated in `status.csv`.

5. Scoring: Once lyrics are retrieved and, if necessary, translated, they are scored using ChatGPT based on a prompt provided in `scoring_prompt.txt`. The scores are stored in the `Notation_X.csv` files under the `notations` folder (managed by `score.py`).

 To retrieve songs for a country not in the current list, you may first run the `complete_flow.py` file and then run the `score.py` file.

### Automated Scoring Flow:

- Input: Lyrics from the `raw_lyrics` or `translated_lyrics` folders.

- Processing: Using OpenAI's ChatGPT, the lyrics are scored based on the provided prompt (scoring_prompt.txt).
    -  You may run the `score.py` file to generate scores for a given prompt.

- Output: The resulting scores are written to the next available `Notation_X.csv` file.

  
## Important Notes
-   Data Quality: In some cases, the Genius API doesn’t return the exact lyrics. When it can’t find an exact match for the artist and song combination, it sometimes pulls the closest match instead. This occasionally leads to lyrics from different songs or even playlists with artist names and song titles. Because of this, the scores of these songs were set to -1.
    
-   Scoring Prompt Modification: To cater the situation where exact lyrics aren’t retrieved, the scoring prompt was modified to skip the scoring and simply return -1.
    
-   Notation File Structure: This file will not include songs with -1 score.
    
-   Rate Limiting: Both Spotify and Genius APIs have rate limits, so if many requests are made in a short time, there may be delays or API blocking.
 
  ### Stats 
- A total of 16,890 song lyrics were expected to be retrieved across all countries and years
    - Lyrics Retrieved = 14,762
    - Couldn't be retrieved =2,128
- Total songs that were to be scored in top 20 countries = 4,186
    - 742 of these songs had a score of -1. 

`variables.py`:

This file defines important arrays and dictionaries used throughout the project:


- countries_to_be_scored: This array contains the list of the top 20 countries for which lyrics will be scored (This can be modified to retrieve scores for songs from more countries).

- countries_to_be_translated: This array contains the same list of top 20 countries for which lyrics will be translated from their original language into English (This can be modified to retrieve translations for songs from more countries).

- alternateCountryNames: A dictionary that maps official country names to their alternate names or abbreviations. This helps in identifying playlists more effectively on Spotify when fetching top songs for each country.

- min_year: Defines the earliest year in the range from which songs should be retrieved.

- max_year: Defines the latest year in the range from which songs should be retrieved.

- n: Specifies the number of top songs to retrieve for each country.

`.env` file format:


- The `.env` file should contain API keys required for various services like Spotify and Genius.

```

SPOTIPY_CLIENT_ID=your_spotify_client_id

SPOTIPY_CLIENT_SECRET=your_spotify_client_secret

GENIUS_API_KEY=your_genius_api_key

OPENAI_API_KEY=your_openai_api_key

```

<div style="page-break-after: always"></div>

`scoring_prompt.txt`:

This file contains the prompt used by ChatGPT to score the lyrics. It defines how to evaluate a song's impact on oxytocin release based on its themes, language, and tone.

  

`file_paths.py`:

This Python file defines all the key paths used across the project:

-`country_year_to_be_retrieved_path`: Path to the CSV file listing country and year combinations to be processed.

- `status_df_path`: Path to the CSV file tracking the status of lyrics retrieval and translation.

- `songs_list_df_path`: Path to the file storing the top songs for each country and year.

- `raw_lyrics_path`: Directory path for storing raw lyrics.

- `translated_lyrics_path`: Directory path for storing translated lyrics.

- `translation_prompt_path`: Path to the prompt file used for translation.

- `scoring_prompt_path`: Path to the prompt file used for scoring.

  

`requirements.txt`:

Lists the Python packages that need to be installed for the project to function. Some of these include:

- `spotipy`: For Spotify API integration.

- `openai`: For using ChatGPT's translation and scoring.

- `lyricsgenius`: For fetching lyrics from the Genius API.




## CSV Files Explanation:

  

`status.csv`:

- Description: This CSV file tracks the progress of retrieving, translating, and scoring lyrics for each song. Each row corresponds to a song and includes:

- `country`: The country from which the song originated.

- `year`: The year the song was released.

- `song_title`: The title of the song.

- `artist`: The artist(s) who performed the song.

- `rank`: The song’s ranking within the top 25 for that country and year.

- `retrieved`: Whether the lyrics have been retrieved (`Retrieved` or `Not Retrieved`).

- `language`: The language of the lyrics (`English`, `Not English`, or `NA`).

- `translated`: Whether the lyrics have been translated into English (`Yes` or `No`).

Example:
country    | year    | song_title | artist  | rank    | retrieved | language | translated
| -------- | ------- |----------- | ------- |-------- | ----------|----------| ------- |
Indonesia |2018|11 Januari|Gigi|14|Retrieved|Not English|Yes
Indonesia|2018|Nuansa Bening|VIDI|15|Retrieved|Not English|Yes
Indonesia|2018|Tegar|Rossa|16|Retrieved|Not English|Yes



- top_n_country_year_multi_threading.csv: Stores the top 25 songs per country and year fetched from Spotify.

- Notation_X.csv: Stores the final scores of the songs after processing.

  

## Functions

  

### For Future Use:

The code is modular, allowing for easy customization of prompts and data processing workflows. Key components:

- TranslateLyrics: Function to translate lyrics using ChatGPT.

- ScoreLyrics: Function to score song lyrics using a scoring prompt.

- get_top_n_songs: Fetches the top songs for a given country and year using the Spotify API.

- retrieveLyrics: Retrieves lyrics from the Genius API.

- update_status_df: Keeps the status CSV updated with new songs.

- detect_new_changes (from `detect_changes.py`): This function should be used if new songs are manually added to the directory structure. It scans the directory, updates the `status.csv` with new songs, and translates non-English lyrics so they can be scored later.

- complete_flow: This function should be used to retrieve songs for a country not in the current list and run the whole flow on it to retrieve lyrics and translation, then to generate scores ScoreLyrics should be called. 

  
  



  

---
  

