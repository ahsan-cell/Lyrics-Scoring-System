import pandas as pd
from concurrent.futures import ThreadPoolExecutor, as_completed
from get_top_songs import get_top_n_songs
from file_paths import country_year_to_be_retrieved_path,songs_list_df_path
from variables import n
# Assume output_df and country_year are already defined
country_year=pd.read_csv(country_year_to_be_retrieved_path)
def process_row(row):
    print(row['country'], row['year'])
    
    # Fetch top songs for a specific country and year
    top_songs = get_top_n_songs(country_name=row['country'], year=row['year'], n=n)
    
    # If songs are retrieved, process them into new rows
    if top_songs is not None:
        new_rows = []
        for song in top_songs:
            if (song['song'] is None) or (song['artist'] is None):
                continue
            new_row = {
                'country': row['country'],
                'year': str(row['year']),
                'song_title': song['song'],
                'artist': song['artist'],
                'rank': str(song['rank'])
            }
            new_rows.append(new_row)
        return new_rows
    return []

# Define a function to run in parallel for each row
def process_rows_parallel(df):
    global output_df
    output_df = pd.DataFrame(columns=['country', 'year', 'song_title', 'artist', 'rank'])
    
    # Use ThreadPoolExecutor for multithreading
    with ThreadPoolExecutor(max_workers=10) as executor:  # Adjust `max_workers` based on your needs
        futures = [executor.submit(process_row, row) for _, row in df.iterrows()]

        for future in as_completed(futures):
            new_rows = future.result()
            if new_rows:
                # Convert the list of new rows to a DataFrame and concatenate it
                new_row_df = pd.DataFrame(new_rows)
                output_df = pd.concat([output_df, new_row_df], ignore_index=True)
                
    return output_df

# Run the parallel processing
def gather_data_main():
    output_df = process_rows_parallel(country_year)
    print(output_df)
    output_df.to_csv(songs_list_df_path,mode='w',index=False)
