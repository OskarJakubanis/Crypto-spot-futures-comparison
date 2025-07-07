import requests
import logging

# Setup logger with INFO level to see messages
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

# Define Binance API endpoints for spot and futures prices
BINANCE_API_URL = "https://api.binance.com/api/v3/ticker/price"
BINANCE_FUTURES_API_URL = "https://fapi.binance.com/fapi/v1/ticker/price"

def fetch_spot_data():
    try:
        response = requests.get(BINANCE_API_URL)
        response.raise_for_status()
        data = response.json()
        logger.info(f"Fetched {len(data)} spot records")
        return data
    except requests.RequestException as e:
        logger.error(f"Error fetching spot data: {e}")
        return []

def fetch_futures_data():
    try:
        response = requests.get(BINANCE_FUTURES_API_URL)
        response.raise_for_status()
        data = response.json()
        logger.info(f"Fetched {len(data)} futures records")
        return data
    except requests.RequestException as e:
        logger.error(f"Error fetching futures data: {e}")
        return []

def fetch_all_data():
    spot = fetch_spot_data()
    futures = fetch_futures_data()
    return {"spot": spot, "futures": futures}

def compare_prices(spot_data, futures_data):
    # Convert to dictionaries for quick lookup
    spot_dict = {item["symbol"]: float(item["price"]) for item in spot_data}
    futures_dict = {item["symbol"]: float(item["price"]) for item in futures_data}

    # Compare only symbols that exist in both
    common_symbols = set(spot_dict.keys()) & set(futures_dict.keys())
    comparison = []

    for symbol in common_symbols:
        spot_price = spot_dict[symbol]
        futures_price = futures_dict[symbol]
        diff_pct = ((futures_price - spot_price) / spot_price) * 100
        comparison.append({
            "symbol": symbol,
            "spot": spot_price,
            "futures": futures_price,
            "diff_pct": diff_pct
        })

    # Sort from highest absolute difference to lowest
    comparison_sorted = sorted(comparison, key=lambda x: abs(x["diff_pct"]), reverse=True)
    return comparison_sorted

if __name__ == "__main__":
    all_data = fetch_all_data()
    comparison = compare_prices(all_data["spot"], all_data["futures"])

    print(f"\n{'Symbol':<15} {'Spot':>10} {'Futures':>10} {'Diff (%)':>10}")
    print("-" * 50)
    for entry in comparison:
        print(f"{entry['symbol']:<15} {entry['spot']:>10.4f} {entry['futures']:>10.4f} {entry['diff_pct']:>10.2f}")
