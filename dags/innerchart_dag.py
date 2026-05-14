from datetime import datetime
from airflow import DAG
from airflow.operators.bash import BashOperator

PROJECT_DIR = "/opt/airflow/project"
DBT_DIR = f"{PROJECT_DIR}/InnerChart"
PROFILES_DIR = "/opt/airflow/.dbt"

default_args = {
    "owner": "innerchart",
    "start_date": datetime(2026, 5, 13),
    "retries": 1,
}

with DAG(
    dag_id="innerchart_pipeline",
    default_args=default_args,
    schedule_interval="0 6 * * 0",  # every Sunday at 6am
    catchup=False,
    description="Weekly pipeline: Ingest → Transform → Load Snowflake → dbt",
) as dag:

    # ── INGESTION ────────────────────────────────────────────────────────────
    ingest_spotify = BashOperator(
        task_id="ingest_spotify",
        bash_command=f"python {PROJECT_DIR}/ingestion/spotify.py",
    )

    ingest_lastfm = BashOperator(
        task_id="ingest_lastfm",
        bash_command=f"python {PROJECT_DIR}/ingestion/lastfm.py",
    )

    ingest_billboard = BashOperator(
        task_id="ingest_billboard",
        bash_command=f"python {PROJECT_DIR}/ingestion/billboard.py",
    )

    # ── TRANSFORMATION ───────────────────────────────────────────────────────
    clean_spotify = BashOperator(
        task_id="clean_spotify",
        bash_command=f"python {PROJECT_DIR}/transformation/clean_spotify.py",
    )

    clean_lastfm = BashOperator(
        task_id="clean_lastfm",
        bash_command=f"python {PROJECT_DIR}/transformation/clean_lastfm.py",
    )

    clean_billboard = BashOperator(
        task_id="clean_billboard",
        bash_command=f"python {PROJECT_DIR}/transformation/clean_billboard.py",
    )

    # ── SNOWFLAKE LOAD ───────────────────────────────────────────────────────
    load_snowflake = BashOperator(
        task_id="load_snowflake",
        bash_command=f"python {PROJECT_DIR}/load/snowflake_loader.py",
    )

    # ── DBT ─────────────────────────────────────────────────────────────────
    dbt_run = BashOperator(
        task_id="dbt_run",
        bash_command=f"dbt run --profiles-dir {PROFILES_DIR} --project-dir {DBT_DIR}",
    )

    # ── DEPENDENCIES ─────────────────────────────────────────────────────────
    ingest_spotify >> clean_spotify
    ingest_lastfm >> clean_lastfm
    ingest_billboard >> clean_billboard

    [clean_spotify, clean_lastfm, clean_billboard] >> load_snowflake >> dbt_run
