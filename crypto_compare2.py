from flask import Flask
import requests
import pandas as pd

app = Flask(__name__)

def fetch_binance_data():
    url_spot = "https://api.binance.com/api/v3/ticker/price"
    url_futures = "https://fapi.binance.com/fapi/v1/ticker/price"

    # Pobierz ceny spot
    spot_resp = requests.get(url_spot)
    spot_data = spot_resp.json()

    # Pobierz ceny futures
    futures_resp = requests.get(url_futures)
    futures_data = futures_resp.json()

    # Filtrujemy tylko symbole kończące się na USDT lub USDC
    spot_dict = {item['symbol']: float(item['price']) for item in spot_data if item['symbol'].endswith(('USDT','USDC'))}
    futures_dict = {item['symbol']: float(item['price']) for item in futures_data if item['symbol'].endswith(('USDT','USDC'))}

    return spot_dict, futures_dict

def fetch_bybit_data():
    url_spot = "https://api.bybit.com/spot/v1/symbols"
    url_futures = "https://api.bybit.com/derivatives/v3/public/tickers"

    # Pobierz spot symbols (potem ich ceny)
    spot_resp = requests.get(url_spot)
    spot_symbols = [item['name'] for item in spot_resp.json().get('result', []) if item['name'].endswith(('USDT','USDC'))]

    spot_prices = {}
    # Bybit spot ceny są na https://api.bybit.com/spot/quote/v1/ticker/price?symbol=XXX
    for symbol in spot_symbols:
        price_resp = requests.get(f"https://api.bybit.com/spot/quote/v1/ticker/price?symbol={symbol}")
        price_data = price_resp.json()
        if price_data.get('retCode') == 0:
            spot_prices[symbol] = float(price_data['result']['price'])

    # Pobierz futures dane
    futures_resp = requests.get(url_futures)
    futures_data = futures_resp.json()

    futures_prices = {}
    for item in futures_data.get('result', []):
        symbol = item['symbol']
        if symbol.endswith(('USDT','USDC')):
            futures_prices[symbol] = float(item['lastPrice'])

    return spot_prices, futures_prices

def prepare_dataframe():
    # Pobieramy dane z obu API
    bnc_spot, bnc_futures = fetch_binance_data()
    bbt_spot, bbt_futures = fetch_bybit_data()

    # Zbierz wszystkie symbole (unifikujemy listę)
    symbols = set(list(bnc_spot.keys()) + list(bnc_futures.keys()) + list(bbt_spot.keys()) + list(bbt_futures.keys()))

    rows = []
    for sym in symbols:
        bnc_spot_price = bnc_spot.get(sym, 0)
        bnc_futures_price = bnc_futures.get(sym, 0)
        bbt_spot_price = bbt_spot.get(sym, 0)
        bbt_futures_price = bbt_futures.get(sym, 0)

        # Oblicz różnice procentowe (unikamy dzielenia przez 0)
        def diff_pct(futures, spot):
            if spot > 0:
                return round((futures - spot) / spot * 100, 2)
            else:
                return 0.0

        diff_bnc = diff_pct(bnc_futures_price, bnc_spot_price)
        diff_bbt = diff_pct(bbt_futures_price, bbt_spot_price)

        rows.append({
            'Symbol': sym,
            'Bnc Spot': bnc_spot_price,
            'Bnc Futures': bnc_futures_price,
            'Diff % (Bnc)': diff_bnc,
            'Bbt Spot': bbt_spot_price,
            'Bbt Futures': bbt_futures_price,
            'Diff % (Bbt)': diff_bbt
        })

    df = pd.DataFrame(rows)

    # Dodajemy kolumnę decyzji (możesz tu podmienić logikę)
    def decyzja(row):
        if row['Diff % (Bnc)'] > 5:
            return 'Kupuj futures (Bnc)'
        elif row['Diff % (Bnc)'] < -5:
            return 'Sprzedaj futures (Bnc)'
        elif row['Diff % (Bbt)'] > 5:
            return 'Kupuj futures (Bbt)'
        elif row['Diff % (Bbt)'] < -5:
            return 'Sprzedaj futures (Bbt)'
        else:
            return 'Brak sygnału'

    df['Decyzja'] = df.apply(decyzja, axis=1)

    return df.sort_values(by='Diff % (Bnc)', ascending=False).reset_index(drop=True)

def color_diff(val):
    if val > 0:
        return 'color: blue; font-weight: bold;'
    elif val < 0:
        return 'color: orange; font-weight: bold;'
    else:
        return ''

def color_decyzja(val):
    if 'Kupuj' in val:
        return 'background-color: lightgreen; font-weight: bold;'
    elif 'Sprzedaj' in val:
        return 'background-color: #f08080; font-weight: bold;'  # light red
    else:
        return ''

@app.route('/')
def index():
    df = prepare_dataframe()

    styled = (df.style
              .applymap(color_diff, subset=['Diff % (Bnc)', 'Diff % (Bbt)'])
              .applymap(color_decyzja, subset=['Decyzja'])
              .set_properties(**{'text-align': 'center'})
              .set_table_styles([dict(selector='th', props=[('text-align', 'center')])])
              .render())

    html = f"""
    <html>
    <head>
        <title>Top Futures Spot Diff</title>
        <style>
            table {{ border-collapse: collapse; width: 100%; }}
            th, td {{ border: 1px solid #ddd; padding: 8px; }}
            th {{ background-color: #f2f2f2; }}
        </style>
    </head>
    <body>
        <h2>Top Futures Spot Diff - Binance vs Bybit</h2>
        {styled}
    </body>
    </html>
    """
    return html

if __name__ == '__main__':
    app.run(debug=True)
