from mage_ai.settings.repo import get_repo_path
from mage_ai.io.config import ConfigFileLoader
from mage_ai.io.google_cloud_storage import GoogleCloudStorage

from pandas import DataFrame
from os import path

import pyarrow as pa
import pyarrow.parquet as pq
import os

if 'data_exporter' not in globals():
    from mage_ai.data_preparation.decorators import data_exporter


@data_exporter
def export_data(data, *args, **kwargs):
    os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = '/home/personal-gcp.json'
    print(os.environ['GOOGLE_APPLICATION_CREDENTIALS'])
    bucket_name = 'mage-zoomcamp-ai2ys-module-2'
    project_id = 'dezoomcamp-module-2'
    table_name = 'nyc_taxi_data'
    root_path = f'{bucket_name}/{table_name}'


    data['lpep_pickup_date'] = data['lpep_pickup_datetime'].dt.date
    table = pa.Table.from_pandas(data)
    gcs = pa.fs.GcsFileSystem()
    pq.write_to_dataset(
        table, 
        root_path=root_path, 
        partition_cols=['lpep_pickup_date'], 
        filesystem=gcs)
