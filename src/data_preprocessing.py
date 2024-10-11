# data_preprocessing.py
import pandas as pd
import re
from bs4 import BeautifulSoup

def load_data(filepath):
    df = pd.read_csv(filepath)
    return df

def preprocess_data(df):
    # Fill missing values
    df['Title (English)'] = df['Title (English)'].fillna(df['Title (Romaji)'])
    df['Title (Native)'] = df['Title (Native)'].fillna('Unknown')
    df['Year'] = pd.to_numeric(df['Year'], errors='coerce').fillna(9999).astype('int64')
    df['Mean Score'] = df['Mean Score'].fillna(df['Mean Score'].median())
    df['Episodes'] = df['Episodes'].fillna(-1)
    df['Description'] = df['Description'].fillna('Not Available')
    df['Season'] = df['Season'].fillna('Not Available')

    # Clean HTML tags in Description
    df['Description'] = df['Description'].apply(clean_html)

    # Convert object type columns to lowercase
    df[df.select_dtypes(include=['object']).columns] = df.select_dtypes(include=['object']).apply(lambda x: x.str.lower())

    # Remove rows where 'Genres' is NaN
    df = df.dropna(subset=['Genres'])
    df.loc[:, 'Genres'] = df['Genres'].str.split(', ')   # Convert 'Genres' column to list

    # Reindex the DataFrame
    df.reset_index(drop=True, inplace=True)

    return df

def clean_html(text):
    """Remove HTML tags and unnecessary whitespace from text."""
    if re.search(r'<.*?>', text):
        return ' '.join(BeautifulSoup(text, "html.parser").stripped_strings)
    else:
        return text
