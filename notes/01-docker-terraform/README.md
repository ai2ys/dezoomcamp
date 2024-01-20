# Docker + Postgres
The following can be executed using :octocat: GitHub Codespaces, the benefits are that the following tools are pre-installed:

- `Docker`
- `Docker-Compose`
- `Python` including `pip`
- `Jupyter` and `Jupyter Lab`

🐧 All instructions are for Linux based systems.

The commands assume that GitHub Codespaces is used and accessed from your local VS Code.

## Start container with postgres

Starting the Postgres container running the following commands in the terminal.

```bash
# change the working directory
cd notes/01-docker-terraform

# create folder 
mkdir -p ny_taxi_postgres_data

# run postgres container
docker run -it --rm \
    -e POSTGRES_USER="root" \
    -e POSTGRES_PASSWORD="root" \
    -e POSTGRES_DB="ny_taxi" \
    -v ./ny_taxi_postgres_data:/var/lib/postgresql/data \
    -p 5432:5432 \
    postgres:16
```

If this works successfully it the output in the terminal will say:

```bash
2024-01-16 09:41:27.446 UTC [1] LOG:  database system is ready to accept connections
```

## Connecting via `pgcli`

Open another terminal and run the following:

```bash
# install pgcli
pip install pgcli

# display help
pgcli --help

# connect to postgres
pgcli --host localhost --port 5432 --user root --dbname ny_taxi
# short version
pgcli -h localhost -p 5432 -u root -d ny_taxi
```

Starting and exiting `pgcli`:

```bash
$ pgcli -h localhost -p 5432 -u root -d ny_taxi
Password for root: 
Server: PostgreSQL 16.1 (Debian 16.1-1.pgdg120+1)
Version: 4.0.1
Home: http://pgcli.com
root@localhost:ny_taxi> exit
Goodbye!
```

Listing tables in the database, after having executed the notebook from the section below.

```bash
root@localhost:ny_taxi> \dt
+--------+------------------+-------+-------+
| Schema | Name             | Type  | Owner |
|--------+------------------+-------+-------|
| public | yellow_taxi_data | table | root  |
+--------+------------------+-------+-------+
SELECT 1
Time: 0.006s
```

## Downloading the dataset
The dataset used is the TLC Trip Record Data from the New York City Taxi & Limousine Commission. 

https://www.nyc.gov/site/tlc/about/tlc-trip-record-data.page

Downloading and unzipping the dataset.

```bash
wget -qO- https://github.com/DataTalksClub/nyc-tlc-data/releases/download/yellow/yellow_tripdata_2021-01.csv.gz | gunzip > yellow_tripdata_2021-01.csv
```

But `pandas` can also read `.gz` files directly. Therefore the following command is sufficient.

```bash
wget https://github.com/DataTalksClub/nyc-tlc-data/releases/download/yellow/yellow_tripdata_2021-01.csv.gz
```

## Ingesting data into Postgres  using Python (Jupyter Notebook)

Using GitHuh codespaces the Jupyter Notebook can immediately executed by opening it [upload_data.ipynb](upload_data.ipynb).

Required libraries:

- `pandas`
- `psycopg2` 
    - PostgreSQL database adapter
- `sqlalchemy`
    - SQLAlchemy is the Python SQL toolkit


## Connecting `pgAdmin` to `Postgres`

Instructions for running `pgAdmin` in a Docker container: 
[pgAdmin 4 (Container)](https://www.pgadmin.org/download/pgadmin-4-container/)

```bash
# create network
docker network create pg-network

# run postgres container, if not already running
docker run --rm -it \
    -e POSTGRES_USER="root" \
    -e POSTGRES_PASSWORD="root" \
    -e POSTGRES_DB="ny_taxi" \
    -v $(realpath ./ny_taxi_postgres_data):/var/lib/postgresql/data \
    -p 5432:5432 \
    --name pg-database \
    --network=pg-network \
    postgres:16

docker run --rm -it \
    -e PGADMIN_DEFAULT_EMAIL="admin@admin.com" \
    -e PGADMIN_DEFAULT_PASSWORD="root" \
    -p "8080:80" \
    --name pgadmin \
    --network=pg-network \
    dpage/pgadmin4:8.2

```

<!-- In GitHub Codespaces the port `8080` has to get added manually `PORTS` tab to the forwarded Ports.  After that I was able to click on the link in the field `Forwarded Address` of the `PORTS` tab.

Getting error when logging in to `pgAdmin`:
```bash
CSRFError: 400 Bad Request: The referrer does not match the host.
```

https://github.com/pgadmin-org/pgadmin4/issues/5432


- setting `PGADMIN_CONFIG_ENHANCED_COOKIE_PROTECTION="False"` did not help
- setting `PGADMIN_CONFIG_WTF_CSRF_ENABLED="False"` did help, but it not recommended

```bash
docker run --rm -it \
    -e PGADMIN_DEFAULT_EMAIL="admin@admin.com" \
    -e PGADMIN_DEFAULT_PASSWORD="root" \
    -e PGADMIN_CONFIG_WTF_CSRF_ENABLED="False" \
    -p "8080:80" \
    --name pgadmin \
    --network=pg-network \
    dpage/pgadmin4:8.2 
``` -->

### Connecting pgAdmin to database

Open `pgAdmin` in browser [http://127.0.0.1:8080](http://127.0.0.1:8080).

Right click on `Servers` and select `Servers > Register > Server`
- General
    - Name: "Docker localhost"
- Connection (*Fill in data from Docker Postgres container*)
    - Host name/address: "pg-database"
    - Port: "5432"
    - Username: "root"
    - Passwort: "root"

## Convert notebook to script

```bash
jupyter nbconvert --to=script upload_data.ipynb 
```

The clean up the notebook and rename it to [ingest_data.py](ingest_data.py). Later move it to a folder called [`ingest_data`](ingest_data).

Before testing the script drop the existing table in the database.

```sql
DROP TABLE IF EXISTS yellow_taxi_data;
```

Run script locally

```bash
python ./ingest_data/ingest_data.py \
    --user root \
    --password root \
    --host localhost \
    --port 5432 \
    --database ny_taxi \
    --table yellow_taxi_data \
    --url https://github.com/DataTalksClub/nyc-tlc-data/releases/download/yellow/yellow_tripdata_2021-01.csv.gz \
    --compression gzip \
    --chunksize 10000
```

Use Docker container for running the script

```bash
docker compose build
docker compose run --rm ingest_data
# optional, in case of shutting down the containers
docker compose down
```

Use http server for downloading dataset from local machine to Docker container

```bash
# terminal 1
python -m http.server 8000
```

```bash
## terminal 2
# "host.docker.internal" is the hostname that resolves to the internal IP address used by the host, for remote systems ifconfig has to be used to get the IP address

URL=http://host.docker.internal:8000/yellow_tripdata_2021-01.csv.gz \
docker compose run --rm ingest_data
```

## pgAdmin - persistency of configuration

:information_source: 
https://www.pgadmin.org/docs/pgadmin4/latest/container_deployment.html

* In case of issues with mounting a config folder check section "Mapped Files and Directories".

Create folder to be mapped to `/var/lib/pgadmin` in the container.

```bash
mkdir -p pgadmin_data
```

Mount folder to contaner directory `/var/lib/pgadmin` by adding the following to the `docker-compose.yml` file.

```yaml
    volumes:
      - ./pgadmin_data:/var/lib/pgadmin
``` 

```bash
sudo chown -R 5050:5050 pgadmin_data
```

## `pgcli` running in Docker container

```bash
$ docker run -it --rm --network pg-network ai2ys/dockerized-pgcli:4.0.1 
175dd47cda07:/# pgcli -h pg-database -U root -p 5432 -d ny_taxi
Password for root: 
Server: PostgreSQL 16.1 (Debian 16.1-1.pgdg120+1)
Version: 4.0.1
Home: http://pgcli.com
root@pg-database:ny_taxi> \dt
+--------+------------------+-------+-------+
| Schema | Name             | Type  | Owner |
|--------+------------------+-------+-------|
| public | yellow_taxi_data | table | root  |
+--------+------------------+-------+-------+
SELECT 1
Time: 0.009s
root@pg-database:ny_taxi>
```

Added `pgcli` service to [`docker-compose.yml`](docker-compose.yml). Will automatically connect to the database.

```bash
docker compose run --rm pgcli
```


## Trouble shooting with postgres container
https://stackoverflow.com/questions/56188573/permission-issue-with-postgresql-in-docker-container


https://hub.docker.com/_/postgres, section
"Arbitrary --user Notes"


---

# SQL Refresher

Downloading the zones lookup table and ingesting it into the database.

https://d37ci6vzurychx.cloudfront.net/misc/taxi+_zone_lookup.csv

Ingest zones to database

```bash
docker compose run --rm ingest_data_misc "python ingest_zones.py \
    --user root \
    --password root \
    --host postgres \
    --port 5432 \
    --database ny_taxi \
    --table taxi_zones \
    --url https://d37ci6vzurychx.cloudfront.net/misc/taxi+_zone_lookup.csv \
    --chunksize 10000"
```

## SQL queries

Select all rows from table `zones`.
```sql
SELECT
	*
FROM
	zones;
```

Select 10 rows from table `yellow_taxi_data`.
```sql
SELECT
	*
FROM
	yellow_taxi_data
LIMIT 10;
```

Displaying location string instead of location id.

```sql
SELECT
	*
FROM
    yellow_taxi_data t, 
	zones z
WHERE
	t."PULocationID" = z."LocationID" AND
	t."DOLocationID" = z."LocationID"
LIMIT 10;
```

Resulting in error:

```basERROR:  operator does not exist: text = bigint
LINE 7:  t."PULocationID" = z."LocationID" AND
                          ^
HINT:  No operator matches the given name and argument types. You might need to add explicit type casts. 

SQL state: 42883
Character: 74
```

Check for datatypes of columns `PULocationID` and `LocationID`.

```sql	
SELECT column_name, data_type
FROM information_schema.columns
WHERE table_name = 'yellow_taxi_data' AND column_name = 'PULocationID';
```

Add information for both tables into one query.

```sql
SELECT column_name, data_type
FROM information_schema.columns
WHERE table_name = 'zones' AND column_name = 'LocationID'
UNION ALL
SELECT column_name, data_type
FROM information_schema.columns
WHERE table_name = 'yellow_taxi_data' AND column_name = 'PULocationID';
```
Result
```text
column_name     | data_type
----------------+-----------
"LocationID"	"bigint"
"PULocationID"	"text"
```

Cast `PULocationID` to `bigint` in the query.

```sql
SELECT
    *
FROM
    yellow_taxi_data t, 
    zones zpu,
    zones zdo
WHERE
    t."PULocationID"::bigint = zpu."LocationID" AND
    t."DOLocationID"::bigint = zdo."LocationID"
LIMIT 10;
```
The result has a lot of columns, therefore only a few are selected.


The following query is equivalent to the one above, but only a few columns are selected.
Where the pickup and dropoff location are joined with the zones table. Additionally the columns `Borough` and `Zone` are concatenated.

```sql
SELECT
    tpep_pickup_datetime,
	tpep_dropoff_datetime,
	total_amount,
	CONCAT(zpu."Borough", zpu."Zone") AS "pu_loc",
	CONCAT(zdo."Borough", zdo."Zone") AS "do_loc"
FROM
    yellow_taxi_data t, 
    zones zpu,
	zones zdo
WHERE
    t."PULocationID"::bigint = zpu."LocationID" AND
    t."DOLocationID"::bigint = zdo."LocationID"
LIMIT 10;
```

Other kind of getting the same result. 

```sql
SELECT
    tpep_pickup_datetime,
	tpep_dropoff_datetime,
	total_amount,
	/* concat column values */
	CONCAT(zpu."Borough", ' - ', zpu."Zone") AS "pu_loc",
	CONCAT(zdo."Borough", ' - ', zdo."Zone") AS "do_loc"
FROM
	/* join tables */
    yellow_taxi_data t 
	JOIN zones zpu
		ON t."PULocationID"::bigint = zpu."LocationID"
	JOIN zones zdo
		ON t."DOLocationID"::bigint = zdo."LocationID"
LIMIT 10;

```
The difference is that the `WHERE` clause is replaced by `JOIN` clauses.
<!-- 
List columns that have `NULL` values with the number of `NULL` values.

```sql
SELECT
    column_name,
    data_type,
    COUNT(*) AS num_null
FROM
    information_schema.columns
WHERE
    table_name = 'yellow_taxi_data' AND
    is_nullable = 'YES'
GROUP BY
    column_name,
    data_type   
ORDER BY
    num_null DESC;
```

This query seems to have some flaws -->


Truncate (remove) time of `tpep_pickup_datetime` and `tpep_dropoff_datetime` columns.

```sql
SELECT
    tpep_pickup_datetime,
    tpep_dropoff_datetime,
--    /* truncate/remove time */
    DATE_TRUNC('day', tpep_pickup_datetime),
    total_amount
FROM
    yellow_taxi_data t
LIMIT 10;
```

```sql
SELECT DATA_TYPE
FROM INFORMATION_SCHEMA.COLUMNS
WHERE TABLE_NAME = 'yellow_taxi_data'
AND COLUMN_NAME = 'tpep_pickup_datetime';
```

```sql
SELECT
    tpep_pickup_datetime,
    tpep_dropoff_datetime,
--    /* cast as date */
    CAST(tpep_pickup_datetime AS DATE),
    total_amount
FROM
    yellow_taxi_data t
LIMIT 10;
```

Check how many entries have the same day
```sql
SELECT
    CAST(tpep_pickup_datetime AS DATE) as "day",
    COUNT(*)
FROM
    yellow_taxi_data t
GROUP BY
    CAST(tpep_pickup_datetime AS DATE)
ORDER BY
    "day" ASC;
```

Order by count
```sql
SELECT
    CAST(tpep_pickup_datetime AS DATE) as "day",
    COUNT(*) as "count"
FROM
    yellow_taxi_data t
GROUP BY
    CAST(tpep_pickup_datetime AS DATE)
ORDER BY
    "count" DESC;
```

Maximum total amount per day
```sql
SELECT
    CAST(tpep_pickup_datetime AS DATE) as "day",
    COUNT(*) as "count",
	MAX(total_amount) as "max"
FROM
    yellow_taxi_data t
GROUP BY
    CAST(tpep_pickup_datetime AS DATE)
ORDER BY
    "max" DESC;
```

---

# Terraform