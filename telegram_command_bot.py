"""
NSE Stock Alert Bot with Telegram Commands
Your dad can control everything by just messaging the bot!

Commands:
  /add ETERNAL 275 300   - Add alert for ETERNAL stock
  /update ETERNAL 270 305 - Update alert thresholds
  /list                  - Show all active alerts (for this chat)
  /remove ETERNAL         - Remove alert
  /help                  - Show help
"""

import yfinance as yf
import requests
import time
import threading
from datetime import datetime
from typing import Dict
from flask import Flask


class TelegramCommandBot:
    def __init__(self, telegram_bot_token: str):
        self.bot_token = telegram_bot_token
        self.alerts: Dict[str, Dict] = {}
        self.alert_sent: Dict[str, Dict] = {}
        self.last_update_id = 0
        self.monitoring_active = False
        self.user_chat_ids = set()

    def send_message(self, chat_id: str, message: str) -> bool:
        """Send message to specific chat"""
        url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"
        payload = {"chat_id": chat_id, "text": message, "parse_mode": "HTML"}

        try:
            r = requests.post(url, json=payload, timeout=20)
            return r.status_code == 200
        except Exception as e:
            print(f"Error sending message: {e}")
            return False

    def get_updates(self):
        """Get new messages from Telegram (long polling)"""
        url = f"https://api.telegram.org/bot{self.bot_token}/getUpdates"
        params = {"offset": self.last_update_id + 1, "timeout": 30}

        try:
            r = requests.get(url, params=params, timeout=35)
            if r.status_code == 200:
                return r.json().get("result", [])
        except Exception as e:
            print(f"Error getting updates: {e}")
        return []

    def add_alert(self, chat_id: str, stock_symbol: str, lower_price: float, upper_price: float) -> None:
        """Add a price alert"""
        sym = stock_symbol.upper()
        ticker = f"{sym}.NS"

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

    def remove_alert(self, stock_symbol: str) -> bool:
        """Remove a price alert"""
        sym = stock_symbol.upper()
        if sym in self.alerts:
            del self.alerts[sym]
            if sym in self.alert_sent:
                del self.alert_sent[sym]
            return True
        return False

    def get_current_price(self, ticker: str):
        """Fetch current price from yfinance"""
        try:
            stock = yf.Ticker(ticker)
            data = stock.history(period="1d")
            if not data.empty:
                return round(float(data["Close"].iloc[-1]), 2)
        except Exception as e:
            print(f"Error fetching price for {ticker}: {e}")
        return None

    def check_alerts(self) -> None:
        """Check all alerts and send notifications"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        for stock_symbol, alert_data in list(self.alerts.items()):
            if not alert_data.get("active", False):
                continue

            current_price = self.get_current_price(alert_data["ticker"])
            if current_price is None:
                continue

            upper_price = alert_data["upper_price"]
            lower_price = alert_data["lower_price"]
            chat_id = alert_data["chat_id"]

            # Upper breach
            if current_price >= upper_price and not self.alert_sent[stock_symbol]["upper_sent"]:
                msg = (
                    f"🚨 <b>PRICE ALERT - UPPER BREACH</b> 🚨\n\n"
                    f"Stock: <b>{stock_symbol}</b>\n"
                    f"Current Price: ₹<b>{current_price}</b>\n"
                    f"Upper Threshold: ₹{upper_price}\n"
                    f"Time: {timestamp}"
                )
                self.send_message(chat_id, msg)
                self.alert_sent[stock_symbol]["upper_sent"] = True

            # Lower breach
            elif current_price <= lower_price and not self.alert_sent[stock_symbol]["lower_sent"]:
                msg = (
                    f"🚨 <b>PRICE ALERT - LOWER BREACH</b> 🚨\n\n"
                    f"Stock: <b>{stock_symbol}</b>\n"
                    f"Current Price: ₹<b>{current_price}</b>\n"
                    f"Lower Threshold: ₹{lower_price}\n"
                    f"Time: {timestamp}"
                )
                self.send_message(chat_id, msg)
                self.alert_sent[stock_symbol]["lower_sent"] = True

            # Reset if back in range
            elif lower_price < current_price < upper_price:
                if self.alert_sent[stock_symbol]["upper_sent"] or self.alert_sent[stock_symbol]["lower_sent"]:
                    self.alert_sent[stock_symbol]["upper_sent"] = False
                    self.alert_sent[stock_symbol]["lower_sent"] = False

            print(f"[{timestamp}] {stock_symbol}: ₹{current_price} (Range: {lower_price}-{upper_price})")

    def monitoring_loop(self) -> None:
        """Background monitoring loop"""
        self.monitoring_active = True
        print("🔄 Monitoring started")

        while self.alerts:
            self.check_alerts()
            time.sleep(60)

        self.monitoring_active = False
        print("⏹️ Monitoring stopped (no alerts)")

    def start_monitoring_thread(self) -> None:
        """Start monitoring in background thread"""
        if not self.monitoring_active:
            t = threading.Thread(target=self.monitoring_loop, daemon=True)
            t.start()

    def handle_command(self, chat_id: str, message_text: str) -> None:
        """Process commands"""
        message_text = message_text.strip()
        self.user_chat_ids.add(chat_id)

        if message_text.startswith("/start") or message_text.startswith("/help"):
            help_text = (
                "🤖 <b>NSE Stock Alert Bot</b>\n\n"
                "<b>Commands:</b>\n"
                "➕ /add STOCK LOWER UPPER\n"
                "   Example: /add ETERNAL 275 300\n\n"
                "✏️ /update STOCK LOWER UPPER\n"
                "   Example: /update ETERNAL 270 305\n\n"
                "📋 /list - Show all your alerts\n"
                "❌ /remove STOCK - Remove an alert\n"
                "   Example: /remove ETERNAL\n\n"
                "💡 /help - Show this message\n\n"
                "<b>Notes:</b>\n"
                "• Uses NSE symbols (e.g., RELIANCE, TCS, INFY)\n"
                "• Checks every 60 seconds\n"
                "• Alerts reset if price returns inside range"
            )
            self.send_message(chat_id, help_text)
            return

        # /add STOCK LOWER UPPER
        if message_text.startswith("/add"):
            parts = message_text.split()
            if len(parts) != 4:
                self.send_message(chat_id, "❌ Use: /add STOCK LOWER UPPER\nExample: /add ETERNAL 275 300")
                return
            try:
                stock = parts[1].upper()
                lower = float(parts[2])
                upper = float(parts[3])
                if lower >= upper:
                    self.send_message(chat_id, "❌ Lower price must be less than upper price!")
                    return

                test_price = self.get_current_price(f"{stock}.NS")
                if test_price is None:
                    self.send_message(chat_id, f"⚠️ Could not fetch price for {stock}. Check the NSE symbol.")
                    return

                self.add_alert(chat_id, stock, lower, upper)
                self.send_message(
                    chat_id,
                    f"✅ <b>Alert Added!</b>\n\n"
                    f"Stock: {stock}\n"
                    f"Current Price: ₹{test_price}\n"
                    f"Lower Limit: ₹{lower}\n"
                    f"Upper Limit: ₹{upper}",
                )
            except ValueError:
                self.send_message(chat_id, "❌ Prices must be numbers.\nExample: /add ETERNAL 275 300")
            return

        # /update STOCK LOWER UPPER
        if message_text.startswith("/update"):
            parts = message_text.split()
            if len(parts) != 4:
                self.send_message(chat_id, "❌ Use: /update STOCK LOWER UPPER\nExample: /update ETERNAL 270 305")
                return
            try:
                stock = parts[1].upper()
                lower = float(parts[2])
                upper = float(parts[3])
                if lower >= upper:
                    self.send_message(chat_id, "❌ Lower price must be less than upper price!")
                    return

                if stock not in self.alerts or self.alerts[stock].get("chat_id") != chat_id:
                    self.send_message(chat_id, f"❌ No alert found for {stock}. Use /add to create one.")
                    return

                self.alerts[stock]["lower_price"] = lower
                self.alerts[stock]["upper_price"] = upper
                self.alert_sent[stock] = {"upper_sent": False, "lower_sent": False}

                cur = self.get_current_price(f"{stock}.NS")
                self.send_message(
                    chat_id,
                    f"✅ <b>Alert Updated!</b>\n\n"
                    f"Stock: {stock}\n"
                    f"Current Price: ₹{cur if cur is not None else 'N/A'}\n"
                    f"New Lower Limit: ₹{lower}\n"
                    f"New Upper Limit: ₹{upper}",
                )
            except ValueError:
                self.send_message(chat_id, "❌ Prices must be numbers.\nExample: /update ETERNAL 270 305")
            return

        # /list
        if message_text.startswith("/list"):
            user_alerts = {k: v for k, v in self.alerts.items() if v.get("chat_id") == chat_id}
            if not user_alerts:
                self.send_message(chat_id, "📋 You have no active alerts. Use /add to create one.")
                return

            out = "📋 <b>Your Active Alerts:</b>\n\n"
            for stock, a in user_alerts.items():
                cur = self.get_current_price(a["ticker"])
                out += (
                    f"<b>{stock}</b>\n"
                    f"Current: {'₹' + str(cur) if cur is not None else 'N/A'}\n"
                    f"Range: ₹{a['lower_price']} - ₹{a['upper_price']}\n\n"
                )
            self.send_message(chat_id, out)
            return

        # /remove STOCK
        if message_text.startswith("/remove"):
            parts = message_text.split()
            if len(parts) != 2:
                self.send_message(chat_id, "❌ Use: /remove STOCK\nExample: /remove ETERNAL")
                return

            stock = parts[1].upper()
            if stock in self.alerts and self.alerts[stock].get("chat_id") == chat_id:
                self.remove_alert(stock)
                self.send_message(chat_id, f"✅ Alert removed for {stock}")
            else:
                self.send_message(chat_id, f"❌ No alert found for {stock}")
            return

        self.send_message(chat_id, "❓ Unknown command. Send /help to see commands.")

    def run(self) -> None:
        """Main bot loop"""
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
    """
    Tiny HTTP server so Railway sees an open port and keeps the service healthy.
    """
    app = Flask(__name__)

    @app.get("/")
    def home():
        return "OK", 200

    # Railway provides PORT; default for local testing
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

    # Start web server for Railway health checks
    threading.Thread(target=start_web_server, daemon=True).start()

    bot = TelegramCommandBot(TELEGRAM_BOT_TOKEN)

    print("\n✅ Bot initialized!")
    print("\n📱 Telegram steps:")
    print("   1) Open your bot")
    print("   2) Send /start")
    print("   3) Send /add ETERNAL 275 300")
    print("\n" + "=" * 60 + "\n")

    bot.run()


if __name__ == "__main__":
    main()
