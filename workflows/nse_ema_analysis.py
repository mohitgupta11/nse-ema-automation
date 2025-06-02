import os
import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta
from ta.trend import EMAIndicator
import smtplib
from email.message import EmailMessage

# Set date strings
today = datetime.now()
yesterday = today - timedelta(days=1)
today_str = today.strftime("%Y-%m-%d")
yesterday_str = yesterday.strftime("%Y-%m-%d")

# Load Nifty 500 symbols from NSE
nifty_500_url = "https://archives.nseindia.com/content/indices/ind_nifty500list.csv"
nifty_500 = pd.read_csv(nifty_500_url)
symbols = nifty_500['Symbol'].tolist()

results = []

# Loop through symbols
for symbol in symbols:
    try:
        data = yf.download(f"{symbol}.NS", period="1y", interval="1d", progress=False)
        if data.empty or len(data) < 200:
            continue

        data["EMA50"] = EMAIndicator(close=data["Close"], window=50).ema_indicator()
        data["EMA200"] = EMAIndicator(close=data["Close"], window=200).ema_indicator()

        current_price = data["Close"].iloc[-1]
        ema_50 = data["EMA50"].iloc[-1]
        ema_200 = data["EMA200"].iloc[-1]

        if current_price < ema_50 and current_price < ema_200:
            results.append({
                "Symbol": symbol,
                "Price": round(current_price, 2),
                "EMA50": round(ema_50, 2),
                "EMA200": round(ema_200, 2)
            })

    except Exception as e:
        print(f"Error processing {symbol}: {e}")

# Save today's results
df_today = pd.DataFrame(results)
today_file = f"below_ema_list_{today_str}.csv"
df_today.to_csv(today_file, index=False)

# Compare with yesterday's file
yesterday_file = f"below_ema_list_{yesterday_str}.csv"
new_entries = pd.DataFrame()

if os.path.exists(yesterday_file):
    df_yesterday = pd.read_csv(yesterday_file)
    new_entries = df_today[~df_today["Symbol"].isin(df_yesterday["Symbol"])]
    new_entries_file = f"new_entries_{today_str}.csv"
    new_entries.to_csv(new_entries_file, index=False)
else:
    print("Yesterday's data not found. Skipping comparison.")
    new_entries_file = None

# Send Email with attachments
def send_email(subject, body, to_email, attachments=[]):
    EMAIL_ADDRESS = os.getenv("EMAIL_USER")
    EMAIL_PASSWORD = os.getenv("EMAIL_PASS")

    if not EMA
