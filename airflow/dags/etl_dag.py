from airflow import DAG
from airflow.providers.standard.operators.python import PythonOperator
from datetime import datetime
from pipeline.tasks import extract_data, transform_data, load_data

DEFAULT_API_URL = 'http://api:8000/data'
DEFAULT_RAW_DATA_PATH = '/tmp/sales_data_raw.json'
DEFAULT_PROCESSED_DATA_PATH = '/tmp/sales_data_processed'
DEFAULT_DB_CONN = 'postgresql+psycopg2://admin:admin@postgres:5432/pipeline_db'

default_args = {
    'start_date': datetime(2025, 7, 1)
}

with DAG(
    dag_id='etl_sales_pipeline',
    default_args=default_args,
    schedule='@daily',  # Runs every day at midnight (0 0 * * *)
    is_paused_upon_creation=False,
    catchup=False,
    tags=['etl', 'pandas', 'postgres']
) as dag:

    extract_task = PythonOperator(
        task_id='extract_data',
        python_callable=extract_data
    )

    transform_task = PythonOperator(
        task_id='transform_data',
        python_callable=transform_data
    )

    load_task = PythonOperator(
        task_id='load_data',
        python_callable=load_data
    )

    extract_task >> transform_task >> load_task