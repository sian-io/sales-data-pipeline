from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, concat_ws, to_timestamp
import requests
import json

default_args = {
    'start_date': datetime(2025, 7, 1),
    'email_on_failure': True,
    'email': ['example@email.com']
}

# 1. EXTRACTION
def extract_data():
    url = 'http://api:8000/data'
    response = requests.get(url)
    response.raise_for_status()
    data = response.json()

    # Save raw JSON to disk
    with open('/tmp/sales_data_raw.json', 'w') as f:
        json.dump(data, f)

# 2. TRANSFORMATION
def transform_data():
    spark = (
        SparkSession.builder
        .appName('TransformSalesData')
        .config('spark.jars', '/opt/airflow/jars/postgresql.jar')
        .getOrCreate()
    )

    # Read JSON file with Spark
    df = spark.read.json('/tmp/sales_data_raw.json')

    # Remove cancelled orders
    df_transformed = df.filter(col('status') != 'cancelled')

    # Create revenue column
    df_transformed = df_transformed.withColumn('revenue', col('quantity') * col('price'))

    # Combine 'date' and 'time' into a single datetime column
    df_transformed = df_transformed.withColumn(
        'datetime',
        to_timestamp(concat_ws(' ', df_transformed['date'], df_transformed['time']), 'yyyy-MM-dd HH:mm:ss')
    )

    # Drop unnecessary columns
    df_transformed = df_transformed.drop('date', 'time')

    # Save as CSV for the loading step
    df_transformed.write.mode('overwrite').option('header', True).csv('/tmp/sales_data_processed')

# 3. LOADING
def load_data():
    spark = (
        SparkSession.builder
        .appName('LoadSalesToPostgres')
        .config('spark.jars', '/opt/airflow/jars/postgresql.jar')
        .getOrCreate()
    )

    df = spark.read.option('header', True).csv('/tmp/sales_data_processed')

    (
        df.write.format('jdbc')
        .option('url', 'jdbc:postgresql://postgres:5432/sales_data')
        .option('dbtable', 'sales')
        .option('user', 'airflow')
        .option('password', 'airflow')
        .option('driver', 'org.postgresql.Driver')
        .mode('append')
        .save()
    )

# DAG definition
with DAG(
    dag_id='etl_sales_pipeline',
    default_args=default_args,
    schedule_interval='@daily',
    catchup=False,
    tags=['etl', 'spark', 'postgres']
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