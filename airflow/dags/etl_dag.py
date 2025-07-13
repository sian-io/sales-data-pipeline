from airflow import DAG
from airflow.providers.standard.operators.python import PythonOperator
from datetime import datetime
from sqlalchemy import create_engine
import pandas as pd
import requests
import json

default_args = {
    'start_date': datetime(2025, 7, 1)
}

# Explicitly define the schema for the JSON data to avoid TypeErrors
schema = {
    'seller_id': 'int',
    'product_id': 'int',
    'category': 'str',
    'quantity': 'int',
    'price': 'float',
    'status': 'str',
    'date': 'str',
    'time': 'str'
}

def extract_data():
    url = 'http://api:8000/data'
    response = requests.get(url)
    response.raise_for_status()
    data = response.json()

    with open('/tmp/sales_data_raw.json', 'w') as f:
        json.dump(data, f)


def transform_data():
    df = pd.read_json('/tmp/sales_data_raw.json', dtype=schema)

    # Remove cancelled orders for analysis
    df = df[df['status'] != 'Cancelled']

    df['revenue'] = df['quantity'] * df['price']

    # Combine 'date' and 'time' into a single timestamp column for better time series analysis
    df['datetime'] = (df['date'] + ' ' + df['time']).astype('datetime64[ns]')

    # Original 'date' and 'time' columns are no longer needed
    df = df.drop(columns=['date', 'time'])

    df.to_parquet('/tmp/sales_data_processed')


def load_data():
    df = pd.read_parquet('/tmp/sales_data_processed')

    # Check if DataFrame is empty before loading to avoid silent failures
    if df.empty:
        raise ValueError('DataFrame is empty. No data to load into PostgreSQL.')

    engine = create_engine('postgresql+psycopg2://admin:admin@postgres:5432/pipeline_db')
    
    df.to_sql('sales', engine, schema='treated', if_exists='append', index=False)


with DAG(
    dag_id='etl_sales_pipeline',
    default_args=default_args,
    schedule='@hourly',
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
