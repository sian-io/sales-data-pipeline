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

    # Define date and time from yesterday
    yesterday = (
        datetime.now().replace(
            hour=0,
            minute=0,
            second=0,
            microsecond=0
        ) - timedelta(days=1)
    )

    num_records = random.randint(10000, 100000)
    for _ in range(num_records):

        seller_id = random.randint(1, 50)
        product_id = random.randint(1, 100)
        quantity = random.randint(1, 10)
        status = random.choice(statuses)

        # Generate a random purchase time within the day
        seconds = random.randint(0, 86399)
        purchase_dt = yesterday + timedelta(seconds=seconds)
        purchase_date = purchase_dt.strftime('%Y-%m-%d')
        purchase_time = purchase_dt.strftime('%H:%M:%S')

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
            'date': purchase_date,
            'time': purchase_time
        }

        data.append(record)

    return data
