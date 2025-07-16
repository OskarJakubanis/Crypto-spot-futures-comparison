# 🚀 Crypto Spot vs Futures Price Comparison 📈

This project is a lightweight web dashboard that compares the basis (futures - spot) for cryptocurrencies traded on Binance and Bybit.
It helps identify potential arbitrage opportunities and provides market insight for USDT/USDC pairs.

---

## 🎯 Project Goals

- Compare **spot vs futures** prices from Binance and Bybit.
- Compute **basis (% difference)** between markets.
- Display **24h price change** and suggest potential trade directions.
- Provide a clean, browser-based **dashboard** using Flask and Jinja.

---

## 🛠 Technologies Used

- Python 3.9+
- Flask (for web server and HTML rendering)
- Requests (for API calls)
- Jinja2 (Flask’s built-in templating engine)

Dependencies are listed in [`requirements.txt`](./requirements.txt).

---

## 📁 File Overview

- `crypto_compare1.py` – Main app – fetches prices, computes % differences, renders the table  
- `requirements.txt` – Python packages needed to run the app  
- `README.md` – Project overview and usage instructions

---

## 🚀 How to Run

1. Clone the repository.
2. Install requirements: pip install -r requirements.txt.
3. Run the app: python crypto_compare.py.
4. Visit in your browser: http://127.0.0.1:5000.

---

## 💡 Example
![KRYPTO](https://github.com/user-attachments/assets/b88c3208-68b7-427a-b2dc-a8cd22831e58)


---

## 🧠 Logic Summary: How to Interpret Trading Signals?
Based on the difference between spot and futures prices and the 24-hour price changes, the app provides simple trading recommendations.

| Condition                                          | Recommendation    | What It Means                           |
|---------------------------------------------------|-------------------|----------------------------------------|
| Futures > Spot by more than 0.5% **and** futures 24h change > 0 | Buy Futures       | Bullish market, buy futures contracts  |
| Futures < Spot by more than 0.5% **and** futures 24h change < 0 | Short Futures     | Bearish market, short futures contracts|
| Spot 24h change > 0 **and** futures vs spot difference < 0.5%    | Buy Spot          | Market rising but futures close to spot, buy spot |
| Spot 24h change < 0                                | Avoid or Sell Spot | Market falling, avoid or sell spot      |

---

## 📬 Contact

Questions, suggestions or want to collaborate? Open an issue or connect directly.
Feel free to expand it with more exchanges or features! Good luck and happy trading! 💰🔥
