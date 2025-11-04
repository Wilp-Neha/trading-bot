from flask import Flask, render_template_string, request, redirect, url_for, session
from flask_pymongo import PyMongo
from py5paisa import FivePaisaClient
from datetime import datetime

app = Flask(__name__)
app.secret_key = "super_secret_key_123"  # Needed for sessions

# --- MongoDB Config ---
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

# --- Strategy ---
def simple_strategy(price, stock):
    if price > 2500:
        return ("SELL", f"{stock} is overvalued, consider profit booking.")
    elif price < 2400:
        return ("BUY", f"{stock} is undervalued, good entry point.")
    else:
        return ("HOLD", f"{stock} is stable, maintain current position.")

# --- Market Feed List ---
market_feed = [
    {"Exch": "N", "ExchType": "C", "Symbol": "RELIANCE", "Expiry": "", "StrikePrice": "0", "OptionType": ""},
    {"Exch": "N", "ExchType": "C", "Symbol": "TCS", "Expiry": "", "StrikePrice": "0", "OptionType": ""},
    {"Exch": "N", "ExchType": "C", "Symbol": "INFY", "Expiry": "", "StrikePrice": "0", "OptionType": ""}
]

# --- HTML Templates ---
login_html = """
<!DOCTYPE html>
<html>
<head>
  <title>Login - Trading Bot</title>
  <style>
    body {
      font-family: 'Poppins', sans-serif;
      background: linear-gradient(rgba(0,0,0,0.6), rgba(0,0,0,0.8)),
                  url('https://cdn.dribbble.com/users/1248377/screenshots/15087917/media/92e5b5d01116dfc80f4d6c189f48291d.png');
      background-size: cover;
      background-position: center;
      height: 100vh;
      color: white;
      display: flex;
      align-items: center;
      justify-content: center;
    }
    .login-box {
      background-color: rgba(13,17,23,0.9);
      padding: 40px;
      border-radius: 10px;
      text-align: center;
      width: 350px;
      box-shadow: 0px 4px 10px rgba(0,0,0,0.5);
    }
    input[type=text], input[type=password] {
      width: 90%;
      padding: 10px;
      margin: 10px 0;
      border: none;
      border-radius: 5px;
      background-color: #161b22;
      color: white;
    }
    button {
      background-color: #238636;
      color: white;
      border: none;
      padding: 10px 20px;
      border-radius: 5px;
      cursor: pointer;
      margin-top: 10px;
    }
    button:hover {
      background-color: #2ea043;
    }
  </style>
</head>
<body>
  <div class="login-box">
    <h2>🤖 AI Trading Bot Login</h2>
    <form method="POST" action="{{ url_for('login') }}">
      <input type="text" name="username" placeholder="Username" required><br>
      <input type="password" name="password" placeholder="Password" required><br>
      <button type="submit">Login</button>
    </form>
    <p style="color:#aaa;font-size:13px;margin-top:15px;">Demo User: admin | Password: 1234</p>
  </div>
</body>
</html>
"""

# --- Base Template for Inner Pages ---
base_html = """
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>{{ title }}</title>
  <style>
    body {
        font-family: 'Segoe UI', sans-serif;
        background: linear-gradient(rgba(13,17,23,0.9), rgba(13,17,23,0.9)),
                    url('https://images.unsplash.com/photo-1642104704075-f7a315f1a77f?auto=format&fit=crop&w=1350&q=80');
        background-size: cover;
        background-attachment: fixed;
        color: #c9d1d9;
        margin: 0;
        padding: 0;
    }
    header {
        background-color: rgba(22,27,34,0.9);
        padding: 12px 20px;
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
    nav a:hover { text-decoration: underline; color: #00c6ff; }
    .container { width: 90%; margin: auto; padding: 25px; }
    table {
        border-collapse: collapse;
        width: 85%;
        margin: 20px auto;
        background-color: rgba(22,27,34,0.8);
        border-radius: 10px;
        overflow: hidden;
    }
    th, td {
        border: 1px solid #30363d;
        padding: 12px;
        text-align: center;
    }
    th { background-color: #21262d; }
    tr:hover { background-color: #2d333b; }
    .buy { color: #00c853; }
    .sell { color: #ff1744; }
    .hold { color: #ffb300; }
    h2 { color: #58a6ff; text-align: center; }
    footer {
        text-align: center;
        padding: 25px;
        color: #8b949e;
        border-top: 1px solid #30363d;
        background-color: rgba(13,17,23,0.95);
    }
    .logout {
        color: #ff6b6b;
        text-decoration: none;
    }
    .logout:hover { text-decoration: underline; }
  </style>
</head>
<body>
  <header>
    <div><b>📊 Trading Bot Dashboard</b></div>
    <nav>
      <a href="{{ url_for('dashboard') }}">Dashboard</a>
      <a href="{{ url_for('advisory') }}">Advisory</a>
      <a href="{{ url_for('copytrading') }}">Copy Trading</a>
      <a href="{{ url_for('algotrading') }}">Algo Trading</a>
      <a href="{{ url_for('portfolio') }}">Portfolio</a>
      <a href="{{ url_for('history') }}">History</a>
      <a class="logout" href="{{ url_for('logout') }}">Logout</a>
    </nav>
  </header>

  <div class="container">
    {{ content | safe }}
  </div>

  <footer>
    <p>© 2025 Automated Trading System | Flask + 5Paisa + MongoDB</p>
    <p>📧 Contact: <a href="mailto:wilpneha@gmail.com" style="color:#58a6ff;">wilpneha@gmail.com</a></p>
  </footer>
</body>
</html>
"""

# --- LOGIN SYSTEM ---
@app.route("/", methods=["GET", "POST"])
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        if username == "admin" and password == "1234":
            session["user"] = username
            return redirect(url_for("dashboard"))
        else:
            return render_template_string(login_html + "<p style='color:red;text-align:center;'>Invalid credentials</p>")
    return render_template_string(login_html)
# --- Market Status (Live from 5Paisa) ---
@app.route("/market_status")
@login_required
def market_status():
    try:
        status = client.get_market_status()
        content = f"""
        <h2>📊 Market Status</h2>
        <table>
          <tr><th>Exchange</th><th>Status</th><th>Message</th></tr>
          <tr><td>NSE</td><td>{status.get('NSE', {}).get('Status', 'N/A')}</td><td>{status.get('NSE', {}).get('Message', '')}</td></tr>
          <tr><td>BSE</td><td>{status.get('BSE', {}).get('Status', 'N/A')}</td><td>{status.get('BSE', {}).get('Message', '')}</td></tr>
        </table>
        """
        return render_template_string(base_html, title="Market Status", content=content)
    except Exception as e:
        return render_template_string(base_html, title="Error", content=f"<h2>Error fetching market status: {e}</h2>")

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

# --- LOGIN REQUIRED DECORATOR ---
def login_required(f):
    def wrapper(*args, **kwargs):
        if "user" not in session:
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    wrapper.__name__ = f.__name__
    return wrapper

# --- INNER PAGES ---
@app.route("/dashboard")
@login_required
def dashboard():
    res = client.fetch_market_feed(market_feed)
    if not res or "Data" not in res:
        content = "<h2>⚠️ Token expired or data unavailable. Please refresh your token.</h2>"
        return render_template_string(base_html, title="Dashboard", content=content)

    rows = "".join([f"<tr><td>{s['Symbol']}</td><td>{s['LastRate']}</td><td class='{simple_strategy(s['LastRate'], s['Symbol'])[0].lower()}'>{simple_strategy(s['LastRate'], s['Symbol'])[0]}</td></tr>" for s in res["Data"]])
    content = f"<h2>Live Market Dashboard</h2><table><tr><th>Stock</th><th>Price</th><th>Signal</th></tr>{rows}</table>"
    return render_template_string(base_html, title="Dashboard", content=content)

@app.route("/advisory")
@login_required
def advisory():
    res = client.fetch_market_feed(market_feed)
    if not res or "Data" not in res:
        content = "<h2>⚠️ Data unavailable.</h2>"
        return render_template_string(base_html, title="Advisory", content=content)

    items = "".join([f"<li><b>{s['Symbol']}</b> → {simple_strategy(s['LastRate'], s['Symbol'])[0]} (₹{s['LastRate']}) → {simple_strategy(s['LastRate'], s['Symbol'])[1]}</li>" for s in res["Data"]])
    content = f"<h2>Market Advisory</h2><ul>{items}</ul>"
    return render_template_string(base_html, title="Advisory", content=content)

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
    rows = "".join([f"<tr><td>{h['stock']}</td><td>{h['qty']}</td><td>{h['buy_price']}</td><td>{h['current_price']}</td><td style='color:{'green' if h['pl']>=0 else 'red'}'>{h['pl']}</td></tr>" for h in holdings])
    content = f"<h2>Portfolio Overview</h2><table><tr><th>Stock</th><th>Qty</th><th>Buy Price</th><th>Current Price</th><th>P/L</th></tr>{rows}</table>"
    return render_template_string(base_html, title="Portfolio", content=content)

@app.route("/history")
@login_required
def history():
    trades = list(mongo.db.trades.find().sort("_id", -1))
    rows = "".join([f"<tr><td>{t.get('stock','')}</td><td>{t.get('signal','')}</td><td>{t.get('price','')}</td><td>{t.get('timestamp','')}</td></tr>" for t in trades])
    content = f"<h2>Trade History (MongoDB)</h2><table><tr><th>Stock</th><th>Signal</th><th>Price</th><th>Timestamp</th></tr>{rows}</table>"
    return render_template_string(base_html, title="History", content=content)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
