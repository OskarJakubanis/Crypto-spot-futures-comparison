from flask import Flask, render_template_string
import requests
import logging

app = Flask(__name__)
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
        active = {s["symbol"] for s in data.get("symbols", []) if s.get("status") == "TRADING"}
        return active
    except Exception as e:
        app.logger.error(f"Error fetching exchange info: {e}")
        return set()

def fetch_prices(url):
    try:
        resp = requests.get(url)
        resp.raise_for_status()
        data = resp.json()
        return {item["symbol"]: float(item["price"]) for item in data}
    except Exception as e:
        app.logger.error(f"Error fetching prices: {e}")
        return {}

@app.route("/")
def index():
    spot_symbols = get_active_symbols(BINANCE_SPOT_EXCHANGE_INFO)
    futures_symbols = get_active_symbols(BINANCE_FUTURES_EXCHANGE_INFO)
    common = spot_symbols.intersection(futures_symbols)

    spot_prices = fetch_prices(BINANCE_SPOT_PRICE)
    futures_prices = fetch_prices(BINANCE_FUTURES_PRICE)

    rows = []
    for sym in sorted(common):
        sp = spot_prices.get(sym)
        fp = futures_prices.get(sym)
        if sp is None or fp is None or sp == 0:
            continue
        diff = (fp - sp) / sp * 100
        rows.append({"symbol": sym, "spot": sp, "futures": fp, "diff": diff})

    # HTML z prostym stylem i auto-refresh co 30 sekund
    html = """
    <html>
    <head>
        <title>Binance Spot vs Futures Price Difference</title>
        <meta http-equiv="refresh" content="30">
        <style>
          body { font-family: Arial, sans-serif; margin: 30px; }
          table { border-collapse: collapse; width: 100%; }
          th, td { padding: 8px 12px; border: 1px solid #ccc; text-align: right; }
          th { background-color: #f2f2f2; }
          td.symbol { text-align: left; }
        </style>
    </head>
    <body>
        <h1>Binance Spot vs Futures Price Difference</h1>
        <table>
            <tr><th>Symbol</th><th>Spot</th><th>Futures</th><th>Diff (%)</th></tr>
            {% for r in rows %}
            <tr>
                <td class="symbol">{{ r.symbol }}</td>
                <td>{{ "%.6f"|format(r.spot) }}</td>
                <td>{{ "%.6f"|format(r.futures) }}</td>
                <td>{{ "%.2f"|format(r.diff) }}</td>
            </tr>
            {% endfor %}
        </table>
        <p>Strona odświeża się automatycznie co 30 sekund.</p>
    </body>
    </html>
    """
    return render_template_string(html, rows=rows)

if __name__ == "__main__":
    app.run(debug=True)
