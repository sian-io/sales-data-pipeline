from fastapi import FastAPI
from datetime import datetime, timedelta, time
import random

# Possible product categories and order statuses
categories = ['Electronics', 'Clothing', 'Tools', 'Food', 'Toys']
statuses = ['Pending', 'Shipped', 'Delivered', 'Cancelled']

app = FastAPI()

@app.get('/data')
def get_data():

    data = []

    # Define date and time from last hour (UTC when running in Docker)
    last_hour_timestamp = datetime.now() - timedelta(hours=1)
    last_hour_day = last_hour_timestamp.strftime('%Y-%m-%d')
    last_hour_hour = last_hour_timestamp.hour

    num_records = random.randint(1000, 5000)
    for _ in range(num_records):

        seller_id = random.randint(1, 50)
        product_id = random.randint(1, 100)
        quantity = random.randint(1, 10)
        status = random.choice(statuses)
        purchase_time = time(
            hour=last_hour_hour,
            minute=random.randint(0, 59),
            second=random.randint(0, 59)
        ).isoformat()

        # Rng seeded on product_id for consistent prices and categories
        product_rng = random.Random(product_id)

        category = product_rng.choice(categories)
        price = round(product_rng.uniform(19.99, 1499.99), 2)

        record = {
            'seller_id': seller_id,
            'product_id': product_id,
            'category': category,
            'quantity': quantity,
            'price': price,
            'status': status,
            'date': last_hour_day,
            'time': purchase_time
        }

        data.append(record)

    return data
