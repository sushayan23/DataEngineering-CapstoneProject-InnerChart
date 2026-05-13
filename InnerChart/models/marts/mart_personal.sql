select
    t.rank,
    t.title,
    t.artist,
    t.popularity,
    t.release_date,
    t.duration_s,
    t.explicit,
    a.genres,
    a.followers,
    t.fetched_at
from {{ ref('stg_spotify_tracks') }} t
left join {{ ref('stg_spotify_artists') }} a
    on lower(t.artist) = lower(a.artist)
