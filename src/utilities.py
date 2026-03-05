from __future__ import annotations

from fuzzywuzzy import process


def fuzzy_match_title(input_title: str, titles: list[str], threshold: int = 55) -> str | None:
    """Return the best title match above threshold or None."""
    result = process.extractOne(input_title, titles)
    if not result:
        return None
    title = result[0]
    confidence = result[1]
    return title if confidence >= threshold else None
