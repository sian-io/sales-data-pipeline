import time
import pandas as pd
import streamlit as st
from sqlalchemy import create_engine

# Connection using service name from docker-compose
engine = create_engine('postgresql+psycopg2://admin:admin@postgres:5432/pipeline_db')

st.set_page_config(page_title='Sales Dashboard', layout='wide')
st.title('Real-Time Sales Dashboard')

placeholder = st.empty()

refresh_interval = 10  # seconds

while True:
    df = pd.read_sql('SELECT * FROM treated.sales ORDER BY datetime DESC LIMIT 1000', engine)

    total_revenue = df['revenue'].sum()
    avg_ticket = df['revenue'].mean()
    total_orders = len(df)
    total_quantity = df['quantity'].sum()
    revenue_by_category = df.groupby('category')['revenue'].sum().sort_values(ascending=False)

    with placeholder.container():
        kpi1, kpi2, kpi3, kpi4 = st.columns(4)
        kpi1.metric('Total Revenue', f"${total_revenue:,.2f}")
        kpi2.metric('Average Ticket', f"${avg_ticket:,.2f}")
        kpi3.metric('Total Orders', total_orders)
        kpi4.metric('Quantity Sold', int(total_quantity))

        st.subheader('Revenue by Category')
        st.bar_chart(revenue_by_category)

        st.subheader('Revenue Over Time')
        st.line_chart(df.sort_values('datetime').set_index('datetime')['revenue'])

        st.subheader('Recent Sales')
        st.dataframe(df)

    time.sleep(refresh_interval)
