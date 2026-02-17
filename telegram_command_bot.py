"""
NSE Stock Alert Bot with Telegram Commands
Your dad can control everything by just messaging the bot!

Commands:
/add ETERNAL 275 300 - Add alert for ETERNAL stock
/list - Show all active alerts
/remove ETERNAL - Remove alert
/help - Show help
"""

import os
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
        self.user_chat_ids = set()  # Store all users who interact with bot

    def send_message(self, chat_id: str, message: str):
        """Send message to specific chat"""
        url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"
        payload = {
            "chat_id": chat_id,
            "text": message,
            "parse_mode": "HTML",
        }
        try:
            response = requests.post(url, json=payload, timeout=20)
            return response.status_code == 200
        except Exception as e:
            print(f"Error sending message: {e}")
            return False

    def get_updates(self):
        """Get new messages from Telegram"""
        url = f"https://api.telegram.org/bot{self.bot_token}/getUpdates"
        params = {"offset": self.last_update_id + 1, "timeout": 30}

        try:
            response = requests.get(url, params=params, timeout=35)
            if response.status_code == 200:
                return response.json().get("result", [])
        except Exception as e:
            print(f"Error getting updates: {e}")
        return []

    def add_alert(self, chat_id: str, stock_symbol: str, lower_price: float, upper_price: float):
        """Add a price alert"""
        ticker = f"{stock_symbol.upper()}.NS"

        self.alerts[stock_symbol.upper()] = {
            "ticker": ticker,
            "upper_price": upper_price,
            "lower_price": lower_price,
            "chat_id": chat_id,
            "active": True,
        }

        self.alert_sent[stock_symbol.upper()] = {
            "upper_sent": False,
            "lower_sent": False,
        }

        # Start monitoring if not already running
        if not self.monitoring_active:
            self.start_monitoring_thread()

        return True

    def remove_alert(self, stock_symbol: str):
        """Remove a price alert"""
        stock_symbol = stock_symbol.upper()
        if stock_symbol in self.alerts:
            del self.alerts[stock_symbol]
            del self.alert_sent[stock_symbol]
            return True
        return False

    def get_current_price(self, ticker: str):
        """Fetch current price"""
        try:
            stock = yf.Ticker(ticker)
            data = stock.history(period="1d", interval="1m")
            if not data.empty:
                return round(float(data["Close"].iloc[-1]), 2)
        except Exception as e:
            print(f"Error fetching price for {ticker}: {e}")
        return None

    def check_alerts(self):
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

            # Check upper threshold
            if current_price >= upper_price and not self.alert_sent[stock_symbol]["upper_sent"]:
                message = (
                    f"🚨 <b>PRICE ALERT - UPPER BREACH</b> 🚨\n\n"
                    f"Stock: <b>{stock_symbol}</b>\n"
                    f"Current Price: ₹<b>{current_price}</b>\n"
                    f"Upper Threshold: ₹{upper_price}\n"
                    f"Time: {timestamp}"
                )
                self.send_message(chat_id, message)
                self.alert_sent[stock_symbol]["upper_sent"] = True

            # Check lower threshold
            elif current_price <= lower_price and not self.alert_sent[stock_symbol]["lower_sent"]:
                message = (
                    f"🚨 <b>PRICE ALERT - LOWER BREACH</b> 🚨\n\n"
                    f"Stock: <b>{stock_symbol}</b>\n"
                    f"Current Price: ₹<b>{current_price}</b>\n"
                    f"Lower Threshold: ₹{lower_price}\n"
                    f"Time: {timestamp}"
                )
                self.send_message(chat_id, message)
                self.alert_sent[stock_symbol]["lower_sent"] = True

            # Reset alerts if back in range
            elif lower_price < current_price < upper_price:
                if self.alert_sent[stock_symbol]["upper_sent"] or self.alert_sent[stock_symbol]["lower_sent"]:
                    self.alert_sent[stock_symbol]["upper_sent"] = False
                    self.alert_sent[stock_symbol]["lower_sent"] = False

            print(f"[{timestamp}] {stock_symbol}: ₹{current_price} (Range: {lower_price}-{upper_price})")

    def monitoring_loop(self):
        """Background monitoring loop"""
        self.monitoring_active = True
        print("🔄 Monitoring started")

        while self.alerts:  # Keep running while there are alerts
            self.check_alerts()
            time.sleep(60)  # Check every minute

        self.monitoring_active = False
        print("⏹️ Monitoring stopped (no alerts)")

    def start_monitoring_thread(self):
        """Start monitoring in background thread"""
        if not self.monitoring_active:
            thread = threading.Thread(target=self.monitoring_loop, daemon=True)
            thread.start()

    def handle_command(self, chat_id: str, message_text: str):
        """Process commands from users"""
        message_text = message_text.strip()

        # Store chat ID
        self.user_chat_ids.add(chat_id)

        # /start or /help
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
                "<b>How it works:</b>\n"
                "• Set upper and lower price limits\n"
                "• Get instant alerts when breached\n"
                "• Update limits anytime with /update\n"
                "• Monitor multiple stocks\n"
                "• Runs 24/7 automatically"
            )
            self.send_message(chat_id, help_text)

        # /add STOCK LOWER UPPER
        elif message_text.startswith("/add"):
            parts = message_text.split()
            if len(parts) != 4:
                self.send_message(
                    chat_id,
                    "❌ Invalid format!\n\n"
                    "Use: /add STOCK LOWER UPPER\n"
                    "Example: /add ETERNAL 275 300",
                )
                return

            try:
                stock = parts[1].upper()
                lower = float(parts[2])
                upper = float(parts[3])

                if lower >= upper:
                    self.send_message(chat_id, "❌ Lower price must be less than upper price!")
                    return

                # Check if stock exists
                test_price = self.get_current_price(f"{stock}.NS")
                if test_price is None:
                    self.send_message(
                        chat_id,
                        f"⚠️ Could not fetch price for {stock}. Please verify the stock symbol.\n"
                        f"NSE symbols: RELIANCE, TCS, INFY, HDFCBANK, etc.",
                    )
                    return

                self.add_alert(chat_id, stock, lower, upper)

                self.send_message(
                    chat_id,
                    f"✅ <b>Alert Added!</b>\n\n"
                    f"Stock: {stock}\n"
                    f"Current Price: ₹{test_price}\n"
                    f"Lower Limit: ₹{lower}\n"
                    f"Upper Limit: ₹{upper}\n\n"
                    f"You'll be notified when price breaches these limits.",
                )

            except ValueError:
                self.send_message(
                    chat_id,
                    "❌ Invalid price values! Use numbers only.\n"
                    "Example: /add ETERNAL 275 300",
                )

        # /update STOCK LOWER UPPER
        elif message_text.startswith("/update"):
            parts = message_text.split()
            if len(parts) != 4:
                self.send_message(
                    chat_id,
                    "❌ Invalid format!\n\n"
                    "Use: /update STOCK LOWER UPPER\n"
                    "Example: /update ETERNAL 270 305",
                )
                return

            try:
                stock = parts[1].upper()
                lower = float(parts[2])
                upper = float(parts[3])

                if lower >= upper:
                    self.send_message(chat_id, "❌ Lower price must be less than upper price!")
                    return

                # Check if alert exists and belongs to this user
                if stock not in self.alerts or self.alerts[stock].get("chat_id") != chat_id:
                    self.send_message(
                        chat_id,
                        f"❌ No alert found for {stock}.\n\n"
                        f"Use /add {stock} {lower} {upper} to create one.",
                    )
                    return

                # Get current price
                test_price = self.get_current_price(f"{stock}.NS")

                # Update the alert
                self.alerts[stock]["upper_price"] = upper
                self.alerts[stock]["lower_price"] = lower

                # Reset alert flags so it can trigger again with new thresholds
                self.alert_sent[stock] = {"upper_sent": False, "lower_sent": False}

                self.send_message(
                    chat_id,
                    f"✅ <b>Alert Updated!</b>\n\n"
                    f"Stock: {stock}\n"
                    f"Current Price: ₹{test_price if test_price else 'N/A'}\n"
                    f"New Lower Limit: ₹{lower}\n"
                    f"New Upper Limit: ₹{upper}\n\n"
                    f"Alerts reset - you'll be notified at new thresholds.",
                )

            except ValueError:
                self.send_message(
                    chat_id,
                    "❌ Invalid price values! Use numbers only.\n"
                    "Example: /update ETERNAL 270 305",
                )

        # /list
        elif message_text.startswith("/list"):
            user_alerts = {k: v for k, v in self.alerts.items() if v.get("chat_id") == chat_id}

            if not user_alerts:
                self.send_message(chat_id, "📋 You have no active alerts.\n\nUse /add to create one!")
                return

            list_text = "📋 <b>Your Active Alerts:</b>\n\n"
            for stock, alert_data in user_alerts.items():
                current_price = self.get_current_price(alert_data["ticker"])
                price_str = f"₹{current_price}" if current_price else "N/A"

                list_text += (
                    f"<b>{stock}</b>\n"
                    f"Current: {price_str}\n"
                    f"Range: ₹{alert_data['lower_price']} - ₹{alert_data['upper_price']}\n\n"
                )

            self.send_message(chat_id, list_text)

        # /remove STOCK
        elif message_text.startswith("/remove"):
            parts = message_text.split()
            if len(parts) != 2:
                self.send_message(
                    chat_id,
                    "❌ Invalid format!\n\nUse: /remove STOCK\nExample: /remove ETERNAL",
                )
                return

            stock = parts[1].upper()

            # Check if alert belongs to this user
            if stock in self.alerts and self.alerts[stock].get("chat_id") == chat_id:
                self.remove_alert(stock)
                self.send_message(chat_id, f"✅ Alert removed for {stock}")
            else:
                self.send_message(chat_id, f"❌ No alert found for {stock}")

        else:
            self.send_message(chat_id, "❓ Unknown command. Send /help to see available commands.")

    def run(self):
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

    port = int(os.environ.get("PORT", "8080"))
    app.run(host="0.0.0.0", port=port)


def main():
    """Main function"""
    print("=" * 60)
    print("NSE STOCK ALERT BOT - TELEGRAM COMMAND MODE")
    print("=" * 60)

    # Read token from env var (Railway Variables)
    TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "YOUR_BOT_TOKEN_HERE")

    if not TELEGRAM_BOT_TOKEN or TELEGRAM_BOT_TOKEN == "YOUR_BOT_TOKEN_HERE":
        print("\n❌ ERROR: Please set your Telegram Bot Token")
        print("\nRailway Steps:")
        print("1. Go to your Railway project → Variables")
        print("2. Add TELEGRAM_BOT_TOKEN = <your token from BotFather>")
        print("3. Redeploy")
        return

    # Start the web server in the background (Railway health)
    threading.Thread(target=start_web_server, daemon=True).start()

    # Initialize and run bot
    bot = TelegramCommandBot(TELEGRAM_BOT_TOKEN)

    print("\n✅ Bot initialized!")
    print("\n📱 Now open Telegram and:")
    print("   1. Search for your bot")
    print("   2. Send /start")
    print("   3. Send /add ETERNAL 275 300")
    print("\n" + "=" * 60 + "\n")

    bot.run()


if __name__ == "__main__":
    main()
