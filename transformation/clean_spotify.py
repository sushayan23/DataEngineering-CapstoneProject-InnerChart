import os
import json
import pandas as pd
import s3fs
from dotenv import load_dotenv

load_dotenv()

BUCKET = "innerchart-data-lake"
DATE_STR = pd.Timestamp.now().strftime("%Y-%m-%d")
fs = s3fs.S3FileSystem()


def normalize_release_date(date_str):
    if pd.isna(date_str):
        return None
    parts = str(date_str).split("-")
    if len(parts) == 1:
        return f"{parts[0]}-01-01"
    if len(parts) == 2:
        return f"{parts[0]}-{parts[1]}-01"
    return date_str


def clean_tracks(df):
    df["release_date"] = df["release_date"].apply(normalize_release_date)
    df["release_date"] = pd.to_datetime(df["release_date"], errors="coerce")
    df["duration_s"] = (df["duration_ms"] / 1000).round(1)
    df = df.drop(columns=["duration_ms"])
    df["explicit"] = df["explicit"].astype(bool)
    return df


def clean_artists(df):
    df["genres"] = df["genres"].apply(
        lambda g: json.dumps(list(g)) if isinstance(g, (list, set)) else "[]"
    )
    return df


def load_and_upload(local_key, clean_fn, out_key):
    raw_path = f"s3://{BUCKET}/raw/{local_key}"
    cleaned_path = f"s3://{BUCKET}/cleaned/{out_key}"

    with fs.open(raw_path, "rb") as f:
        df = pd.read_parquet(f)

    df = clean_fn(df)

    with fs.open(cleaned_path, "wb") as f:
        df.to_parquet(f, index=False)

    print(f"Cleaned → {cleaned_path} ({len(df)} rows)")


load_and_upload(
    f"spotify/spotify_top_tracks_{DATE_STR}.parquet",
    clean_tracks,
    f"spotify/spotify_top_tracks_{DATE_STR}.parquet",
)

load_and_upload(
    f"spotify/spotify_top_artists_{DATE_STR}.parquet",
    clean_artists,
    f"spotify/spotify_top_artists_{DATE_STR}.parquet",
)
