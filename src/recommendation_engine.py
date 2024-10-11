import pandas as pd
import difflib 
from fuzzywuzzy import process
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.preprocessing import MinMaxScaler
import re  # Make sure to import re for regex operations

# Define the available genres with their synonyms
available_genres = {
    'action': ['action', 'acton', 'actions', 'fight', 'combat'],
    'adventure': ['adventure', 'adventures', 'advnture', 'exploration', 'journey', 'quest'],
    'comedy': ['comedy', 'funny', 'humor', 'comedies', 'laugh', 'hilarious'],
    'drama': ['drama', 'dramatic', 'tearjerker', 'dramas', 'emotional', 'melodrama'],
    'ecchi': ['ecchi', 'ecci', 'etchi', 'ecchy', 'fanservice', 'fan service', 'sexy', 'lewd'],
    'fantasy': ['fantasy', 'fantasies', 'magical', 'magic', 'fantasy world', 'mythical', 'myth', 'fictional'],
    'hentai': ['hentai', 'adult', 'porn', 'anime porn', 'explicit'],
    'horror': ['horror', 'scary', 'spooky', 'creepy', 'terror', 'thriller', 'gory', 'gore', 'ghost'],
    'mahou shoujo': ['mahou shoujo', 'magical girl', 'magical girls', 'mahoshoujo', 'mahoushoujo'],
    'mecha': ['mecha', 'robots', 'mechas', 'mech', 'giant robots', 'robot battle', 'robot fights', 'gundam', 'evangelion'],
    'music': ['music', 'musical', 'songs', 'song', 'singing', 'band', 'concert', 'musician', 'musicals'],
    'mystery': ['mystery', 'mysteries', 'detective', 'whodunit', 'crime', 'investigation', 'puzzle', 'thriller'],
    'psychological': ['psychological', 'mind', 'psychology', 'mental', 'thriller', 'psychological thriller', 'intense', 'philosophical', 'thought-provoking'],
    'romance': ['romance', 'romantic', 'love', 'romcom', 'rom com', 'romantic comedy', 'relationships', 'love story', 'dating', 'couples'],
    'sci-fi': ['sci-fi', 'science fiction', 'scifi', 'sci fi', 'futuristic', 'technology', 'space', 'aliens', 'cyberpunk', 'robots'],
    'slice of life': ['slice of life', 'life', 'daily life', 'everyday life', 'relatable', 'real life', 'slice-of-life'],
    'sports': ['sports', 'sport', 'athletics', 'athlete', 'soccer', 'football', 'basketball', 'tennis', 'baseball', 'swimming', 'volleyball', 'competition'],
    'supernatural': ['supernatural', 'super natural', 'ghosts', 'spirits', 'paranormal', 'magic', 'otherworldly', 'unexplained'],
    'thriller': ['thriller', 'suspense', 'intense', 'mystery', 'psychological thriller', 'crime thriller', 'action thriller', 'edge-of-your-seat', 'gripping']
}


class RecommendationEngine:
    def __init__(self, df):
        self.df = df
        self.vectorizer = TfidfVectorizer(stop_words='english', max_features=5000)
        self.description_matrix = self.vectorizer.fit_transform(df['Description'])

        # Normalize numerical columns
        scaler = MinMaxScaler()
        self.df[['Year', 'Mean Score', 'Popularity', 'Episodes']] = scaler.fit_transform(self.df[['Year', 'Mean Score', 'Popularity', 'Episodes']])

        # Prepare genre and season columns
        self.genre_set = set([genre for sublist in df['Genres'] for genre in sublist])
        for genre in self.genre_set:
            self.df[genre] = self.df['Genres'].apply(lambda x: 1 if genre in x else 0)

        # One-hot encoding for 'Season'
        self.df = pd.get_dummies(self.df, columns=['Season'])

    def fuzzy_match_genre(self, input_genre):
        """
        Match user input genres with available genres using fuzzy logic.
        """
        genres_list = list(available_genres.keys())
        best_match = process.extractOne(input_genre, genres_list)
        if best_match[1] < 60:  # Increase the threshold to avoid incorrect matches
            return None
        return best_match[0]

    def fuzzy_match_title(self, input_title):
        best_match = process.extractOne(input_title, self.df['Title (English)'])
        if best_match[1] < 50:  # Threshold for fuzzy matching
            return None
        return best_match[0]

    def recommend_anime_by_genre(self, user_input, top_n=5):
        input_genres = self.extract_genres_from_input(user_input)
        
        # If no exact genre match, try fuzzy matching
        if not input_genres:
            fuzzy_genre = self.fuzzy_match_genre(user_input)
            if fuzzy_genre:
                input_genres.add(fuzzy_genre)

        if not input_genres:
            return "Hmm, I couldn't detect a clear genre. Could you try rephrasing that?"

        recommended_anime = self.df[self.df['Genres'].apply(lambda genres: isinstance(genres, list) and all(genre in genres for genre in input_genres))]
        if recommended_anime.empty:
            return "Sorry! I couldn't find any anime matching those genres."
        
        recommended_anime = recommended_anime.sort_values(by='Popularity', ascending=False).head(top_n)
        return recommended_anime[['Title (English)', 'Genres']]

    def recommend_anime(self, input_value, top_n=10):
        matched_title = self.fuzzy_match_title(input_value)
        
        if matched_title is None:
            # Suggest close matches
            close_matches = process.extract(input_value, self.df['Title (English)'], limit=3)
            suggestions = ", ".join([match[0] for match in close_matches if match[1] > 40])
            return f"Sorry! I couldn't find an exact match for '{input_value}'. Did you mean: {suggestions}?"

        matched_index = self.df[self.df['Title (English)'] == matched_title].index
        if matched_index.empty:
            return "Sorry! I couldn't find your anime."

        matched_index = matched_index[0]  # Get the first matched index

        genre_cols = list(self.genre_set)
        genre_similarity = cosine_similarity(self.df[genre_cols], self.df[genre_cols].iloc[[matched_index]]).flatten()

        season_cols = [col for col in self.df.columns if col.startswith('Season_')]
        season_similarity = cosine_similarity(self.df[season_cols], self.df[season_cols].iloc[[matched_index]]).flatten()

        description_similarity = cosine_similarity(self.description_matrix, self.description_matrix[matched_index:matched_index + 1]).flatten()

        combined_similarity = (0.5 * genre_similarity) + (0.2 * season_similarity) + (0.3 * description_similarity)
        self.df['weighted_score'] = combined_similarity * self.df['Popularity'] * self.df['Mean Score']

        recommendations = self.df[self.df['Title (English)'] != matched_title].sort_values('weighted_score', ascending=False).head(top_n)
        return recommendations[['Title (English)', 'Genres']]

    def extract_genres_from_input(self, user_input):
        # Same genre extraction logic as before
        genres_found = set()
        user_input_lower = user_input.lower()
        for genre, synonyms in available_genres.items():
            for synonym in synonyms:
                if re.search(r'\b' + re.escape(synonym) + r'\b', user_input_lower):
                    genres_found.add(genre)
                    break
        return genres_found
