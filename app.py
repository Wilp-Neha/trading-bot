from flask import Flask, jsonify, render_template_string, request, redirect, url_for
from flask_pymongo import PyMongo
from py5paisa import FivePaisaClient
from datetime import datetime

app = Flask(__name__)

# --- MongoDB Configuration ---
app.config["MONGO_URI"] = "mongodb+srv://tradinguser:9No99YJL1YAT71dM@cluster1.bv5s021.mongodb.net/tradingdb?retryWrites=true&w=majority"
mongo = PyMongo(app)

# --- 5Paisa Credentials ---
cred = {
    "APP_NAME": "5P53420117",
    "APP_SOURCE": "25774",
    "USER_ID": "EiQjGoK1oL5",
    "PASSWORD": "bM70U1eUchW",
    "USER_KEY": "j1XFKr6kUg0DAHgty85BLtZ1zCwxOr3B",
    "ENCRYPTION_KEY": "rqj6zhHtpX8iFG5KXDvyDerQAIXNw8ro"
}

client = FivePaisaClient(cred=cred)
with open("token.txt", "r") as f:
    token = f.read().strip()
client.get_oauth_session(token)

# --- Global Variables ---
algo_mode = False
algo_trades = []

# --- Strategy ---
def simple_strategy(price, stock):
    if price > 2500:
        return ("SELL", f"{stock} is overvalued, consider profit booking.")
    elif price < 2400:
        return ("BUY", f"{stock} is undervalued, good entry point.")
    else:
        return ("HOLD", f"{stock} is stable, maintain current position.")

# --- Stocks to monitor ---
market_feed = [
    {"Exch":"N","ExchType":"C","Symbol":"RELIANCE","Expiry":"","StrikePrice":"0","OptionType":""},
    {"Exch":"N","ExchType":"C","Symbol":"TCS","Expiry":"","StrikePrice":"0","OptionType":""},
    {"Exch":"N","ExchType":"C","Symbol":"INFY","Expiry":"","StrikePrice":"0","OptionType":""}
]

# --- Base HTML Template with styling ---
base_html = """
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>{{ title }}</title>
  <style>
    body {
        font-family: 'Segoe UI', sans-serif;
        background-color: #0d1117;
        color: #c9d1d9;
        margin: 0;
        padding: 0;
    }
    header {
        background-color: #161b22;
        padding: 10px 20px;
        display: flex;
        justify-content: space-between;
        align-items: center;
        color: #58a6ff;
    }
    nav a {
        color: #58a6ff;
        margin-right: 15px;
        text-decoration: none;
        font-weight: 500;
    }
    nav a:hover {
        text-decoration: underline;
    }
    table {
        border-collapse: collapse;
        width: 80%;
        margin: 20px auto;
        background-color: #161b22;
    }
    th, td {
        border: 1px solid #30363d;
        padding: 12px;
        text-align: center;
    }
    th {
        background-color: #21262d;
    }
    tr:hover {
        background-color: #21262d;
    }
    .buy { color: #00c853; }
    .sell { color: #ff1744; }
    .hold { color: #ffb300; }
    .container {
        width: 90%;
        margin: auto;
        padding: 20px;
    }
    h2 { color: #58a6ff; text-align: center; }
    footer {
        text-align: center;
        padding: 15px;
        color: #8b949e;
        border-top: 1px solid #30363d;
        margin-top: 30px;
    }
    .button {
        background-color: #238636;
        color: white;
        padding: 8px 15px;
        border: none;
        border-radius: 5px;
        cursor: pointer;
    }
    .button:hover { background-color: #2ea043; }
  </style>
</head>
<body>
  <header>
    <div><b>📈 Trading Bot Dashboard</b></div>
    <nav>
      <a href="/">Home</a>
      <a href="/dashboard">Dashboard</a>
      <a href="/advisory">Advisory</a>
      <a href="/copytrading">Copy Trading</a>
      <a href="/algotrading">Algo Trading</a>
      <a href="/portfolio">Portfolio</a>
      <a href="/history">History</a>
    </nav>
  </header>

  <div class="container">
    {{ content | safe }}
  </div>

  <footer>
    © 2025 Automated Trading System | Flask + 5Paisa + MongoDB
  </footer>
</body>
</html>
"""

# --- Routes ---

@app.route("/")
def home():
    content = """
    <h2>Welcome to the Automated Trading & Advisory System</h2>
    <p style='text-align:center;'>Monitor live markets, run trading strategies, simulate copy trades, and manage your portfolio — all in one place.</p>
    """
    return render_template_string(base_html, title="Home", content=content)

@app.route("/dashboard")
def dashboard():
    try:
        res = client.fetch_market_feed(market_feed)
        if not res or "Data" not in res:
            content = "<h2>⚠️ Token expired or data unavailable.</h2><p>Please refresh your token.</p>"
            return render_template_string(base_html, title="Dashboard", content=content)

        rows = ""
        for s in res["Data"]:
            price = s["LastRate"]
            sig, _ = simple_strategy(price, s["Symbol"])
            rows += f"<tr><td>{s['Symbol']}</td><td>{price}</td><td class='{sig.lower()}'>{sig}</td></tr>"

        content = f"""
        <h2>Trading Dashboard</h2>
        <table>
          <tr><th>Stock</th><th>Price</th><th>Signal</th></tr>
          {rows}
        </table>
        """
        return render_template_string(base_html, title="Dashboard", content=content)
    except Exception as e:
        return render_template_string(base_html, title="Error", content=f"<h2>Error: {e}</h2>")

@app.route("/advisory")
def advisory():
    res = client.fetch_market_feed(market_feed)
    if not res or "Data" not in res:
        content = "<h2>⚠️ Token expired or data unavailable.</h2>"
        return render_template_string(base_html, title="Advisory", content=content)

    items = ""
    for s in res["Data"]:
        price = s["LastRate"]
        sig, msg = simple_strategy(price, s["Symbol"])
        items += f"<li><b>{s['Symbol']}</b> → {sig} (₹{price}) → {msg}</li>"

    content = f"""
    <h2>Market Advisory Report</h2>
    <ul>{items}</ul>
    """
    return render_template_string(base_html, title="Advisory", content=content)

@app.route("/portfolio")
def portfolio():
    holdings = [
        {"stock":"RELIANCE","qty":10,"buy_price":2400,"current_price":2450},
        {"stock":"TCS","qty":5,"buy_price":3500,"current_price":3550},
        {"stock":"INFY","qty":8,"buy_price":1400,"current_price":1380}
    ]
    for h in holdings:
        h["pl"] = round((h["current_price"] - h["buy_price"]) * h["qty"], 2)

    rows = "".join([
        f"<tr><td>{h['stock']}</td><td>{h['qty']}</td><td>{h['buy_price']}</td><td>{h['current_price']}</td><td style='color:{'green' if h['pl']>=0 else 'red'}'>{h['pl']}</td></tr>"
        for h in holdings
    ])
    content = f"""
    <h2>Portfolio Overview</h2>
    <table>
      <tr><th>Stock</th><th>Qty</th><th>Buy Price</th><th>Current Price</th><th>P/L</th></tr>
      {rows}
    </table>
    """
    return render_template_string(base_html, title="Portfolio", content=content)

@app.route("/history")
def history():
    trades = list(mongo.db.trades.find().sort("_id", -1))
    rows = "".join([
        f"<tr><td>{t.get('stock','')}</td><td>{t.get('signal','')}</td><td>{t.get('price','')}</td><td>{t.get('timestamp','')}</td></tr>"
        for t in trades
    ])
    content = f"""
    <h2>Trade History (MongoDB)</h2>
    <table>
      <tr><th>Stock</th><th>Signal</th><th>Price</th><th>Timestamp</th></tr>
      {rows}
    </table>
    """
    return render_template_string(base_html, title="History", content=content)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
