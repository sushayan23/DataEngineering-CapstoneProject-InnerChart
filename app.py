import os 
import streamlit as st
import snowflake.connector
import pandas as pd
import plotly.express as px
from dotenv import load_dotenv
from pathlib import Path

load_dotenv(Path(__file__).parent / ".env")

conn = snowflake.connector.connect(
    account=os.environ["SNOWFLAKE_ACCOUNT"],
    user=os.environ["SNOWFLAKE_USER"],
    password=os.environ["SNOWFLAKE_PASSWORD"],
    warehouse=os.environ["SNOWFLAKE_WAREHOUSE"],
    database=os.environ["SNOWFLAKE_DATABASE"],
    schema=os.environ["SNOWFLAKE_SCHEMA"],
    session_parameters={"PYTHON_CONNECTOR_QUERY_RESULT_FORMAT": "JSON"},
)

@st.cache_data
def load_data():
    df_personal = pd.read_sql("SELECT rank::NUMBER as rank, title, artist, popularity::NUMBER as popularity, release_date::VARCHAR as release_date, explicit, duration_s::NUMBER as duration_s FROM mart_personal ORDER BY rank", conn)
    df_overlap = pd.read_sql("SELECT title, artist, overlap_category, in_personal, in_mainstream, in_enthusiast, group_count FROM mart_overlap", conn)
    df_mainstream = pd.read_sql("SELECT rank, title, artist, peak_position, weeks_on_chart FROM mart_mainstream ORDER BY rank", conn)
    df_enthusiasts = pd.read_sql("SELECT rank, artist, listeners, playcount FROM mart_enthusiasts ORDER BY rank", conn)
    for df in [df_personal, df_overlap, df_mainstream, df_enthusiasts]:
        df.columns = df.columns.str.lower()
    df_personal["duration_s"] = pd.to_numeric(df_personal["duration_s"], errors="coerce")
    df_personal["rank"] = pd.to_numeric(df_personal["rank"], errors="coerce")
    return df_personal, df_overlap, df_mainstream, df_enthusiasts

df_personal, df_overlap, df_mainstream, df_enthusiasts = load_data()

st.set_page_config(page_title="InnerChart", layout="wide")

st.title("🎵 InnerChart")
st.subheader("How mainstream are you as a music listener?")

st.markdown("---")

st.header("Your Listening Profile")

overlap_counts = df_overlap["overlap_category"].value_counts().reset_index()
overlap_counts.columns = ["Category", "Count"]

fig_overlap = px.pie(
    overlap_counts,
    names="Category",
    values="Count",
    title="Where are the tracks overlapping"
)

st.plotly_chart(fig_overlap, use_container_width=True)

personal_tracks = df_overlap[df_overlap["in_personal"] == 1]
total = len(personal_tracks)
pct_mainstream = len(personal_tracks[personal_tracks["in_mainstream"] == 1]) / total * 100
pct_enthusiast = len(personal_tracks[personal_tracks["in_enthusiast"] == 1]) / total * 100
pct_both = len(personal_tracks[(personal_tracks["in_mainstream"] == 1) & (personal_tracks["in_enthusiast"] == 1)]) / total * 100

st.subheader("Percentage of Your Tracks in Other Categories.")
col1, col2, col3 = st.columns(3)
col1.metric("Also in Billboard", f"{pct_mainstream:.0f}%")
col2.metric("Also in Last.fm", f"{pct_enthusiast:.0f}%")
col3.metric("In all three", f"{pct_both:.0f}%")

overlapping = df_overlap[df_overlap["group_count"] > 1][["title", "artist", "overlap_category"]].sort_values("overlap_category")
st.subheader("Tracks with overlap")
st.dataframe(overlapping, use_container_width=True, hide_index=True)

st.markdown("---")
st.header("Your Top 50 Tracks")

st.dataframe(
    df_personal[["rank", "title", "artist", "release_date", "explicit", "duration_s"]],
    use_container_width=True,
    hide_index=True,
)

fig_duration = px.bar(
    df_personal.sort_values("rank"),
    x="title",
    y="duration_s",
    title="Track Duration of Your Top 50 (in seconds)",
    labels={"title": "Track", "duration_s": "Duration (s)"},
)
fig_duration.update_layout(xaxis_tickangle=-45, xaxis_showticklabels=False)
st.plotly_chart(fig_duration, use_container_width=True)

df_dur = df_personal.dropna(subset=["duration_s"])
if not df_dur.empty:
    def duration_label(s):
        if s < 180: return "Under 3 min"
        if s < 240: return "3–4 min"
        return "Over 4 min"
    dur_counts = df_dur["duration_s"].apply(duration_label).value_counts().reset_index()
    dur_counts.columns = ["Category", "Count"]
    fig_dur_pie = px.pie(dur_counts, names="Category", values="Count", title="Track Length Distribution")
    st.plotly_chart(fig_dur_pie, use_container_width=True)

col_left, col_right = st.columns(2)

with col_left:
    explicit_counts = (
        df_personal["explicit"]
        .map(lambda x: "Explicit" if x in (True, 1, "true", "True") else "Clean")
        .value_counts()
        .reset_index()
    )
    explicit_counts.columns = ["Type", "Count"]
    fig_explicit = px.pie(explicit_counts, names="Type", values="Count", title="Explicit vs. Clean Tracks")
    st.plotly_chart(fig_explicit, use_container_width=True)

with col_right:
    artist_counts = df_personal["artist"].value_counts().reset_index()
    artist_counts.columns = ["Artist", "Tracks"]
    artist_counts = artist_counts[artist_counts["Tracks"] > 1]
    if not artist_counts.empty:
        fig_artists = px.bar(
            artist_counts,
            x="Artist",
            y="Tracks",
            title="Artists with Multiple Tracks in Your Top 50",
            labels={"Artist": "Artist", "Tracks": "Number of Tracks"},
        )
        fig_artists.update_layout(xaxis_tickangle=-45)
        st.plotly_chart(fig_artists, use_container_width=True)
    else:
        st.info("Each artist appears only once in your Top 50.")

st.markdown("---")
st.header("Billboard Hot 100")

st.dataframe(
    df_mainstream[["rank", "title", "artist", "peak_position", "weeks_on_chart"]],
    use_container_width=True,
    hide_index=True,
)

fig_weeks = px.bar(
    df_mainstream.sort_values("weeks_on_chart", ascending=False).head(20),
    x="title",
    y="weeks_on_chart",
    title="Top 20 Billboard Tracks by Weeks on Chart",
    labels={"title": "Track", "weeks_on_chart": "Weeks on Chart"},
)
fig_weeks.update_layout(xaxis_tickangle=-45, xaxis_showticklabels=False)
st.plotly_chart(fig_weeks, use_container_width=True)

st.markdown("---")
st.header("Last.fm Top Tracks")

st.dataframe(
    df_enthusiasts[["rank", "artist", "listeners", "playcount"]],
    use_container_width=True,
    hide_index=True,
)

fig_listeners = px.bar(
    df_enthusiasts.sort_values("rank").head(20),
    x="artist",
    y="listeners",
    title="Top 20 Last.fm Artists by Listeners",
    labels={"artist": "Artist", "listeners": "Listeners"},
)
fig_listeners.update_layout(xaxis_tickangle=-45, xaxis_showticklabels=False)
st.plotly_chart(fig_listeners, use_container_width=True)
