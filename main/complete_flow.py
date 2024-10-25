from util import make_country_year_to_retrieved,update_status_df
from gather_data import gather_data_main
from lyrics_retriever import main_lyrics_retriever,make_status_df
from translating_and_scoring_functions import TranslateLyrics
from variables import min_year, max_year

def complete_flow():
    make_country_year_to_retrieved(min_year,max_year)
    gather_data_main()
    make_status_df()
    main_lyrics_retriever()
    update_status_df() 
    TranslateLyrics()

complete_flow()    
    
