#!/usr/bin/env python
# coding: utf-8


# # Upload Data to PostgreSQL Database
from time import time
import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy import engine
from sqlalchemy import text
# from IPython.display import display
import argparse


def main(args):
    username = args.user
    password = args.password
    host = args.host
    port = args.port
    database = args.database
    table = args.table
    url = args.url
    compression = args.compression
    chunksize = args.chunksize

    engine_param = f'postgresql://{username}:{password}@{host}:{port}/{database}'
    print(engine_param)
    engine = create_engine(engine_param)

    datetime_columns = [
        'tpep_pickup_datetime',
        'tpep_dropoff_datetime',
    ]

    df_empty = pd.read_csv(
        url, 
        compression='gzip', 
        parse_dates=datetime_columns, 
        nrows=0)
    df_empty.to_sql(name='yellow_taxi_data', con=engine, if_exists='replace')

    # Query the first 5 rows (should be empty)
    with engine.connect() as conn:
        result = conn.execute(text("SELECT * FROM yellow_taxi_data")).fetchall()
        print("\nFirst 5 Rows:")
        print(result)


    # reset the iterator
    df_chunks = pd.read_csv(url, compression='gzip', parse_dates=datetime_columns, chunksize=1e5)
    for i, chunk in enumerate(df_chunks):
        t_start = time()
        chunk.to_sql(name='yellow_taxi_data', con=engine, if_exists='append')
        t_end = time()
        print(f'inserted chunk no. "{i: 3d}" another chunk, took "{t_end - t_start:.3f}" seconds')

    # Query the first 5 rows (should be empty)
    with engine.connect() as conn:
        result = conn.execute(text("SELECT count(*) FROM yellow_taxi_data;")).fetchall()
        print("\nNumber of lines:")
        print(result)

    # #check number of rows in CSV file, this will include header
    # get_ipython().system('wc -l yellow_tripdata_2021-01.csv')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
                        prog='Postgre data ingestion',
                        description='Script to ingest data into Postgre database',
                        epilog='')
    parser.add_argument('--user', type=str, help='DB user name')
    parser.add_argument('--password', type=str, help='DB password')
    parser.add_argument('--host', type=str, help='DB host')
    parser.add_argument('--port', type=str, help='DB port')
    parser.add_argument('--database', type=str, help='DB name')
    parser.add_argument('--table', type=str, help='Table name')
    parser.add_argument('--url', type=str, help='Url of input file (CSV file)')
    parser.add_argument('--compression', default=None, type=str, help='Compression type of input file (CSV file)')    
    parser.add_argument('--chunksize', default=1e5, type=int, help='Chunk size to read CSV file')
    args = parser.parse_args()
    main(args)