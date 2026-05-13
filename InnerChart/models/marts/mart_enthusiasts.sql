select
    t.rank,
    t.title,
    t.artist,
    t.listeners,
    t.playcount,
    a.listeners as artist_listeners,
    a.playcount as artist_playcount,
    t.fetched_at
from {{ ref('stg_lastfm_tracks') }} t
left join {{ ref('stg_lastfm_artists') }} a
    on lower(t.artist) = lower(a.artist)
