# utilities.py
import re
from fuzzywuzzy import process
import pandas as pd

# Available genres and their synonyms
available_genres = {
    'action': ['action'],
    'adventure': ['adventure', 'adventures'],
    'comedy': ['comedy'],
    'drama': ['drama'],
    'ecchi': ['ecchi'],
    'fantasy': ['fantasy'],
    'hentai': ['hentai'],
    'horror': ['horror'],
    'mahou shoujo': ['mahou shoujo', 'magical girl'],
    'mecha': ['mecha'],
    'music': ['music'],
    'mystery': ['mystery'],
    'psychological': ['psychological'],
    'romance': ['romance', 'romantic'],
    'sci-fi': ['sci-fi', 'science fiction'],
    'slice of life': ['slice of life'],
    'sports': ['sports'],
    'supernatural': ['supernatural'],
    'thriller': ['thriller']
}

def extract_genres_from_input(user_input):
    """
    Extract genres from user input based on predefined synonyms.

    Args:
        user_input (str): The input string from the user.

    Returns:
        set: A set of extracted genres.
    """
    genres_found = set()
    user_input_lower = user_input.lower()
    for genre, synonyms in available_genres.items():
        for synonym in synonyms:
            if re.search(r'\b' + re.escape(synonym) + r'\b', user_input_lower):
                genres_found.add(genre)
                break
    return genres_found

# In utilities.py

def fuzzy_match_title(input_title, df):
    best_match = process.extractOne(input_title, df['Title (English)'])
    if best_match[1] < 50:  # Threshold for fuzzy matching
        return None
    return best_match[0]


def clean_html(text):
    """
    Remove HTML tags and unnecessary whitespace from text.

    Args:
        text (str): The input text with potential HTML tags.

    Returns:
        str: Cleaned text without HTML tags.
    """
    if re.search(r'<.*?>', text):
        from bs4 import BeautifulSoup
        return ' '.join(BeautifulSoup(text, "html.parser").stripped_strings)
    return text

def normalize_dataframe(df):
    """
    Normalize specified numerical columns in the DataFrame.

    Args:
        df (pd.DataFrame): The DataFrame to normalize.

    Returns:
        pd.DataFrame: The normalized DataFrame.
    """
    from sklearn.preprocessing import MinMaxScaler

    # Specify numerical columns to normalize
    scaler = MinMaxScaler()
    df[['Year', 'Mean Score', 'Popularity', 'Episodes']] = scaler.fit_transform(df[['Year', 'Mean Score', 'Popularity', 'Episodes']])
    return df
