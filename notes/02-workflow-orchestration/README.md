# 02 Workflow Orchrestration


## 2.2.1 What is Orchestration?

Mage & DE Zoomcamp - 🎞️ https://youtu.be/Li8-MWHhTbo?feature=shared

Slides: https://docs.google.com/presentation/d/17zSxG5Z-tidmgY-9l7Al1cPmz4Slh4VPK6o2sryFYvw/

![image_01.png](images/image_01.png)

### Architecture
- Extract &rarr; Pluss data from source
- Transform &rarr; Data cleaning, transformation & partitioning
- Load &rarr; API to Mage, Mage to Postgres, GCS, BigQuery


### What is Orchestration?

- Large part of data engineering is extracting, transforming, and laoding data between sources
- Orchestration is the process of automating these steps
- Data orchestrator manages scheduling, trigering, and monitoring and resource allocation


> - Every workflow requires sequential steps
> - Steps are tasks
> - Workflows are DAGs (directed acyclic graphs)

Book: 
Fundamentals of Data Engineering: Plan and Build Robust Data Systems

### What is a good orchestrator/solution?

- Orchestrator handles workflow management
    - Execute tasks in the right order
    - Manage dependencies
    - ...

- Automation
- Error handling & recovery
    - Retrying failed tasks
    - ...
- Recovery
    - Back fill missing data
    - Recover lost data
- Monitoring, alerting
    - Notification
- Resource optimization
- Oberservability
    - Debugging, etc.
- Compliance/Auditing


## 2.2.2 What is Mage?

🎞️ https://youtu.be/AicKRcK3pa4?si=ji4r2laIWX14K3b_

Resources



Slides: https://docs.google.com/presentation/d/1y_5p3sxr6Xh1RqE6N8o2280gUzAdiic2hPhYUUD6l88/


- Mage - Open Source pipeline tool for orchestrating, tracking, and integrating data
- Projects consist of pipelines (DAGs), each pipeline consists of blocks (tasks), blocks are usually used to load, transform, or export data
- Unique blocks of Mage are:
    - Sensors (trigger on events)
    - Conditionals (branching logic, if-else logic, ...)
    - Dynamics (can create dynamic children)
    - Webhooks
    - Data Integration
    - Unified Pipelines
    - Multi-user envs
    - Templating
    - ...


Mage 
- Hybrid environment
    - GUI or pure code
    - Block are testable, reusable pieces of code


![images/image_02.png](images/image_02.png)

- Mage instance has 1 or more projects
- Each project has 1 or more pipelines
- Each pipeline has 1 or more blocks


Pipelines
- Workflows (DAGs) that execute data operations
- Represented by YAML files

Blocks
- Files (Python, SQL, R, ...) that can be executed independently or within a pipeline
- Reusable, atomic pieces of code performing a specific task
- A block is a file &rarr; changing the file changes the block everywhere it is used

Block anatomy
- Imports
- Decorator (e.g. data loader)
- Function (returning a dataframe)
    - Block have to return a dataframe
    - Only this part gets executed when the block is run
- Assertion (or test)


## 2.2.2 - Configure Mage

🎞️ https://youtu.be/2SV-av3L3-k?si=PC_f5RrWtqsTWAK9

Setting up MAGE using GitHub repo (getting started): https://github.com/mage-ai/mage-zoomcamp

- Branch `solution` contains solution: https://github.com/mage-ai/mage-zoomcamp/tree/solutions

1. Rename `dev.env` to `.env`
    - `dev.env` is a template for the `.env` file
    - `.env` might contain secrets and is not committed to GitHub (in `.gitignore`)
1. Build image `docker-compose build`
1. Run image `docker-compose up`
1. Open [http://localhost:6789 ]( http://localhost:6789 )



## 2.2.2 - A Simple Pipeline

🎞️ https://youtu.be/stI-gg4QBnI?si=jV5xtnW5Fsu0rcBD

- Create a new pipeline &rarr; `+ New pipeline` (top left) will create new pipeline
- 
- `Pipelines` overview page, select `Pipelines` in sidebar &rarr; overview of all pipelines


## 2.2.3 - Configuring Postgres

🎞️ https://youtu.be/pmhI-ezd3BE?si=PqzUfN7WaJYjAG7s

Using Docker compose file
- service "magic" (MAGE image)
- service "postgres" (Postgres image)

Mage instance 
1. Select `Files` from the sidebar
1. Open `io_config.yml`
    - Manages connections
    - Contains `default` connection
    - Own connection profiles can get specified in Mage by adding a profile to the file (similar to `default`)
    - Example `dev` profile
        - We have to "pull in" environment variables from the `.env` file using "ginger templating" for interpolating the environment variables
            ```yaml
            dev:
              # PostgresSQL
              POSTGRES_CONNECT_TIMEOUT: 10
              POSTGRES_DBNAME: {{ env_var('POSTGRES_DBNAME') }}
              POSTGRES_SCHEMA: {{ env_var('POSTGRES_SCHEMA') }} # Optional
              POSTGRES_USER: {{ env_var('POSTGRES_USER') }}
              POSTGRES_PASSWORD: {{ env_var('POSTGRES_PASSWORD') }}
              POSTGRES_HOST: {{ env_var('POSTGRES_HOST') }}
              POSTGRES_PORT: {{ env_var('POSTGRES_PORT') }}        
            ```
        
Test Postgres connection
1. Create new pipeline - Standard (batch)
1. Select `Edit > Pipeline settings` and change pipeline name to `test_config` then click `Save pipeline settings`
1. Select `Edit pipeline` from sidebar
1. Select `+ Data loader > SQL` and name it `test_postgres`
    - Specify `Connection ` as `PostgreSQL` (dropdown menu)
    - Specify `Profile` as `dev` (dropdown menu) 
    - Select `Use raw SQL` (checkbox) &rarr; not Mage but Postgres will run the SQL command
        ```SQL
        SELECT 1;
        ```
    - Click ▶️ button or `CTRL+Enter`, output should look like this
        ```text
        Postgres initialized
        └─ Opening connection to PostgreSQL database...DONE/usr/local/lib/python3.10/site-packages/mage_ai/io/sql.py:167: UserWarning: pandas only supports SQLAlchemy connectable (engine/connection) or database string URI or sqlite3 DBAPI2 connection. Other DBAPI2 objects are not tested. Please consider using SQLAlchemy.
          return read_sql(query, self.conn)
        ```
        

## 2.2.3 ETL: API to Postgres

🎞️ https://youtu.be/Maidfe7oKLs?si=stM0mvV3yj0dFmXL

**Loading data from an API (compressed CSV file) to Postgres DB.**

1. Create new Batch pipeline `+ New > Standard (batch)`
1. `Edit > pipeline settings` and rename it to `api_to_postgres` and click `Save pipeline settings`
1. Go to `Edit pipeline` from sidebar
1. Select `+ Data loader > Python > API` and rename `load_api_data` and click `Save and add`
1. Set variable in Python script `load_data_from_api` method and declare data types
    ```python
    url = 'https://github.com/DataTalksClub/nyc-tlc-data/releases/download/yellow/yellow_tripdata_2021-01.csv.gz'

    # reduces memory usage in pandas
    taxi_dtypes = {
        'VendorID': pd.Int64Dtype(),
        'passenger_count': pd.Int64Dtype(),
        'trip_distance': float,
        'RatecodeID':pd.Int64Dtype(),
        'store_and_fwd_flag':str,
        'PULocationID':pd.Int64Dtype(),
        'DOLocationID':pd.Int64Dtype(),
        'payment_type': pd.Int64Dtype(),
        'fare_amount': float,
        'extra':float,
        'mta_tax':float,
        'tip_amount':float,
        'tolls_amount':float,
        'improvement_surcharge':float,
        'total_amount':float,
        'congestion_surcharge':float
    }
    return pd.read_csv(
        url, sep=',', compression='gzip', dtype=taxi_dtypes, 
        parse_dates=['tpep_pickup_datetime', 'tpep_dropoff_datetime'])
    ```
    ```
    > Remark: Data types have to get mapped, this reduces memory usage in pandas. Additionally if data types change this will cause the pipeline to fail which is good in that case.
1. Click ▶️ button or `CTRL+Enter` for execution

**Add transformation block**

1. Select `+ Transformation > Python > Generic (no template)` and rename it to `transform_taxi_data` (button below code block from previous block) then click `Save and add`
1. Drop columns with 'passenger_count == 0' by editing `transform` method
    ```python
    indices = data['passenger_count']>0
    num_rows_zero_passengers = data['passenger_count'].eq(0).sum()
    print("Num rows with zero passengers:", num_rows_zero_passengers)
    return data[indices]
    ```
1. Add assertion to the block (can have multiple assertions)
    ```python
    @test
    def test_output(output, *args) -> None:
        assert output['passenger_count'].eq(0).sum() == 0, 'There are rows with zero passengers'
    ```
1. Export the data (Python or SQL, here Python), select `+ Data exporter > Python > PostgreSQL`, rename it to `taxi_data_to_postgres` and click `Save and add`
1. In Block define in method `export_data_to_postgres` and replace the dataset if it exits
    ```python	
    schema_name = 'ny_taxi'         # modified
    table_name = 'yellow_cab_data'  # modified
    config_profile = 'dev'          # modified
    config_path = path.join(get_repo_path(), 'io_config.yaml')

    with Postgres.with_config(ConfigFileLoader(config_path, config_profile)) as loader:
        loader.export(
            df,
            schema_name,
            table_name,
            index=False,  # Specifies whether to include index in exported table
            if_exists='replace',  # Specify resolution policy if table name already exists
        )
    ```
1. Click ▶️ button or `CTRL+Enter` for execution
1. Check if export works by adding SQL dataloader block `+ Data loader > SQL` and rename it to `load_taxi_data` and click `Save and add`
1. Select `Connection` as `PostgreSQL` and `Profile` as `dev` and `Use raw SQL` and add the following SQL command
    ```SQL
    SELECT * FROM ny_taxi.yellow_cab_data LIMIT 10;
    ```
1. Click ▶️ button or `CTRL+Enter` for execution
