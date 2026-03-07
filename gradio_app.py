from __future__ import annotations

import re
from typing import Any

import gradio as gr
import pandas as pd

from src.config import DATA_PATH
from src.data_preprocessing import load_data, preprocess_data
from src.recommendation_engine import RecommendationEngine

APP_TITLE = "AniScope AI"
ChatHistory = list[dict[str, str]]


def _to_markdown_table(df: pd.DataFrame) -> str:
    if df.empty:
        return "No results found."

    rows = []
    for _, row in df.iterrows():
        title = row.get("Title (English)", "Unknown")
        genres = row.get("Genres", [])
        genre_text = ", ".join(genres) if isinstance(genres, list) else str(genres)
        rows.append(f"- **{title}**  \n  Genres: {genre_text}")
    return "\n".join(rows)


def _build_engine() -> RecommendationEngine:
    df = preprocess_data(load_data(DATA_PATH))
    return RecommendationEngine(df)


ENGINE = _build_engine()


def _intent(text: str) -> str | None:
    lowered = text.lower()
    if any(word in lowered for word in ["recommend", "suggest", "recommendation"]):
        return "recommend"
    if any(word in lowered for word in ["detail", "info", "information", "about"]):
        return "details"
    return None


def _extract_title_hint(text: str) -> str | None:
    lowered = text.lower().strip()

    quoted = re.search(r"[\"']([^\"']{2,80})[\"']", text)
    if quoted:
        return quoted.group(1).strip()

    patterns = [
        r"(?:like|similar to|based on|from)\s+(.+?)(?:\s+(?:with|that|which|and)\b|[?.!,]|$)",
        r"(?:details|info|information)\s+(?:about|for|on)\s+(.+?)(?:[?.!,]|$)",
    ]
    for pattern in patterns:
        match = re.search(pattern, lowered)
        if match:
            candidate = text[match.start(1) : match.end(1)].strip(" .,!?:;\"'")
            if len(candidate) >= 2:
                return candidate

    if len(text.split()) <= 6:
        return text.strip(" .,!?:;\"'")

    return None


def _append(history: ChatHistory | None, user: str, bot: str) -> ChatHistory:
    chat = history or []
    chat.append({"role": "user", "content": user})
    chat.append({"role": "assistant", "content": bot})
    return chat


def _reset_state() -> dict[str, Any]:
    return {"stage": "root", "mode": None}


def handle_chat(message: str, history: ChatHistory | None, state: dict[str, Any] | None):
    current = state or _reset_state()
    text = (message or "").strip()
    if not text:
        return history, current, ""

    lowered = text.lower()

    if lowered in {"reset", "start over", "restart"}:
        current = _reset_state()
        history = _append(history, text, "Session reset. Ask for recommendations or anime details.")
        return history, current, ""

    if lowered in {"help", "commands"}:
        bot = (
            "Try:\n"
            "- 'recommend me anime'\n"
            "- 'details about toradora'\n"
            "- '/title cowboy bebop'\n"
            "- '/genre action sci-fi'\n"
            "- '/details fullmetal alchemist'\n"
            "- 'reset'"
        )
        history = _append(history, text, bot)
        return history, current, ""

    if lowered.startswith("/title "):
        query = text[7:].strip()
        result = ENGINE.recommend_anime(query, top_n=8)
        bot = result if isinstance(result, str) else _to_markdown_table(result)
        history = _append(history, text, bot)
        return history, current, ""

    if lowered.startswith("/genre "):
        query = text[7:].strip()
        result = ENGINE.recommend_anime_by_genre(query, top_n=8)
        bot = result if isinstance(result, str) else _to_markdown_table(result)
        history = _append(history, text, bot)
        return history, current, ""

    if lowered.startswith("/details "):
        query = text[9:].strip()
        result = ENGINE.get_anime_details(query)
        if isinstance(result, str):
            bot = result
        else:
            bot = (
                f"**{result['title']}**\n\n"
                f"- Romaji: {result['title_romaji']}\n"
                f"- Native: {result['title_native']}\n"
                f"- Genres: {', '.join(result['genres'])}\n"
                f"- Year: {result['year']}\n"
                f"- Mean Score: {result['mean_score']:.2f}\n\n"
                f"{result['description'][:650]}"
            )
        history = _append(history, text, bot)
        return history, current, ""

    if current["stage"] == "root":
        found = _intent(text)
        if found == "recommend":
            # Prefer one-shot responses when users provide a natural-language request.
            title_hint = _extract_title_hint(text)
            if title_hint:
                result = ENGINE.recommend_anime(title_hint, top_n=8)
                if not (
                    isinstance(result, str)
                    and (
                        result.startswith("Could not find")
                        or result.startswith("No anime title matched")
                    )
                ):
                    bot = result if isinstance(result, str) else _to_markdown_table(result)
                    history = _append(history, text, bot)
                    current = _reset_state()
                    return history, current, ""

            genre_result = ENGINE.recommend_anime_by_genre(text, top_n=8)
            if not (
                isinstance(genre_result, str)
                and genre_result.startswith("I could not detect a genre clearly")
            ):
                bot = genre_result if isinstance(genre_result, str) else _to_markdown_table(genre_result)
                history = _append(history, text, bot)
                current = _reset_state()
                return history, current, ""

            current["stage"] = "recommend_mode"
            bot = "Great. Do you want recommendations by **title** or **genre**?"
            history = _append(history, text, bot)
            return history, current, ""
        if found == "details":
            title_hint = _extract_title_hint(text)
            if title_hint:
                result = ENGINE.get_anime_details(title_hint)
                if isinstance(result, str):
                    bot = result
                else:
                    bot = (
                        f"**{result['title']}**\n\n"
                        f"- Romaji: {result['title_romaji']}\n"
                        f"- Native: {result['title_native']}\n"
                        f"- Genres: {', '.join(result['genres'])}\n"
                        f"- Year: {result['year']}\n"
                        f"- Mean Score: {result['mean_score']:.2f}\n\n"
                        f"{result['description'][:650]}"
                    )
                history = _append(history, text, bot)
                current = _reset_state()
                return history, current, ""

            current["stage"] = "details_query"
            bot = "Perfect. Tell me the anime title you want details for."
            history = _append(history, text, bot)
            return history, current, ""

        bot = "I can help with recommendations or anime details. Type `help` for commands."
        history = _append(history, text, bot)
        return history, current, ""

    if current["stage"] == "recommend_mode":
        if "title" in lowered:
            current["stage"] = "recommend_title_query"
            history = _append(history, text, "Nice choice. Enter an anime title.")
            return history, current, ""
        if "genre" in lowered:
            current["stage"] = "recommend_genre_query"
            history = _append(history, text, "Great. Enter one or more genres (for example: action sci-fi).")
            return history, current, ""

        history = _append(history, text, "Please type **title** or **genre**.")
        return history, current, ""

    if current["stage"] == "recommend_title_query":
        result = ENGINE.recommend_anime(text, top_n=8)
        bot = result if isinstance(result, str) else _to_markdown_table(result)
        history = _append(history, text, bot)
        current = _reset_state()
        return history, current, ""

    if current["stage"] == "recommend_genre_query":
        result = ENGINE.recommend_anime_by_genre(text, top_n=8)
        bot = result if isinstance(result, str) else _to_markdown_table(result)
        history = _append(history, text, bot)
        current = _reset_state()
        return history, current, ""

    if current["stage"] == "details_query":
        result = ENGINE.get_anime_details(text)
        if isinstance(result, str):
            bot = result
        else:
            bot = (
                f"**{result['title']}**\n\n"
                f"- Romaji: {result['title_romaji']}\n"
                f"- Native: {result['title_native']}\n"
                f"- Genres: {', '.join(result['genres'])}\n"
                f"- Year: {result['year']}\n"
                f"- Mean Score: {result['mean_score']:.2f}\n\n"
                f"{result['description'][:650]}"
            )
        history = _append(history, text, bot)
        current = _reset_state()
        return history, current, ""

    history = _append(history, text, "Type `reset` and try again.")
    current = _reset_state()
    return history, current, ""


def quick_title(title: str, history: ChatHistory | None, state: dict[str, Any] | None):
    msg = f"/title {title}"
    return handle_chat(msg, history, state)


def quick_genre(genre: str, history: ChatHistory | None, state: dict[str, Any] | None):
    msg = f"/genre {genre}"
    return handle_chat(msg, history, state)


def clear_chat():
    return [], _reset_state(), ""


CUSTOM_CSS = """
:root {
  --brand-bg: #f7f7f3;
  --brand-surface: #ffffff;
  --brand-accent: #0f766e;
  --brand-accent-2: #b45309;
  --brand-text: #0f172a;
}
.gradio-container {
  background: radial-gradient(circle at 10% 10%, #fef3c7 0%, #f7f7f3 40%, #e0f2fe 100%);
}
#hero {
  border: 1px solid #d6d3d1;
  border-radius: 18px;
  padding: 18px;
  background: var(--brand-surface);
  box-shadow: 0 10px 30px rgba(2, 6, 23, 0.08);
}
#hero h1 {
  color: var(--brand-text);
}
#hero p {
  color: #334155;
}
button.primary {
  background: linear-gradient(135deg, var(--brand-accent), #2563eb) !important;
  border: none !important;
}
"""


with gr.Blocks(title=APP_TITLE) as demo:
    state = gr.State(_reset_state())

    with gr.Column(elem_id="hero"):
        gr.Markdown("# AniScope AI")
        gr.Markdown(
            "A polished showcase UI with guided chat, quick actions, and recommendation intelligence."
        )

    with gr.Row():
        with gr.Column(scale=3):
            chatbot = gr.Chatbot(label="Concierge Chat", height=520)
            message = gr.Textbox(
                label="Message",
                placeholder="Type: recommend me anime, details about toradora, or /title cowboy bebop",
            )
            with gr.Row():
                send = gr.Button("Send", variant="primary")
                clear = gr.Button("Clear")
        with gr.Column(scale=2):
            gr.Markdown("### Quick Actions")
            quick_title_input = gr.Textbox(label="Quick title", value="cowboy bebop")
            quick_title_btn = gr.Button("Recommend from Title")
            quick_genre_input = gr.Textbox(label="Quick genre", value="action sci-fi")
            quick_genre_btn = gr.Button("Recommend from Genre")
            gr.Markdown("### Pro Tips")
            gr.Markdown("- Use `help` for commands")
            gr.Markdown("- Use `reset` to restart flow")
            gr.Markdown("- Slash commands: `/title`, `/genre`, `/details`")

    send.click(handle_chat, inputs=[message, chatbot, state], outputs=[chatbot, state, message])
    message.submit(handle_chat, inputs=[message, chatbot, state], outputs=[chatbot, state, message])

    quick_title_btn.click(
        quick_title,
        inputs=[quick_title_input, chatbot, state],
        outputs=[chatbot, state, message],
    )
    quick_genre_btn.click(
        quick_genre,
        inputs=[quick_genre_input, chatbot, state],
        outputs=[chatbot, state, message],
    )
    clear.click(clear_chat, outputs=[chatbot, state, message])


if __name__ == "__main__":
    demo.launch(theme=gr.themes.Soft(), css=CUSTOM_CSS)
