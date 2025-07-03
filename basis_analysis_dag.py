from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta

# Importujemy funkcje z Twoich plików
from fetch_data import fetch_spot_data, fetch_futures_data
from fetch_and_compare_prices import merge_and_save_raw_data
from basis_analysis import calculate_basis
from report_generator import generate_report

default_args = {
    'owner': 'airflow',
    'start_date': datetime(2025, 7, 3),
    'retries': 1,
    'retry_delay': timedelta(minutes=5)
}

with DAG(
    dag_id='crypto_basis_analysis_daily',
    default_args=default_args,
    schedule_interval='0 8 * * *',  # codziennie o 8:00 rano
    catchup=False
) as dag:

    task_fetch_spot = PythonOperator(
        task_id='fetch_spot_data',
        python_callable=fetch_spot_data
    )

    task_fetch_futures = PythonOperator(
        task_id='fetch_futures_data',
        python_callable=fetch_futures_data
    )

    task_merge_data = PythonOperator(
        task_id='merge_spot_and_futures',
        python_callable=merge_and_save_raw_data
    )

    task_calculate_basis = PythonOperator(
        task_id='calculate_basis',
        python_callable=calculate_basis
    )

    task_generate_report = PythonOperator(
        task_id='generate_report',
        python_callable=generate_report
    )

    # Definicja kolejności zadań
    [task_fetch_spot, task_fetch_futures] >> task_merge_data >> task_calculate_basis >> task_generate_report
