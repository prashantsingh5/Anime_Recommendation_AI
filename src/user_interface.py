from __future__ import annotations

from fuzzywuzzy import process

try:
    from .config import DATA_PATH
    from .constants import GENRE_OR_TITLE_KEYWORDS, REQUEST_KEYWORDS
    from .data_preprocessing import load_data, preprocess_data
    from .recommendation_engine import RecommendationEngine
except ImportError:
    from config import DATA_PATH
    from constants import GENRE_OR_TITLE_KEYWORDS, REQUEST_KEYWORDS
    from data_preprocessing import load_data, preprocess_data
    from recommendation_engine import RecommendationEngine


def _match_intent(user_input: str) -> str | None:
    choices = REQUEST_KEYWORDS["recommendation"] + REQUEST_KEYWORDS["details"]
    result = process.extractOne(user_input, choices)
    if not result:
        return None

    best, confidence = result
    if confidence < 60:
        return None

    if best in REQUEST_KEYWORDS["recommendation"]:
        return "recommendation"
    return "details"


def _match_recommendation_type(user_input: str) -> str | None:
    choices = GENRE_OR_TITLE_KEYWORDS["genre"] + GENRE_OR_TITLE_KEYWORDS["title"]
    result = process.extractOne(user_input, choices)
    if not result:
        return None

    best, confidence = result
    if confidence < 60:
        return None

    if best in GENRE_OR_TITLE_KEYWORDS["genre"]:
        return "genre"
    return "title"


def _print_table_or_message(result) -> None:
    if isinstance(result, str):
        print(f"Agent: {result}")
    else:
        print("Agent: Here are your results:")
        print(result.to_string(index=False))


def start_conversation() -> None:
    df = preprocess_data(load_data(DATA_PATH))
    engine = RecommendationEngine(df)

    print("Agent: Welcome to Anime Recommendation AI.")
    print("Agent: Ask for recommendations or details, or type 'exit' anytime.")

    while True:
        user_input = input("User: ").strip()
        if not user_input:
            print("Agent: Please type something so I can help.")
            continue

        lowered = user_input.lower()
        if lowered in {"exit", "quit", "q"}:
            print("Agent: Thanks for using Anime Recommendation AI. Goodbye.")
            break

        intent = _match_intent(lowered)
        if intent == "details":
            title = input("Agent: Which anime title should I describe?\nUser: ").strip()
            details = engine.get_anime_details(title)
            print(f"Agent: {details}")
            continue

        if intent == "recommendation":
            rec_type_input = input(
                "Agent: Do you want recommendations by genre or based on a title?\nUser: "
            ).strip().lower()
            rec_type = _match_recommendation_type(rec_type_input)

            if rec_type == "genre":
                genre_input = input("Agent: Enter one or more genres: \nUser: ").strip()
                result = engine.recommend_anime_by_genre(genre_input)
                _print_table_or_message(result)
                continue

            if rec_type == "title":
                title_input = input("Agent: Enter an anime title: \nUser: ").strip()
                result = engine.recommend_anime(title_input)
                _print_table_or_message(result)
                continue

            print("Agent: I could not determine genre vs title. Try again.")
            continue

        print("Agent: I can help with recommendations or anime details. Please rephrase.")
