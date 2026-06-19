import pytest
from datetime import datetime
from fastapi.testclient import TestClient
from api.main import (
    app, 
    CATEGORIES, 
    STATUSES, 
    get_yesterday_midnight, 
    generate_single_record, 
    generate_dataset_batch
)

client = TestClient(app)

# PYTHON UNIT TESTS

def test_get_yesterday_midnight():
    """Validates that yesterday's date calculator returns correct midnight hours."""
    midnight_dt = get_yesterday_midnight()
    assert midnight_dt.hour == 0
    assert midnight_dt.minute == 0
    assert midnight_dt.second == 0
    assert midnight_dt.microsecond == 0
    
    # Must be between 1 and 2 days offset from current time
    time_difference = datetime.now() - midnight_dt
    assert 1 <= time_difference.days < 2


def test_generate_single_record_valid_structure():
    """Validates that a single record contains all expected fields and formats."""
    yesterday = get_yesterday_midnight()
    record = generate_single_record(yesterday_midnight=yesterday)
    
    expected_keys = {
        'seller_id', 'product_id', 'category', 'quantity', 
        'price', 'status', 'date', 'time'
    }
    assert set(record.keys()) == expected_keys
    
    # Validate domains
    assert record['category'] in CATEGORIES
    assert record['status'] in STATUSES
    assert 1 <= record['seller_id'] <= 50
    assert 1 <= record['product_id'] <= 100


def test_generate_dataset_batch():
    """Validates that the batch generator outputs correct lengths and array types."""
    yesterday = get_yesterday_midnight()
    batch_size = 5
    batch = generate_dataset_batch(size=batch_size, yesterday_midnight=yesterday)
    
    assert len(batch) == batch_size
    assert isinstance(batch, list)
    assert all(isinstance(rec, dict) for rec in batch)


# INTEGRATION & ENDPOINT TESTS

def test_get_data_success_with_limit_override():
    """Validates that endpoint responds instantly with HTTP 200 when limit override is supplied."""
    response = client.get("/data?limit=10")
    assert response.status_code == 200
    
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 10  # Verifies override constraint works


def test_get_data_schema_and_constraints_fast():
    """Validates schema fields and constraints using a lightweight micro-payload."""
    response = client.get("/data?limit=5")
    assert response.status_code == 200
    data = response.json()
    
    sample_record = data[0]
    expected_keys = {
        'seller_id', 'product_id', 'category', 'quantity', 
        'price', 'status', 'date', 'time'
    }
    assert set(sample_record.keys()) == expected_keys
    
    # Type validations
    assert isinstance(sample_record['seller_id'], int)
    assert 1 <= sample_record['seller_id'] <= 50
    assert isinstance(sample_record['product_id'], int)
    assert 1 <= sample_record['product_id'] <= 100
    assert sample_record['category'] in CATEGORIES
    assert sample_record['status'] in STATUSES
    assert isinstance(sample_record['quantity'], int)
    assert isinstance(sample_record['price'], (int, float))