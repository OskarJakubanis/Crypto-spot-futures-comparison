# Used Functions and Modules – Crypto Basis Comparison App

## **requests**
- **`requests.get(url).json()`** – Sends an HTTP GET request to the specified `url` and returns the response converted to a Python object (parsed from JSON).

---

## **flask**
- **`Flask(__name__)`** – Creates a Flask application instance; `__name__` helps Flask locate resources.
- **`@app.route("/")`** – A decorator that defines the endpoint for the home page (root URL).
- **`render_template_string(template, data=...)`** – Renders an HTML template directly from a string and injects the provided `data` (e.g., `results`).
- **`app.run(debug=True)`** – Starts the Flask development server in debug mode.

---

## **Data Structure Operations**
- **`set(keys) & set(keys)`** – Finds the intersection of symbol sets to get common trading pairs.
- **`sorted(iterable)`** – Sorts a list of symbols alphabetically.
- **`results.sort(key=lambda x: x['diff_bnc'], reverse=True)`** – Sorts the `results` list by Binance percentage difference in descending order.
- **`append()`** – Adds a new row (dictionary) to the `results` list.
- **`if symbol.endswith(('USDT', 'USDC'))`** – Filters trading pairs ending with USDT or USDC.
- **`float(value)`** – Converts string values from the API to floating-point numbers.
- **`((fut - spot) / spot) * 100 if spot != 0 else 0`** – Calculates the percentage difference between futures and spot prices (avoids division by zero).
