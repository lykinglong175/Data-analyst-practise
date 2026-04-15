# E-commerce Data Pipeline

An end-to-end data pipeline for an e-commerce business, transforming raw transactional data into clean, tested, business-ready models — automated with Airflow and deployed to BigQuery.

## Architecture

```
Raw CSV Data (seeds)
      ↓
Staging Layer (dbt views)     ← clean & standardize fields
      ↓
Marts Layer (dbt tables)      ← business logic & aggregations
      ↓
BigQuery                      ← cloud data warehouse
      ↑
Airflow DAG                   ← daily automated scheduling
```

## Models

| Model | Type | Description |
|---|---|---|
| `stg_users` | View | Cleaned user data |
| `stg_orders` | View | Cleaned order data |
| `stg_products` | View | Cleaned product data with margin |
| `stg_order_items` | View | Cleaned order line items with subtotal |
| `dim_users` | Table | Customer order history & lifetime value |
| `dim_products` | Table | Product sales & profitability by status |
| `fct_order_items` | Incremental | Order line item facts with gross profit |

## Data Lineage

![Lineage Graph](images/lineage.png)

## BigQuery

![BigQuery](images/bigquery.png)

## Airflow DAG

![Airflow](images/airflow.png)

Daily pipeline: `dbt_seed → dbt_run → dbt_test`

## Data Quality

15 automated tests across all staging models:
- `unique` — no duplicate IDs
- `not_null` — no missing primary keys
- `relationships` — all foreign keys valid
- `accepted_values` — status fields validated

## Tech Stack

- **dbt** — data transformation & testing
- **BigQuery** — cloud data warehouse
- **Airflow** — pipeline orchestration
- **Docker** — containerized Airflow environment
- **DuckDB** — local development

## Quick Start

```bash
# Activate environment
venv\Scripts\activate.bat

# Run full pipeline
cd ecommerce_shop
dbt build

# Start Airflow
cd airflow
docker-compose up -d
```
