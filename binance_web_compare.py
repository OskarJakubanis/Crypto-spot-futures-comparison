import requests
import logging
from flask import Flask, render_template_string

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

BINANCE_SPOT_API = "https://api.binance.com/api/v3/ticker/price"
BINANCE_FUTURES_API = "https://fapi.binance.com/fapi/v1/ticker/price"
BINANCE_FUTURES_INFO = "https://fapi.binance.com/fapi/v1/exchangeInfo"

app = Flask(__name__)

def fetch_spot_data():
    try:
        resp = requests.get(BINANCE_SPOT_API)
        resp.raise_for_status()
        data = resp.json()
        logger.info(f"Fetched {len(data)} spot records")
        return data
    except Exception as e:
        logger.error(f"Spot fetch error: {e}")
        return []

def fetch_futures_data():
    try:
        resp = requests.get(BINANCE_FUTURES_API)
        resp.raise_for_status()
        data = resp.json()
        logger.info(f"Fetched {len(data)} futures records")
        return data
    except Exception as e:
        logger.error(f"Futures fetch error: {e}")
        return []

def fetch_futures_info():
    try:
        resp = requests.get(BINANCE_FUTURES_INFO)
        resp.raise_for_status()
        data = resp.json()
        logger.info("Fetched futures exchange info")
        return data.get("symbols", [])
    except Exception as e:
        logger.error(f"Futures info fetch error: {e}")
        return []

def filter_active_futures_symbols(futures_info):
    # We take only symbols with status 'TRADING'
    active_symbols = {item['symbol'] for item in futures_info if item.get('status') == 'TRADING'}
    return active_symbols

def match_suffix(symbol):
    # Extract USDT or USDC suffix (or other stablecoin suffix if needed)
    # Assuming symbol ends with one of these suffixes (USDT, USDC)
    for suffix in ["USDT", "USDC"]:
        if symbol.endswith(suffix):
            return suffix
    return None

@app.route("/")
def home():
    spot_data = fetch_spot_data()
    futures_data = fetch_futures_data()
    futures_info = fetch_futures_info()
    active_futures = filter_active_futures_symbols(futures_info)

    # Convert futures and spot lists to dict for quick lookup by symbol
    spot_dict = {item['symbol']: float(item['price']) for item in spot_data}
    futures_dict = {item['symbol']: float(item['price']) for item in futures_data}

    results = []
    for symbol, spot_price in spot_dict.items():
        suffix = match_suffix(symbol)
        if not suffix:
            continue  # skip symbols without USDT or USDC suffix

        # Only compare if futures has the exact same symbol and it is active
        if symbol in active_futures and symbol in futures_dict:
            futures_price = futures_dict[symbol]
            # Calculate percentage difference: ((futures - spot) / spot) * 100
            if spot_price != 0:
                diff_percent = ((futures_price - spot_price) / spot_price) * 100
            else:
                diff_percent = 0
            results.append({
                "symbol": symbol,
                "spot": spot_price,
                "futures": futures_price,
                "diff": diff_percent
            })

    # Sort results by absolute difference desc
    results.sort(key=lambda x: abs(x["diff"]), reverse=True)

    # Simple HTML table template
    html = """
    <html>
    <head>
      <title>Binance Spot vs Futures Comparison</title>
      <meta http-equiv="refresh" content="60">
      <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        table { border-collapse: collapse; width: 100%; }
        th, td { border: 1px solid #ccc; padding: 8px; text-align: right; }
        th { background: #333; color: white; }
        td.symbol { text-align: left; font-weight: bold; }
        tr:nth-child(even) { background: #f9f9f9; }
      </style>
    </head>
    <body>
      <h1>Binance Spot vs Futures Price Differences (USDT/USDC only)</h1>
      <p>Auto-refresh every 60 seconds</p>
      <table>
        <tr>
          <th>Symbol</th>
          <th>Spot Price</th>
          <th>Futures Price</th>
          <th>Diff (%)</th>
        </tr>
        {% for row in results %}
        <tr>
          <td class="symbol">{{row.symbol}}</td>
          <td>{{"%.6f"|format(row.spot)}}</td>
          <td>{{"%.6f"|format(row.futures)}}</td>
          <td style="color: {{'green' if row.diff >= 0 else 'red'}}">{{"%.2f"|format(row.diff)}}</td>
        </tr>
        {% endfor %}
      </table>
    </body>
    </html>
    """

    return render_template_string(html, results=results)

if __name__ == "__main__":
    app.run(debug=True)
