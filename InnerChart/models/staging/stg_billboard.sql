select
    "RANK"::NUMBER as rank,
    title,
    artist,
    chart_date::DATE as chart_date,
    last_week::NUMBER as last_week,
    peak_position::NUMBER as peak_position,
    weeks_on_chart::NUMBER as weeks_on_chart,
    TRY_TO_TIMESTAMP_NTZ(fetched_at) as fetched_at
from {{ source('streamingdata', 'billboard_hot100') }}
where TO_DATE(TRY_TO_TIMESTAMP_NTZ(fetched_at)) = (
    select MAX(TO_DATE(TRY_TO_TIMESTAMP_NTZ(fetched_at)))
    from {{ source('streamingdata', 'billboard_hot100') }}
)
