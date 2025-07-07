import requests
import logging
from flask import Flask, render_template_string

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

BINANCE_API_URL = "https://api.binance.com/api/v3/ticker/price"
BINANCE_FUTURES_API_URL = "https://fapi.binance.com/fapi/v1/ticker/price"

app = Flask(__name__)

def fetch_spot_data():
    try:
        response = requests.get(BINANCE_API_URL)
        response.raise_for_status()
        data = response.json()
        logger.info(f"Fetched {len(data)} spot records")
        return data
    except Exception as e:
        logger.error(f"Error fetching spot data: {e}")
        return []

def fetch_futures_data():
    try:
        response = requests.get(BINANCE_FUTURES_API_URL)
        response.raise_for_status()
        data = response.json()
        logger.info(f"Fetched {len(data)} futures records")
        return data
    except Exception as e:
        logger.error(f"Error fetching futures data: {e}")
        return []

def get_common_symbols(spot_data, futures_data):
    spot_symbols = set(item['symbol'] for item in spot_data)
    futures_symbols = set(item['symbol'] for item in futures_data)
    common = spot_symbols.intersection(futures_symbols)
    logger.info(f"Found {len(common)} common symbols between spot and futures")
    return common

def prepare_comparison_data():
    spot_data = fetch_spot_data()
    futures_data = fetch_futures_data()

    common_symbols = get_common_symbols(spot_data, futures_data)

    # Tworzymy słowniki dla szybkiego dostępu do cen po symbolu
    spot_dict = {item['symbol']: float(item['price']) for item in spot_data if item['symbol'] in common_symbols}
    futures_dict = {item['symbol']: float(item['price']) for item in futures_data if item['symbol'] in common_symbols}

    comparison_list = []
    for symbol in common_symbols:
        spot_price = spot_dict[symbol]
        futures_price = futures_dict[symbol]
        # różnica procentowa futures względem spot
        diff_percent = ((futures_price - spot_price) / spot_price) * 100 if spot_price != 0 else 0
        comparison_list.append({
            'symbol': symbol,
            'spot': spot_price,
            'futures': futures_price,
            'diff_percent': diff_percent
        })

    # Sortujemy malejąco po różnicy procentowej
    comparison_list.sort(key=lambda x: abs(x['diff_percent']), reverse=True)

    return comparison_list

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8" />
    <title>Binance Spot vs Futures Price Difference</title>
    <meta http-equiv="refresh" content="10" />
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        table { border-collapse: collapse; width: 100%; }
        th, td { border: 1px solid #ddd; padding: 8px; text-align: right; }
        th { background-color: #f2f2f2; }
        td.symbol { text-align: left; font-weight: bold; }
        tr:hover { background-color: #f9f9f9; }
    </style>
</head>
<body>
    <h2>Binance Spot vs Futures Price Difference (refresh every 10s)</h2>
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
                <td>{{ "{:.6f}".format(row.spot) }}</td>
                <td>{{ "{:.6f}".format(row.futures) }}</td>
                <td>{{ "{:.2f}".format(row.diff_percent) }}</td>
            </tr>
            {% endfor %}
        </tbody>
    </table>
</body>
</html>
"""

@app.route("/")
def home():
    data = prepare_comparison_data()
    return render_template_string(HTML_TEMPLATE, data=data)

if __name__ == "__main__":
    app.run(debug=True)
