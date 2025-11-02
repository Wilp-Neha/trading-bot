from flask import Flask, jsonify, render_template_string, request, redirect, url_for
from flask_pymongo import PyMongo
from py5paisa import FivePaisaClient
from datetime import datetime

app = Flask(__name__)

# --- MongoDB Configuration ---
app.config["MONGO_URI"] = "mongodb+srv://tradinguser:9No99YJL1YAT71dM@cluster1.bv5s021.mongodb.net/tradingdb?retryWrites=true&w=majority"
mongo = PyMongo(app)

# --- Test Route ---
@app.route("/testdb")
def testdb():
    try:
        mongo.db.trades.insert_one({"name": "test_trade", "profit": 500})
        return "✅ Successfully connected to MongoDB and inserted test record!"
    except Exception as e:
        return f"❌ MongoDB error: {e}"

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


# Global variables for algo mode & trade log
algo_mode = False
algo_trades = []

# Simple strategy with advisory messages
def simple_strategy(price, stock):
    if price > 2500:
        return ("SELL", f"{stock} is overvalued, consider profit booking.")
    elif price < 2400:
        return ("BUY", f"{stock} is undervalued, good entry point.")
    else:
        return ("HOLD", f"{stock} is stable, maintain current position.")

# Sample stocks list
market_feed = [
    {"Exch":"N","ExchType":"C","Symbol":"RELIANCE","Expiry":"","StrikePrice":"0","OptionType":""},
    {"Exch":"N","ExchType":"C","Symbol":"TCS","Expiry":"","StrikePrice":"0","OptionType":""},
    {"Exch":"N","ExchType":"C","Symbol":"INFY","Expiry":"","StrikePrice":"0","OptionType":""}
]

# Homepage
@app.route("/")
def home():
    html = """
    <html>
    <head><title>Trading Bot</title></head>
    <body>
      <h1>Welcome to Automated Market Advisory System</h1>
      <ul>
        <li><a href='/market_status'>Market Status</a></li>
        <li><a href='/signals'>Trading Signals (JSON)</a></li>
        <li><a href='/dashboard'>Dashboard (Table)</a></li>
        <li><a href='/advisory'>Market Advisory Report</a></li>
        <li><a href='/copytrading'>Copy Trading Simulation</a></li>
        <li><a href='/algotrading'>Algo Trading</a></li>
        <li><a href='/portfolio'>Portfolio</a></li>
        <li><a href='/history'>Trade History</a></li>
      </ul>
    </body>
    </html>
    """
    return html

# Market Status JSON
@app.route("/market_status")
def market_status():
    status = client.get_market_status()
    return jsonify(status)

# Trading Signals JSON
# --- Trading Signals JSON ---
@app.route("/signals")
def signals():
    res = client.fetch_market_feed(market_feed)
    output = []

    for s in res["Data"]:
        price = s["LastRate"]
        sig, msg = simple_strategy(price, s["Symbol"])
        trade_data = {
            "stock": s["Symbol"],
            "price": price,
            "signal": sig,
            "advice": msg,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        output.append(trade_data)

        # ✅ Save only BUY/SELL signals
        if sig in ["BUY", "SELL"]:
            mongo.db.trades.insert_one(trade_data)

    return jsonify({"data": output})

# Dashboard HTML
@app.route("/dashboard")
def dashboard():
    res = client.fetch_market_feed(market_feed)
    output = []
    for s in res["Data"]:
        price = s["LastRate"]
        sig, msg = simple_strategy(price, s["Symbol"])
        output.append({"stock": s["Symbol"], "price": price, "signal": sig})

    html = """
    <html>
    <head><title>Trading Dashboard</title></head>
    <body>
      <h2>Trading Dashboard</h2>
      <table border="1" cellpadding="10">
        <tr><th>Stock</th><th>Price</th><th>Signal</th></tr>
        {% for row in data %}
        <tr>
          <td>{{ row.stock }}</td>
          <td>{{ row.price }}</td>
          <td style="color: {% if row.signal=='BUY' %}green{% elif row.signal=='SELL' %}red{% else %}orange{% endif %};">
            {{ row.signal }}
          </td>
        </tr>
        {% endfor %}
      </table>
      <br>
      <a href='/'>Back to Home</a>
    </body>
    </html>
    """
    return render_template_string(html, data=output)

# Advisory Page
@app.route("/advisory")
def advisory():
    res = client.fetch_market_feed(market_feed)
    output = []
    for s in res["Data"]:
        price = s["LastRate"]
        sig, msg = simple_strategy(price, s["Symbol"])
        output.append({"stock": s["Symbol"], "price": price, "signal": sig, "advice": msg})

    html = """
    <html>
    <head><title>Market Advisory</title></head>
    <body>
      <h2>Market Advisory Report</h2>
      <ul>
        {% for row in data %}
          <li><b>{{ row.stock }}</b> → {{ row.signal }} (Price: {{ row.price }}) → {{ row.advice }}</li>
        {% endfor %}
      </ul>
      <br>
      <a href='/'>Back to Home</a>
    </body>
    </html>
    """
    return render_template_string(html, data=output)

# Copy Trading Simulation
@app.route("/copytrading")
def copytrading():
    res = client.fetch_market_feed(market_feed)
    master_trades = []
    for s in res["Data"]:
        price = s["LastRate"]
        sig, msg = simple_strategy(price, s["Symbol"])
        master_trades.append({"stock": s["Symbol"], "price": price, "signal": sig})

    # Simulate 2 followers copying master
    followers = ["UserA", "UserB"]
    copied_trades = []
    for t in master_trades:
        copied_trades.append({"trader":"Master","stock":t["stock"],"action":t["signal"],"price":t["price"],"status":"Executed"})
        for f in followers:
            copied_trades.append({"trader":f,"stock":t["stock"],"action":t["signal"],"price":t["price"],"status":"Copied"})

    html = """
    <html>
    <head><title>Copy Trading</title></head>
    <body>
      <h2>Copy Trading Dashboard</h2>
      <table border="1" cellpadding="10">
        <tr><th>Trader</th><th>Stock</th><th>Action</th><th>Price</th><th>Status</th></tr>
        {% for row in trades %}
        <tr>
          <td>{{ row.trader }}</td>
          <td>{{ row.stock }}</td>
          <td>{{ row.action }}</td>
          <td>{{ row.price }}</td>
          <td>{{ row.status }}</td>
        </tr>
        {% endfor %}
      </table>
      <br>
      <a href='/'>Back to Home</a>
    </body>
    </html>
    """
    return render_template_string(html, trades=copied_trades)

# Algo Trading Page
@app.route("/algotrading", methods=["GET", "POST"])
def algotrading():
    global algo_mode, algo_trades

    if request.method == "POST":
        mode = request.form.get("mode")
        algo_mode = (mode == "ON")
        return redirect(url_for("algotrading"))

    res = client.fetch_market_feed(market_feed)
    for s in res["Data"]:
        price = s["LastRate"]
        sig, msg = simple_strategy(price, s["Symbol"])
        if algo_mode and sig in ["BUY", "SELL"]:
            algo_trades.append({"stock": s["Symbol"], "price": price, "action": sig, "status": "Executed"})

    html = """
    <html>
    <head><title>Algo Trading</title></head>
    <body>
      <h2>Algo Trading Dashboard</h2>
      <form method="post">
        <label>Algo Mode: </label>
        <select name="mode" onchange="this.form.submit()">
          <option value="OFF" {% if not algo_mode %}selected{% endif %}>OFF</option>
          <option value="ON" {% if algo_mode %}selected{% endif %}>ON</option>
        </select>
      </form>
      <br>
      <table border="1" cellpadding="10">
        <tr><th>Stock</th><th>Action</th><th>Price</th><th>Status</th></tr>
        {% for row in trades %}
        <tr>
          <td>{{ row.stock }}</td>
          <td>{{ row.action }}</td>
          <td>{{ row.price }}</td>
          <td>{{ row.status }}</td>
        </tr>
        {% endfor %}
      </table>
      <br>
      <a href='/'>Back to Home</a>
    </body>
    </html>
    """
    return render_template_string(html, algo_mode=algo_mode, trades=algo_trades)

# Portfolio Page (Mock Holdings)
@app.route("/portfolio")
def portfolio():
    holdings = [
        {"stock":"RELIANCE","qty":10,"buy_price":2400,"current_price":2450},
        {"stock":"TCS","qty":5,"buy_price":3500,"current_price":3550},
        {"stock":"INFY","qty":8,"buy_price":1400,"current_price":1380}
    ]

    for h in holdings:
        h["pl"] = round((h["current_price"] - h["buy_price"]) * h["qty"], 2)

    html = """
    <html>
    <head><title>Portfolio</title></head>
    <body>
      <h2>Portfolio (Mock)</h2>
      <table border="1" cellpadding="10">
        <tr><th>Stock</th><th>Quantity</th><th>Buy Price</th><th>Current Price</th><th>P/L</th></tr>
        {% for h in holdings %}
        <tr>
          <td>{{ h.stock }}</td>
          <td>{{ h.qty }}</td>
          <td>{{ h.buy_price }}</td>
          <td>{{ h.current_price }}</td>
          <td style="color:{% if h.pl>=0 %}green{% else %}red{% endif %}">{{ h.pl }}</td>
        </tr>
        {% endfor %}
      </table>
      <br>
      <a href='/'>Back to Home</a>
    </body>
    </html>
    """
    return render_template_string(html, holdings=holdings)

# Trade History (Mock Data)
@app.route("/history")
def history():
    trades = list(mongo.db.trades.find().sort("_id", -1))  # Latest first

    html = """
    <html>
    <head><title>Trade History</title></head>
    <body>
      <h2>Trade History (MongoDB)</h2>
      <table border="1" cellpadding="10">
        <tr><th>Stock</th><th>Action</th><th>Price</th><th>Timestamp</th></tr>
        {% for t in trades %}
        <tr>
          <td>{{ t.stock }}</td>
          <td>{{ t.signal }}</td>
          <td>{{ t.price }}</td>
          <td>{{ t.timestamp }}</td>
        </tr>
        {% endfor %}
      </table>
      <br>
      <a href='/'>Back to Home</a>
    </body>
    </html>
    """
    return render_template_string(html, trades=trades)

if __name__ == "__main__":
    print(app.url_map)  # just for confirmation
    app.run(host="0.0.0.0", port=5000, debug=True)


