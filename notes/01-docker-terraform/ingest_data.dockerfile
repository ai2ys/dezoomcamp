FROM python:3.11-slim-bookworm

RUN apt-get update && apt-get install -y \
    wget=1.21.3-1+b2 \
    && rm -rf /var/lib/apt/lists/*
RUN pip install --no-cache-dir \
    pandas \
    sqlalchemy \
    psycopg2

WORKDIR /app
COPY ingest_data.py .

CMD ["python", "ingest_data.py"]
