FROM apache/airflow:3.0.2-python3.11

COPY requirements.txt /opt/airflow/requirements.txt

USER airflow
RUN pip install --no-cache-dir -r /opt/airflow/requirements.txt