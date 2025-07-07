import requests
from flask import Flask, render_template_string

app = Flask(__name__)

TEMPLATE = """
<!doctype html>
<html>
<head>
    <title>Crypto Futures Basis Comparison</title>
    <style>
        body { font-family: Arial; padding: 20px; }
        table { border-collapse: collapse; width: 100%; margin-top: 20px; font-size: 14px; }
        th, td { border: 1px solid #ccc; padding: 6px 8px; text-align: right; }
        th { background-color: #f2f2f2; }
        td:first-child, th:first-child { text-align: left; }
    </style>
</head>
<body>
    <h2>Crypto Futures Basis Comparison: Binance vs Bybit (USDT/USDC)</h2>
    <table>
        <thead>
            <tr>
                <th>Symbol</th>
                <th>Bnc Spot</th>
                <th>Bnc Fut</th>
                <th>Diff % (Bnc)</th>
                <th>24h % (Bnc Spot)</th>
                <th>24h % (Bnc Fut)</th>
                <th>Δ24h (Bnc)</th>
                <th>Bbt Spot</th>
                <th>Bbt Fut</th>
                <th>Diff % (Bbt)</th>
                <th>24h % (Bbt Spot)</th>
                <th>24h % (Bbt Fut)</th>
                <th>Δ24h (Bbt)</th>
            </tr>
        </thead>
        <tbody>
            {% for row in data %}
            <tr>
                <td>{{ row.symbol }}</td>
                <td>{{ "%.6f"|format(row.bnc_spot) }}</td>
                <td>{{ "%.6f"|format(row.bnc_fut) }}</td>
                <td>{{ "%.2f"|format(row.diff_bnc) }}</td>
                <td>{{ "%.2f"|format(row.bnc_spot_24h) }}</td>
                <td>{{ "%.2f"|format(row.bnc_fut_24h) }}</td>
                <td>{{ "%.2f"|format(row.delta_24h_bnc) }}</td>
                <td>{{ "%.6f"|format(row.bbt_spot) }}</td>
                <td>{{ "%.6f"|format(row.bbt_fut) }}</td>
                <td>{{ "%.2f"|format(row.diff_bbt) }}</td>
                <td>{{ "%.2f"|format(row.bbt_spot_24h) }}</td>
                <td>{{ "%.2f"|format(row.bbt_fut_24h) }}</td>
                <td>{{ "%.2f"|format(row.delta_24h_bbt) }}</td>
            </tr>
            {% endfor %}
        </tbody>
    </table>
</body>
</html>
"""

def fetch_binance():
    spot_resp = requests.get("https://api.binance.com/api/v3/ticker/24hr").json()
    fut_resp = requests.get("https://fapi.binance.com/fapi/v1/ticker/24hr").json()

    spot_dict = {}
    fut_dict = {}

    for item in spot_resp:
        symbol = item['symbol']
        if symbol.endswith(('USDT', 'USDC')):
            spot_dict[symbol] = {
                'price': float(item['lastPrice']),
                'priceChangePercent': float(item['priceChangePercent'])
            }

    for item in fut_resp:
        symbol = item['symbol']
        if symbol.endswith(('USDT', 'USDC')):
            fut_dict[symbol] = {
                'price': float(item['lastPrice']),
                'priceChangePercent': float(item['priceChangePercent'])
            }

    return spot_dict, fut_dict

def fetch_bybit():
    # Bybit Spot
    spot_resp = requests.get("https://api.bybit.com/v5/market/tickers?category=spot").json()
    fut_resp = requests.get("https://api.bybit.com/v5/market/tickers?category=linear").json()

    spot_dict = {}
    fut_dict = {}

    for item in spot_resp['result']['list']:
        symbol = item['symbol']
        if symbol.endswith(('USDT', 'USDC')):
            spot_dict[symbol] = {
                'price': float(item['lastPrice']),
                'priceChangePercent': float(item['price24hPcnt']) * 100  # API returns decimal like 0.01 for 1%
            }

    for item in fut_resp['result']['list']:
        symbol = item['symbol']
        if symbol.endswith(('USDT', 'USDC')):
            fut_dict[symbol] = {
                'price': float(item['lastPrice']),
                'priceChangePercent': float(item['price24hPcnt']) * 100
            }

    return spot_dict, fut_dict

@app.route("/")
def compare():
    bnc_spot, bnc_fut = fetch_binance()
    bbt_spot, bbt_fut = fetch_bybit()

    # We want symbols common to all 4 sets
    symbols = set(bnc_spot.keys()) & set(bnc_fut.keys()) & set(bbt_spot.keys()) & set(bbt_fut.keys())

    results = []

    for sym in sorted(symbols):
        bs = bnc_spot[sym]['price']
        bf = bnc_fut[sym]['price']
        bnc_spot_24h = bnc_spot[sym]['priceChangePercent']
        bnc_fut_24h = bnc_fut[sym]['priceChangePercent']
        diff_bnc = ((bf - bs) / bs) * 100 if bs else 0
        delta_24h_bnc = bnc_fut_24h - bnc_spot_24h

        ys = bbt_spot[sym]['price']
        yf = bbt_fut[sym]['price']
        bbt_spot_24h = bbt_spot[sym]['priceChangePercent']
        bbt_fut_24h = bbt_fut[sym]['priceChangePercent']
        diff_bbt = ((yf - ys) / ys) * 100 if ys else 0
        delta_24h_bbt = bbt_fut_24h - bbt_spot_24h

        results.append({
            'symbol': sym,
            'bnc_spot': bs,
            'bnc_fut': bf,
            'diff_bnc': diff_bnc,
            'bnc_spot_24h': bnc_spot_24h,
            'bnc_fut_24h': bnc_fut_24h,
            'delta_24h_bnc': delta_24h_bnc,
            'bbt_spot': ys,
            'bbt_fut': yf,
            'diff_bbt': diff_bbt,
            'bbt_spot_24h': bbt_spot_24h,
            'bbt_fut_24h': bbt_fut_24h,
            'delta_24h_bbt': delta_24h_bbt,
        })

    # Sort by Binance diff descending
    results.sort(key=lambda x: x['diff_bnc'], reverse=True)

    return render_template_string(TEMPLATE, data=results)

if __name__ == "__main__":
    app.run(debug=True)
