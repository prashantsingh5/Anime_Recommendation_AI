import pandas as pd

from src.evaluation import _metrics_at_k, evaluate_offline
from src.recommendation_engine import RecommendationEngine


def _sample_df() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "Title (Romaji)": ["A", "B", "C", "D", "E"],
            "Title (English)": ["A", "B", "C", "D", "E"],
            "Title (Native)": ["A", "B", "C", "D", "E"],
            "Genres": [
                ["action", "adventure"],
                ["action"],
                ["action", "comedy"],
                ["romance"],
                ["action", "thriller"],
            ],
            "Episodes": [12, 12, 24, 13, 26],
            "Description": [
                "adventure action space",
                "intense action battle",
                "action comedy school",
                "romance drama slice",
                "action thriller mystery",
            ],
            "Season": ["spring", "summer", "fall", "winter", "spring"],
            "Year": [2010, 2012, 2014, 2016, 2018],
            "Mean Score": [80, 81, 82, 70, 83],
            "Popularity": [50, 60, 55, 40, 65],
        }
    )


def test_metrics_at_k_basic_case():
    precision, recall, hit_rate = _metrics_at_k(
        recommended_titles=["A", "B", "C"],
        relevant_titles={"B", "Z"},
        k=3,
    )
    assert precision == 1 / 3
    assert recall == 1 / 2
    assert hit_rate == 1.0


def test_evaluate_offline_returns_valid_ranges():
    engine = RecommendationEngine(_sample_df())
    metrics = evaluate_offline(engine, k=3, sample_size=5, min_relevant=1, random_state=42)

    assert 0.0 <= metrics.precision_at_k <= 1.0
    assert 0.0 <= metrics.recall_at_k <= 1.0
    assert 0.0 <= metrics.hit_rate_at_k <= 1.0
    assert metrics.k == 3
