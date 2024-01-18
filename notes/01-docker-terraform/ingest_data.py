#!/usr/bin/env python
# coding: utf-8


# # Upload Data to PostgreSQL Database
from time import time
import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy import engine
from sqlalchemy import text
from IPython.display import display


datetime_columns = [
    'tpep_pickup_datetime',
    'tpep_dropoff_datetime',
]

df_empty = pd.read_csv(
    'yellow_tripdata_2021-01.csv.gz', 
    compression='gzip', 
    parse_dates=datetime_columns, 
    nrows=0)
# display(df_empty.head())
engine = create_engine('postgresql://root:root@localhost:5432/ny_taxi')
empty_df.to_sql(name='yellow_taxi_data', con=engine, if_exists='replace')

# Query the first 5 rows (should be empty)
with engine.connect() as conn:
    result = conn.execute(text("SELECT * FROM yellow_taxi_data")).fetchall()
    print("\nFirst 5 Rows:")
    print(result)


# reset the iterator
df_chunks = pd.read_csv('yellow_tripdata_2021-01.csv.gz', compression='gzip', parse_dates=datetime_columns, chunksize=1e5)
for i, chunk in enumerate(df_chunks):
    t_start = time()
    chunk.to_sql(name='yellow_taxi_data', con=engine, if_exists='append')
    t_end = time()
    print(f'inserted chunk no. "{i: 5d}" another chunk, took "{t_end - t_start:.3f}" seconds')

# Query the first 5 rows (should be empty)
with engine.connect() as conn:
    result = conn.execute(text("SELECT count(*) FROM yellow_taxi_data;")).fetchall()
    print("\nNumber of lines:")
    print(result)

#check number of rows in CSV file, this will include header
get_ipython().system('wc -l yellow_tripdata_2021-01.csv')

