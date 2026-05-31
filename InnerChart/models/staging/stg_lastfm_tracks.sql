select
    "RANK"::NUMBER as rank,
    title,
    artist,
    listeners::NUMBER as listeners,
    playcount::NUMBER as playcount,
    TRY_TO_TIMESTAMP_NTZ(fetched_at) as fetched_at
from {{ source('streamingdata', 'lastfm_top_tracks') }}
where TRY_TO_TIMESTAMP_NTZ(fetched_at) = (
    select MAX(TRY_TO_TIMESTAMP_NTZ(fetched_at))
    from {{ source('streamingdata', 'lastfm_top_tracks') }}
)
