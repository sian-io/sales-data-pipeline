from airflow import DAG
from airflow.providers.standard.operators.python import PythonOperator
from datetime import datetime
from sqlalchemy import create_engine
import pandas as pd
import requests
import json

DEFAULT_API_URL = 'http://api:8000/data'
DEFAULT_RAW_DATA_PATH = '/tmp/sales_data_raw.json'
DEFAULT_PROCESSED_DATA_PATH = '/tmp/sales_data_processed'
DEFAULT_DB_CONN = 'postgresql+psycopg2://admin:admin@postgres:5432/pipeline_db'

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

def extract_data(url: str = DEFAULT_API_URL, output_path: str = DEFAULT_RAW_DATA_PATH) -> None:
    """Fetches raw sales data from the REST API and stores it locally as a raw JSON file."""
    response = requests.get(url)
    response.raise_for_status()
    data = response.json()

    with open(output_path, 'w') as f:
        json.dump(data, f)


def transform_data(input_path: str = DEFAULT_RAW_DATA_PATH, output_path: str = DEFAULT_PROCESSED_DATA_PATH) -> None:
    """Reads raw JSON sales data, cleans and formats the features, and exports it to a compressed Parquet format.
    
    Filters out 'Cancelled' records, computes individual revenue, merges date/time columns into an 
    explicit datetime64 timestamp, and sorts chronologically.
    """
    df = pd.read_json(input_path, dtype=schema)

    # Remove cancelled orders for analysis
    df = df[df['status'] != 'Cancelled']

    df['revenue'] = df['quantity'] * df['price']

    combined_dt_string = df['date'].astype(str) + ' ' + df['time'].astype(str)
    df['datetime'] = pd.to_datetime(combined_dt_string)

    # Original 'date' and 'time' columns are no longer needed
    df = df.drop(columns=['date', 'time'])

    # Sort by datetime for consistency with auto-incremental id column
    df = df.sort_values(by='datetime')

    df.to_parquet(output_path)


def load_data(input_path: str = DEFAULT_PROCESSED_DATA_PATH, db_conn: str = DEFAULT_DB_CONN) -> None:
    """Reads the processed Parquet sales dataset and appends it to the PostgreSQL database table.
    
    Validates that the input dataset contains records before initiating a database session to prevent silent failures.
    """
    df = pd.read_parquet(input_path)

    # Check if DataFrame is empty before loading to avoid silent failures
    if df.empty:
        raise ValueError('DataFrame is empty. No data to load into PostgreSQL.')

    engine = create_engine(db_conn)
    df.to_sql('sales', engine, schema='treated', if_exists='append', index=False)


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