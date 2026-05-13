with personal as (
    select lower(title) as title, lower(artist) as artist
    from {{ ref('stg_spotify_tracks') }}
),

mainstream as (
    select lower(title) as title, lower(artist) as artist
    from {{ ref('stg_billboard') }}
),

enthusiast as (
    select lower(title) as title, lower(artist) as artist
    from {{ ref('stg_lastfm_tracks') }}
),

combined as (
    select title, artist, 'personal'   as source_group from personal
    union all
    select title, artist, 'mainstream' as source_group from mainstream
    union all
    select title, artist, 'enthusiast' as source_group from enthusiast
),

aggregated as (
    select
        title,
        artist,
        max(case when source_group = 'personal'   then 1 else 0 end) as in_personal,
        max(case when source_group = 'mainstream' then 1 else 0 end) as in_mainstream,
        max(case when source_group = 'enthusiast' then 1 else 0 end) as in_enthusiast
    from combined
    group by title, artist
)

select
    title,
    artist,
    in_personal,
    in_mainstream,
    in_enthusiast,
    (in_personal + in_mainstream + in_enthusiast) as group_count,
    case
        when in_personal = 1 and in_mainstream = 1 and in_enthusiast = 1 then 'all_three'
        when in_personal = 1 and in_mainstream = 1                       then 'personal_and_mainstream'
        when in_personal = 1 and in_enthusiast = 1                       then 'personal_and_enthusiast'
        when in_mainstream = 1 and in_enthusiast = 1                     then 'mainstream_and_enthusiast'
        when in_personal = 1                                              then 'personal_only'
        when in_mainstream = 1                                            then 'mainstream_only'
        else                                                                   'enthusiast_only'
    end as overlap_category
from aggregated
