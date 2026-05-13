import pandas as pd
import s3fs
from dotenv import load_dotenv

load_dotenv()

BUCKET = "innerchart-data-lake"
DATE_STR = pd.Timestamp.now().strftime("%Y-%m-%d")
fs = s3fs.S3FileSystem()


def clean_artists(df):
    df["listeners"] = pd.to_numeric(df["listeners"], errors="coerce").astype("Int64")
    df["playcount"] = pd.to_numeric(df["playcount"], errors="coerce").astype("Int64")
    return df


def clean_tracks(df):
    df["listeners"] = pd.to_numeric(df["listeners"], errors="coerce").astype("Int64")
    df["playcount"] = pd.to_numeric(df["playcount"], errors="coerce").astype("Int64")
    return df


def load_and_upload(raw_key, clean_fn, out_key):
    raw_path = f"s3://{BUCKET}/raw/{raw_key}"
    cleaned_path = f"s3://{BUCKET}/cleaned/{out_key}"

    with fs.open(raw_path, "rb") as f:
        df = pd.read_parquet(f)

    df = clean_fn(df)

    with fs.open(cleaned_path, "wb") as f:
        df.to_parquet(f, index=False)

    print(f"Cleaned → {cleaned_path} ({len(df)} rows)")


load_and_upload(
    f"lastfm/lastfm_top_artists_{DATE_STR}.parquet",
    clean_artists,
    f"lastfm/lastfm_top_artists_{DATE_STR}.parquet",
)

load_and_upload(
    f"lastfm/lastfm_top_tracks_{DATE_STR}.parquet",
    clean_tracks,
    f"lastfm/lastfm_top_tracks_{DATE_STR}.parquet",
)
