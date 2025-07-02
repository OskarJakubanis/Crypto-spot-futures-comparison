from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
import requests
import pandas as pd

default_args = {
    'owner': 'Oskar',
    'depends_on_past': False,
    'start_date': datetime(2025, 7, 2),
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

dag = DAG(
    'fetch_and_compare_prices',
    default_args=default_args,
    schedule_interval='@daily',
    catchup=False
)

def fetch_spot_prices():
    url = "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin,ethereum,cardano&vs_currencies=usd"
    response = requests.get(url)
    data = response.json()
    # Konwersja na DataFrame
    spot_df = pd.DataFrame(data).T.reset_index()
    spot_df.columns = ['coin', 'price_usd']
    spot_df.to_csv('/tmp/spot_prices.csv', index=False)
    print("Spot prices saved.")

def fetch_futures_prices():
    # Tu może być inny endpoint lub symulacja, bo CoinGecko nie ma futures bezpośrednio
    # Na potrzeby demo, pobierzemy takie same ceny z lekką zmianą, symulując futures
    spot_df = pd.read_csv('/tmp/spot_prices.csv')
    spot_df['futures_price_usd'] = spot_df['price_usd'] * 1.03  # +3% symulacja futures
    spot_df.to_csv('/tmp/futures_prices.csv', index=False)
    print("Futures prices saved.")

def compare_prices():
    spot = pd.read_csv('/tmp/spot_prices.csv')
    futures = pd.read_csv('/tmp/futures_prices.csv')
    df = spot.merge(futures[['coin', 'futures_price_usd']], on='coin')
    df['diff'] = df['futures_price_usd'] - df['price_usd']
    df['diff_pct'] = df['diff'] / df['price_usd'] * 100

    # Top 3 wzrosty
    top_up = df.sort_values('diff_pct', ascending=False).head(3)
    # Top 3 spadki
    top_down = df.sort_values('diff_pct').head(3)

    top_up.to_csv('/tmp/top_3_increase.csv', index=False)
    top_down.to_csv('/tmp/top_3_decrease.csv', index=False)
    df.to_csv('/tmp/compare_results.csv', index=False)
    print("Comparison done and saved.")

task_fetch_spot = PythonOperator(
    task_id='fetch_spot_prices',
    python_callable=fetch_spot_prices,
    dag=dag
)

task_fetch_futures = PythonOperator(
    task_id='fetch_futures_prices',
    python_callable=fetch_futures_prices,
    dag=dag
)

task_compare = PythonOperator(
    task_id='compare_prices',
    python_callable=compare_prices,
    dag=dag
)

task_fetch_spot >> task_fetch_futures >> task_compare
