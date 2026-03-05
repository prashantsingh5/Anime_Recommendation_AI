from __future__ import annotations

import re

import pandas as pd
from fuzzywuzzy import process
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.preprocessing import MinMaxScaler

try:
    from .config import SIMILARITY_WEIGHTS, TITLE_MATCH_THRESHOLD, TOP_N_DEFAULT
    from .constants import GENRE_SYNONYMS
except ImportError:
    from config import SIMILARITY_WEIGHTS, TITLE_MATCH_THRESHOLD, TOP_N_DEFAULT
    from constants import GENRE_SYNONYMS


class RecommendationEngine:
    """Core ranking and retrieval logic for anime recommendations."""

    def __init__(self, df: pd.DataFrame) -> None:
        self.raw_df = df.copy()
        self.df = df.copy()
        self._prepare_features()

    def _prepare_features(self) -> None:
        self.df["Description"] = self.df["Description"].fillna("")
        self.vectorizer = TfidfVectorizer(stop_words="english", max_features=8000)
        self.description_matrix = self.vectorizer.fit_transform(self.df["Description"])

        self.genre_set = sorted({genre for genres in self.df["Genres"] for genre in genres})
        for genre in self.genre_set:
            self.df[f"genre::{genre}"] = self.df["Genres"].apply(lambda items: 1 if genre in items else 0)

        self.df = pd.get_dummies(self.df, columns=["Season"], prefix="season")
        self.season_cols = [column for column in self.df.columns if column.startswith("season_")]

        numeric_cols = ["Year", "Mean Score", "Popularity", "Episodes"]
        scaler = MinMaxScaler()
        self.df[numeric_cols] = scaler.fit_transform(self.df[numeric_cols])
        self.numeric_cols = numeric_cols

    def fuzzy_match_title(self, input_title: str) -> str | None:
        result = process.extractOne(input_title, self.df["Title (English)"])
        if not result:
            return None
        title = result[0]
        confidence = result[1]
        return title if confidence >= TITLE_MATCH_THRESHOLD else None

    def extract_genres_from_input(self, user_input: str) -> set[str]:
        genres_found: set[str] = set()
        lowered = user_input.lower()
        for genre, synonyms in GENRE_SYNONYMS.items():
            if any(re.search(r"\b" + re.escape(synonym) + r"\b", lowered) for synonym in synonyms):
                genres_found.add(genre)
        return genres_found

    def recommend_anime_by_genre(self, user_input: str, top_n: int = TOP_N_DEFAULT) -> pd.DataFrame | str:
        genres = self.extract_genres_from_input(user_input)
        if not genres:
            candidates = process.extract(user_input, list(GENRE_SYNONYMS.keys()), limit=1)
            if candidates and candidates[0][1] >= 70:
                genres.add(candidates[0][0])

        if not genres:
            return "I could not detect a genre clearly. Try something like 'action fantasy'."

        filtered = self.df[self.df["Genres"].apply(lambda g: all(item in g for item in genres))].copy()
        if filtered.empty:
            return "No anime matched all selected genres. Try a broader genre mix."

        filtered["display_score"] = 0.7 * filtered["Mean Score"] + 0.3 * (1 - filtered["Popularity"])
        output = filtered.sort_values("display_score", ascending=False).head(top_n)
        return output[["Title (English)", "Genres"]]

    def recommend_anime(self, input_title: str, top_n: int = TOP_N_DEFAULT) -> pd.DataFrame | str:
        matched_title = self.fuzzy_match_title(input_title)
        if matched_title is None:
            close = process.extract(input_title, self.df["Title (English)"], limit=3)
            suggestions = ", ".join([title for title, score in close if score >= 45])
            if suggestions:
                return f"Could not find an exact title. Did you mean: {suggestions}?"
            return "Could not find a matching title."

        target_index = self.df[self.df["Title (English)"] == matched_title].index[0]

        genre_cols = [f"genre::{genre}" for genre in self.genre_set]
        genre_similarity = cosine_similarity(self.df[genre_cols], self.df[genre_cols].iloc[[target_index]]).flatten()

        season_similarity = cosine_similarity(self.df[self.season_cols], self.df[self.season_cols].iloc[[target_index]]).flatten()

        description_similarity = cosine_similarity(
            self.description_matrix, self.description_matrix[target_index : target_index + 1]
        ).flatten()

        numeric_similarity = cosine_similarity(
            self.df[self.numeric_cols], self.df[self.numeric_cols].iloc[[target_index]]
        ).flatten()

        combined = (
            SIMILARITY_WEIGHTS["genre"] * genre_similarity
            + SIMILARITY_WEIGHTS["description"] * description_similarity
            + SIMILARITY_WEIGHTS["season"] * season_similarity
            + SIMILARITY_WEIGHTS["numeric"] * numeric_similarity
        )

        ranking = self.df.copy()
        ranking["score"] = combined
        ranking = ranking[ranking["Title (English)"] != matched_title]
        output = ranking.sort_values("score", ascending=False).head(top_n)
        return output[["Title (English)", "Genres"]]

    def get_anime_details(self, input_title: str) -> dict[str, object] | str:
        matched_title = self.fuzzy_match_title(input_title)
        if matched_title is None:
            return f"No anime title matched '{input_title}'."

        record = self.raw_df[self.raw_df["Title (English)"] == matched_title].iloc[0]
        return {
            "title": record["Title (English)"],
            "title_romaji": record.get("Title (Romaji)", ""),
            "title_native": record.get("Title (Native)", ""),
            "genres": record["Genres"],
            "description": record["Description"],
            "year": int(record["Year"]),
            "mean_score": float(record["Mean Score"]),
        }
