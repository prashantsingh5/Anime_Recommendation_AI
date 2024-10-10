import pandas as pd
from fuzzywuzzy import process
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.preprocessing import MinMaxScaler
import re  # Make sure to import re for regex operations

# Define the available genres with their synonyms
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

    def fuzzy_match_title(self, input_title):
        best_match = process.extractOne(input_title, self.df['Title (English)'])
        if best_match[1] < 50:  # Threshold for fuzzy matching
            return None
        return best_match[0]

    def recommend_anime_by_genre(self, user_input, top_n=5):
        input_genres = self.extract_genres_from_input(user_input)
        if not input_genres:
            return "Sorry! No genres detected in your input."

        recommended_anime = self.df[self.df['Genres'].apply(lambda genres: isinstance(genres, list) and all(genre in genres for genre in input_genres))]
        if recommended_anime.empty:
            return "Sorry! No anime found matching the specified genres."

        recommended_anime = recommended_anime.sort_values(by='Popularity', ascending=False).head(top_n)
        return recommended_anime[['Title (English)', 'Genres']]

    def recommend_anime(self, input_value, top_n=10):
        matched_title = self.fuzzy_match_title(input_value)
        if matched_title is None:
            return "Sorry! Unable to find your anime, so unable to recommend any anime."

        matched_index = self.df[self.df['Title (English)'] == matched_title].index
        if matched_index.empty:
            return "Sorry! Unable to find your anime, so unable to recommend any anime."

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
