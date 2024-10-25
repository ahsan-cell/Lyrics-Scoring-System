from openai_functions import ChatGPT
import pandas as pd
import os
import langid
from file_paths import translated_lyrics_path,raw_lyrics_path,translation_prompt_path,scoring_prompt_path,status_df_path
from util import read_file,detect_language
from variables import countries_to_be_scored,countries_to_be_translated




def TranslateLyrics(countries = countries_to_be_translated):
    """
    Translates song lyrics into English for non-English songs in a given dataset.

    This function reads a CSV file containing metadata about song lyrics, identifies 
    non-English songs from a predefined list of countries, and translates their lyrics 
    into English using an external translation service. Translated lyrics are saved 
    into a directory, and the dataset is updated to mark which songs have been translated.

    Parameters:
    -----------
    dataframe_path : str
        The file path to the CSV file containing the song metadata. The CSV must have
        the following columns: 'country', 'year', 'song_title', 'language', 'retrieved', 
        and 'translated'.
    
    countries : list of str, optional
        A list of country names to filter songs by. By default, the function uses a list 
        of 20 specific countries including "China", "India", "United States", and others.

    Returns:
    --------
    None
        The function modifies the CSV file in place, updating the 'translated' column for
        songs that have been translated. The lyrics are saved to the 'main/src/lyrics/translated_lyrics' 
        directory.

    Notes:
    ------
    - Only songs marked as 'retrieved' will be processed.
    - If the song's language is 'Not English' and it hasn't been translated yet (i.e., 'translated' is 'No'),
      the function will attempt to translate the lyrics.
    - The function saves the translated lyrics to a directory structure organized by country and year.
    - If translation fails, the 'translated' column will be updated to 'NA'.
    - Any exceptions encountered during execution will be caught and printed, and the CSV will still be 
      saved with any changes up to that point.
    """
    translation_prompt=read_file(translation_prompt_path)
    if translation_prompt is None:
            raise SystemExit("No translation prompt provided. Exiting the program.")
    try:
        dataframe=pd.read_csv(status_df_path)
        for index,row in dataframe.iterrows():
            if row['country'] in countries:
                if  row['retrieved']=='Retrieved':
                    path=os.path.join(raw_lyrics_path,row['country'],str(row['year']),row['song_title']+'.txt')
                    with open(path, 'r', encoding='utf-8') as file:
                        content = file.read()
                        if row['language']=='Not English' and row['translated']=='No':
                            print(row['country'],row['year'],row['song_title'],'Translating....')
                            translatedContent=ChatGPT().translator(content,translation_prompt)
                            if translatedContent is None:
                                dataframe.at[index,'translated']='NA'
                                print('Translation Failed.')
                                continue
                            print(row['country'],row['year'],row['song_title'],'Translation done')
                            save_path=os.path.join(translated_lyrics_path,row['country'],str(row['year']))
                            if not os.path.exists(save_path):
                                os.makedirs(save_path)
                            with open(os.path.join(save_path,row['song_title']+'.txt'), 'w', encoding='utf-8') as file2:
                                file2.write(translatedContent)
                            print('translation saved')
                            dataframe.at[index,'translated']='Yes'
  
        dataframe.to_csv(status_df_path,index=False)
    except Exception as e:
        print('Exception in TranslateLyrics: ',e)
        dataframe.to_csv(status_df_path,index=False)
                    
                
def ScoreLyrics(dataframe_path,countries= countries_to_be_scored):
    """
    Scores song lyrics from a given dataset for a predefined list of countries.

    This function reads a CSV file containing metadata about song lyrics and processes
    the lyrics for songs from a specified list of countries. It calculates a score 
    for the lyrics based on their content using an external scoring function.

    Parameters:
    -----------
    dataframe_path : str
        The file path to the CSV file containing the song metadata. The CSV must have
        the following columns: 'country', 'year', 'song_title', 'language', 'retrieved', 
        'translated', and 'rank'.
    
    countries : list of str, optional
        A list of country names to filter songs by. By default, the function uses a list 
        of 20 specific countries including "China", "India", "United States", and others.

    Returns:
    --------
    pandas.DataFrame
        A DataFrame containing the filtered songs with columns for 'country', 'year',
        'song_title', 'rank', and 'score'. Only the songs with lyrics that have been 
        retrieved are included. The score is calculated and added to the 'score' column.

    Notes:
    ------
    - Lyrics files are expected to be in the 'main/src/lyrics/raw_lyrics' or 
      'main/src/lyrics/translated_lyrics' directories, depending on whether the song 
      is in English or has been translated.
    - Lyrics are scored only if they have been marked as 'retrieved' in the dataset.
    - If the song is not in English but has been translated, the translated lyrics 
      will be used for scoring.
    - Make sure that the lyrics are translated before running this function
    """
    scoring_prompt=read_file(scoring_prompt_path)
    if scoring_prompt is None:
            raise SystemExit("No scoring prompt provided. Exiting the program.")    
    dataframe=pd.read_csv(dataframe_path)
    top_countries=dataframe[dataframe['country'].isin(countries)]
    top_countries['score']=None
    print('Scoring...')
    for index,row in top_countries.iterrows():
        if  (row['retrieved']=='Retrieved') and (row['language']=='English'):
            path=os.path.join(raw_lyrics_path,row['country'],str(row['year']),row['song_title']+'.txt')
            with open(path, 'r', encoding='utf-8') as file:
                content = file.read()
                score=ChatGPT().scoring(content,scoring_prompt)
                print(row['country'],row['year'],row['song_title'],'score=',score)
                top_countries.at[index,'score']=score
        elif (row['retrieved']=='Retrieved') and (row['language']=='Not English') and (row['translated']=='Yes'):
            path=os.path.join(translated_lyrics_path,row['country'],str(row['year']),row['song_title']+'.txt')
            with open(path, 'r', encoding='utf-8') as file:
                content = file.read()
                score=ChatGPT().scoring(content,scoring_prompt)
                print(row['country'],row['year'],row['song_title'],'score=',score)
                top_countries.at[index,'score']=score
        elif (row['retrieved']=='Retrieved') and (row['language']=='Not English') and (row['translated'].isna()):
            top_countries.at[index,'score']=-1

    top_countries=top_countries[top_countries['retrieved']=='Retrieved']
    return top_countries[['country','year','song_title','rank','score']]
    


                    
                

