from flask import Flask, jsonify, render_template_string, request, redirect, url_for, session
from flask_pymongo import PyMongo
from py5paisa import FivePaisaClient
from datetime import datetime
from functools import wraps
import logging

app = Flask(__name__)
app.secret_key = "replace_this_with_a_secure_random_key"

# --- MongoDB Configuration ---
app.config["MONGO_URI"] = "mongodb+srv://tradinguser:9No99YJL1YAT71dM@cluster1.bv5s021.mongodb.net/tradingdb?retryWrites=true&w=majority"
mongo = PyMongo(app)

# --- Configure structured logging ---
logging.basicConfig(
    format='%(levelname)s | %(asctime)s | %(message)s',
    level=logging.INFO,
    datefmt='%Y-%m-%d %H:%M:%S'
)
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
try:
    with open("token.txt", "r") as f:
        token = f.read().strip()
    client.get_oauth_session(token)
    app.logger.info("Logged in!!")
except Exception:
    app.logger.warning("⚠️ 5Paisa token missing or expired.")

# --- Login setup ---
DEMO_USER = "admin"
DEMO_PASS = "admin123"

def login_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if not session.get("logged_in"):
            app.logger.warning(f"WARNING | ACCESS | Unauthorized access attempt to {request.path}")
            return redirect(url_for("login"))
        app.logger.info(f"INFO | ACCESS | User accessing {request.path}")
        return f(*args, **kwargs)
    return wrapper

# --- Shared Base Layout ---
BASE_HTML = """
<!doctype html>
<html>
<head>
  <meta charset="utf-8">
  <title>{{ title or "Market Advisory System" }}</title>
  <meta name="viewport" content="width=device-width,initial-scale=1">
  <style>
    body {
      margin:0; padding:0;
      background: url('{{ bg_image }}') center/cover fixed no-repeat;
      font-family: 'Segoe UI', Roboto, sans-serif;
      color: #eaf6fb;
      min-height:100vh;
      display:flex;
      flex-direction:column;
    }
    header {
      background: rgba(0,0,0,0.6);
      padding: 14px 24px;
      display:flex;
      justify-content:space-between;
      align-items:center;
      box-shadow: 0 2px 8px rgba(0,0,0,0.7);
    }
    .brand { font-weight:700; color:#00e5ff; font-size:18px; }
    nav a {
      color: #d9f4ff;
      margin-right:14px;
      text-decoration:none;
      font-size:14px;
    }
    nav a:hover { color:#00e5ff; }
    main {
      width:min(1100px,96%);
      margin:30px auto;
      background: rgba(0,0,0,0.55);
      padding:20px;
      border-radius:10px;
      box-shadow: 0 6px 20px rgba(0,0,0,0.6);
    }
    table { width:100%; border-collapse:collapse; color:#e8f7fb; }
    th, td { padding:10px; border-bottom:1px solid rgba(255,255,255,0.08); text-align:left; }
    th { color:#a9b8c4; font-size:13px; }
    .signal-buy { color:#00ff99; font-weight:700; }
    .signal-sell { color:#ff4d6d; font-weight:700; }
    .signal-hold { color:#ffc966; font-weight:700; }
    footer {
      margin-top:auto;
      padding:12px;
      text-align:center;
      font-size:14px;
      background:rgba(0,0,0,0.5);
      color:#9aa9b2;
    }
    .btn {
      background: linear-gradient(90deg,#00e5ff,#2efb85);
      border:none;
      padding:8px 12px;
      border-radius:6px;
      color:#002;
      font-weight:700;
      cursor:pointer;
    }
  </style>
</head>
<body>
  <header>
    <div class="brand">Automated Market Advisory System</div>
    <nav>
      {% if session.get('logged_in') %}
        <a href="{{ url_for('market_status') }}">Market Status</a>
        <a href="{{ url_for('signals') }}">Signals</a>
        <a href="{{ url_for('dashboard') }}">Dashboard</a>
        <a href="{{ url_for('advisory') }}">Advisory</a>
        <a href="{{ url_for('copytrading') }}">Copy Trading</a>
        <a href="{{ url_for('algotrading') }}">Algo Trading</a>
        <a href="{{ url_for('portfolio') }}">Portfolio</a>
        <a href="{{ url_for('history') }}">History</a>
        <a href="{{ url_for('logout') }}">Logout</a>
      {% endif %}
    </nav>
  </header>
  <main>
    {{ content|safe }}
  </main>
  <footer>
    <a href="mailto:wilpneha@gmail.com" style="color:#00e5ff;">wilpneha@gmail.com</a>
  </footer>
</body>
</html>
"""

# --- Login Page ---
@app.route("/login", methods=["GET", "POST"])
def login():
    bg = "https://wallpapercave.com/wp/wp8172895.jpg"
    error = None
    if request.method == "POST":
        if request.form["username"] == DEMO_USER and request.form["password"] == DEMO_PASS:
            session["logged_in"] = True
            return redirect(url_for("dashboard"))
        else:
            error = "Invalid credentials"
    html = """
    <div style="display:flex;justify-content:center;align-items:center;min-height:70vh;">
      <div style="background:rgba(0,0,0,0.5);padding:24px;border-radius:10px;width:360px;text-align:center;">
        <h2 style="color:#00e5ff;margin-bottom:10px;">User Login</h2>
        {% if error %}<p style="color:#ff4d6d;">{{ error }}</p>{% endif %}
        <form method="post">
          <input type="text" name="username" placeholder="Username" required style="width:100%;padding:10px;margin-bottom:10px;border-radius:6px;border:none;">
          <input type="password" name="password" placeholder="Password" required style="width:100%;padding:10px;margin-bottom:12px;border-radius:6px;border:none;">
          <button class="btn" type="submit">Login</button>
        </form>
      </div>
    </div>
    """
    content = render_template_string(html, error=error)
    return render_template_string(BASE_HTML, title="Login", content=content, bg_image=bg)

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

# --- Strategy ---
def simple_strategy(price, stock):
    if price > 2500:
        return ("SELL", f"{stock} is overvalued, consider profit booking.")
    elif price < 2400:
        return ("BUY", f"{stock} is undervalued, good entry point.")
    else:
        return ("HOLD", f"{stock} is stable, maintain current position.")

# --- Stocks list ---
market_feed = [
    {"Exch":"N","ExchType":"C","Symbol":s,"Expiry":"","StrikePrice":"0","OptionType":""}
    for s in ["RELIANCE","TCS","INFY","HDFCBANK","ICICIBANK","SBIN","LT","WIPRO"]
]

# --- Helpers ---
def safe_fetch(func, *args, **kwargs):
    try:
        return func(*args, **kwargs)
    except Exception as e:
        app.logger.warning(f"5Paisa fetch failed: {e}")
        return None

def get_inner_bg():
    return "https://img.freepik.com/premium-photo/black-modern-futuristic-trading-secret-thumbnail-background_769134-386.jpg"

@app.route("/")
def home():
    return redirect(url_for("login"))

@app.route("/market_status")
@login_required
def market_status():
    res = safe_fetch(client.get_market_status)
    if not res:
        content = "<h3>Market Status</h3><p style='color:#ff4d6d;'>Token expired or API unavailable.</p>"
    else:
        # Handle both dict and list formats
        if isinstance(res, dict):
            rows = "".join([f"<tr><td>{k}</td><td>{v}</td></tr>" for k, v in res.items()])
        elif isinstance(res, list):
            # List of markets
            rows = ""
            for item in res:
                for k, v in item.items():
                    rows += f"<tr><td>{k}</td><td>{v}</td></tr>"
                rows += "<tr><td colspan='2'><hr style='border:0;border-top:1px solid rgba(255,255,255,0.2);'></td></tr>"
        else:
            rows = "<tr><td colspan='2'>Unexpected data format</td></tr>"

        content = f"""
        <h2>Market Status</h2>
        <table>
          <thead><tr><th>Parameter</th><th>Value</th></tr></thead>
          <tbody>{rows}</tbody>
        </table>
        """
    return render_template_string(BASE_HTML, title="Market Status", content=content, bg_image=get_inner_bg())


# --- Signals Page ---
@app.route("/signals")
@login_required
def signals():
    res = safe_fetch(client.fetch_market_feed, market_feed)
    if not res or "Data" not in res:
        content = "<p>No signal data (token expired).</p>"
    else:
        rows = ""
        for s in res["Data"]:
            price = s["LastRate"]
            sig, msg = simple_strategy(price, s["Symbol"])
            color_class = "signal-buy" if sig=="BUY" else "signal-sell" if sig=="SELL" else "signal-hold"
            rows += f"<tr><td>{s['Symbol']}</td><td>{price}</td><td class='{color_class}'>{sig}</td><td>{msg}</td></tr>"
        content = f"<h2>Trading Signals</h2><table><thead><tr><th>Stock</th><th>Price</th><th>Signal</th><th>Advice</th></tr></thead><tbody>{rows}</tbody></table>"

         # ✅ Save only BUY/SELL signals
        if sig in ["BUY", "SELL"]:
            mongo.db.trades.insert_one(trade_data)
    return render_template_string(BASE_HTML, title="Signals", content=content, bg_image=get_inner_bg())

# --- Advisory ---
@app.route("/advisory")
@login_required
def advisory():
    res = safe_fetch(client.fetch_market_feed, market_feed)
    lines = []
    if res and "Data" in res:
        for s in res["Data"]:
            price = s["LastRate"]
            sig, msg = simple_strategy(price, s["Symbol"])
            lines.append(f"{s['Symbol']} → {sig} (Price: {price}) → {msg}")
    content = "<h2>Market Advisory Report</h2><ul>" + "".join([f"<li>{l}</li>" for l in lines]) + "</ul>"
    return render_template_string(BASE_HTML, title="Advisory", content=content, bg_image=get_inner_bg())

# --- Dashboard ---
@app.route("/dashboard")
@login_required
def dashboard():
    res = safe_fetch(client.fetch_market_feed, market_feed)
    if not res or "Data" not in res:
        content = "<p>No data.</p>"
    else:
        rows = ""
        for s in res["Data"]:
            price = s["LastRate"]
            sig, _ = simple_strategy(price, s["Symbol"])
            color_class = "signal-buy" if sig=="BUY" else "signal-sell" if sig=="SELL" else "signal-hold"
            rows += f"<tr><td>{s['Symbol']}</td><td>{price}</td><td class='{color_class}'>{sig}</td></tr>"
        content = f"<h2>Dashboard</h2><table><tr><th>Stock</th><th>Price</th><th>Signal</th></tr>{rows}</table>"
    return render_template_string(BASE_HTML, title="Dashboard", content=content, bg_image=get_inner_bg())

# --- Copy Trading ---
@app.route("/copytrading")
@login_required
def copytrading():
    res = safe_fetch(client.fetch_market_feed, market_feed)
    master_trades, copied_trades = [], []
    if res and "Data" in res:
        for s in res["Data"]:
            price = s["LastRate"]
            sig, _ = simple_strategy(price, s["Symbol"])
            master_trades.append({"stock": s["Symbol"], "price": price, "signal": sig})
        followers = ["UserA", "UserB"]
        for t in master_trades:
            copied_trades.append({"trader":"Master","stock":t["stock"],"action":t["signal"],"price":t["price"],"status":"Executed"})
            for f in followers:
                copied_trades.append({"trader":f,"stock":t["stock"],"action":t["signal"],"price":t["price"],"status":"Copied"})
    rows = "".join([f"<tr><td>{r['trader']}</td><td>{r['stock']}</td><td>{r['action']}</td><td>{r['price']}</td><td>{r['status']}</td></tr>" for r in copied_trades])
    content = f"<h2>Copy Trading Simulation</h2><table><tr><th>Trader</th><th>Stock</th><th>Action</th><th>Price</th><th>Status</th></tr>{rows}</table>"
    return render_template_string(BASE_HTML, title="Copy Trading", content=content, bg_image=get_inner_bg())

# --- Algo Trading ---
algo_mode = False
algo_trades = []

@app.route("/algotrading", methods=["GET", "POST"])
@login_required
def algotrading():
    global algo_mode, algo_trades
    if request.method == "POST":
        mode = request.form.get("mode")
        algo_mode = (mode == "ON")
        return redirect(url_for("algotrading"))

    res = safe_fetch(client.fetch_market_feed, market_feed)
    if res and "Data" in res:
        for s in res["Data"]:
            price = s["LastRate"]
            sig, _ = simple_strategy(price, s["Symbol"])
            if algo_mode and sig in ["BUY", "SELL"]:
                algo_trades.append({"stock": s["Symbol"], "price": price, "action": sig, "status": "Executed"})
    rows = "".join([f"<tr><td>{t['stock']}</td><td>{t['action']}</td><td>{t['price']}</td><td>{t['status']}</td></tr>" for t in algo_trades])
    content = f"""
    <h2>Algo Trading</h2>
    <form method='post'>
      <label>Algo Mode:</label>
      <select name='mode' onchange='this.form.submit()'>
        <option value='OFF' {'selected' if not algo_mode else ''}>OFF</option>
        <option value='ON' {'selected' if algo_mode else ''}>ON</option>
      </select>
    </form><br>
    <table><tr><th>Stock</th><th>Action</th><th>Price</th><th>Status</th></tr>{rows}</table>
    """
    return render_template_string(BASE_HTML, title="Algo Trading", content=content, bg_image=get_inner_bg())

# --- Portfolio ---
@app.route("/portfolio")
@login_required
def portfolio():
    holdings = [
        {"stock":"RELIANCE","qty":10,"buy_price":2400,"current_price":2450},
        {"stock":"TCS","qty":5,"buy_price":3500,"current_price":3550},
        {"stock":"INFY","qty":8,"buy_price":1400,"current_price":1380}
    ]
    for h in holdings:
        h["pl"] = round((h["current_price"] - h["buy_price"]) * h["qty"], 2)
    rows = "".join([f"<tr><td>{h['stock']}</td><td>{h['qty']}</td><td>{h['buy_price']}</td><td>{h['current_price']}</td><td style='color:{'#00ff99' if h['pl']>=0 else '#ff4d6d'}'>{h['pl']}</td></tr>" for h in holdings])
    content = f"<h2>Portfolio (Mock)</h2><table><tr><th>Stock</th><th>Qty</th><th>Buy Price</th><th>Current Price</th><th>P/L</th></tr>{rows}</table>"
    return render_template_string(BASE_HTML, title="Portfolio", content=content, bg_image=get_inner_bg())

# --- Trade History ---
@app.route("/history")
@login_required
def history():
    trades = list(mongo.db.trades.find().sort("_id", -1))
    rows = "".join([f"<tr><td>{t.get('stock','-')}</td><td>{t.get('signal','-')}</td><td>{t.get('price','-')}</td><td>{t.get('timestamp','-')}</td></tr>" for t in trades])
    content = f"<h2>Trade History (MongoDB)</h2><table><tr><th>Stock</th><th>Action</th><th>Price</th><th>Timestamp</th></tr>{rows}</table>"
    return render_template_string(BASE_HTML, title="Trade History", content=content, bg_image=get_inner_bg())

if __name__ == "__main__":
    print(app.url_map)
    app.run(host="0.0.0.0", port=5000, debug=True)
