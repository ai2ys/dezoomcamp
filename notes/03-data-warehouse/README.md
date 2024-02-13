# 03 Data Warehouse

## 3.1.1 - Data Warehouse and BigQuery and 3.1.2 - Partitioning and Clustering

🎞️ <https://youtu.be/jrHljAoD6nM?si=_doAtu_tJ479RKWw>
🎞️ <https://youtu.be/-CqXf7vhhDs?feature=shared>

- Slides <https://docs.google.com/presentation/d/1a3ZoBAXFk8-EhUsd7rAZd-5p_HpltkzSeujjRGB2TAI/edit?usp=sharing>
- Big Query basic SQL <https://github.com/DataTalksClub/data-engineering-zoomcamp/blob/main/03-data-warehouse/big_query.sql>

### OLAP vs OLTP

- Online Analytical Processing (OLAP)
- Online-Transaction-Processing (OLTP)

What is the difference

- **OLAP:** is used for reporting and analytics. It is a read-only process.
- **OLTP:** is used for transactional processing. It is a read-write process.

1. OLAP (Online Analytical Processing):

    - **Purpose:** OLAP is designed for analyzing aggregated data. It helps you gain insights, create reports, and identify trends.
    - **Data Model:** OLAP systems use multidimensional data models. Imagine a cube where each dimension represents a different data attribute. Cells in the cube hold values or measures at the intersection of these dimensions.
    - **Example Use Case:** You might use OLAP to analyze sales data across different regions, time periods, and product categories.

1. OLTP (Online Transaction Processing):

    - **Purpose:** OLTP focuses on processing database transactions. It handles tasks like order processing, inventory updates, and customer account management.
    - **Data Model:** OLTP systems use a relational database with tables. Each row represents an entity instance (like a customer), and each column represents an attribute (like name or address).
    - **Example Use Case:** OLTP systems handle real-time transactions, such as processing online orders or updating stock levels.

Key Differences:

- **Purpose:** OLAP analyzes data, while OLTP processes transactions.
- **Data Formatting:** OLAP uses multidimensional models, while OLTP relies on relational databases.
- **Performance Focus:** OLAP prioritizes data read operations, whereas OLTP balances read and write operations.
- **Example:** OLAP for business intelligence, OLTP for day-to-day transactions.

### Data Warehouse

- **Data Warehouse:**
- OLAP solution
- Used for reporting and analysis

A data warehouse is a system that stores and manages large volumes of data. It is designed for query and analysis rather than transaction processing. It usually contains historical data derived from transaction data, but it can include data from other sources.

Data ware can be transformed into data marts, which are smaller data warehouses focused on a specific business line or team (purchasing, sales, inventory, ...).

### BigQuery

- Serverless, highly scalable, and cost-effective multi-cloud data warehouse
- Built-in features for machine learning and geospatial analysis

Flexibility of BigQuery how to stores the data, separating storage and compute.

Things to take care of

- BigQuery usually caches data. Turning at off for demo and reproducible results.
  - Click on the `More` button on the top right corner of the query editor
  - Select `Query settings`
  - In section `Cache preference` uncheck `Use cached results`

BigQuery comes with a lot of open source public datasets, which can be used for learning and testing.

BigQuery costs (two main pricing models)

- On demand pricing (mostly better suited)
- Flat rate pricing

Queries used in video: <https://github.com/DataTalksClub/data-engineering-zoomcamp/blob/main/03-data-warehouse/big_query.sql>

- External data sources
  - Create an external table to query data stored in Cloud Storage, Google Drive, or Google Sheets
  - Table information does not contain information about `Table size`, `Number of rows` because the data is not stored in BigQuery as it resides in an external source like Google Cloud Storage
  - Costs for querying external data can not be estimated in advance
  - Creating an external table, see example from link above (highlight the lines of code you want to execute and click `Run` or `Cmd/Ctrl + Enter`)

    ```sql
    -- Creating external table referring to gcs path
    CREATE OR REPLACE EXTERNAL TABLE `taxi-rides-ny.nytaxi.external_yellow_tripdata`
    OPTIONS (
        format = 'CSV',
        uris = ['gs://nyc-tl-data/trip data/yellow_tripdata_2019-*.csv', 'gs://nyc-tl-data/trip data/yellow_tripdata_2020-*.csv']
    );
        ```

        In this example there is a Bucket `nyc-tl-data` with a folder `trip data` and files `yellow_tripdata_2019-*.csv` and `yellow_tripdata_2020-*.csv` that are used for creating the external table.
- Partitioned tables
  - <https://cloud.google.com/bigquery/docs/partitioned-tables>
  - The number of partitions is limited to 4,000 partitions per table
  - The type of datatype used for partitioning is limited to time unit columns, ingestion time or integer ranges
    - When partitioning based on hours it might be a good choice to define an expiration time for the data to avoid having too many partitions
  - Partitioned tables are a good fit for time-series data (e.g. partition by date)
  - ℹ️ When doing queries on partitioned tables, BigQuery can skip scanning partitions that do not contain data relevant to the query &rarr reduces costs
  - Partitioning not suitable in case of small datasets
  - Create partitioned table
    -- Create a partitioned table from external table

    ```sql
    -- Create a partitioned table from external table
    CREATE OR REPLACE TABLE taxi-rides-ny.nytaxi.yellow_tripdata_partitoned
    PARTITION BY
        DATE(tpep_pickup_datetime) AS
    SELECT * FROM taxi-rides-ny.nytaxi.external_yellow_tripdata;
    ```

        The keyword `PARTITION BY` is used to specify the column to partition the table by. In this case, the column `tpep_pickup_datetime` is used to partition the table by date.
  - In the `Table info` you can see the 'partition' information (`Table Type: Partitioned`, `Partitioned by: DAY`, ``Partitioned on field: tpep_pickup_datetime`, ...)
  - Check how many rows are falling into which partition (check for bias in the partition).

    ```sql
    -- Let's look into the partitons - how many rows are in each partition
    SELECT table_name, partition_id, total_rows
    FROM `nytaxi.INFORMATION_SCHEMA.PARTITIONS`
    WHERE table_name = 'yellow_tripdata_partitoned'
    ORDER BY total_rows DESC;
    ```

    There should not be a large difference between the number of rows in each partition. If there is a large difference this might indicate that the column used for partitioning is not a good choice.

- Clustering
  - Up to four columns can be specified for clustering
    - Must be top-level, non-repeated columns
    - Data type must be of the following types: `DATE`, `BOOL`, `GEOGRAPHY`, `INT64`, `NUMERIC`, `BIGNUMERIC`, `STRING`, `STRING`, `TIMESTAMP`, `DATETIME`
  - Will group the data based on the columns specified within the partition
  - Multiple columns can be used for clustering
  - The order of the columns is important, because the data is sorted based on the order of the columns
  - Example for clustering a partitioned table

    ```sql
    -- Creating a partition and cluster table
    CREATE OR REPLACE TABLE taxi-rides-ny.nytaxi.yellow_tripdata_partitoned_clustered
    PARTITION BY DATE(tpep_pickup_datetime)
    CLUSTER BY VendorID AS
    SELECT * FROM taxi-rides-ny.nytaxi.external_yellow_tripdata;
      ```

    The keyword `CLUSTER BY` is used to specify the column to cluster the table by. In this case, the column `VendorID` is used to cluster the table by passenger count.
  - In the `Table info` (details section) the clustering information can be found below the partitioning information (..., `Clustered by: VendorID`)
  - Clustering improves filter and aggregation performance

## 3.2.1 BigQuery Best Practices

🎞️ <https://youtu.be/k81mLJVX08w?feature=shared>

> ❗️Important
>
> - Tables smaller than 1 GB are not recommended to be clustered (adds more overhead than benefits, same for partitioning)
> - Cost reduction
>   - Avoid `SELECT *` (specify column names)
>   - Always price queries before running them (right top corner of the query editor)
>   - Use clustering and partitioning
>   - Use streaming inserts with caution (can increase costs drastically)
>   - Materialize query results in stage
>
> - Query performance
>   - Filter on partitioned or clustered columns
>   - Denormalize data (means to store data in a single table that is not normalized)
>   - Use nested or repeated columns (in case of complicated data structures, that will help denormalize the data)
>   - Do not use external data too much (use it only when necessary)
>   - Reduce data before using `JOIN` (means to filter the data before joining it)
>   - Do not treat `WITH` caluses as prepared statements (means to use `WITH` clauses only for readability and not for performance)
>   - Avoid oversharding tables (means to avoid creating too many partitions or clusters)
>   - Avoid using `JavaScript` user-defined functions
>   - Use approximante aggregation functions (e.g. `HyperLogLog++`)
>   - Order statements should be at the last part of the query
>   - Optimize join patterns
>     - Place tables iwth largest number of rows first, followed by the smaller tables (fewer rows), and then the tables with the smallest number of rows (reason is because the second table would be broadcasted to all nodes)
>
> ℹ️ Information
>
> - There are different icons that indicate partitioned and clustered tables in the BigQuery UI.
> - Clustering &rarr; cost benefit unknown
> - Partitioning &rarr; cost benefit known

## 3.2.2 Internals of BigQuery

🎞️ [https://youtu.be/eduHi1inM4s?feature=shared](https://youtu.be/eduHi1inM4s?feature=shared)

BigQuery stores data in into a separate storage called `Colossus`, which is a "cheap storage" and stores data in a columnar format.

Advantage of separating storage and compute

- Significant cost savings
  - In case more storage is needed, only storage costs are increased
  - In case more compute is needed, only compute costs are increased
- Most cost occur when reading the data or running the queries

Jupiter network

- Because of the separation of storage and compute a bad network connection can lead to slow queries. This is a disadvantage where jupiter network comes into play. Jupiter network is inside BigQuery data centers (provides ~1TB/s network speed).

Dremel

- Query execution engine
- Divides query into a tree structure and separates the query into smaller parts so that each node can execute a subset of the query

Record oriented vs column oriented

- Record oriented databases store data in rows (similar CSV)
  - Easy to process and understand
- column (tree) oriented structure
  - Data of same row can be seen in multiple places
  - BigQuery uses column oriented structure
  - Better aggregation performance
  - Generally querying only a few columns and filter and aggregate on them

## 3.3.1  BigQuery Machine Learning

🎞️ <https://youtu.be/B-WtpB0PuG4?feature=shared>

- BQ allows building the model in the data warehouse itself &rarr; removes extra step of exporting the data
- Pricing see <https://cloud.google.com/bigquery/pricing#bqml>
- Deployment of model using a Docker image possible
- Introduction to BQ ML <https://cloud.google.com/bigquery/docs/bqml-introduction>
- Create ML models in BQ <https://cloud.google.com/bigquery/docs/create-machine-learning-model>
- DeZoomCamp course `SQL` queries used for ML in the video <https://github.com/DataTalksClub/data-engineering-zoomcamp/blob/main/03-data-warehouse/big_query_ml.sql> 


## 3.3.2 BigQuery Machine Learning Deployment

🎞️ <https://youtu.be/BjARzEWaznU?feature=shared>

Export model

- Export model tutorial <https://cloud.google.com/bigquery/docs/export-model-tutorial>
- DeZoomCamp course notes <https://github.com/DataTalksClub/data-engineering-zoomcamp/blob/main/03-data-warehouse/extract_model.md>
    ```bash
    # Login to Google Cloud
    gcloud auth login
    
    # Export model from BigQuery into Google Cloud Storage
    bq --project_id taxi-rides-ny extract -m nytaxi.tip_model gs://taxi_ml_model/tip_model
    
    # Copy model from Google Cloud Storage
    mkdir /tmp/model
    gsutil cp -r gs://taxi_ml_model/tip_model /tmp/model
    mkdir -p serving_dir/tip_model/1
    cp -r /tmp/model/tip_model/* serving_dir/tip_model/1
    
    # Start container using the model and making a POST request to try out the model
    docker pull tensorflow/serving
    docker run \
        -p 8501:8501 \
        --mount type=bind,source=pwd/serving_dir/tip_model,target=/models/tip_model \
        -e MODEL_NAME=tip_model \
        -t tensorflow/serving \
        & \
        curl -d '{"instances": [{"passenger_count":1, "trip_distance":12.2, "PULocationID":"193", "DOLocationID":"264", "payment_type":"2","fare_amount":20.4,"tolls_amount":0.0}]}' -X POST http://localhost:8501/v1/models/tip_model:predict
    # http://localhost:8501/v1/models/tip_model
    ```
