# This script:
#1. Fetches current spot and futures prices from Binance REST APIs,
#2. logs info about the fetched data,
#3. handles errors gracefully,
#4. and returns combined data for further use.

import requests  # to perform HTTP requests to APIs
import time      # for potential delays (e.g., sleep)
import logging   # for logging info and errors

# Setup logger with INFO level to see messages
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

# Define Binance API endpoints for spot and futures prices
BINANCE_API_URL = "https://api.binance.com/api/v3/ticker/price"
BINANCE_FUTURES_API_URL = "https://fapi.binance.com/fapi/v1/ticker/price"

def fetch_spot_data():
    # This function sends a request to Binance spot API
    try:
        response = requests.get(BINANCE_API_URL)
        response.raise_for_status()  # Check if response is OK
        data = response.json()       # Parse JSON response into Python object
        # Log how many records were fetched
        logger.info(f"Fetched {len(data)} spot records")
        return data
    except requests.RequestException as e:
        # Handle connection or response errors
        logger.error(f"Error fetching spot data: {e}")
        return []

def fetch_futures_data():
    # Similar to above, but for Binance futures API
    try:
        response = requests.get(BINANCE_FUTURES_API_URL)
        response.raise_for_status()
        data = response.json()
        # Log how many records were fetched from futures
        logger.info(f"Fetched {len(data)} futures records")
        return data
    except requests.RequestException as e:
        # Handle errors in the futures request
        logger.error(f"Error fetching futures data: {e}")
        return []

def fetch_all_data():
    # Combine results from both API calls
    spot = fetch_spot_data()
    futures = fetch_futures_data()
    # Return a dictionary containing both spot and futures data
    return {"spot": spot, "futures": futures}

if __name__ == "__main__":
    # Main entry point of the script
    all_data = fetch_all_data()
    # Print how many records were fetched in total
    print(f"Fetched data: spot={len(all_data['spot'])}, futures={len(all_data['futures'])}")
