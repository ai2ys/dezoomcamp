# 04 Analytics engineering

Course note created by course peer of previous cohorts:
🗒️<https://github.com/ziritrion/dataeng-zoomcamp/blob/c4447687719f76ca04cedfcc1ac8f8ad23eb0cde/notes/4_analytics.md> 

## dbt(Data Build Tool) crash course for beginners: Zero to Hero

🎞️ <https://youtu.be/C6BNAfaeqXY?feature=shared> (other resource outside of course)

Docker images for dbt: https://github.com/dbt-labs/dbt-core/pkgs/container/dbt-core


![](./images/001_dbt_overview.png)

Supported data plattforms by dbt: <https://docs.getdbt.com/docs/supported-data-platforms>

`dbt` key concepts:
- Models (SQL statements)
    - Defined in `.sql` files
    - Can reference other models or tables in data warehouse
    - Model names are the file names
- Macros
    - Simplifying reusing SQL code fragments across models
- Tests (two primary ways of defining dbt tests)
    - Generic
        - Out of the box tests that can be applied across multiple data models
    - Singular
        - Custom tests are for a specific model
- Snapshots
    - Track changes in data over time

### dbt Cloud and BigQuery

Prerequisites:

- dbt Cloud Account
- GCP Account
- GCP Project
- BigQuery set up
- Github account

#### dbt Cloud Account

1. Got to <https://www.getdbt.com/> and create an account.
1. Log in to dbt Cloud and create a new project
    - With the free account there is a default project and it is not possible to create a new one.
1. Select connection, here BigQuery
1. Add service account `JSON` file
    - How to get service account `JSON`
        1. Go to GCP console
        1. Go to `IAM & Admin` > `Service accounts`
        1. Click `Create service account` and name it (e.g. `dbt-service-account`) and add role (here `Owner`, but should get restricted permissions in production environment)
        1. After creation click on the account and select the `KEYS` tab and select `ADD KEY 🔽 > Create new key` then select `JSON`
    - Upload downloaded `JSON` file to dbt Cloud using `Upload a Service Account JSON file`, this will fill in fields automatically
1. Development credentials
    - Specified `Dataset` name will be used in BigQuery, this dataset name will be used in the further up specified project name in BigQuery
1. Click `Test connection`
1. Click `Next`
1. Link code repository to dbt Cloud
    - Select `Github` and authorize dbt Cloud to access the repository



    
## In general instructions

<https://github.com/DataTalksClub/data-engineering-zoomcamp/tree/main/04-analytics-engineering>



## 4.1.1 - Analytics Engineering

🎞️ <https://youtu.be/uF76d5EmdtU?feature=shared>

## 4.1.2 - What is dbt?

🎞️ <https://youtu.be/gsKuETFJr54?feature=shared>

## 4.2.1 - 4.2.1 - Start Your dbt Project BigQuery and dbt Cloud (Alternative A)

🎞️ <https://youtu.be/J0XCDyKiU64?feature=shared>

DBT project can get created in a subdiretory of the GitHub repository, this can get specified in `Project details > Project subdirectory` in dbt cloud.
DBT will be on the default branch of the repository in `read-only` mode, to allow dbt cloud to make changes creating a new branch from dbt cloud is necessary.
In the project settings `Setup a repository` access can be granted to a specific repository. Furthermore a sub directory can be specified.

From the menu in the dbt cloud select `Develop 🔽 > Cloud IDE` 

- There will be an error message regarding a missing environment. Create it as development and do not specify a branch.
- In GitHub create a new branch, e.g. `dev-dbt`
- Click again on `Develop 🔽 > Cloud IDE` 
- Change the branch to the newly created branch `dev-dbt`
- Initialize the project and then commit the changes
- In the `dbt_project.yml` edit the name and model and remove the indicated `models` section below
     ```yml
    name: 'taxi_rides_ny'
    # ...
    models:
        taxi_rides_ny:
            # delete everything here
    ```
- In the command bar (bottom) run `dbt build` (there is an error message, but it seems not relevant at the moment, also ignored in the video)
- Commit changes

## 4.2.2 Start Your dbt Project: Postgres and dbt Core Locally (Alternative B)

### Additional resources

- dbt with BigQuery on Docker<br>
<https://github.com/DataTalksClub/data-engineering-zoomcamp/blob/main/04-analytics-engineering/docker_setup/README.md>
<br>or<br>
<https://docs.getdbt.com/docs/core/docker-install>

- dbt with Docker<br>
<https://docs.getdbt.com/docs/core/docker-install>

- dbt with BigQuery on Docker<br>
    - <https://github.com/dbt-labs/dbt-bigquery/pkgs/container/dbt-bigquery>

### Steps accompished

1. Create [docker-compose.yml](./docker-compose.yml) file using the BigQuery image
1. Created `profiles.yml` file in the `~/.dbt` directory using the following template <https://docs.getdbt.com/docs/core/connect-data-platform/bigquery-setup#service-account-file>
    ```yml	
    bq-dbt-workshop:
        target: dev
        outputs:
            dev:
                type: bigquery
                method: service-account
                project: <GCP_PROJECT_ID>
                dataset: <DBT_DATASET_NAME>
                threads: 4 # Must be a value of 1 or greater
                keyfile: /.gcp/credentials/gcp_bigquery.json
                # additional settings provided by dezoomcamp
                location: EU
                priority: interactive
                timeout_seconds: 300
                fixed_retries: 1
    ```
1. Run `docker compose ...` to start the dbt container
    ```bash
    docker compose run dbt-bigquery init --profile "bq-dbt-workshop"
    # Enter a name for your project (letters, digits, underscore): ny_taxi_rides_docker

    # Test connection, should output "All checks passed!"
    docker compose run --workdir="/usr/app/dbt/ny_taxi_rides_docker" dbt-bigquery
 debug
    ```

🎞️ <https://youtu.be/1HmL63e-vRs?feature=shared>

## 4.3.1 - Build the First dbt Models

🎞️<https://youtu.be/ueVy2N54lyc?feature=shared>


### General information

#### Modual data modeling structure

1. Tables that we loaded (sources)
1. Models that we build (transformations like cleaning, deduplication, etc.)

#### Materializations in dbt Cloud

- Ephemeral materializations (temporary, only exist for duration of a single dbt run)
- View (virtual table, that can be queried like a table)
- Table (physical table in the database)
- Incremental materializations (efficient updates to existing tables, reducing the need for full data refreshes)

#### `FROM` clause of a dbt model

- Sources - data loaded to our data warehouse
- Seeds - CSV files in `seeds` directory
- Ref - macro to reference underlying tables and views (dependencies are built automatically)


### Prerequsites

- 🎞️ <https://youtu.be/Mork172sK_c?feature=shared>
- Use public dataset available in `BigQuery` <https://console.cloud.google.com/marketplace/product/city-of-new-york/nyc-tlc-trips>
    - Click `View dataset`
    - Got to ny_your_taxi_trips` and for one of the required datasets click `... > Query`
        ```sql
        SELECT * FROM `bigquery-public-data.new_york_taxi_trips.tlc_green_trips_2019` LIMIT 10 
        ```
        - `bigquery-public-data.new_york_taxi_trips.tlc_green_trips_2019`
        - `bigquery-public-data.new_york_taxi_trips.tlc_green_trips_2020`
        - `bigquery-public-data.new_york_taxi_trips.tlc_yellow_trips_2019`
        - `bigquery-public-data.new_york_taxi_trips.tlc_yellow_trips_2020`
    - Go to own account (top in the Explorer) and create a dataset `trips_data_all` (use same name as defined in schema in schema.yml), select multi region `US` as region (will not work with `EU` region because of location of the public dataset)
    - Create a query `+`
        ```sql
        CREATE TABLE `dezoomcamp-module-4.trips_data_all.green_tripdata` AS
        SELECT * FROM `bigquery-public-data.new_york_taxi_trips.tlc_green_trips_2019`;

        CREATE TABLE `dezoomcamp-module-4.trips_data_all.yellow_tripdata` AS
        SELECT * FROM `bigquery-public-data.new_york_taxi_trips.tlc_yellow_trips_2019`;

        INSERT INTO `dezoomcamp-module-4.trips_data_all.green_tripdata` 
        SELECT * FROM `bigquery-public-data.new_york_taxi_trips.tlc_green_trips_2020`;

        INSERT INTO `dezoomcamp-module-4.trips_data_all.yellow_tripdata`
        SELECT * FROM `bigquery-public-data.new_york_taxi_trips.tlc_yellow_trips_2020`;

        -- Fixes yellow table schema
        ALTER TABLE `dezoomcamp-module-4.trips_data_all.yellow_tripdata`
        RENAME COLUMN vendor_id TO VendorID;
        ALTER TABLE `dezoomcamp-module-4.trips_data_all.yellow_tripdata`
        RENAME COLUMN pickup_datetime TO tpep_pickup_datetime;
        ALTER TABLE `dezoomcamp-module-4.trips_data_all.yellow_tripdata`
        RENAME COLUMN dropoff_datetime TO tpep_dropoff_datetime;
        ALTER TABLE `dezoomcamp-module-4.trips_data_all.yellow_tripdata`
        RENAME COLUMN rate_code TO RatecodeID;
        ALTER TABLE `dezoomcamp-module-4.trips_data_all.yellow_tripdata`
        RENAME COLUMN imp_surcharge TO improvement_surcharge;
        ALTER TABLE `dezoomcamp-module-4.trips_data_all.yellow_tripdata`
        RENAME COLUMN pickup_location_id TO PULocationID;
        ALTER TABLE `dezoomcamp-module-4.trips_data_all.yellow_tripdata`
        RENAME COLUMN dropoff_location_id TO DOLocationID;

        -- Fixes green table schema
        ALTER TABLE `dezoomcamp-module-4.trips_data_all.green_tripdata`
        RENAME COLUMN vendor_id TO VendorID;
        ALTER TABLE `dezoomcamp-module-4.trips_data_all.green_tripdata`
        RENAME COLUMN pickup_datetime TO lpep_pickup_datetime;
        ALTER TABLE `dezoomcamp-module-4.trips_data_all.green_tripdata`
        RENAME COLUMN dropoff_datetime TO lpep_dropoff_datetime;
        ALTER TABLE `dezoomcamp-module-4.trips_data_all.green_tripdata`
        RENAME COLUMN rate_code TO RatecodeID;
        ALTER TABLE `dezoomcamp-module-4.trips_data_all.green_tripdata`
        RENAME COLUMN imp_surcharge TO improvement_surcharge;
        ALTER TABLE `dezoomcamp-module-4.trips_data_all.green_tripdata`
        RENAME COLUMN pickup_location_id TO PULocationID;
        ALTER TABLE `dezoomcamp-module-4.trips_data_all.green_tripdata`
        RENAME COLUMN dropoff_location_id TO DOLocationID;
        ```
        Note: do not run all at once because of quota limitations, only run a few at one time.


### Starting - defining the schema
Go to dbt Cloud project in IDE

- Open `dbt_project.yml` already prepared in the previous steps (alternative A)
- Create folder `models/staging` (initial layer of the models that are cleaning the source data)
- Create file `models/staging/schema.yml`

    ```yaml
    # schema.yml
    version: 2
    sources:
        - name: staging
        database: <your_project> # e.g. bigquery (top level name in bigquery resources for the project)
        schema: trips_data_all # schema is one level below the database name

        tables:
            - name: green_tripdata
            - name: yellow_tripdata
    ```

- In editor click on `Generate model` hint above `green_tripdata` in schema. Save it as `models/staging/stg_green_tripdata.sql`.

- Now run `dbt build` (command bar bottom left), but delete the `models/examples` folder as this will cause an error.


### Macros

- Macros are `Jinja` code that can be reused, see <https://en.wikipedia.org/wiki/Jinja_(template_engine)>
- Jinja delimiters:
    - {% ... %} for statements (control blocks, macro definitions)
    - {{ ... }} for expressions (literals, math, comparisons, logic, macro calls...)
    - {# ... #} for comments.

- Create file `macros/get_payment_type_description.sql` 
    ```jinja
    {#
        This macro returns the description of the payment_type 
    #}

    {% macro get_payment_type_description(payment_type) -%}

        case {{ dbt.safe_cast("payment_type", api.Column.translate_type("integer")) }}  
            when 1 then 'Credit card'
            when 2 then 'Cash'
            when 3 then 'No charge'
            when 4 then 'Dispute'
            when 5 then 'Unknown'
            when 6 then 'Voided trip'
            else 'EMPTY'
        end

    {%- endmacro %}
    ```
### Packages

- Comparable to libraries in other programming languages
- Standalone dbt projects for specific problems
- When adding a package to a project, all parts of the projects (models and macros) become part ot the project
- Imported in `packages.yml` file and installed with `dbt deps` command
- [dbt package hub](https://hub.getdbt.com/) list of useful packages
- Creating a package (go to the IDE) and create a `packages.yml` file at the same level as `dbt_project.yml` and add the following content
    ```yml
    packages:
      - package: dbt-labs/dbt_utils
        version: 1.1.1
    ```	
    Run `dbt deps` in the command bar (bottom left) to install the package (will usually run automatically when the file is saved or at login). The command will also install the dependencies of the package. Installed packages will be located in the `dbt_packages` directory.
    ```sql
    -- Can be used similar to functions in python <package_name.function>
    -- e.g. select statement of stg_green_tripdata.sql
    select
        {{ dbt_utils.surrogate_key(['vendorid', 'lpep_pickup_datetime']) }} as tripid,
        cast(vendorid as integer) as vendorid,
        -- ... other columns and rest of the query
    ```

> **Note**:
>
> - In `BigQuery` click refresh on the database to see what has changed under `dbt_<username>`  
>
> - `Compile` can be used instead of `Build` to see how the SQL code will look like after the Jinja code has been processed without actually running the code.
>
> - Under the `target` directory in the `dbt` project it can be seen what has already been running. 

### Variables

- Variables can be used across the project
- Variables can be used by using the `{{ var('...') }}` function
- 2 options for defining variables
    - `dbt_project.yml` file
        ```yml
        vars:
            payment_type_values: [1, 2, 3, 4, 5, 6]
        ```
    - command line argument
        ```bash
        dbt build --m <your-model.sql> --var 'is_test_run: false'
        ```
        Will override the default value
        ```sql
        -- dbt build --m <your-model.sql> --var 'is_test_run: false'
        {% if var('is_test_run', default=true) %}

            limit 100

        {% endif %}
        ```
        Multiple variables can be set at once using the `--vars` flag passing a dictionary of variables
        ```bash
        dbt run --vars '{ 'is_test_run': 'false' }'
        ```
> **Note**:
>
> - Useful to limit the number of rows in the development environment (cheaper and faster)

### ?

- Create folder `models/core`
- Create a master data table
    - Create file `models/core/dim_zones.sql`
    - Using seeds mentioned before adding the CSV file `seeds/taxi_zone_lookup.csv` and `build`
    - Adding the following to `seeds/seeds_properties.yml` (create it if it does not exist)
        ```yml
        version: 2

        seeds: 
        - name: taxi_zone_lookup
            description: >
            Taxi Zones roughly based on NYC Department of City Planning's Neighborhood
            Tabulation Areas (NTAs) and are meant to approximate neighborhoods, so you can see which
            neighborhood a passenger was picked up in, and which neighborhood they were dropped off in. 
            Includes associated service_zone (EWR, Boro Zone, Yellow Zone)
        ```
    - Adding `models/core/dim_zones.sql`
        ```sql
        select 
            locationid, 
            borough, 
            zone, 
            replace(service_zone,'Boro','Green') as service_zone
        from {{ ref('taxi_zone_lookup') }}
        ```
    - Adding ``models/core/fact_trips.sql (put yellow and green trips together), should be a table (more performant)
        ```sql
        {{
            config(
                materialized='table'
            )
        }}

        with green_tripdata as (
            select *, 
                'Green' as service_type
            from {{ ref('stg_green_tripdata') }}
        ), 
        yellow_tripdata as (
            select *, 
                'Yellow' as service_type
            from {{ ref('stg_yellow_tripdata') }}
        ), 
        trips_unioned as (
            select * from green_tripdata
            union all 
            select * from yellow_tripdata
        ), 
        dim_zones as (
            select * from {{ ref('dim_zones') }}
            where borough != 'Unknown'
        )
        select trips_unioned.tripid, 
            trips_unioned.vendorid, 
            trips_unioned.service_type,
            trips_unioned.ratecodeid, 
            trips_unioned.pickup_locationid, 
            pickup_zone.borough as pickup_borough, 
            pickup_zone.zone as pickup_zone, 
            trips_unioned.dropoff_locationid,
            dropoff_zone.borough as dropoff_borough, 
            dropoff_zone.zone as dropoff_zone,  
            trips_unioned.pickup_datetime, 
            trips_unioned.dropoff_datetime, 
            trips_unioned.store_and_fwd_flag, 
            trips_unioned.passenger_count, 
            trips_unioned.trip_distance, 
            trips_unioned.trip_type, 
            trips_unioned.fare_amount, 
            trips_unioned.extra, 
            trips_unioned.mta_tax, 
            trips_unioned.tip_amount, 
            trips_unioned.tolls_amount, 
            trips_unioned.ehail_fee, 
            trips_unioned.improvement_surcharge, 
            trips_unioned.total_amount, 
            trips_unioned.payment_type, 
            trips_unioned.payment_type_description
        from trips_unioned
        inner join dim_zones as pickup_zone
        on trips_unioned.pickup_locationid = pickup_zone.locationid
        inner join dim_zones as dropoff_zone
        on trips_unioned.dropoff_locationid = dropoff_zone.locationid
        ```
        Apply command `Build 🔽 > Build+model (Up/downsteam)

⚠️ dbt build failed

Video at 53:20
https://youtu.be/ueVy2N54lyc?list=PLaNLNpjZpzwgneiI-Gl8df8GCsPYp_6Bs&t=3200

## 4.3.2 