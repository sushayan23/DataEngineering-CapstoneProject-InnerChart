import os
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from dotenv import load_dotenv
import pandas as pd
import boto3
from botocore.exceptions import NoCredentialsError, ClientError

load_dotenv()

# Authenticate with Spotify using OAuth — requires user-top-read scope
CACHE_PATH = os.environ.get("SPOTIPY_CACHE_PATH", ".cache")

sp = spotipy.Spotify(
    auth_manager=SpotifyOAuth(
        client_id=os.environ["SPOTIFY_CLIENT_ID"],
        client_secret=os.environ["SPOTIFY_CLIENT_SECRET"],
        redirect_uri=os.environ["SPOTIFY_REDIRECT_URI"],
        scope="user-top-read",
        cache_path=CACHE_PATH,
        open_browser=False,
    ),
    requests_timeout=60
)

os.makedirs("data", exist_ok=True)

# ── TOP TRACKS ────────────────────────────────────────────────────────────────

# Fetch the user's top 50 tracks for the medium-term window (approx. last 6 months) according to Spotify
response = sp.current_user_top_tracks(limit=50, time_range="medium_term")

tracks_data = []
for i, track in enumerate(response["items"]):
    tracks_data.append({
        "rank": i + 1,
        "track_id": track["id"],
        "title": track["name"],
        "artist": track["artists"][0]["name"],
        "artist_id": track["artists"][0]["id"],
        "popularity": track.get("popularity"),
        "release_date": track["album"]["release_date"],
        "duration_ms": track["duration_ms"],
        "explicit": track["explicit"],
        "time_range": "medium_term",
        "fetched_at": pd.Timestamp.now(),
    })

tracks_df = pd.DataFrame(tracks_data)
tracks_df.to_parquet("data/spotify_top_tracks.parquet", index=False)
#print(f"Saved {len(tracks_df)} top tracks.")
#print(tracks_df.head())

date_str = pd.Timestamp.now().strftime("%Y-%m-%d")
try:
    s3 = boto3.client("s3")
    s3.upload_file(
        Filename= "data/spotify_top_tracks.parquet",
        Bucket = "innerchart-data-lake",
        Key = f"raw/spotify/spotify_top_tracks_{date_str}.parquet"
    )
except NoCredentialsError:
    print("AWS credentials not found")
except ClientError as e:
    print(f"Upload failed: {e}")

# ── TOP ARTISTS ───────────────────────────────────────────────────────────────

# Fetch the user's top 50 artists for the medium-term window
# note: genres are not fetched here because Spotify's API no longer reliably returns
# genre data. Genre enrichment will be done via Last.fm tags in the transform step.
artist_response = sp.current_user_top_artists(limit=50, time_range="medium_term")

artists_data = []
for i, artist in enumerate(artist_response["items"]):
    artists_data.append({
        "rank": i + 1,
        "artist_id": artist["id"],
        "artist": artist["name"],
        "genres": artist.get("genres", []),
        "popularity": artist.get("popularity"),
        "followers": artist.get("followers", {}).get("total"),
        "time_range": "medium_term",
        "fetched_at": pd.Timestamp.now(),
    })

artists_df = pd.DataFrame(artists_data)
artists_df.to_parquet("data/spotify_top_artists.parquet", index=False)
#print(f"Saved {len(artists_df)} top artists.")
#print(artists_df.head())

#s3 upload 
try:
    s3.upload_file(
        Filename= "data/spotify_top_artists.parquet",
        Bucket = "innerchart-data-lake",
        Key = f"raw/spotify/spotify_top_artists_{date_str}.parquet"
    )
except NoCredentialsError:
    print("AWS credentials not found")
except ClientError as e:
    print(f"Upload failed: {e}")