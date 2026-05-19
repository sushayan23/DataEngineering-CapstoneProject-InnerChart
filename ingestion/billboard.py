import os
import requests
import pandas as pd
import boto3
from botocore.exceptions import NoCredentialsError, ClientError

os.makedirs("data", exist_ok=True)

#get the data
url = "https://raw.githubusercontent.com/mhollingshead/billboard-hot-100/main/recent.json"
response = requests.get(url)
data = response.json()

#create empty list to save data within it for DataFrame creation
songs = []

chart_date = data["date"]
for track in data["data"]:
    songs.append({
        "chart_date": chart_date,
        "song": track["song"],
        "artist": track["artist"],
        "rank": track["this_week"],
        "last_week": track["last_week"],
        "peak_position": track["peak_position"],
        "weeks_on_chart": track["weeks_on_chart"],
        "fetched_at": pd.Timestamp.now()
        })
    
#create DataFrame and save data as parquet
df = pd.DataFrame(songs)
df.to_parquet("data/billboard_hot100.parquet", index=False)
print(df.head())

#upload to S3 bucket
date_str = pd.Timestamp.now().strftime("%Y-%m-%d")
try:
    s3 = boto3.client("s3")
    s3.upload_file(
        Filename= "data/billboard_hot100.parquet",
        Bucket = "innerchart-data-lake",
        Key = f"raw/billboard/billboard_hot100_{date_str}.parquet"
    )
except NoCredentialsError:
    print("AWS credentials not found")
except ClientError as e:
    print(f"Upload failed: {e}")