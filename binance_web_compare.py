import requests
import logging
from flask import Flask, render_template_string

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

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

def filter_and_compare(spot_data, futures_data):
    # Map symbol -> price for futures for quick lookup
    futures_dict = {item['symbol']: float(item['price']) for item in futures_data}

    results = []
    for spot in spot_data:
        symbol = spot['symbol']
        spot_price = float(spot['price'])

        # Check if futures have exact same symbol
        futures_price = futures_dict.get(symbol)
        if futures_price is None:
            continue

        # Check if stablecoin suffix matches (e.g. USDT == USDT, USDC == USDC)
        # Extract suffix after last 3 or 4 chars: common stablecoins are USDT (4 chars) or USDC (4 chars)
        # We can compare last 4 chars here
        suffix_spot = symbol[-4:]
        suffix_futures = symbol[-4:]
        if suffix_spot != suffix_futures:
            continue

        diff_percent = ((futures_price - spot_price) / spot_price) * 100
        results.append({
            'symbol': symbol,
            'spot': spot_price,
            'futures': futures_price,
            'diff_percent': diff_percent
        })

    # Sort by absolute difference descending
    results.sort(key=lambda x: abs(x['diff_percent']), reverse=True)
    return results

app = Flask(__name__)

HTML_TEMPLATE = """
<!doctype html>
<html lang="en">
<head>
    <meta charset="UTF-8" />
    <title>Binance Spot vs Futures Comparison</title>
    <style>
        body { font-family: monospace; margin: 20px; }
        table { border-collapse: collapse; width: 100%; }
        th, td { border: 1px solid #ccc; padding: 8px; text-align: right; }
        th { background-color: #f0f0f0; }
        td.symbol { text-align: left; font-weight: bold; }
    </style>
    <meta http-equiv="refresh" content="10" />
</head>
<body>
    <h2>Binance Spot vs Futures Comparison</h2>
    <table>
        <thead>
            <tr>
                <th>Symbol</th>
                <th>Spot Price</th>
                <th>Futures Price</th>
                <th>Difference (%)</th>
            </tr>
        </thead>
        <tbody>
            {% for row in data %}
            <tr>
                <td class="symbol">{{ row.symbol }}</td>
                <td>{{ "%.6f"|format(row.spot) }}</td>
                <td>{{ "%.6f"|format(row.futures) }}</td>
                <td>{{ "%.2f"|format(row.diff_percent) }}</td>
            </tr>
            {% endfor %}
        </tbody>
    </table>
    <p>Data auto-refreshes every 10 seconds.</p>
</body>
</html>
"""

@app.route("/")
def index():
    spot_data = fetch_spot_data()
    futures_data = fetch_futures_data()
    comparison = filter_and_compare(spot_data, futures_data)
    return render_template_string(HTML_TEMPLATE, data=comparison)

if __name__ == "__main__":
    app.run(debug=True)
