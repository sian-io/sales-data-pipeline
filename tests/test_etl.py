import pytest
import pandas as pd
import json
from unittest.mock import patch, MagicMock
from pipeline.tasks import (
    extract_data, 
    transform_data, 
    load_data, 
    schema
)

@pytest.fixture
def mock_raw_json_data():
    """Creates a mock JSON payload to simulate the raw data extractor output."""
    return [
        # Normal active record (must be processed)
        {
            'seller_id': 1, 'product_id': 10, 'category': 'Electronics',
            'quantity': 2, 'price': 100.0, 'status': 'Delivered',
            'date': '2026-06-14', 'time': '10:30:00'
        },
        # Cancelled record (must be filtered out and dropped)
        {
            'seller_id': 2, 'product_id': 20, 'category': 'Tools',
            'quantity': 1, 'price': 50.0, 'status': 'Cancelled',
            'date': '2026-06-14', 'time': '11:00:00'
        },
        # Out-of-order record (must be sorted chronologically)
        {
            'seller_id': 3, 'product_id': 30, 'category': 'Toys',
            'quantity': 3, 'price': 10.0, 'status': 'Shipped',
            'date': '2026-06-14', 'time': '09:15:00'
        }
    ]


# EXTRACT TASK UNIT TEST

@patch('requests.get')
def test_extract_data_saves_json(mock_get, tmp_path):
    """Validates that extract_data successfully handles REST API payloads and writes a physical file."""
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = [{"item": "data"}]
    mock_get.return_value = mock_response

    fake_output_file = tmp_path / "raw_api_data.json"

    extract_data(url="http://fake-api/data", output_path=str(fake_output_file))

    mock_get.assert_called_once_with("http://fake-api/data")
    
    with open(fake_output_file, 'r') as f:
        written_data = json.load(f)
    assert written_data == [{"item": "data"}]


# TRANSFORM TASK UNIT TEST

def test_transform_data_logic(mock_raw_json_data, tmp_path):
    """Validates entire Pandas vector mathematics, cleanings, and sorting logic."""
    fake_input_file = tmp_path / "sales_data_raw.json"
    fake_output_dir = tmp_path / "sales_data_processed"

    with open(fake_input_file, 'w') as f:
        json.dump(mock_raw_json_data, f)

    transform_data(input_path=str(fake_input_file), output_path=str(fake_output_dir))

    processed_df = pd.read_parquet(fake_output_dir)

    assert 'Cancelled' not in processed_df['status'].values
    assert len(processed_df) == 2  # Out of 3 initial records, 1 was dropped

    assert processed_df.iloc[0]['seller_id'] == 3
    
    assert processed_df.loc[processed_df['seller_id'] == 1, 'revenue'].values[0] == 200.0
    assert processed_df.loc[processed_df['seller_id'] == 3, 'revenue'].values[0] == 30.0

    assert 'date' not in processed_df.columns
    assert 'time' not in processed_df.columns
    assert 'datetime' in processed_df.columns
    assert pd.api.types.is_datetime64_any_dtype(processed_df['datetime'])


# LOAD TASK UNIT TEST

def test_load_data_raises_value_error_on_empty_df(tmp_path):
    """Validates load_data safely throws an exception if the dataframe is empty."""
    fake_empty_parquet = tmp_path / "empty.parquet"
    
    pd.DataFrame().to_parquet(fake_empty_parquet)

    with pytest.raises(ValueError, match="DataFrame is empty. No data to load into PostgreSQL."):
        load_data(input_path=str(fake_empty_parquet), db_conn="sqlite:///:memory:")


@patch('pipeline.tasks.create_engine')
@patch('pandas.DataFrame.to_sql')
def test_load_data_triggers_db_loading(mock_to_sql, mock_create_engine, mock_raw_json_data, tmp_path):
    """Validates that load_data instantiates a SQLAlchemy engine and invokes the to_sql load mechanism."""
    fake_parquet_file = tmp_path / "data.parquet"
    
    df_with_schema = pd.DataFrame(mock_raw_json_data).astype(schema)
    df_with_schema.to_parquet(fake_parquet_file)

    load_data(input_path=str(fake_parquet_file), db_conn="postgresql+psycopg2://admin:admin@postgres:5432/pipeline_db")

    mock_create_engine.assert_called_once_with("postgresql+psycopg2://admin:admin@postgres:5432/pipeline_db")
    mock_to_sql.assert_called_once()