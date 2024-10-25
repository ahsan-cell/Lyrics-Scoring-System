from util import update_status_df
from translating_and_scoring_functions import TranslateLyrics
from file_paths import status_df_path,raw_lyrics_path

def detect_new_changes():
    """
    Run this function if you have added a new song directly into the direcotry strcutre.
    This function will preprocess those new songs to make sure they are ready for scoring
    """
    
    update_status_df()
    TranslateLyrics()

detect_new_changes()