## Week 3 Homework
ATTENTION: At the end of the submission form, you will be required to include a link to your GitHub repository or other public code-hosting site. This repository should contain your code for solving the homework. If your solution includes code that is not in file format (such as SQL queries or shell commands), please include these directly in the README file of your repository.

<b><u>Important Note:</b></u> <p> For this homework we will be using the 2022 Green Taxi Trip Record Parquet Files from the New York
City Taxi Data found here: </br> https://www.nyc.gov/site/tlc/about/tlc-trip-record-data.page </br>
If you are using orchestration such as Mage, Airflow or Prefect do not load the data into Big Query using the orchestrator.</br> 
Stop with loading the files into a bucket. </br></br>
<u>NOTE:</u> You will need to use the PARQUET option files when creating an External Table</br>

<b>SETUP:</b></br>
Create an external table using the Green Taxi Trip Records Data for 2022. </br>
Create a table in BQ using the Green Taxi Trip Records for 2022 (do not partition or cluster this table). </br>
</p>


```bash
# 1. create a bucket in GCS
# 2. then download the files using the script below
# 3. upload the data to the bucket


#!/bin/bash
# Base URL
base_url="https://d37ci6vzurychx.cloudfront.net/trip-data/green_tripdata_2022"

# Loop over all months
for month in $(seq -w 12)
do
    # Construct the URL
    url="${base_url}-${month}.parquet"

    # Download the file
    wget $url
done

# go to BigQuery Studio
```


```sql	
-- Create an external table using the Green Taxi Trip Records Data for 2022.
CREATE OR REPLACE EXTERNAL TABLE your_project_id.your_dataset.external_table_name
OPTIONS(
  format="PARQUET",
  uris=[
    "gs://your_bucket_name/green_tripdata_2022-*.parquet"
  ]
)
-- Create a non partitioned table from external table
CREATE OR REPLACE TABLE your_project_id.your_dataset.table_name AS
SELECT * FROM your_project_id.your_dataset.external_table_name;
```

In BigQuery Studio
1. Select your project
2. Click on the three vertical dots `...` on the right side of the project name in the explorer
    - Click on `Create dataset`
    - Name the dataset `new_york_taxi_trips`
    - Select region `EU`
    - Click `Create dataset`
4. Run the following query to create a table in BQ using the Green Taxi Trip Records for 2022 (do not partition or cluster this table).


```sql	
-- create external table
CREATE OR REPLACE EXTERNAL TABLE dezoomcamp-homework-3.new_york_taxi_trips.external_green_taxi_2022
OPTIONS(
  format="PARQUET",
  uris=[
    "gs://dezoomcamp-homework3-bucket/green_tripdata_2022-*.parquet"
  ]
);

-- Create a non partitioned table from external table
CREATE OR REPLACE TABLE new_york_taxi_trips.green_taxi_2022 AS
SELECT * FROM dezoomcamp-homework-3.new_york_taxi_trips.external_green_taxi_2022;
```

## Question 1:
Question 1: What is count of records for the 2022 Green Taxi Data??
- 65,623,481
- **840,402**
- 1,936,423
- 253,647

```sql
-- record count
SELECT COUNT(1) FROM `dezoomcamp-homework-3.new_york_taxi_trips.green_taxi_2022`
-- answer: 840402

-- or check "number of rows" in the table details  
```


## Question 2:
Write a query to count the distinct number of PULocationIDs for the entire dataset on both the tables.</br> 
What is the estimated amount of data that will be read when this query is executed on the External Table and the Table?

- **0 MB for the External Table and 6.41MB for the Materialized Table**
- 18.82 MB for the External Table and 47.60 MB for the Materialized Table
- 0 MB for the External Table and 0MB for the Materialized Table
- 2.14 MB for the External Table and 0MB for the Materialized Table

```sql
-- count distinct PULocationID
SELECT COUNT(DISTINCT PULocationID) FROM dezoomcamp-homework-3.new_york_taxi_trips.green_taxi_2022;
SELECT COUNT(DISTINCT PULocationID) FROM dezoomcamp-homework-3.new_york_taxi_trips.external_green_taxi_2022;
```


## Question 3:
How many records have a fare_amount of 0?
- 12,488
- 128,219
- 112
- **1,622**

```sql
-- count records with fare_amount of 0
SELECT COUNT(fare_amount) FROM `dezoomcamp-homework-3.new_york_taxi_trips.green_taxi_2022` WHERE fare_amount = 0;
```

## Question 4:
What is the best strategy to make an optimized table in Big Query if your query will always order the results by PUlocationID and filter based on lpep_pickup_datetime? (Create a new table with this strategy)
- Cluster on lpep_pickup_datetime Partition by PUlocationID
- **Partition by lpep_pickup_datetime  Cluster on PUlocationID**
- Partition by lpep_pickup_datetime and Partition by PUlocationID
- Cluster on by lpep_pickup_datetime and Cluster on PUlocationID

```sql	
-- check the columns in the table
SELECT 
  column_name
FROM 
  `dezoomcamp-homework-3.new_york_taxi_trips.INFORMATION_SCHEMA.COLUMNS`
WHERE 
  table_name = 'green_taxi_2022';

-- create a partitioned table converting lpep_pickup_datetime and lpep_dropoff_datetime to date
CREATE OR REPLACE TABLE new_york_taxi_trips.green_taxi_2022_partitioned
PARTITION BY DATE(lpep_pickup_datetime)
CLUSTER BY PULocationID
AS
SELECT 
  VendorID,
  CAST(lpep_pickup_datetime AS TIMESTAMP) AS lpep_pickup_datetime,
  CAST(lpep_dropoff_datetime AS TIMESTAMP) AS lpep_dropoff_datetime,
  store_and_fwd_flag,
  RatecodeID,
  PULocationID,
  DOLocationID,
  passenger_count,
  trip_distance,
  fare_amount,
  extra,
  mta_tax,
  tip_amount,
  tolls_amount,
  ehail_fee,
  improvement_surcharge,
  total_amount,
  payment_type,
  trip_type,
  congestion_surcharge
FROM new_york_taxi_trips.green_taxi_2022;

-- create materialized table with datetime columns
CREATE OR REPLACE TABLE new_york_taxi_trips.green_taxi_2022
AS
SELECT 
  VendorID,
  CAST(lpep_pickup_datetime AS TIMESTAMP) AS lpep_pickup_datetime,
  CAST(lpep_dropoff_datetime AS TIMESTAMP) AS lpep_dropoff_datetime,
  store_and_fwd_flag,
  RatecodeID,
  PULocationID,
  DOLocationID,
  passenger_count,
  trip_distance,
  fare_amount,
  extra,
  mta_tax,
  tip_amount,
  tolls_amount,
  ehail_fee,
  improvement_surcharge,
  total_amount,
  payment_type,
  trip_type,
  congestion_surcharge
FROM new_york_taxi_trips.green_taxi_2022;
```


## Question 5:
Write a query to retrieve the distinct PULocationID between lpep_pickup_datetime
06/01/2022 and 06/30/2022 (inclusive)</br>

Use the materialized table you created earlier in your from clause and note the estimated bytes. Now change the table in the from clause to the partitioned table you created for question 4 and note the estimated bytes processed. What are these values? </br>

Choose the answer which most closely matches.</br> 

- 22.82 MB for non-partitioned table and 647.87 MB for the partitioned table
- **12.82 MB for non-partitioned table and 1.12 MB for the partitioned table**
- 5.63 MB for non-partitioned table and 0 MB for the partitioned table
- 10.31 MB for non-partitioned table and 10.31 MB for the partitioned table

```sql

-- distinct PULocationID between lpep_pickup_datetime 06/01/2022 and 06/30/2022
SELECT COUNT(DISTINCT PULocationID) FROM `dezoomcamp-homework-3.new_york_taxi_trips.green_taxi_2022` WHERE lpep_pickup_datetime BETWEEN '2022-06-01' AND '2022-06-30';

-- distinct PULocationID between lpep_pickup_datetime 06/01/2022 and 06/30/2022
SELECT COUNT(DISTINCT PULocationID) FROM `dezoomcamp-homework-3.new_york_taxi_trips.green_taxi_2022_partitioned` WHERE lpep_pickup_datetime BETWEEN '2022-06-01' AND '2022-06-30';
```

## Question 6: 
Where is the data stored in the External Table you created?

- Big Query
- **GCP Bucket**
- Big Table
- Container Registry


## Question 7:
It is best practice in Big Query to always cluster your data:
- True
- **False**


## (Bonus: Not worth points) Question 8:
No Points: Write a `SELECT count(*)` query FROM the materialized table you created. How many bytes does it estimate will be read? Why?

```sql
-- count records in the materialized table
SELECT COUNT(*) FROM `dezoomcamp-homework-3.new_york_taxi_trips.green_taxi_2022`
-- answer: (0 bytes) and the table details shows "number of rows" as 840,402
```
 
## Submitting the solutions

* Form for submitting: https://courses.datatalks.club/de-zoomcamp-2024/homework/hw3

