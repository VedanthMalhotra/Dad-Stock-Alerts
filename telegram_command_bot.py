"""
NSE Stock Alert Bot with Telegram Commands (Railway-friendly)

Commands:
  /add SYMBOL LOWER UPPER
    Example: /add INFY 1350 1550

  /update SYMBOL LOWER UPPER
    Example: /update INFY 1340 1560

  /list
  /remove SYMBOL
  /help

Behavior:
- Alerts trigger ONCE (then become inactive)
- /update re-activates an alert
- /add ALWAYS adds (even if price feed is temporarily down)
- IMPORTANT: Each command sends EXACTLY ONE reply message (no double prompts)
"""

import time
import threading
from datetime import datetime
from typing import Dict

import requests
from flask import Flask


class TelegramCommandBot:
    def __init__(self, telegram_bot_token: str):
        self.bot_token = telegram_bot_token

        # alerts[symbol] = {ticker, upper_price, lower_price, chat_id, active}
        self.alerts: Dict[str, Dict] = {}

        # alert_sent[symbol] = {upper_sent, lower_sent}
        self.alert_sent: Dict[str, Dict] = {}

        self.last_update_id = 0
        self.monitoring_active = False
        self.lock = threading.Lock()

    # -------------------- Telegram helpers --------------------

    def send_message(self, chat_id: str, message: str) -> bool:
        url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"
        payload = {"chat_id": chat_id, "text": message, "parse_mode": "HTML"}
        try:
            r = requests.post(url, json=payload, timeout=20)
            return r.status_code == 200
        except Exception as e:
            print(f"Error sending message: {e}")
            return False

    def get_updates(self):
        url = f"https://api.telegram.org/bot{self.bot_token}/getUpdates"
        params = {"offset": self.last_update_id + 1, "timeout": 30, "allowed_updates": ["message"]}
        try:
            r = requests.get(url, params=params, timeout=35)
            if r.status_code == 200:
                return r.json().get("result", [])
        except Exception as e:
            print(f"Error getting updates: {e}")
        return []

    # -------------------- Alerts storage --------------------

    def add_alert(self, chat_id: str, stock_symbol: str, lower_price: float, upper_price: float) -> None:
        sym = stock_symbol.upper()
        ticker = f"{sym}.NS"
        with self.lock:
            self.alerts[sym] = {
                "ticker": ticker,
                "upper_price": upper_price,
                "lower_price": lower_price,
                "chat_id": chat_id,
                "active": True,
            }
            self.alert_sent[sym] = {"upper_sent": False, "lower_sent": False}

        if not self.monitoring_active:
            self.start_monitoring_thread()

    def remove_alert(self, chat_id: str, stock_symbol: str) -> bool:
        sym = stock_symbol.upper()
        with self.lock:
            if sym in self.alerts and self.alerts[sym].get("chat_id") == chat_id:
                del self.alerts[sym]
                if sym in self.alert_sent:
                    del self.alert_sent[sym]
                return True
        return False

    # -------------------- Price fetching (Yahoo chart endpoint) --------------------

    def get_current_price(self, ticker: str):
        """
        Fetch current price from Yahoo Finance chart endpoint directly.
        Tries intervals: 1m -> 5m -> 15m (fallbacks are more stable on cloud IPs).
        """
        url = f"https://query1.finance.yahoo.com/v8/finance/chart/{ticker}"

        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                          "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "application/json,text/plain,*/*",
            "Accept-Language": "en-US,en;q=0.9",
            "Connection": "keep-alive",
        }

        intervals = ["1m", "5m", "15m"]

        for interval in intervals:
            params = {"range": "1d", "interval": interval}

            for attempt in range(3):
                try:
                    response = requests.get(url, params=params, headers=headers, timeout=20)

                    if response.status_code != 200:
                        print(f"Yahoo HTTP {response.status_code} for {ticker} interval={interval}")
                        time.sleep(1 + attempt)
                        continue

                    if "application/json" not in response.headers.get("Content-Type", "").lower():
                        print(f"Yahoo returned non-JSON for {ticker} interval={interval}")
                        time.sleep(1 + attempt)
                        continue

                    data = response.json()
                    result = data.get("chart", {}).get("result")
                    if not result:
                        print(f"No chart result for {ticker} interval={interval}")
                        time.sleep(1 + attempt)
                        continue

                    quotes = result[0].get("indicators", {}).get("quote", [])
                    if not quotes:
                        print(f"No quote data for {ticker} interval={interval}")
                        time.sleep(1 + attempt)
                        continue

                    closes = quotes[0].get("close", [])
                    if not closes:
                        print(f"No close series for {ticker} interval={interval}")
                        time.sleep(1 + attempt)
                        continue

                    for price in reversed(closes):
                        if price is not None:
                            return round(float(price), 2)

                    time.sleep(1 + attempt)

                except Exception as e:
                    print(f"Error fetching price for {ticker} interval={interval}: {e}")
                    time.sleep(1 + attempt)

        return None

    # -------------------- Monitoring --------------------

    def check_alerts(self) -> None:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        with self.lock:
            snapshot = list(self.alerts.items())

        for stock_symbol, alert_data in snapshot:
            if not alert_data.get("active", False):
                continue

            current_price = self.get_current_price(alert_data["ticker"])
            if current_price is None:
                continue

            upper_price = alert_data["upper_price"]
            lower_price = alert_data["lower_price"]
            chat_id = alert_data["chat_id"]

            # Upper breach -> trigger ONCE then deactivate
            if current_price >= upper_price and not self.alert_sent.get(stock_symbol, {}).get("upper_sent", False):
                msg = (
                    f"🚨 <b>PRICE ALERT - UPPER BREACH</b> 🚨\n\n"
                    f"Stock: <b>{stock_symbol}</b>\n"
                    f"Current Price: ₹<b>{current_price}</b>\n"
                    f"Upper Threshold: ₹{upper_price}\n"
                    f"Time: {timestamp}"
                )
                self.send_message(chat_id, msg)

                with self.lock:
                    if stock_symbol in self.alert_sent:
                        self.alert_sent[stock_symbol]["upper_sent"] = True
                    if stock_symbol in self.alerts:
                        self.alerts[stock_symbol]["active"] = False

            # Lower breach -> trigger ONCE then deactivate
            elif current_price <= lower_price and not self.alert_sent.get(stock_symbol, {}).get("lower_sent", False):
                msg = (
                    f"🚨 <b>PRICE ALERT - LOWER BREACH</b> 🚨\n\n"
                    f"Stock: <b>{stock_symbol}</b>\n"
                    f"Current Price: ₹<b>{current_price}</b>\n"
                    f"Lower Threshold: ₹{lower_price}\n"
                    f"Time: {timestamp}"
                )
                self.send_message(chat_id, msg)

                with self.lock:
                    if stock_symbol in self.alert_sent:
                        self.alert_sent[stock_symbol]["lower_sent"] = True
                    if stock_symbol in self.alerts:
                        self.alerts[stock_symbol]["active"] = False

            print(f"[{timestamp}] {stock_symbol}: ₹{current_price} (Range: {lower_price}-{upper_price})")

    def monitoring_loop(self) -> None:
        self.monitoring_active = True
        print("🔄 Monitoring started")

        while True:
            with self.lock:
                has_active = any(a.get("active") for a in self.alerts.values())

            if not has_active:
                time.sleep(5)
                continue

            self.check_alerts()
            time.sleep(60)

    def start_monitoring_thread(self) -> None:
        if not self.monitoring_active:
            t = threading.Thread(target=self.monitoring_loop, daemon=True)
            t.start()

    # -------------------- Command handling (ONE reply per command) --------------------

    def handle_command(self, chat_id: str, message_text: str) -> None:
        text = message_text.strip()
        parts = text.split()
        cmd = parts[0].lower() if parts else ""

        if cmd in ("/start", "/help"):
            help_text = (
                "🤖 <b>NSE Stock Alert Bot</b>\n\n"
                "<b>Commands:</b>\n"
                "➕ /add STOCK LOWER UPPER\n"
                "   Example: /add INFY 1350 1550\n\n"
                "✏️ /update STOCK LOWER UPPER\n"
                "   Example: /update INFY 1340 1560\n\n"
                "📋 /list - Show your alerts\n"
                "❌ /remove STOCK - Remove an alert\n\n"
                "<b>Notes:</b>\n"
                "• Each alert triggers once, then becomes inactive\n"
                "• /update re-activates an alert\n"
                "• /add works even if price feed is temporarily unavailable"
            )
            self.send_message(chat_id, help_text)
            return

        if cmd == "/add":
            if len(parts) != 4:
                self.send_message(chat_id, "❌ Use: /add STOCK LOWER UPPER\nExample: /add INFY 1350 1550")
                return

            try:
                stock = parts[1].upper()
                lower = float(parts[2])
                upper = float(parts[3])

                if lower >= upper:
                    self.send_message(chat_id, "❌ Lower price must be less than upper price!")
                    return

                # Always add first
                self.add_alert(chat_id, stock, lower, upper)

                # Then try to fetch current price (optional)
                test_price = self.get_current_price(f"{stock}.NS")

                if test_price is None:
                    msg = (
                        f"✅ <b>Alert Added!</b>\n\n"
                        f"Stock: {stock}\n"
                        f"Lower Limit: ₹{lower}\n"
                        f"Upper Limit: ₹{upper}\n\n"
                        f"⚠️ Price feed temporarily unavailable.\n"
                        f"The bot will keep checking and alert when data is available."
                    )
                else:
                    msg = (
                        f"✅ <b>Alert Added!</b>\n\n"
                        f"Stock: {stock}\n"
                        f"Current Price: ₹{test_price}\n"
                        f"Lower Limit: ₹{lower}\n"
                        f"Upper Limit: ₹{upper}\n\n"
                        f"Note: If current price is already outside the range, it may trigger immediately."
                    )

                self.send_message(chat_id, msg)
                return

            except ValueError:
                self.send_message(chat_id, "❌ Prices must be numbers.\nExample: /add INFY 1350 1550")
                return

        if cmd == "/update":
            if len(parts) != 4:
                self.send_message(chat_id, "❌ Use: /update STOCK LOWER UPPER\nExample: /update INFY 1340 1560")
                return

            try:
                stock = parts[1].upper()
                lower = float(parts[2])
                upper = float(parts[3])

                if lower >= upper:
                    self.send_message(chat_id, "❌ Lower price must be less than upper price!")
                    return

                with self.lock:
                    if stock not in self.alerts or self.alerts[stock].get("chat_id") != chat_id:
                        self.send_message(chat_id, f"❌ No alert found for {stock}. Use /add to create one.")
                        return

                    self.alerts[stock]["lower_price"] = lower
                    self.alerts[stock]["upper_price"] = upper
                    self.alerts[stock]["active"] = True
                    self.alert_sent[stock] = {"upper_sent": False, "lower_sent": False}

                cur = self.get_current_price(f"{stock}.NS")
                msg = (
                    f"✅ <b>Alert Updated!</b>\n\n"
                    f"Stock: {stock}\n"
                    f"Current Price: ₹{cur if cur is not None else 'N/A'}\n"
                    f"New Lower Limit: ₹{lower}\n"
                    f"New Upper Limit: ₹{upper}\n"
                    f"Status: Active"
                )
                self.send_message(chat_id, msg)
                return

            except ValueError:
                self.send_message(chat_id, "❌ Prices must be numbers.\nExample: /update INFY 1340 1560")
                return

        if cmd == "/list":
            with self.lock:
                user_alerts = {k: v for k, v in self.alerts.items() if v.get("chat_id") == chat_id}

            if not user_alerts:
                self.send_message(chat_id, "📋 You have no alerts. Use /add to create one.")
                return

            out = "📋 <b>Your Alerts:</b>\n\n"
            for stock, a in user_alerts.items():
                cur = self.get_current_price(a["ticker"])
                status = "✅ Active" if a.get("active") else "⏸️ Inactive (triggered)"
                out += (
                    f"<b>{stock}</b>\n"
                    f"Status: {status}\n"
                    f"Current: {'₹' + str(cur) if cur is not None else 'N/A'}\n"
                    f"Range: ₹{a['lower_price']} - ₹{a['upper_price']}\n\n"
                )

            self.send_message(chat_id, out)
            return

        if cmd == "/remove":
            if len(parts) != 2:
                self.send_message(chat_id, "❌ Use: /remove STOCK\nExample: /remove INFY")
                return

            stock = parts[1].upper()
            removed = self.remove_alert(chat_id, stock)
            if removed:
                self.send_message(chat_id, f"✅ Alert removed for {stock}")
            else:
                self.send_message(chat_id, f"❌ No alert found for {stock}")
            return

        self.send_message(chat_id, "❓ Unknown command. Send /help to see commands.")

    # -------------------- Main loop --------------------

    def run(self) -> None:
        print("🤖 Bot started! Send /help to the bot on Telegram.\n")

        while True:
            try:
                updates = self.get_updates()

                for update in updates:
                    self.last_update_id = update["update_id"]

                    if "message" in update and "text" in update["message"]:
                        chat_id = str(update["message"]["chat"]["id"])
                        message_text = update["message"]["text"]
                        username = update["message"].get("from", {}).get("username", "Unknown")
                        print(f"📨 Message from @{username}: {message_text}")
                        self.handle_command(chat_id, message_text)

                time.sleep(1)

            except KeyboardInterrupt:
                print("\n⏹️ Bot stopped")
                break
            except Exception as e:
                print(f"Error: {e}")
                time.sleep(5)


def start_web_server():
    """Tiny HTTP server so Railway sees an open port and keeps the service healthy."""
    app = Flask(__name__)

    @app.get("/")
    def home():
        return "OK", 200

    import os
    port = int(os.environ.get("PORT", "8080"))
    app.run(host="0.0.0.0", port=port)


def main():
    print("=" * 60)
    print("NSE STOCK ALERT BOT - TELEGRAM COMMAND MODE")
    print("=" * 60)

    # ✅ HARD-CODE YOUR REAL TOKEN HERE
    TELEGRAM_BOT_TOKEN = "8093483580:AAFD2CH7iEmNTF-Cf3OPF45X9ecmpbBqjN0"

    if TELEGRAM_BOT_TOKEN.strip() == "" or TELEGRAM_BOT_TOKEN == "PASTE_YOUR_REAL_TOKEN_HERE":
        print("\n❌ ERROR: Please paste your real Telegram bot token in the code.")
        return

    # Start tiny web server for Railway health checks
    threading.Thread(target=start_web_server, daemon=True).start()

    bot = TelegramCommandBot(TELEGRAM_BOT_TOKEN)

    print("\n✅ Bot initialized!")
    print("\n📱 Telegram steps:")
    print("   1) Open your bot")
    print("   2) Send /start")
    print("   3) Send /add INFY 1350 1550")
    print("\n" + "=" * 60 + "\n")

    bot.run()


if __name__ == "__main__":
    main()
