from sqlalchemy import create_engine
import pandas as pd
import requests
import json

DEFAULT_API_URL = 'http://api:8000/data'
DEFAULT_RAW_DATA_PATH = '/tmp/sales_data_raw.json'
DEFAULT_PROCESSED_DATA_PATH = '/tmp/sales_data_processed'
DEFAULT_DB_CONN = 'postgresql+psycopg2://admin:admin@postgres:5432/pipeline_db'

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
    """Reads raw JSON sales data, cleans and formats the features, and exports it to a compressed Parquet format."""
    df = pd.read_json(input_path, dtype=schema)

    df = df[df['status'] != 'Cancelled']

    df['revenue'] = df['quantity'] * df['price']

    # Defensive string casting prevents Pandas auto-date-parsing TypeError crashes
    combined_dt_string = df['date'].astype(str) + ' ' + df['time'].astype(str)

    df['datetime'] = pd.to_datetime(combined_dt_string)
    df = df.drop(columns=['date', 'time'])
    df = df.sort_values(by='datetime')

    df.to_parquet(output_path)


def load_data(input_path: str = DEFAULT_PROCESSED_DATA_PATH, db_conn: str = DEFAULT_DB_CONN) -> None:
    """Reads the processed Parquet sales dataset and appends it to the PostgreSQL database table."""
    df = pd.read_parquet(input_path)

    if df.empty:
        raise ValueError('DataFrame is empty. No data to load into PostgreSQL.')

    engine = create_engine(db_conn)
    df.to_sql('sales', engine, schema='treated', if_exists='append', index=False)