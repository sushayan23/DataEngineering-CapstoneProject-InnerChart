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
where TRY_TO_TIMESTAMP_NTZ(fetched_at) = (
    select MAX(TRY_TO_TIMESTAMP_NTZ(fetched_at))
    from {{ source('streamingdata', 'spotify_top_artists') }}
)
