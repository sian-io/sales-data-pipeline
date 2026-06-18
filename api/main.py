from fastapi import FastAPI, Query
from datetime import datetime, timedelta
import random

# Possible product categories and order statuses for the generator
CATEGORIES = ['Electronics', 'Clothing', 'Tools', 'Toys']
STATUSES = ['Pending', 'Shipped', 'Delivered', 'Cancelled']

app = FastAPI(
    title="Sales Generation API",
    description="A modular API for synthesizing daily sales pipeline data",
    version="1.1.0"
)

def get_yesterday_midnight() -> datetime: 
    """Calculates and returns yesterday's datetime at midnight (00:00:00)."""
    return datetime.now().replace(
        hour=0, minute=0, second=0, microsecond=0
    ) - timedelta(days=1)


def generate_single_record(yesterday_midnight: datetime, seed_by_product_id: bool = True) -> dict:
    """Generates a single randomized sales record with optional deterministic product seeding."""
    seller_id = random.randint(1, 50)
    product_id = random.randint(1, 100)
    quantity = random.randint(1, 10)
    status = random.choice(STATUSES)

    # Distribute the transaction time randomly across the 24-hour window
    random_seconds = random.randint(0, 86399)
    purchase_dt = yesterday_midnight + timedelta(seconds=random_seconds)
    purchase_date = purchase_dt.strftime('%Y-%m-%d')
    purchase_time = purchase_dt.strftime('%H:%M:%S')

    # Seed local RNG based on product_id to keep categories and prices consistent
    if seed_by_product_id:
        product_rng = random.Random(product_id)
    else:
        product_rng = random.Random()

    category = product_rng.choice(CATEGORIES)
    price = round(product_rng.uniform(49.99, 1499.99), 2)

    return {
        'seller_id': seller_id,
        'product_id': product_id,
        'category': category,
        'quantity': quantity,
        'price': price,
        'status': status,
        'date': purchase_date,
        'time': purchase_time
    }


def generate_dataset_batch(size: int, yesterday_midnight: datetime) -> list[dict]:
    """Generates a batch of sales records for a given dataset size."""
    return [generate_single_record(yesterday_midnight) for _ in range(size)]


@app.get('/data')
def get_data(limit: int | None = Query(
    default=None, 
    description="Optional parameter to force a specific dataset size for unit testing"
)):
    """API endpoint returning simulated sales records from yesterday.
    
    If limit is specified, generates exactly that amount,
    If limit is None, falls back to randomized daily generation (10,000 to 100,000 records).
    """
    yesterday = get_yesterday_midnight()
    
    # Define volume size: Use user override if provided, otherwise randomize
    num_records = limit if limit is not None else random.randint(10000, 100000)
    
    return generate_dataset_batch(size=num_records, yesterday_midnight=yesterday)
