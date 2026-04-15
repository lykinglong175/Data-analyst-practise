from airflow import DAG
from airflow.operators.bash import BashOperator
from datetime import datetime, timedelta
import os
DBT_PROJ_DIR = os.getenv('DBT_PROJ_DIR', '/opt/airflow/dbt/ecommerce_shop/')

default_args = {
    'owner': 'yelan',
    'retries': 3,
    'retry_delay': timedelta(minutes=5),
}

with DAG(
    'dbt_ecommerce_shop',
    default_args=default_args,
    description='A DAG to run dbt models for e-commerce data',
    schedule_interval=timedelta(days=1),
    start_date=datetime(2024, 6, 1),
    catchup=False,
    tags=['dbt', 'ecommerce']

) as dag:

    dbt_seed = BashOperator(
        task_id='dbt_seed',
        bash_command=f'cd {DBT_PROJ_DIR} && dbt seed'
    )

    dbt_run = BashOperator(
        task_id='dbt_run',
        bash_command=f'cd {DBT_PROJ_DIR} && dbt run'
    )

    dbt_test = BashOperator(
        task_id='dbt_test', 
        bash_command=f'cd {DBT_PROJ_DIR} && dbt test'
    )

    dbt_seed >> dbt_run >> dbt_test