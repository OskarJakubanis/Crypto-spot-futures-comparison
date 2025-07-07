import requests
import logging

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

BINANCE_SPOT_EXCHANGE_INFO = "https://api.binance.com/api/v3/exchangeInfo"
BINANCE_FUTURES_EXCHANGE_INFO = "https://fapi.binance.com/fapi/v1/exchangeInfo"
BINANCE_SPOT_PRICE = "https://api.binance.com/api/v3/ticker/price"
BINANCE_FUTURES_PRICE = "https://fapi.binance.com/fapi/v1/ticker/price"

def get_active_symbols(url):
    try:
        resp = requests.get(url)
        resp.raise_for_status()
        data = resp.json()
        symbols = data.get("symbols", [])
        # Pobierz symbole tylko aktywne i z status "TRADING"
        active = {s["symbol"] for s in symbols if s.get("status") == "TRADING"}
        logger.info(f"Found {len(active)} active symbols from {url}")
        return active
    except requests.RequestException as e:
        logger.error(f"Error fetching exchange info from {url}: {e}")
        return set()

def fetch_prices(url):
    try:
        resp = requests.get(url)
        resp.raise_for_status()
        data = resp.json()
        # Zwróć dict symbol->price
        return {item["symbol"]: float(item["price"]) for item in data}
    except requests.RequestException as e:
        logger.error(f"Error fetching prices from {url}: {e}")
        return {}

def main():
    spot_symbols = get_active_symbols(BINANCE_SPOT_EXCHANGE_INFO)
    futures_symbols = get_active_symbols(BINANCE_FUTURES_EXCHANGE_INFO)

    # Wspólne symbole (dostępne na spot i futures)
    common_symbols = spot_symbols.intersection(futures_symbols)
    logger.info(f"Common symbols on spot and futures: {len(common_symbols)}")

    spot_prices = fetch_prices(BINANCE_SPOT_PRICE)
    futures_prices = fetch_prices(BINANCE_FUTURES_PRICE)

    print(f"{'Symbol':<12} {'Spot':>10} {'Futures':>10} {'Diff (%)':>10}")
    print("-" * 45)

    for symbol in sorted(common_symbols):
        spot_price = spot_prices.get(symbol)
        futures_price = futures_prices.get(symbol)
        if spot_price is None or futures_price is None:
            continue
        diff_pct = ((futures_price - spot_price) / spot_price) * 100 if spot_price != 0 else 0
        print(f"{symbol:<12} {spot_price:>10.6f} {futures_price:>10.6f} {diff_pct:>10.2f}")

if __name__ == "__main__":
    main()
