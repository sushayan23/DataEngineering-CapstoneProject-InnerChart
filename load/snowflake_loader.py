import os
import snowflake.connector
from dotenv import load_dotenv

load_dotenv()

STAGE = "InnerChart.STREAMINGDATA.s3_cleaned"
FILE_FORMAT = "InnerChart.STREAMINGDATA.parquet_format"

TABLES = [
    {
        "table": "InnerChart.STREAMINGDATA.spotify_top_tracks",
        "pattern": ".*spotify_top_tracks.*",
        "prefix": "spotify/",
    },
    {
        "table": "InnerChart.STREAMINGDATA.spotify_top_artists",
        "pattern": ".*spotify_top_artists.*",
        "prefix": "spotify/",
    },
    {
        "table": "InnerChart.STREAMINGDATA.lastfm_top_tracks",
        "pattern": ".*lastfm_top_tracks.*",
        "prefix": "lastfm/",
    },
    {
        "table": "InnerChart.STREAMINGDATA.lastfm_top_artists",
        "pattern": ".*lastfm_top_artists.*",
        "prefix": "lastfm/",
    },
    {
        "table": "InnerChart.STREAMINGDATA.billboard_hot100",
        "pattern": ".*billboard.*",
        "prefix": "billboard/",
    },
]

conn = snowflake.connector.connect(
    account=os.environ["SNOWFLAKE_ACCOUNT"],
    user=os.environ["SNOWFLAKE_USER"],
    password=os.environ["SNOWFLAKE_PASSWORD"],
    warehouse=os.environ["SNOWFLAKE_WAREHOUSE"],
    database="InnerChart",
    schema="STREAMINGDATA",
)

cursor = conn.cursor()

for t in TABLES:
    sql = f"""
        COPY INTO {t['table']}
        FROM @{STAGE}/{t['prefix']}
        FILE_FORMAT = (FORMAT_NAME = '{FILE_FORMAT}')
        PATTERN = '{t['pattern']}'
        MATCH_BY_COLUMN_NAME = CASE_INSENSITIVE
        FORCE = FALSE
    """
    cursor.execute(sql)
    rows = cursor.fetchone()
    print(f"Loaded {t['table']}: {rows}")

cursor.close()
conn.close()
