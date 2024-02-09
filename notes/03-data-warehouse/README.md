# 03 Data Warehouse

## 3.1.1 - Data Warehouse and BigQuery

🎞️ https://youtu.be/jrHljAoD6nM?si=_doAtu_tJ479RKWw

- Slides https://docs.google.com/presentation/d/1a3ZoBAXFk8-EhUsd7rAZd-5p_HpltkzSeujjRGB2TAI/edit?usp=sharing
- Big Query basic SQL https://github.com/DataTalksClub/data-engineering-zoomcamp/blob/main/03-data-warehouse/big_query.sql

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

- Serverless data warehouse
