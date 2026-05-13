select
    "RANK"::NUMBER as rank,
    artist_id,
    artist,
    genres,
    popularity::NUMBER as popularity,
    followers::NUMBER as followers,
    time_range,
    TRY_TO_TIMESTAMP_NTZ(fetched_at) as fetched_at
from {{ source('streamingdata', 'spotify_top_artists') }}
where TO_DATE(TRY_TO_TIMESTAMP_NTZ(fetched_at)) = (
    select MAX(TO_DATE(TRY_TO_TIMESTAMP_NTZ(fetched_at)))
    from {{ source('streamingdata', 'spotify_top_artists') }}
)
