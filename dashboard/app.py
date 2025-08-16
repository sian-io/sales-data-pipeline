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

    with placeholder.container():
        st.metric('Total Revenue', f"${df['revenue'].sum():,.2f}")
        st.line_chart(df.sort_values('datetime').set_index('datetime')['revenue'])
        st.dataframe(df)

    time.sleep(refresh_interval)
