from fastapi import FastAPI
from datetime import date
import random
import uuid

categories = ['Electronics', 'Clothing', 'Tools', 'Food', 'Toys']
statuses = ['Pending', 'Shipped', 'Delivered', 'Cancelled']

app = FastAPI()

@app.get('/data')
def get_data():

    data = []

    # random ammount of records
    for _ in range(random.randint(100, 500)):

        # completely random data
        transaction_id = str(uuid.uuid4())
        seller_id = random.randint(1, 50)
        product_id = random.randint(1, 100)
        quantity = random.randint(1, 10)
        status = random.choice(statuses)

        product_rng = random.Random(product_id)  # rng seeded on product_id for consistent prices and categories

        # product-consistent random data
        category = product_rng.choice(categories)
        price = round(product_rng.uniform(19.99, 1499.99), 2)

        record = {
            'transaction_id': transaction_id,
            'seller_id': seller_id,
            'product_id': product_id,
            'category': category,
            'quantity': quantity,
            'price': price,
            'status': status,
            'date': date.today()
        }
        data.append(record)

    return data