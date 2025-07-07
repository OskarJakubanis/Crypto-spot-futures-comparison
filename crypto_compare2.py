import requests
from flask import Flask, render_template_string

app = Flask(__name__)

TEMPLATE = """
<!doctype html>
<html>
<head>
    <title>Crypto 24h Analysis Dashboard</title>
    <style>
        body { font-family: Arial, sans-serif; padding: 20px; background: #f7f9fb; }
        h2 { color: #333; }
        table { border-collapse: collapse; width: 100%; margin-top: 20px; }
        th, td { border: 1px solid #ccc; padding: 8px; text-align: right; }
        th { background-color: #e0f0ff; }
        td:first-child, th:first-child { text-align: left; }
    </style>
</head>
<body>
    <h2>📈 Crypto Spot vs Futures 24h Analysis — Binance & Bybit</h2>
    <table>
        <thead>
            <tr>
                <th>Symbol</th>
                <th>Binance Spot</th>
                <th>Binance Futures</th>
                <th>Diff (Price)</th>
                <th>Binance Spot 24h %</th>
                <th>Binance Futures 24h %</th>
                <th>Diff (24h %)</th>
                <th>Bybit Spot</th>
                <th>Bybit Futures</th>
                <th>Diff (Price)</th>
                <th>Bybit Spot 24h %</th>
                <th>Bybit Futures 24h %</th>
                <th>Diff (24h %)</th>
            </tr>
        </thead>
        <tbody>
            {% for row in data %}
            <tr>
                <td>{{ row.symbol }}</td>
                <td>{{ row.binance_spot }}</td>
                <td>{{ row.binance_fut }}</td>
                <td>{{ row.binance_price_diff }}</td>
                <td>{{ row.binance_spot_change }}</td>
                <td>{{ row.binance_fut_change }}</td>
                <td>{{ row.binance_change_diff }}</td>
                <td>{{ row.bybit_spot }}</td>
                <td>{{ row.bybit_fut }}</td>
                <td>{{ row.bybit_price_diff }}</td>
                <td>{{ row.bybit_spot_change }}</td>
                <td>{{ row.bybit_fut_change }}</td>
                <td>{{ row.bybit_change_diff }}</td>
            </tr>
            {% endfor %}
        </tbody>
    </table>
</body>
</html>
"""

def fetch_binance():
    spot_prices = {x['symbol']: float(x['price']) for x in requests.get("https://api.binance.com/api/v3/ticker/price").json()}
    spot_changes = {x['symbol']: float(x['priceChangePercent']) for x in requests.get("https://api.binance.com/api/v3/ticker/24hr").json()}

    fut_data = requests.get("https://fapi.binance.com/fapi/v1/ticker/24hr").json()
    fut_prices = {x['symbol']: float(x['lastPrice']) for x in fut_data}
    fut_changes = {x['symbol']: float(x['priceChangePercent']) for x in fut_data}

    return spot_prices, spot_changes, fut_prices, fut_changes

def fetch_bybit():
    spot_resp = requests.get("https://api.bybit.com/v5/market/tickers?category=spot").json()['result']['list']
    fut_resp = requests.get("https://api.bybit.com/v5/market/tickers?category=linear").json()['result']['list']

    spot_prices = {x['symbol']: float(x['lastPrice']) for x in spot_resp}
    spot_changes = {x['symbol']: float(x['price24hPcnt']) * 100 for x in spot_resp}

    fut_prices = {x['symbol']: float(x['lastPrice']) for x in fut_resp}
    fut_changes = {x['symbol']: float(x['price24hPcnt']) * 100 for x in fut_resp}

    return spot_prices, spot_changes, fut_prices, fut_changes

@app.route("/")
def home():
    b_spot, b_spot_chg, b_fut, b_fut_chg = fetch_binance()
    y_spot, y_spot_chg, y_fut, y_fut_chg = fetch_bybit()

    symbols = set(b_spot.keys()) & set(b_fut.keys()) & set(y_spot.keys()) & set(y_fut.keys())
    symbols = [s for s in symbols if s.endswith("USDT") or s.endswith("USDC")]

    result = []
    for sym in sorted(symbols):
        try:
            bs, bf = b_spot[sym], b_fut[sym]
            bsc, bfc = b_spot_chg[sym], b_fut_chg[sym]
            bd_price = round(bf - bs, 6)
            bd_pct = round(bfc - bsc, 2)

            ys, yf = y_spot[sym], y_fut[sym]
            ysc, yfc = y_spot_chg[sym], y_fut_chg[sym]
            yd_price = round(yf - ys, 6)
            yd_pct = round(yfc - ysc, 2)

            result.append({
                'symbol': sym,
                'binance_spot': round(bs, 6),
                'binance_fut': round(bf, 6),
                'binance_price_diff': bd_price,
                'binance_spot_change': round(bsc, 2),
                'binance_fut_change': round(bfc, 2),
                'binance_change_diff': bd_pct,
                'bybit_spot': round(ys, 6),
                'bybit_fut': round(yf, 6),
                'bybit_price_diff': yd_price,
                'bybit_spot_change': round(ysc, 2),
                'bybit_fut_change': round(yfc, 2),
                'bybit_change_diff': yd_pct,
            })
        except:
            continue

    return render_template_string(TEMPLATE, data=result)

if __name__ == "__main__":
    app.run(debug=True)
