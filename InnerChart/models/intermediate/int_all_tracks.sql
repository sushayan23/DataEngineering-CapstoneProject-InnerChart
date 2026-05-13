select
    rank,
    title,
    artist,
    'personal'   as source_group,
    fetched_at
from {{ ref('stg_spotify_tracks') }}

union all

select
    rank,
    title,
    artist,
    'mainstream' as source_group,
    fetched_at
from {{ ref('stg_billboard') }}

union all

select
    rank,
    title,
    artist,
    'enthusiast' as source_group,
    fetched_at
from {{ ref('stg_lastfm_tracks') }}
