select
    rank,
    title,
    artist,
    chart_date,
    last_week,
    peak_position,
    weeks_on_chart,
    fetched_at
from {{ ref('stg_billboard') }}
