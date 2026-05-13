import pandas as pd
import s3fs
from dotenv import load_dotenv

load_dotenv()

BUCKET = "innerchart-data-lake"
DATE_STR = pd.Timestamp.now().strftime("%Y-%m-%d")
fs = s3fs.S3FileSystem()


def clean_billboard(df):
    df = df.rename(columns={"song": "title"})
    df["chart_date"] = pd.to_datetime(df["chart_date"], errors="coerce")
    df["rank"] = pd.to_numeric(df["rank"], errors="coerce").astype("Int64")
    df["last_week"] = pd.to_numeric(df["last_week"], errors="coerce").astype("Int64")
    df["peak_position"] = pd.to_numeric(df["peak_position"], errors="coerce").astype("Int64")
    df["weeks_on_chart"] = pd.to_numeric(df["weeks_on_chart"], errors="coerce").astype("Int64")
    return df


raw_path = f"s3://{BUCKET}/raw/billboard/billboard_hot100_{DATE_STR}.parquet"
cleaned_path = f"s3://{BUCKET}/cleaned/billboard/billboard_hot100_{DATE_STR}.parquet"

with fs.open(raw_path, "rb") as f:
    df = pd.read_parquet(f)

df = clean_billboard(df)

with fs.open(cleaned_path, "wb") as f:
    df.to_parquet(f, index=False)

print(f"Cleaned - {cleaned_path} ({len(df)} rows)")
