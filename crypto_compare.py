
# Plan: Stworzyć aplikację Flask, która pobiera dane spot i futures z Binance i Bybit,
# filtruje wspólne symbole (USDT/USDC), porównuje ceny i wyświetla jedną tabelę z kolumnami:
# Symbol, Binance Spot, Binance Futures, Bybit Spot, Bybit Futures, Diff (Binance), Diff (Bybit)

import requests
from flask import Flask, render_template_string

app = Flask(__name__)

TEMPLATE = """
<!doctype html>
<html>
<head>
    <title>Crypto Basis Comparison</title>
    <style>
        body { font-family: Arial; padding: 20px; }
        table { border-collapse: collapse; width: 100%; margin-top: 20px; }
        th, td { border: 1px solid #ccc; padding: 8px; text-align: right; }
        th { background-color: #f2f2f2; }
        td:first-child, th:first-child { text-align: left; }
    </style>
</head>
<body>
    <h2>Crypto Basis Comparison: Binance vs Bybit (USDT/USDC)</h2>
    <table>
        <thead>
            <tr>
                <th>Symbol</th>
                <th>Binance Spot</th>
                <th>Binance Futures</th>
                <th>Bybit Spot</th>
                <th>Bybit Futures</th>
                <th>Diff (Binance) %</th>
                <th>Diff (Bybit) %</th>
            </tr>
        </thead>
        <tbody>
            {% for row in data %}
            <tr>
                <td>{{ row.symbol }}</td>
                <td>{{ row.binance_spot or "-" }}</td>
                <td>{{ row.binance_fut or "-" }}</td>
                <td>{{ row.bybit_spot or "-" }}</td>
                <td>{{ row.bybit_fut or "-" }}</td>
                <td>{{ "%.2f"|format(row.diff_binance) if row.diff_binance is not none else "-" }}</td>
                <td>{{ "%.2f"|format(row.diff_bybit) if row.diff_bybit is not none else "-" }}</td>
            </tr>
            {% endfor %}
        </tbody>
    </table>
</body>
</html>
"""

def fetch_binance():
    spot = requests.get("https://api.binance.com/api/v3/ticker/price").json()
    futs = requests.get("https://fapi.binance.com/fapi/v1/ticker/price").json()
    spot_dict = {x['symbol']: float(x['price']) for x in spot if x['symbol'].endswith(('USDT', 'USDC'))}
    futs_dict = {x['symbol']: float(x['price']) for x in futs if x['symbol'].endswith(('USDT', 'USDC'))}
    return spot_dict, futs_dict

def fetch_bybit():
    spot = requests.get("https://api.bybit.com/v5/market/tickers?category=spot").json()['result']['list']
    futs = requests.get("https://api.bybit.com/v5/market/tickers?category=linear").json()['result']['list']
    spot_dict = {x['symbol']: float(x['lastPrice']) for x in spot if x['symbol'].endswith(('USDT', 'USDC'))}
    futs_dict = {x['symbol']: float(x['lastPrice']) for x in futs if x['symbol'].endswith(('USDT', 'USDC'))}
    return spot_dict, futs_dict

@app.route("/")
def compare():
    b_spot, b_fut = fetch_binance()
    y_spot, y_fut = fetch_bybit()

    symbols = set(b_spot.keys()) & set(b_fut.keys()) & set(y_spot.keys()) & set(y_fut.keys())
    results = []

    for sym in sorted(symbols):
        bs, bf = b_spot[sym], b_fut[sym]
        ys, yf = y_spot[sym], y_fut[sym]
        diff_b = ((bf - bs) / bs * 100) if bs else None
        diff_y = ((yf - ys) / ys * 100) if ys else None
        results.append({
            'symbol': sym,
            'binance_spot': round(bs, 6),
            'binance_fut': round(bf, 6),
            'bybit_spot': round(ys, 6),
            'bybit_fut': round(yf, 6),
            'diff_binance': diff_b,
            'diff_bybit': diff_y
        })

    results.sort(key=lambda x: (x['diff_binance'] or 0), reverse=True)
    return render_template_string(TEMPLATE, data=results)

app.run(debug=True)
