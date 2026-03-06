from __future__ import annotations

import argparse

from src.config import DATA_PATH
from src.data_preprocessing import load_data, preprocess_data
from src.evaluation import evaluate_offline
from src.recommendation_engine import RecommendationEngine


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Offline evaluator for AniScope AI")
    parser.add_argument("--k", type=int, default=10, help="Top-k cutoff for metrics")
    parser.add_argument("--sample-size", type=int, default=200, help="Number of seed titles to evaluate")
    parser.add_argument("--min-relevant", type=int, default=5, help="Minimum relevant set size for each seed")
    parser.add_argument("--seed", type=int, default=42, help="Random seed")
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    df = preprocess_data(load_data(DATA_PATH))
    engine = RecommendationEngine(df)

    metrics = evaluate_offline(
        engine,
        k=args.k,
        sample_size=args.sample_size,
        min_relevant=args.min_relevant,
        random_state=args.seed,
    )

    print("Offline Evaluation Results")
    print(f"- evaluated_queries: {metrics.evaluated_queries}")
    print(f"- precision@{metrics.k}: {metrics.precision_at_k:.4f}")
    print(f"- recall@{metrics.k}: {metrics.recall_at_k:.4f}")
    print(f"- hit-rate@{metrics.k}: {metrics.hit_rate_at_k:.4f}")


if __name__ == "__main__":
    main()
