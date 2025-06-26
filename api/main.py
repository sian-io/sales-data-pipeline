from fastapi import FastAPI
from datetime import date, time
import random

categories = ['Electronics', 'Clothing', 'Tools', 'Food', 'Toys']
statuses = ['Pending', 'Shipped', 'Delivered', 'Cancelled']

app = FastAPI()

@app.get('/data')
def get_data():

    data = []

    # today's date
    today = date.today().isoformat()

    # random ammount of records
    num_records = random.randint(1000, 5000)
    for _ in range(num_records):

        # completely random data
        seller_id = random.randint(1, 50)
        product_id = random.randint(1, 100)
        quantity = random.randint(1, 10)
        status = random.choice(statuses)
        purchase_time = time(
            hour=random.randint(0, 23),
            minute=random.randint(0, 59),
            second=random.randint(0, 59)
        ).isoformat()

        # rng seeded on product_id for consistent prices and categories
        product_rng = random.Random(product_id)

        # product-consistent random data
        category = product_rng.choice(categories)
        price = round(product_rng.uniform(19.99, 1499.99), 2)

        record = {
            'seller_id': seller_id,
            'product_id': product_id,
            'category': category,
            'quantity': quantity,
            'price': price,
            'status': status,
            'date': today,
            'time': purchase_time
        }
        data.append(record)

    return data