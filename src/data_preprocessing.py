from __future__ import annotations

import re
from pathlib import Path

import pandas as pd
from bs4 import BeautifulSoup

REQUIRED_COLUMNS = {
    "Title (Romaji)",
    "Title (English)",
    "Title (Native)",
    "Genres",
    "Episodes",
    "Description",
    "Season",
    "Year",
    "Mean Score",
    "Popularity",
}


def load_data(filepath: str | Path) -> pd.DataFrame:
    """Load CSV data from a path and return a DataFrame."""
    return pd.read_csv(filepath)


def clean_html(text: str) -> str:
    """Remove HTML tags and collapse whitespace for clean NLP input."""
    if not isinstance(text, str):
        return ""
    if re.search(r"<.*?>", text):
        text = " ".join(BeautifulSoup(text, "html.parser").stripped_strings)
    return re.sub(r"\s+", " ", text).strip()


def preprocess_data(df: pd.DataFrame) -> pd.DataFrame:
    """Clean and normalize the raw anime dataset for modeling."""
    missing = REQUIRED_COLUMNS - set(df.columns)
    if missing:
        raise ValueError(f"Dataset missing required columns: {sorted(missing)}")

    clean_df = df.copy()

    clean_df["Title (English)"] = clean_df["Title (English)"].fillna(clean_df["Title (Romaji)"])
    clean_df["Title (Native)"] = clean_df["Title (Native)"].fillna("Unknown")

    clean_df["Year"] = pd.to_numeric(clean_df["Year"], errors="coerce")
    clean_df["Year"] = clean_df["Year"].fillna(clean_df["Year"].median())

    clean_df["Mean Score"] = pd.to_numeric(clean_df["Mean Score"], errors="coerce")
    clean_df["Mean Score"] = clean_df["Mean Score"].fillna(clean_df["Mean Score"].median())

    clean_df["Popularity"] = pd.to_numeric(clean_df["Popularity"], errors="coerce")
    clean_df["Popularity"] = clean_df["Popularity"].fillna(clean_df["Popularity"].median())

    clean_df["Episodes"] = pd.to_numeric(clean_df["Episodes"], errors="coerce")
    clean_df["Episodes"] = clean_df["Episodes"].fillna(clean_df["Episodes"].median())

    clean_df["Description"] = clean_df["Description"].fillna("Not available").apply(clean_html)
    clean_df["Season"] = clean_df["Season"].fillna("unknown").astype(str).str.lower()

    clean_df = clean_df.dropna(subset=["Genres", "Title (English)"])
    clean_df["Genres"] = (
        clean_df["Genres"]
        .astype(str)
        .str.lower()
        .str.split(",")
        .apply(lambda values: [v.strip() for v in values if v.strip()])
    )

    clean_df["Title (English)"] = clean_df["Title (English)"].astype(str).str.strip()
    clean_df["Title (Romaji)"] = clean_df["Title (Romaji)"].astype(str).str.strip()

    clean_df.reset_index(drop=True, inplace=True)
    return clean_df
