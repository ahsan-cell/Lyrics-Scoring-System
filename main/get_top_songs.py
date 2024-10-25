import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from dotenv import load_dotenv
import os
import json
import pandas as pd
from variables import alternateCountryNames


# Function to fetch top n unique tracks from a country for a specific year
def get_top_n_songs(year, country_name, n):
    """
    Fetches the top n unique songs from Spotify playlists for a given year and country.

    This function uses the Spotify API to search for playlists matching the specified year
    and country. It extracts a list of unique songs (based on song name and artist name) 
    from the playlists that match the search criteria. The function returns a list of the 
    top n songs with their rank, song name, artist, and album information.

    Parameters:
    -----------
    year : int
        The year for which to search for top songs (e.g., 2023).
    
    country_name : str
        The name of the country to filter playlists by (e.g., "United States").
    
    n : int
        The number of unique top songs to retrieve.
    
    Returns:
    --------
    list of dict or None
        A list of dictionaries representing the top n songs, where each dictionary contains:
        - 'rank': The rank of the song in the list.
        - 'song': The name of the song.
        - 'artist': The name(s) of the artist(s).
        - 'album': The name of the album the song belongs to.
        
        Returns None if no relevant playlists or songs are found.

    Notes:
    ------
    - The function searches for Spotify playlists using a query formatted as "Top {year} {country_name}".
    - Only playlists that match the year and country (or alternative country names) are considered.
    - Tracks are fetched from the playlists, and uniqueness is enforced based on both song name and 
      artist name.
    - The Spotify credentials (`SPOTIPY_CLIENT_ID` and `SPOTIPY_CLIENT_SECRET`) are loaded from the 
      environment variables using `load_dotenv()`.
    - The function stops searching once it collects n unique songs.

    Example usage:
    --------------
    top_songs = get_top_n_songs(2023, "United States", 10)
    """
    load_dotenv()
    client_id =  os.getenv('SPOTIPY_CLIENT_ID')  # Your Spotify API Client ID
    client_secret = os.getenv('SPOTIPY_CLIENT_SECRET')  # Your Spotify API Client Secret
    auth_manager = SpotifyClientCredentials(client_id=client_id, client_secret=client_secret)
    sp = spotipy.Spotify(auth_manager=auth_manager)

    search_query = f"Top {year} {country_name}"
    results = sp.search(q=search_query, type='playlist', limit=50)
    
    unique_songs = set()  # To store unique song-artist pairs
    top_n_songs = []  # Final list of unique top n songs
   
    
    # Loop through all playlists found in search results
    for playlist in results['playlists']['items']:
        # Check if the playlist matches the year and country
        if str(year) in playlist['name'] and (country_name.lower() in playlist['name'].lower() or any(alt_name.lower() in playlist['name'].lower() for alt_name in alternateCountryNames[country_name])):

            playlist_id = playlist['id']
          
                
            # Fetch tracks from the identified playlist
            playlist_tracks = sp.playlist_tracks(playlist_id, limit=100)  # Get a larger number of tracks
    
            # Extract song details, ensuring uniqueness by song name and artist name
            for item in playlist_tracks['items']:
                track = item['track']
                if track is None:
                    continue
                song_artist_pair = (track['name'], ', '.join([artist['name'] for artist in track['artists']]))
                
                if song_artist_pair not in unique_songs:
                    unique_songs.add(song_artist_pair)  # Mark song-artist pair as seen
                    top_n_songs.append({
                        'rank': len(top_n_songs) + 1,  # Rank based on the order they are added
                        'song': track['name'],
                        'artist': song_artist_pair[1],
                        'album': track['album']['name']
                    })
                    
                # Stop once we have n unique songs
                if len(top_n_songs) >= n:
                    break
            
            # If we have collected n unique songs, stop searching through playlists
            if len(top_n_songs) >= n:
                break

    if not top_n_songs:
        return None # No relevant playlists or songs found

    return top_n_songs

# print(get_top_n_songs(country_name='Brazil',year=2024,n=25))