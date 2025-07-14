CREATE SCHEMA IF NOT EXISTS treated;

CREATE TABLE IF NOT EXISTS treated.sales (
    id SERIAL PRIMARY KEY,
    seller_id INTEGER,
    product_id INTEGER,
    category TEXT,
    quantity INTEGER,
    price NUMERIC(10, 2),
    status TEXT,
    revenue NUMERIC(10, 2),
    datetime TIMESTAMP
);
