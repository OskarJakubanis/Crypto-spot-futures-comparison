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
        .blue-bg { background-color: #cce5ff; }
        .yellow-bg { background-color: #fff3cd; }
    </style>
</head>
<body>
    <h2>Crypto Basis Comparison: Binance vs Bybit (USDT/USDC)</h2>
    <table>
        <thead>
            <tr>
                <th>Symbol</th>
                <th>Bnc Spot</th>
                <th>Bnc Futures</th>
                <th class="blue-bg">Diff % (Bnc)</th>
                <th class="yellow-bg">Δ24h (Bnc)</th>
                <th>Bbt Spot</th>
                <th>Bbt Futures</th>
                <th class="blue-bg">Diff % (Bbt)</th>
                <th class="yellow-bg">Δ24h (Bbt)</th>
            </tr>
        </thead>
        <tbody>
            {% for row in data %}
            <tr>
                <td>{{ row.symbol }}</td>
                <td>{{ "%.6f"|format(row.bnc_spot) }}</td>
                <td>{{ "%.6f"|format(row.bnc_fut) }}</td>
                <td class="blue-bg">{{ "%.2f"|format(row.diff_bnc) }}</td>
                <td class="yellow-bg">{{ "%.2f"|format(row.change_24h_bnc) }}</td>
                <td>{{ "%.6f"|format(row.bbt_spot) }}</td>
                <td>{{ "%.6f"|format(row.bbt_fut) }}</td>
                <td class="blue-bg">{{ "%.2f"|format(row.diff_bbt) }}</td>
                <td class="yellow-bg">{{ "%.2f"|format(row.change_24h_bbt) }}</td>
            </tr>
            {% endfor %}
        </tbody>
    </table>
</body>
</html>
"""

def fetch_binance():
    spot = requests.get("https://api.binance.com/api/v3/ticker/24hr").json()
    futs = requests.get("https://fapi.binance.com/fapi/v1/ticker/24hr").json()

    spot_dict = {}
    futs_dict = {}

    for x in spot:
        symbol = x['symbol']
        if symbol.endswith(('USDT', 'USDC')):
            spot_dict[symbol] = {
                'price': float(x['lastPrice']),
                'change_24h': float(x['priceChangePercent'])
            }

    for x in futs:
        symbol = x['symbol']
        if symbol.endswith(('USDT', 'USDC')):
            futs_dict[symbol] = {
                'price': float(x['lastPrice']),
                'change_24h': float(x['priceChangePercent'])
            }

    return spot_dict, futs_dict

def fetch_bybit():
    spot_resp = requests.get("https://api.bybit.com/v5/market/tickers?category=spot").json()
    futs_resp = requests.get("https://api.bybit.com/v5/market/tickers?category=linear").json()

    spot_dict = {}
    futs_dict = {}

    for x in spot_resp['result']['list']:
        symbol = x['symbol']
        if symbol.endswith(('USDT', 'USDC')):
            spot_dict[symbol] = {
                'price': float(x['lastPrice']),
                'change_24h': float(x['price24hPcnt']) * 100  # bybit returns decimal fraction
            }

    for x in futs_resp['result']['list']:
        symbol = x['symbol']
        if symbol.endswith(('USDT', 'USDC')):
            futs_dict[symbol] = {
                'price': float(x['lastPrice']),
                'change_24h': float(x['price24hPcnt']) * 100
            }

    return spot_dict, futs_dict

@app.route("/")
def compare():
    b_spot, b_fut = fetch_binance()
    y_spot, y_fut = fetch_bybit()

    # We take symbols common to all 4 datasets
    symbols = set(b_spot.keys()) & set(b_fut.keys()) & set(y_spot.keys()) & set(y_fut.keys())

    results = []

    for sym in sorted(symbols):
        bs = b_spot[sym]['price']
        bf = b_fut[sym]['price']
        bc_24h_spot = b_spot[sym]['change_24h']
        bc_24h_fut = b_fut[sym]['change_24h']

        ys = y_spot[sym]['price']
        yf = y_fut[sym]['price']
        yb_24h_spot = y_spot[sym]['change_24h']
        yb_24h_fut = y_fut[sym]['change_24h']

        diff_b = ((bf - bs) / bs) * 100 if bs != 0 else 0
        diff_y = ((yf - ys) / ys) * 100 if ys != 0 else 0

        change_24h_bnc = (bc_24h_fut + bc_24h_spot) / 2
        change_24h_bbt = (yb_24h_fut + yb_24h_spot) / 2

        results.append({
            'symbol': sym,
            'bnc_spot': bs,
            'bnc_fut': bf,
            'diff_bnc': diff_b,
            'change_24h_bnc': change_24h_bnc,
            'bbt_spot': ys,
            'bbt_fut': yf,
            'diff_bbt': diff_y,
            'change_24h_bbt': change_24h_bbt
        })

    # Sort by Binance Diff % descending
    results.sort(key=lambda x: x['diff_bnc'], reverse=True)

    return render_template_string(TEMPLATE, data=results)

if __name__ == "__main__":
    app.run(debug=True)
