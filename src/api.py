from __future__ import annotations

from flask import Flask, jsonify, request

try:
    from .config import DATA_PATH, TOP_N_DEFAULT
    from .data_preprocessing import load_data, preprocess_data
    from .recommendation_engine import RecommendationEngine
except ImportError:
    from config import DATA_PATH, TOP_N_DEFAULT
    from data_preprocessing import load_data, preprocess_data
    from recommendation_engine import RecommendationEngine


def create_app() -> Flask:
    app = Flask(__name__)

    df = preprocess_data(load_data(DATA_PATH))
    engine = RecommendationEngine(df)

    @app.get("/health")
    def health() -> tuple[dict[str, str], int]:
        return {"status": "ok"}, 200

    @app.post("/recommend/title")
    def recommend_by_title():
        payload = request.get_json(silent=True) or {}
        title = payload.get("title", "")
        top_n = int(payload.get("top_n", TOP_N_DEFAULT))
        result = engine.recommend_anime(title, top_n=top_n)
        if isinstance(result, str):
            return jsonify({"message": result}), 400
        return jsonify(result.to_dict(orient="records")), 200

    @app.post("/recommend/genre")
    def recommend_by_genre():
        payload = request.get_json(silent=True) or {}
        query = payload.get("query", "")
        top_n = int(payload.get("top_n", TOP_N_DEFAULT))
        result = engine.recommend_anime_by_genre(query, top_n=top_n)
        if isinstance(result, str):
            return jsonify({"message": result}), 400
        return jsonify(result.to_dict(orient="records")), 200

    @app.get("/details")
    def details():
        title = request.args.get("title", "")
        result = engine.get_anime_details(title)
        if isinstance(result, str):
            return jsonify({"message": result}), 404
        return jsonify(result), 200

    return app
