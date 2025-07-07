import requests
from flask import Flask, render_template_string
import logging

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

BINANCE_SPOT_URL = "https://api.binance.com/api/v3/ticker/price"
BINANCE_FUTURES_URL = "https://fapi.binance.com/fapi/v1/ticker/price"
BINANCE_FUTURES_EXCHANGE_INFO = "https://fapi.binance.com/fapi/v1/exchangeInfo"

def fetch_active_futures_symbols():
    try:
        res = requests.get(BINANCE_FUTURES_EXCHANGE_INFO)
        res.raise_for_status()
        data = res.json()
        # Only include symbols that are currently active
        active_symbols = {item['symbol'] for item in data['symbols'] if item['status'] == 'TRADING'}
        return active_symbols
    except Exception as e:
        logger.error(f"Error fetching futures symbols: {e}")
        return set()

def fetch_prices(url):
    try:
        res = requests.get(url)
        res.raise_for_status()
        return {item['symbol']: float(item['price']) for item in res.json()}
    except Exception as e:
        logger.error(f"Error fetching prices from {url}: {e}")
        return {}

@app.route("/")
def compare_prices():
    active_futures = fetch_active_futures_symbols()
    spot_data = fetch_prices(BINANCE_SPOT_URL)
    futures_data = fetch_prices(BINANCE_FUTURES_URL)

    comparison = []
    for symbol in active_futures:
        spot_price = spot_data.get(symbol)
        futures_price = futures_data.get(symbol)
        if spot_price and futures_price and spot_price > 0:
            diff_percent = ((futures_price - spot_price) / spot_price) * 100
            comparison.append((symbol, spot_price, futures_price, diff_percent))

    # Sort descending by % difference
    comparison.sort(key=lambda x: abs(x[3]), reverse=True)

    html = """
    <html>
    <head><title>Spot vs Futures Comparison</title></head>
    <body>
        <h2>🔍 Spot vs Futures Price Difference (Filtered - Active Only)</h2>
        <table border="1" cellpadding="5">
            <tr><th>Symbol</th><th>Spot</th><th>Futures</th><th>Diff (%)</th></tr>
            {% for row in data %}
            <tr>
                <td>{{ row[0] }}</td>
                <td>{{ "%.6f"|format(row[1]) }}</td>
                <td>{{ "%.6f"|format(row[2]) }}</td>
                <td>{{ "%.2f"|format(row[3]) }}</td>
            </tr>
            {% endfor %}
        </table>
        <p>Data auto-refreshes every 30s. (Press F5)</p>
    </body>
    </html>
    """
    return render_template_string(html, data=comparison)

if __name__ == "__main__":
    app.run(debug=True)
