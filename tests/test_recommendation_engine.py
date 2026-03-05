import pandas as pd

from src.recommendation_engine import RecommendationEngine


def _sample_df() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "Title (Romaji)": ["Cowboy Bebop", "Samurai Champloo", "Toradora"],
            "Title (English)": ["Cowboy Bebop", "Samurai Champloo", "Toradora"],
            "Title (Native)": ["A", "B", "C"],
            "Genres": [["action", "adventure"], ["action"], ["romance", "comedy"]],
            "Episodes": [26, 26, 25],
            "Description": [
                "Space bounty hunters and episodic stories.",
                "Samurai road trip with hip-hop style.",
                "A high school romance comedy story.",
            ],
            "Season": ["spring", "summer", "fall"],
            "Year": [1998, 2004, 2008],
            "Mean Score": [85, 83, 80],
            "Popularity": [90, 70, 60],
        }
    )


def test_title_recommendation_returns_dataframe():
    engine = RecommendationEngine(_sample_df())
    result = engine.recommend_anime("cowboy bebop", top_n=2)
    assert isinstance(result, pd.DataFrame)
    assert len(result) == 2


def test_genre_recommendation_handles_genre_text():
    engine = RecommendationEngine(_sample_df())
    result = engine.recommend_anime_by_genre("action adventure", top_n=2)
    assert isinstance(result, pd.DataFrame)
    assert "Cowboy Bebop" in set(result["Title (English)"])


def test_details_returns_dict():
    engine = RecommendationEngine(_sample_df())
    details = engine.get_anime_details("toradora")
    assert isinstance(details, dict)
    assert details["title"] == "Toradora"
