FROM apache/airflow:2.9.0-python3.11
USER root
RUN apt-get update && apt-get install -y --no-install-recommends \
      build-essential libssl-dev libffi-dev \
      && apt-get clean
USER airflow
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . /opt/airflow/project