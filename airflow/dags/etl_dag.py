from airflow import DAG
from airflow.providers.standard.operators.python import PythonOperator
from datetime import datetime
from pipeline.tasks import extract_data, transform_data, load_data

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