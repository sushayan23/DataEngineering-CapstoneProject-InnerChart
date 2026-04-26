import requests
import os
from dotenv import load_dotenv
from pprint import pprint
import pandas as pd
import boto3
from botocore.exceptions import NoCredentialsError, ClientError


load_dotenv()

lastfm_api = os.environ["LASTFM_API_KEY"]

###################### GET TOP ARTITS ##################################

url = f"http://ws.audioscrobbler.com/2.0/?method=chart.getTopArtists&api_key={lastfm_api}&format=json"

response = requests.get(url)

#print("------", response.status_code)
data = response.json()
#pprint(data["artists"]["artist"][0]["name"])

artists_data = []
for i, artist in enumerate(data["artists"]["artist"]):                                                                                                
      artists_data.append({
          "rank": i + 1,                                                                                                                                
          "artist": artist["name"],
          "listeners": artist["listeners"],
          "playcount": artist["playcount"],
          "fetched_at": pd.Timestamp.now()
      })                                                                                                                                                
   
df_artists = pd.DataFrame(artists_data) 
df_artists.to_parquet("data/lastfm_top_artists.parquet", index=False)      

#upload Top Tracks to S3 bucket
date_str = pd.Timestamp.now().strftime("%Y-%m-%d")
try:
    s3 = boto3.client("s3")
    s3.upload_file(
        Filename= "data/lastfm_top_artists.parquet",
        Bucket = "innerchart-data-lake",
        Key = f"raw/lastfm/lastfm_top_artists_{date_str}.parquet"
    )
except NoCredentialsError:
    print("AWS credentials not found")
except ClientError as e:
    print(f"Upload failed: {e}")

###################### GET TOP TRACKS ##################################

url_tracks = f"http://ws.audioscrobbler.com/2.0/?method=chart.getTopTracks&api_key={lastfm_api}&format=json"
response = requests.get(url_tracks)
tracks = response.json()

#pprint(tracks["tracks"]["track"])

tracks_data = []
                                                                                                                                                        
for i, track in enumerate(tracks["tracks"]["track"]):                                                                                                   
    tracks_data.append({
        "rank": i + 1,                                                                                                                                
        "title": track["name"],
        "artist": track["artist"]["name"],
        "listeners": track["listeners"],                                                                                                              
        "playcount": track["playcount"],
        "fetched_at": pd.Timestamp.now()
    })                                                                                                                                                
                    
df_tracks = pd.DataFrame(tracks_data) 
df_tracks.to_parquet("data/lastfm_top_tracks.parquet", index=False)
#print(df_tracks.head())

#upload Top Tracks to S3 bucket
date_str = pd.Timestamp.now().strftime("%Y-%m-%d")
try:
    s3.upload_file(
        Filename= "data/lastfm_top_tracks.parquet",
        Bucket = "innerchart-data-lake",
        Key = f"raw/lastfm/lastfm_top_tracks_{date_str}.parquet"
    )
except NoCredentialsError:
    print("AWS credentials not found")
except ClientError as e:
    print(f"Upload failed: {e}")