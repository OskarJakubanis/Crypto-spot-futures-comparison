# 🚀 Crypto Spot vs Futures Price Comparison 📈

This project is a simple Flask web app that compares **spot** and **futures** prices from two of the biggest crypto platforms: **Binance** and **Bybit**. It shows you a handy table with current prices and the difference between spot and futures for both platforms.

## 💡 What It Does

- 🔍 Fetches spot and futures prices from Binance & Bybit APIs  
- 🔄 Filters symbols ending with **USDT** or **USDC**  
- 📊 Displays a table with these columns:
  - Symbol
  - Binance Spot Price
  - Binance Futures Price
  - Bybit Spot Price
  - Bybit Futures Price
  - % Difference (Binance futures vs spot)
  - % Difference (Bybit futures vs spot)

### 📈 Why It Matters?

- A **higher positive difference** means futures prices are above spot prices → usually a bullish sign, market expects prices to rise 🚀  
- A **negative difference** means futures prices are below spot prices → could signal bearish sentiment, market expects a drop 📉  

This info can help you make smarter trading decisions and understand market sentiment better! 🎯

## ⚙️ How to Run

1. Make sure you have Python (3.7+) installed 🐍  
2. Install dependencies with: pip install -r requirements.txt
3. Run the app: python crypto_compare.py
4. Open your browser and go to:
   👉 **[http://127.0.0.1:5000/](http://127.0.0.1:5000/)** (This is your local address where the app runs. Every user running it locally will use the same link on their own machine.)  
5. Refresh the page whenever you want the latest prices 🔄

---

Feel free to expand it with more exchanges or features! Good luck and happy trading! 💰🔥

---

**Please contact me with any questions, suggestions, or feedback!** I’m happy to help and improve this tool. 😊
