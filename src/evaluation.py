from __future__ import annotations

from dataclasses import dataclass

import pandas as pd

from .recommendation_engine import RecommendationEngine


@dataclass
class OfflineMetrics:
    precision_at_k: float
    recall_at_k: float
    hit_rate_at_k: float
    evaluated_queries: int
    k: int


def _metrics_at_k(recommended_titles: list[str], relevant_titles: set[str], k: int) -> tuple[float, float, float]:
    if k <= 0:
        raise ValueError("k must be > 0")

    top_k = recommended_titles[:k]
    hits = sum(1 for title in top_k if title in relevant_titles)

    precision = hits / k
    recall = (hits / len(relevant_titles)) if relevant_titles else 0.0
    hit_rate = 1.0 if hits > 0 else 0.0
    return precision, recall, hit_rate


def evaluate_offline(
    engine: RecommendationEngine,
    *,
    k: int = 10,
    sample_size: int = 200,
    min_relevant: int = 5,
    random_state: int = 42,
) -> OfflineMetrics:
    """Evaluate recommendation quality using genre-overlap relevance as an offline proxy."""
    if k <= 0:
        raise ValueError("k must be > 0")

    df = engine.raw_df[["Title (English)", "Genres"]].copy()
    df = df.dropna(subset=["Title (English)", "Genres"]).drop_duplicates(subset=["Title (English)"])

    if sample_size > 0 and len(df) > sample_size:
        eval_df = df.sample(n=sample_size, random_state=random_state)
    else:
        eval_df = df

    precision_scores: list[float] = []
    recall_scores: list[float] = []
    hit_scores: list[float] = []

    for _, row in eval_df.iterrows():
        seed_title = row["Title (English)"]
        seed_genres = set(row["Genres"] if isinstance(row["Genres"], list) else [])
        if not seed_genres:
            continue

        relevant_mask = df["Genres"].apply(
            lambda genres: bool(seed_genres.intersection(set(genres if isinstance(genres, list) else [])))
        )
        relevant_titles = set(df.loc[relevant_mask, "Title (English)"].tolist())
        relevant_titles.discard(seed_title)

        if len(relevant_titles) < min_relevant:
            continue

        rec = engine.recommend_anime(seed_title, top_n=k)
        if isinstance(rec, str):
            continue

        recommended_titles = rec["Title (English)"].tolist()
        precision, recall, hit_rate = _metrics_at_k(recommended_titles, relevant_titles, k)

        precision_scores.append(precision)
        recall_scores.append(recall)
        hit_scores.append(hit_rate)

    evaluated = len(precision_scores)
    if evaluated == 0:
        return OfflineMetrics(0.0, 0.0, 0.0, 0, k)

    return OfflineMetrics(
        precision_at_k=sum(precision_scores) / evaluated,
        recall_at_k=sum(recall_scores) / evaluated,
        hit_rate_at_k=sum(hit_scores) / evaluated,
        evaluated_queries=evaluated,
        k=k,
    )
