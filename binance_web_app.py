from flask import Flask, render_template_string
import requests
import logging

# Configure logger
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

# API endpoints
BINANCE_API_URL = "https://api.binance.com/api/v3/ticker/price"
BINANCE_FUTURES_API_URL = "https://fapi.binance.com/fapi/v1/ticker/price"

# Initialize Flask app
app = Flask(__name__)

def fetch_spot_data():
    try:
        response = requests.get(BINANCE_API_URL)
        response.raise_for_status()
        data = response.json()
        logger.info(f"Fetched {len(data)} spot records")
        return {item["symbol"]: float(item["price"]) for item in data}
    except requests.RequestException as e:
        logger.error(f"Error fetching spot data: {e}")
        return {}

def fetch_futures_data():
    try:
        response = requests.get(BINANCE_FUTURES_API_URL)
        response.raise_for_status()
        data = response.json()
        logger.info(f"Fetched {len(data)} futures records")
        return {item["symbol"]: float(item["price"]) for item in data}
    except requests.RequestException as e:
        logger.error(f"Error fetching futures data: {e}")
        return {}

@app.route("/")
def index():
    spot = fetch_spot_data()
    futures = fetch_futures_data()

    comparisons = []
    for symbol in spot:
        if symbol in futures and spot[symbol] > 0:
            diff_percent = ((futures[symbol] - spot[symbol]) / spot[symbol]) * 100
            comparisons.append({
                "symbol": symbol,
                "spot": spot[symbol],
                "futures": futures[symbol],
                "diff": round(diff_percent, 2)
            })

    comparisons.sort(key=lambda x: x["diff"], reverse=True)

    # HTML template string
    template = """
    <html>
    <head>
        <title>Binance Spot vs Futures</title>
        <meta http-equiv="refresh" content="60">
        <style>
            body { font-family: Arial; margin: 2rem; }
            table { border-collapse: collapse; width: 100%; }
            th, td { border: 1px solid #ddd; padding: 8px; text-align: right; }
            th { background-color: #f2f2f2; text-align: center; }
            tr:hover { background-color: #f9f9f9; }
        </style>
    </head>
    <body>
        <h2>Binance Spot vs Futures (% Difference)</h2>
        <p>Auto-refresh co 60 sekund</p>
        <table>
            <tr>
                <th>Symbol</th>
                <th>Spot</th>
                <th>Futures</th>
                <th>Diff (%)</th>
            </tr>
            {% for item in comparisons %}
            <tr>
                <td style="text-align: center">{{ item.symbol }}</td>
                <td>{{ "%.6f"|format(item.spot) }}</td>
                <td>{{ "%.6f"|format(item.futures) }}</td>
                <td>{{ item.diff }}</td>
            </tr>
            {% endfor %}
        </table>
    </body>
    </html>
    """
    return render_template_string(template, comparisons=comparisons)

if __name__ == "__main__":
    app.run(debug=True)
