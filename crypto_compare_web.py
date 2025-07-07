from flask import Flask, render_template_string
import requests

app = Flask(__name__)

TEMPLATE = '''
<!doctype html>
<html>
<head>
    <title>Crypto Basis Comparison</title>
    <style>
        table { border-collapse: collapse; width: 100%; font-family: monospace; }
        th, td { border: 1px solid #ddd; padding: 8px; text-align: right; }
        th { background-color: #333; color: white; }
        tr:nth-child(even) { background-color: #f2f2f2; }
        h2 { margin-top: 40px; }
    </style>
</head>
<body>
    <h1>Crypto Spot vs Futures Comparison (Binance & Bybit)</h1>
    
    {% for exchange_name, rows in data.items() %}
        <h2>{{ exchange_name }}</h2>
        <table>
            <tr>
                <th>Symbol</th>
                <th>Spot</th>
                <th>Futures</th>
                <th>Diff (%)</th>
            </tr>
            {% for row in rows %}
            <tr>
                <td>{{ row.symbol }}</td>
                <td>{{ row.spot }}</td>
                <td>{{ row.futures }}</td>
                <td>{{ "%.2f" | format(row.diff) }}</td>
            </tr>
            {% endfor %}
        </table>
    {% endfor %}
</body>
</html>
'''

def fetch_binance_data():
    spot_url = "https://api.binance.com/api/v3/ticker/price"
    futures_url = "https://fapi.binance.com/fapi/v1/ticker/price"
    
    spot_data = {item['symbol']: float(item['price']) for item in requests.get(spot_url).json()
                 if item['symbol'].endswith(('USDT', 'USDC'))}
    futures_data = {item['symbol']: float(item['price']) for item in requests.get(futures_url).json()
                    if item['symbol'].endswith(('USDT', 'USDC'))}

    common = set(spot_data.keys()) & set(futures_data.keys())

    result = []
    for symbol in common:
        spot_price = spot_data[symbol]
        futures_price = futures_data[symbol]
        if spot_price == 0: continue
        diff_percent = ((futures_price - spot_price) / spot_price) * 100
        result.append({
            'symbol': symbol,
            'spot': spot_price,
            'futures': futures_price,
            'diff': diff_percent
        })
    result.sort(key=lambda x: abs(x['diff']), reverse=True)
    return result

def fetch_bybit_data():
    # Bybit Spot
    spot_url = "https://api.bybit.com/v2/public/tickers"
    spot_response = requests.get(spot_url).json()
    spot_data = {
        item['symbol']: float(item['last_price']) for item in spot_response['result']
        if item['symbol'].endswith(('USDT', 'USDC'))
    }

    # Bybit Futures (USDT Perpetual)
    futures_url = "https://api.bybit.com/v2/public/tickers"
    futures_response = requests.get(futures_url).json()
    futures_data = {
        item['symbol']: float(item['last_price']) for item in futures_response['result']
        if item['symbol'].endswith(('USDT', 'USDC')) and item['symbol'] in spot_data
    }

    common = set(spot_data.keys()) & set(futures_data.keys())
    
    result = []
    for symbol in common:
        spot_price = spot_data[symbol]
        futures_price = futures_data[symbol]
        if spot_price == 0: continue
        diff_percent = ((futures_price - spot_price) / spot_price) * 100
        result.append({
            'symbol': symbol,
            'spot': spot_price,
            'futures': futures_price,
            'diff': diff_percent
        })
    result.sort(key=lambda x: abs(x['diff']), reverse=True)
    return result

@app.route("/")
def index():
    binance_data = fetch_binance_data()
    bybit_data = fetch_bybit_data()
    return render_template_string(TEMPLATE, data={
        "Binance": binance_data,
        "Bybit": bybit_data
    })

if __name__ == "__main__":
    app.run(debug=True)
