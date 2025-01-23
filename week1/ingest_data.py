import argparse
import pandas as pd
import os
from pyarrow.parquet import ParquetFile
import pyarrow as pa 
from sqlalchemy import create_engine
import time

def load_data(config):
    user = config.user
    password = config.password
    host = config.host
    port = config.port
    db = config.db
    url = config.url
    table = config.table
    file_name = config.file_name

 
    os.system(f'wget {url} -O {file_name}')

    if '.parquet' in file_name:
        file = ParquetFile(file_name)
        df_iter = file.iter_batches(batch_size=100000)
    if '.csv' in file_name:
        df_iter = pd.read_csv(file_name,compression='gzip',encoding='utf-8', iterator=True, chunksize=100000)


    engine = create_engine(f'postgresql://{user}:{password}@{host}:{port}/{db}')
    engine.connect()
    count = 0
    start_time = time.time()
    inter_time_save = time.time()
    for batch in df_iter:
        if '.parquet' in file_name:
            df = batch.to_pandas()
        else:
            df = batch
        df.to_sql(name=table,con=engine, if_exists='append')
        count += df.shape[0]
        inter_time = time.time()
        print(f"After Iteration no {int(count/100000)} is {count}. This Iteration took total {inter_time - inter_time_save} sec")
        inter_time_save = inter_time
    print(f"Final Execution time is {time.time() - start_time} Sec")

def testing():
    print("Yes Executed")
    print("Yes Executed 2")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Loading data from .paraquet file link to a Postgres datebase.')
    parser.add_argument('--user')
    parser.add_argument('--password')
    parser.add_argument('--host')
    parser.add_argument('--port')
    parser.add_argument('--db')
    parser.add_argument('--url')
    parser.add_argument('--table')
    parser.add_argument('--file_name')
    args = parser.parse_args()
    load_data(args)


