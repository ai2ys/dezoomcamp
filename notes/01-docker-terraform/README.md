# Docker + Postgres
The following can be executed using :octocat: GitHub Codespaces, the benefits are that the following tools are pre-installed:

- `Docker`
- `Docker-Compose`
- `Python` including `pip`
- `Jupyter` and `Jupyter Lab`

🐧 All instructions are for Linux based systems.

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

The clean up the notebook and rename it to [ingest_data.py](ingest_data.py).

Before testing the script drop the existing table in the database.

```sql
DROP TABLE IF EXISTS yellow_taxi_data;
```


```bash
python ingest_data.py \
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





