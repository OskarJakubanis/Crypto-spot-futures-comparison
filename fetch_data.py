# fetch_data.py

import requests
import time
import logging

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

BINANCE_API_URL = "https://api.binance.com/api/v3/ticker/price"
BINANCE_FUTURES_API_URL = "https://fapi.binance.com/fapi/v1/ticker/price"

def fetch_spot_data():
    """Pobiera aktualne ceny spot z Binance API"""
    try:
        response = requests.get(BINANCE_API_URL)
        response.raise_for_status()
        data = response.json()
        logger.info(f"Pobrano {len(data)} rekordów spot")
        return data
    except requests.RequestException as e:
        logger.error(f"Błąd pobierania danych spot: {e}")
        return []

def fetch_futures_data():
    """Pobiera aktualne ceny futures z Binance Futures API"""
    try:
        response = requests.get(BINANCE_FUTURES_API_URL)
        response.raise_for_status()
        data = response.json()
        logger.info(f"Pobrano {len(data)} rekordów futures")
        return data
    except requests.RequestException as e:
        logger.error(f"Błąd pobierania danych futures: {e}")
        return []

def fetch_all_data():
    """Pobiera dane spot i futures, zwraca je jako słownik"""
    spot = fetch_spot_data()
    futures = fetch_futures_data()
    return {"spot": spot, "futures": futures}

if __name__ == "__main__":
    all_data = fetch_all_data()
    print(f"Pobrano dane: spot={len(all_data['spot'])}, futures={len(all_data['futures'])}")
