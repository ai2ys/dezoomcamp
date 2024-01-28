# Information

Crourse notes from course peer of previous cohort:
https://github.com/ziritrion/dataeng-zoomcamp/blob/main/notes/1_intro.md

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

# GCP setup

🎞️ https://youtu.be/ae-CV2KfoN0?feature=shared

Select from the menu `Navigation menu > Compute Engine > VM instances`. Currently no instances are running.

Create SSH key pair to be able to connect.
Instructions using e.g. Git Bash on Windows.

Documentation from GCP
- https://cloud.google.com/compute/docs/connect/create-ssh-keys
- https://cloud.google.com/compute/docs/connect/add-ssh-keys
- https://cloud.google.com/compute/docs/connect/restrict-ssh-keys
- https://cloud.google.com/compute/docs/connect/standard-ssh#provide-key

```bash
cd ~/.ssh
ssh-keygen -t rsa -f ~/.ssh/KEY_FILENAME -C USERNAME -b 2048
# output of public key
cat ~/.ssh/KEY_FILENAME
# copy public key to clipboard
```

Add **public** (*.pub) key to GCP, from the navigation menu select `Metadata > SSH Keys > Edit > Add SSH key` or `+ ADD ITEM`, if a key has already been added earlier.

From navigation menu select `Compute Engine > VM instances` then select from the `VM instances` menu bar `CREATE INSTANCE` (might be hidden behind `...`).

Specify
- Name
- Region
- Zone
- Machine type (e.g. e2-standard-4, 4 CPUs, 16GB RAM)
Estimation of cost per month and hour.

Boot disk section > Public Images
- Operating system (Ubuntu)
- Version
- Boot disk type (unchanged, balanced persistent disk)
- Size (30 GB)


Creation of VM instances via `gcloud` command line tool, instruction can be found in the documentation `Equivalent Command Line`.

Next to this Click on `Create` for creating the instance.

Check `External IP` (use copy button).

```bash	
ssh -i ~/.ssh/KEY_FILENAME USERNAME@EXTERNAL_IP
```
(`CTRL+D` to logout)

Configuring instance
- Install Miniconda (including init)
    ```bash
    mkdir -p ~/miniconda3
    wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh \
        -O ~/miniconda3/miniconda.sh
    bash ~/miniconda3/miniconda.sh -b -u -p ~/miniconda3
    rm -rf ~/miniconda3/miniconda.sh    
    # init
    ~/miniconda3/bin/conda init bash
    # without logout
    source ~/.bashrc
    ```
- Install Docker (?apt-get install docker.io)
    ```bash
    sudo su
    # Add Docker's official GPG key:
    apt-get update
    apt-get install ca-certificates curl
    install -m 0755 -d /etc/apt/keyrings
    curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc
    chmod a+r /etc/apt/keyrings/docker.asc

    # Add the repository to Apt sources:
    echo \
    "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/ubuntu \
    $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | \
    tee /etc/apt/sources.list.d/docker.list > /dev/null
    apt-get update

    apt-get install docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

    # check installation
    docker run --rm hello-world
    groupadd docker
    # exit su
    exit

    # add standard user to docker group 
    sudo usermod -aG docker $USER
    # logout/login required or reboot in case of VM
    docker run --rm hello-world
    ```
- JupyterLab
    ```bash
    pip install jupyterlab
    ```
- Terraform
    ```bash
    wget -O- https://apt.releases.hashicorp.com/gpg | sudo gpg --dearmor -o /usr/share/keyrings/hashicorp-archive-keyring.gpg
    echo "deb [signed-by=/usr/share/keyrings/hashicorp-archive-keyring.gpg] https://apt.releases.hashicorp.com $(lsb_release -cs) main" | sudo tee /etc/apt/sources.list.d/hashicorp.list
    sudo apt update && sudo apt install terraform
    ```

---

## Creating SSH config file on local PC for GCP
```bash
touch ~/.ssh/config
```

File content
```text
Host dezoomcamp-gcp
    HostName EXTERNAL_IP
    User USERNAME
    IdentityFile ~/.ssh/KEY_FILENAME
```

Connect using the SSH config file
```bash
ssh dezoomcamp-gcp
```

## Accessing GCP in VSCode

Install extensions
- Remote - SSH
- Remote - Containers

## Port forwarding from GCP to local machine

VSCode window connected to GCP via SSH (see indicator at the bottom left in VSCode window).
From the Ports tab select `Forward a Port` and enter port number.

## Setup GCP service account
Explained in other video (https://youtu.be/Y2ux7gq3Z0o?feature=shared).

Select `Navigation menu > IAM & Admin > Service Accounts` then click on `+ Create Service Account`.

1. Service account details
    - Set service account name: "terraform-runner"
    - Click `Create and Continue`.

2. Select role
    - `Cloud Storage > Storage Admin`
    - `+ Add another role`
        - `BigQuery > BigQuery Admin`
    - `+ dd another role`
        - ``

Click `Continue` and `Done`.

Click '...' (vertical dots) on account and select `Manage keys`.

- Click `Add Key > Create new key` and select `JSON`.

The JSON key file gets downloaded (and must never be shared!!!).

Moving it to the user directory in WSL2.

```bash
mv /mnt/c/<username>/Downloads/<key file>.json ~/my-creds.jsom
chmod 600 my-creds.json
```

Update service account with new permissions. Click `IAM` then go to service account and click edit (🖊️.) 


Install VSCode extension for Terraform.

## Transfer service account credentials

Transfering JSON file using `sftp`.

```bash
# connect to gcp VM
sftp dezoomcamp-gcp
# make directory
mkdir .gc
cd .gc
put my-creds.json ny-rides.json
```

Configure Google Cloud `cli`.

```bash
export GOOGLE_APPLICATION_CREDENTIALS=~/.gc/ny-rides.json
gcloud auth activate-service-account --key-file $GOOGLE_APPLICATION_CREDENTIALS
```

The section below could not be executed at the current stage. In case the directory contains Terraform files (*.tf).

Run `terraform init` and after that `terraform plan` and than `terraform apply`.

## Shutdown GCP VM

From terminal

```bash
sudo shutdown now
```

From GCP dashboard select `Compute Engine > VM instances` select the `...` (vertical dots) on the instance and select `Stop`.



---

# Terraform

❓ Why Terraform is useful
- Simplicity in keeping track of infrastructure
- Easier collaboration
- Reproducibility
- Ensure resources are removed

❗What Terraform is not
- No management or updating of code on infrastructure
- No ability to change immutable resources
- No management of resources defined outside of Terraform files

ℹ️ Terraform is
Infrastructure as Code (IaC)
- "Make resources with code files"

## Introduction to Terraform


List of Terraform providers:
https://registry.terraform.io/browse/providers


Terraform will connect to the cloud provider chosen.

- Local Machine
    - Terraform
- Cloud Provider
    - AWS
    - Azure
    - GCP
    - ...

Authorization is needed for Terraform to connect to the cloud provider.

### Key Terraform commands

- `Init` - get me providers I need
- `Plan` - what am I about to do
    - Show me the resources that will get created
- `Apply` - Do what is in the `*.tf` files
- `Destroy` - Destroy all resources defined in the `*.tf` files

### Setup service account on GCP

Service accounts are never meant to login to.



### Terraform on local PC


