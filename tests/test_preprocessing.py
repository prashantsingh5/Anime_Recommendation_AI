import pandas as pd

from src.data_preprocessing import preprocess_data


def test_preprocess_splits_genres_and_cleans_description():
    raw = pd.DataFrame(
        {
            "Title (Romaji)": ["Name"],
            "Title (English)": [None],
            "Title (Native)": [None],
            "Genres": ["Action, Adventure"],
            "Episodes": [None],
            "Description": ["<b>Great</b> anime"],
            "Season": [None],
            "Year": [None],
            "Mean Score": [None],
            "Popularity": [None],
        }
    )

    out = preprocess_data(raw)
    assert out.loc[0, "Title (English)"] == "Name"
    assert out.loc[0, "Genres"] == ["action", "adventure"]
    assert out.loc[0, "Description"] == "Great anime"
