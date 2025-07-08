from flask import Flask, render_template_string
import requests
import pandas as pd

app = Flask(__name__)

def fetch_binance():
    url_spot = "https://api.binance.com/api/v3/ticker/24hr"
    url_futures = "https://fapi.binance.com/fapi/v1/ticker/24hr"
    spot_data = requests.get(url_spot).json()
    futures_data = requests.get(url_futures).json()
    return spot_data, futures_data

def fetch_bybit():
    url_spot = "https://api.bybit.com/v2/public/tickers"
    url_futures = "https://api.bybit.com/v2/public/tickers?category=futures"
    spot_data = requests.get(url_spot).json()
    futures_data = requests.get(url_futures).json()
    return spot_data['result'], futures_data['result']

def filter_symbols(binance_spot, binance_futures, bybit_spot, bybit_futures):
    # We want only symbols with USDT or USDC suffix existing in both spot and futures
    bnc_spot_syms = {item['symbol'] for item in binance_spot if item['symbol'].endswith(('USDT', 'USDC'))}
    bnc_fut_syms = {item['symbol'] for item in binance_futures if item['symbol'].endswith(('USDT', 'USDC'))}
    bbt_spot_syms = {item['symbol'] for item in bybit_spot if item['symbol'].endswith(('USDT', 'USDC'))}
    bbt_fut_syms = {item['symbol'] for item in bybit_futures if item['symbol'].endswith(('USDT', 'USDC'))}

    bnc_common = bnc_spot_syms.intersection(bnc_fut_syms)
    bbt_common = bbt_spot_syms.intersection(bbt_fut_syms)
    common_symbols = bnc_common.intersection(bbt_common)
    return common_symbols

def build_dataframe(binance_spot, binance_futures, bybit_spot, bybit_futures, symbols):
    def find_data(data_list, symbol):
        for d in data_list:
            if d['symbol'] == symbol:
                return d
        return None

    rows = []
    for sym in symbols:
        bnc_spot = find_data(binance_spot, sym)
        bnc_fut = find_data(binance_futures, sym)
        bbt_spot = find_data(bybit_spot, sym)
        bbt_fut = find_data(bybit_futures, sym)

        # Skip if any data missing
        if not all([bnc_spot, bnc_fut, bbt_spot, bbt_fut]):
            continue

        try:
            bnc_spot_price = float(bnc_spot['lastPrice'])
            bnc_fut_price = float(bnc_fut['lastPrice'])
            bnc_spot_change = float(bnc_spot['priceChangePercent'])
            bnc_fut_change = float(bnc_fut['priceChangePercent'])

            bbt_spot_price = float(bbt_spot['last_price'])
            bbt_fut_price = float(bbt_fut['last_price'])
            bbt_spot_change = float(bbt_spot['price_24h_p'])
            bbt_fut_change = float(bbt_fut['price_24h_p'])

            diff_bnc = 100 * (bnc_fut_price - bnc_spot_price) / bnc_spot_price
            diff_bbt = 100 * (bbt_fut_price - bbt_spot_price) / bbt_spot_price

            rows.append({
                'Symbol': sym,
                'Bnc Spot': bnc_spot_price,
                'Bnc Futures': bnc_fut_price,
                'Diff % (Bnc)': round(diff_bnc, 3),
                'Δ24h (Bnc) Spot': round(bnc_spot_change, 3),
                'Δ24h (Bnc) Futures': round(bnc_fut_change, 3),
                'Bbt Spot': bbt_spot_price,
                'Bbt Futures': bbt_fut_price,
                'Diff % (Bbt)': round(diff_bbt, 3),
                'Δ24h (Bbt) Spot': round(bbt_spot_change, 3),
                'Δ24h (Bbt) Futures': round(bbt_fut_change, 3),
            })
        except (ValueError, KeyError):
            continue

    df = pd.DataFrame(rows)
    return df

def get_recommendation(row):
    recs = []

    if row['Diff % (Bnc)'] > 0.2:
        recs.append("Buy futures long (Bnc)")
    elif row['Diff % (Bnc)'] < -0.2:
        recs.append("Short futures (Bnc)")

    if row['Diff % (Bbt)'] > 0.2:
        recs.append("Buy futures long (Bbt)")
    elif row['Diff % (Bbt)'] < -0.2:
        recs.append("Short futures (Bbt)")

    if row['Δ24h (Bnc) Spot'] > 0:
        recs.append("Buy spot (Bnc)")
    elif row['Δ24h (Bnc) Spot'] < 0:
        recs.append("Sell or avoid spot (Bnc)")

    if row['Δ24h (Bbt) Spot'] > 0:
        recs.append("Buy spot (Bbt)")
    elif row['Δ24h (Bbt) Spot'] < 0:
        recs.append("Sell or avoid spot (Bbt)")

    if (row['Δ24h (Bnc) Futures'] > 0) and (row['Diff % (Bnc)'] > 0):
        recs.append("Strong buy futures (Bnc)")

    if (row['Δ24h (Bbt) Futures'] > 0) and (row['Diff % (Bbt)'] > 0):
        recs.append("Strong buy futures (Bbt)")

    if (row['Δ24h (Bnc) Futures'] < 0) and (row['Diff % (Bnc)'] < 0):
        recs.append("Strong short futures (Bnc)")

    if (row['Δ24h (Bbt) Futures'] < 0) and (row['Diff % (Bbt)'] < 0):
        recs.append("Strong short futures (Bbt)")

    if not recs:
        return "No signal"

    return "; ".join(recs)

@app.route('/')
def index():
    # Fetch data
    bnc_spot, bnc_fut = fetch_binance()
    bbt_spot, bbt_fut = fetch_bybit()

    symbols = filter_symbols(bnc_spot, bnc_fut, bbt_spot, bbt_fut)
    df = build_dataframe(bnc_spot, bnc_fut, bbt_spot, bbt_fut, symbols)

    df['Recommendation'] = df.apply(get_recommendation, axis=1)

    # Prepare data for rendering
    data = df.to_dict(orient='records')

    # HTML template with colored columns and two tables
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Crypto Spot vs Futures Comparison</title>
        <style>
            table {border-collapse: collapse; width: 100%; margin-bottom: 40px;}
            th, td {border: 1px solid #ddd; padding: 8px; text-align: center;}
            th {background-color: #333; color: white;}
            .blue-bg {background-color: #cce5ff; color: #004085; font-weight: bold;}
            .yellow-bg {background-color: #fff3cd; color: #856404; font-weight: bold;}
            .green-bg {background-color: #d4edda; color: #155724;}
        </style>
    </head>
    <body>
        <h1>Crypto Spot vs Futures Comparison</h1>

        <table>
            <thead>
                <tr>
                    <th>Symbol</th>
                    <th>Bnc Spot</th>
                    <th>Bnc Futures</th>
                    <th class="blue-bg">Diff % (Bnc)</th>
                    <th class="yellow-bg">Δ24h (Bnc) Spot</th>
                    <th class="yellow-bg">Δ24h (Bnc) Futures</th>
                    <th>Bbt Spot</th>
                    <th>Bbt Futures</th>
                    <th class="blue-bg">Diff % (Bbt)</th>
                    <th class="yellow-bg">Δ24h (Bbt) Spot</th>
                    <th class="yellow-bg">Δ24h (Bbt) Futures</th>
                </tr>
            </thead>
            <tbody>
            {% for row in data %}
                <tr>
                    <td>{{ row['Symbol'] }}</td>
                    <td>{{ "%.6f"|format(row['Bnc Spot']) }}</td>
                    <td>{{ "%.6f"|format(row['Bnc Futures']) }}</td>
                    <td class="blue-bg">{{ row['Diff % (Bnc)'] }}%</td>
                    <td class="yellow-bg">{{ row['Δ24h (Bnc) Spot'] }}%</td>
                    <td class="yellow-bg">{{ row['Δ24h (Bnc) Futures'] }}%</td>
                    <td>{{ "%.6f"|format(row['Bbt Spot']) }}</td>
                    <td>{{ "%.6f"|format(row['Bbt Futures']) }}</td>
                    <td class="blue-bg">{{ row['Diff % (Bbt)'] }}%</td>
                    <td class="yellow-bg">{{ row['Δ24h (Bbt) Spot'] }}%</td>
                    <td class="yellow-bg">{{ row['Δ24h (Bbt) Futures'] }}%</td>
                </tr>
            {% endfor %}
            </tbody>
        </table>

        <h2>Recommendations</h2>
        <table>
            <thead>
                <tr>
                    <th>Symbol</th>
                    <th>Recommendation</th>
                </tr>
            </thead>
            <tbody>
            {% for row in data %}
                <tr>
                    <td>{{ row['Symbol'] }}</td>
                    <td class="green-bg">{{ row['Recommendation'] }}</td>
                </tr>
            {% endfor %}
            </tbody>
        </table>

    </body>
    </html>
    """

    return render_template_string(html, data=data)

if __name__ == "__main__":
    app.run(debug=True)
