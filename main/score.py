from translating_and_scoring_functions import ScoreLyrics
from file_paths import status_df_path,notation_dir
import os


def score_main():
    """
    Scores the songs and saves them in src\notations folder 
    """
    
    scoreDf=ScoreLyrics(status_df_path)
  
    # Check if Notations directory exists
    if not os.path.exists(notation_dir):
        # Create directory if it doesn't exist
        os.makedirs(notation_dir)
        # First file to save as Notation_1.csv
        file_number = 1
    else:
        # Get all the files in the directory
        files = os.listdir(notation_dir)
        # Filter for files starting with 'Notation_'
        notation_files = [f for f in files if f.startswith('Notation_') and f.endswith('.csv')]
        if notation_files:
            # Get the highest numbered file
            last_file = sorted(notation_files)[-1]
            # Extract the number from the filename
            file_number = int(last_file.split('_')[1].split('.')[0]) + 1
        else:
            # If no files exist in the directory
            file_number = 1

    # Define the new file path
    new_file_path = os.path.join(notation_dir, f'Notation_{file_number}.csv')
    # Save the DataFrame to the new CSV file
    scoreDf.to_csv(new_file_path, index=False)
    print(f'DataFrame saved as {new_file_path}')

score_main()