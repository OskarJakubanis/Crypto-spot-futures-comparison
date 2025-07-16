# Import necessary libraries:
import requests # - requests: to fetch data from external APIs
from flask import Flask, render_template_string # - Flask: to create a simple web application / render_template_string: to render HTML templates directly from a string

# Create Flask app instance; __name__ helps Flask locate the app's resources
app = Flask(__name__)

# Create an HTML page (as a multi-line string) that the browser will display.
# The result is a simple web dashboard with real-time trading insights.
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
                <th>Trade</th>
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
                <td>{{ row.trade }}</td>
            </tr>
            {% endfor %}
        </tbody>
    </table>
</body>
</html>
"""

# Define a function to fetch spot and futures prices from Binance
def fetch_binance():
    spot = requests.get("https://api.binance.com/api/v3/ticker/24hr").json()
    futs = requests.get("https://fapi.binance.com/fapi/v1/ticker/24hr").json()

    # Create empty dictionaries to store filtered spot and futures data
    spot_dict = {}
    futs_dict = {}
   
    # Loop through all spot symbols and filter only those ending with USDT or USDC for Binance
    for x in spot:
        symbol = x['symbol']
        if symbol.endswith(('USDT', 'USDC')):
            spot_dict[symbol] = {
                'price': float(x['lastPrice']),
                'change_24h': float(x['priceChangePercent'])
            }

    # Loop through all futures symbols and filter only those ending with USDT or USDC
    for x in futs:
        symbol = x['symbol']
        if symbol.endswith(('USDT', 'USDC')):
            futs_dict[symbol] = {
                'price': float(x['lastPrice']),
                'change_24h': float(x['priceChangePercent'])
            }
    # Return both spot and futures price dictionaries for Binance
    return spot_dict, futs_dict

def fetch_bybit():
    spot_resp = requests.get("https://api.bybit.com/v5/market/tickers?category=spot").json()
    futs_resp = requests.get("https://api.bybit.com/v5/market/tickers?category=linear").json()

    # Create empty dictionaries to store filtered spot and futures data
    spot_dict = {}
    futs_dict = {}

    # Loop through all spot symbols and filter only those ending with USDT or USDC for Bybit
    for x in spot_resp['result']['list']:
        symbol = x['symbol']
        if symbol.endswith(('USDT', 'USDC')):
            spot_dict[symbol] = {
                'price': float(x['lastPrice']),
                'change_24h': float(x['price24hPcnt']) * 100  # bybit returns decimal fraction
            }

    # Loop through all futures symbols and filter only those ending with USDT or USDC
    for x in futs_resp['result']['list']:
        symbol = x['symbol']
        if symbol.endswith(('USDT', 'USDC')):
            futs_dict[symbol] = {
                'price': float(x['lastPrice']),
                'change_24h': float(x['price24hPcnt']) * 100
            }

    # Return both spot and futures price dictionaries for Bybit
    return spot_dict, futs_dict

# Define a function that decides the trading action based on(spot, fut, bc_24h_spot, bc_24h_fut):
def get_trade_action(spot, fut, bc_24h_spot, bc_24h_fut):
    diff = ((fut - spot) / spot) * 100 if spot != 0 else 0

    # conditions to decide which trade action to take
    if diff > 0.5 and bc_24h_fut > 0:
        return "Buy Futures"
    elif diff < -0.5 and bc_24h_fut < 0:
        return "Short Futures"
    elif bc_24h_spot > 0 and abs(diff) < 0.5:
        return "Buy Spot"
    elif bc_24h_spot < 0:
        return "Avoid or Sell Spot"
    else:
        return ""

# Decorator before the function — defines the endpoint for the main page
@app.route("/")

# Define the main view function that runs when the root URL is accessed
def compare():
    b_spot, b_fut = fetch_binance()
    y_spot, y_fut = fetch_bybit()

    # Find symbols that exist in all 4 datasets: Binance spot, Binance futures, Bybit spot, and Bybit futures
    symbols = set(b_spot.keys()) & set(b_fut.keys()) & set(y_spot.keys()) & set(y_fut.keys())

    # Create an empty list to store processed data rows for the table
    results = []


    # Loop through each symbol in alphabetical order and get Binance spot and futures prices
  for sym in sorted(symbols): 

    # Get spot and futures prices + 24h change for Binance
    bs = b_spot[sym]['price']
    bf = b_fut[sym]['price']
    bc_24h_spot = b_spot[sym]['change_24h']     
    bc_24h_fut = b_fut[sym]['change_24h']      

    # Get spot and futures prices + 24h change for Bybit
    ys = y_spot[sym]['price']
    yf = y_fut[sym]['price']
    yb_24h_spot = y_spot[sym]['change_24h']   
    yb_24h_fut = y_fut[sym]['change_24h']      

    # Calculate the percentage difference between futures and spot (for Binance and Bybit)
    diff_b = ((bf - bs) / bs) * 100 if bs != 0 else 0
    diff_y = ((yf - ys) / ys) * 100 if ys != 0 else 0

    # Add one row of data to the results list (used later to render the table)
    results.append({
        'symbol': sym,
        'bnc_spot': bs,
        'bnc_fut': bf,
        'diff_bnc': diff_b,
        'change_24h_spot_bnc': bc_24h_spot,    
        'change_24h_fut_bnc': bc_24h_fut, 
        'bbt_spot': ys,
        'bbt_fut': yf,
        'diff_bbt': diff_y,
        'change_24h_spot_bbt': yb_24h_spot,   
        'change_24h_fut_bbt': yb_24h_fut,     
        'trade': get_trade_action(bs, bf, bc_24h_spot, bc_24h_fut)
    })

    # Sort the results list in descending order so that symbols with the largest Binance spot-futures percentage difference come first
    results.sort(key=lambda x: x['diff_bnc'], reverse=True)

    # Render the HTML template to the browser, passing in the sorted data
    return render_template_string(TEMPLATE, data=results)

# Run the Flask app in debug mode
if __name__ == "__main__":
    app.run(debug=True)
