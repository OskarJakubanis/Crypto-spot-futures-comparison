from flask import Flask, render_template_string
import requests
import pandas as pd

app = Flask(__name__)

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Crypto Futures Monitor</title>
    <style>
        table { border-collapse: collapse; width: 100%; font-family: Arial; }
        th, td { border: 1px solid #ddd; padding: 8px; text-align: center; }
        th { background-color: #f2f2f2; }
    </style>
</head>
<body>
    <h2>Top Futures Spot Diff - Binance vs Bybit</h2>
    {{ table | safe }}
</body>
</html>
"""

def fetch_binance():
    url_spot = "https://api.binance.com/api/v3/ticker/price"
    url_futures = "https://fapi.binance.com/fapi/v1/ticker/price"

    spot_data = {x['symbol']: float(x['price']) for x in requests.get(url_spot).json() if x['symbol'].endswith("USDT")}
    futures_data = {x['symbol']: float(x['price']) for x in requests.get(url_futures).json() if x['symbol'].endswith("USDT")}

    return spot_data, futures_data

def fetch_bybit():
    url_spot = "https://api.bybit.com/v5/market/tickers?category=spot"
    url_futures = "https://api.bybit.com/v5/market/tickers?category=linear"

    try:
        spot_response = requests.get(url_spot)
        spot_response.raise_for_status()
        spot_data = spot_response.json()

        futures_response = requests.get(url_futures)
        futures_response.raise_for_status()
        futures_data = futures_response.json()

        spot = {item['symbol']: float(item['lastPrice']) for item in spot_data.get("result", {}).get("list", []) if item['symbol'].endswith("USDT")}
        futures = {item['symbol']: float(item['lastPrice']) for item in futures_data.get("result", {}).get("list", []) if item['symbol'].endswith("USDT")}

        return spot, futures

    except Exception as e:
        print("Błąd pobierania lub dekodowania danych z Bybit:", e)
        return {}, {}

def calculate_diff(spot, futures):
    data = []
    for symbol in spot:
        if symbol in futures:
            s = spot[symbol]
            f = futures[symbol]
            diff = ((f - s) / s) * 100 if s != 0 else 0
            data.append((symbol, s, f, round(diff, 2)))
    return sorted(data, key=lambda x: abs(x[3]), reverse=True)

@app.route("/")
def index():
    bnc_spot, bnc_fut = fetch_binance()
    bbt_spot, bbt_fut = fetch_bybit()

    bnc_data = calculate_diff(bnc_spot, bnc_fut)
    bbt_data = calculate_diff(bbt_spot, bbt_fut)

    top_data = []
    for row in bnc_data[:5]:
        sym = row[0]
        bybit_row = next((r for r in bbt_data if r[0] == sym), (sym, 0, 0, 0))
        top_data.append([
            sym,
            row[1], row[2], row[3],
            bybit_row[1], bybit_row[2], bybit_row[3]
        ])

    df = pd.DataFrame(top_data, columns=["Symbol", "Bnc Spot", "Bnc Futures", "Diff % (Bnc)", "Bbt Spot", "Bbt Futures", "Diff % (Bbt)"])
    return render_template_string(HTML_TEMPLATE, table=df.to_html(index=False))

if __name__ == "__main__":
    app.run(debug=True)
