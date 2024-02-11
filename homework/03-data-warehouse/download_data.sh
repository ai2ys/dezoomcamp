#!/bin/bash
# Base URL
base_url="https://d37ci6vzurychx.cloudfront.net/trip-data/green_tripdata_2022"

# Loop over all months
for month in $(seq -w 12)
do
    # Construct the URL
    url="${base_url}-${month}.parquet"
    echo downloading "$url"
    # Download the file
    wget $url
done