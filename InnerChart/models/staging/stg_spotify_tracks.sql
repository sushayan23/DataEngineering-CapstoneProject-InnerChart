select
    "RANK"::NUMBER as rank,
    track_id,
    title,
    artist,
    artist_id,
    popularity::NUMBER as popularity,
    TO_DATE(TO_TIMESTAMP_NTZ(release_date::NUMBER, 6)) as release_date,
    duration_s::FLOAT as duration_s,
    explicit::BOOLEAN as explicit,
    time_range,
    TRY_TO_TIMESTAMP_NTZ(fetched_at) as fetched_at
from {{ source('streamingdata', 'spotify_top_tracks') }}
where TRY_TO_TIMESTAMP_NTZ(fetched_at) = (
    select MAX(TRY_TO_TIMESTAMP_NTZ(fetched_at))
    from {{ source('streamingdata', 'spotify_top_tracks') }}
)
