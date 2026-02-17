# 📱 Complete Setup Guide: iPhone + 24/7 Monitoring

## 🎯 Overview

**What we're building:**
- A bot that monitors NSE stocks 24/7
- Your dad controls it from Telegram app on his iPhone
- No coding required on his end - just text messages
- Completely FREE

**Total time: 15-20 minutes**

---

## 📋 What You Need

- [ ] A computer (for initial setup only)
- [ ] Telegram app on iPhone (free download)
- [ ] Replit account (free)
- [ ] UptimeRobot account (free) - for 24/7 uptime

---

## STEP 1: Create Telegram Bot (5 minutes)

### On iPhone or Computer:

1. **Open Telegram app**
   
2. **Search for:** `@BotFather`
   - This is Telegram's official bot creator
   - It has a blue verification checkmark

3. **Start conversation:**
   - Tap "START" button
   
4. **Create your bot:**
   - Type: `/newbot`
   - BotFather will ask questions:
   
   ```
   BotFather: Alright, a new bot. How are we going to call it?
   You: Dad's Stock Alerts
   
   BotFather: Good. Now let's choose a username for your bot.
   You: dadstockalerts_bot
   ```
   
   ⚠️ **Username must:**
   - End with "bot" (like: mystocks_bot)
   - Be unique (try different names if taken)

5. **COPY THE TOKEN:**
   - BotFather sends you a message like:
   ```
   Done! Your token is:
   1234567890:ABCdefGHIjklMNOpqrsTUVwxyz-123456
   ```
   
   - **SAVE THIS TOKEN** - paste it in Notes app or email to yourself
   - You'll need it in Step 3

✅ **Bot created!** Now let's deploy it...

---

## STEP 2: Deploy to Replit (10 minutes)

### 2.1 Create Replit Account

1. **Go to:** https://replit.com
   
2. **Click "Sign up"**
   - Use Google/GitHub account (easiest)
   - Or create with email
   - **FREE account is fine**

3. **Verify email** if needed

### 2.2 Create New Repl

1. **Click the "+ Create Repl" button** (top right)

2. **Choose template:**
   - Select "Python" from the list
   
3. **Name your Repl:**
   - Title: `NSE Stock Alerts`
   - Click "Create Repl"

4. **Wait for it to load** (takes ~10 seconds)

### 2.3 Upload Code

1. **Delete the default code:**
   - You'll see a file called `main.py` with some sample code
   - Select all the text (Cmd+A or Ctrl+A)
   - Delete it

2. **Upload the bot code:**
   
   **Option A - Copy/Paste:**
   - Open the file `telegram_command_bot.py` I gave you
   - Copy ALL the code (Cmd+A, Cmd+C)
   - Paste it into the empty `main.py` in Replit (Cmd+V)
   
   **Option B - File Upload:**
   - Click the 3-dots menu in Files panel
   - Click "Upload file"
   - Select `telegram_command_bot.py`
   - Delete the old `main.py`
   - Rename `telegram_command_bot.py` to `main.py`

3. **Upload requirements.txt:**
   - Click "Upload file" again
   - Select the `requirements.txt` file
   - This tells Replit what Python packages to install

### 2.4 Add Your Bot Token

1. **In the code editor, find this line** (around line 380):
   ```python
   TELEGRAM_BOT_TOKEN = "YOUR_BOT_TOKEN_HERE"
   ```

2. **Replace with your actual token:**
   ```python
   TELEGRAM_BOT_TOKEN = "1234567890:ABCdefGHIjklMNOpqrsTUVwxyz-123456"
   ```
   - Keep the quotes!
   - Paste the token you saved from Step 1

3. **Save the file:**
   - Press Cmd+S (Mac) or Ctrl+S (Windows)
   - Or it auto-saves

### 2.5 Run It!

1. **Click the big green "Run" button** at the top

2. **Wait for installation** (first time only, takes 1-2 minutes):
   - You'll see packages being installed
   - Watch the console on the right

3. **Success message:**
   ```
   🤖 Bot started! Send /help to the bot on Telegram.
   📱 Now open Telegram and...
   ```

4. **COPY THE URL:**
   - At the top of Replit, you'll see a URL like:
   - `https://nse-stock-alerts.yourname.repl.co`
   - **Copy this URL** - you need it for Step 3!

✅ **Bot is running!** But it will sleep after 1 hour... let's fix that...

---

## STEP 3: Keep It Running 24/7 (5 minutes)

### Why We Need This:
Replit's free tier puts inactive apps to "sleep" after 1 hour. UptimeRobot will "ping" your app every 5 minutes to keep it awake - for FREE!

### 3.1 Create UptimeRobot Account

1. **Go to:** https://uptimerobot.com

2. **Click "Sign Up Free"**
   - Use email to create free account
   - Verify your email

3. **Log in**

### 3.2 Add Monitor

1. **Click "+ Add New Monitor"** (big green button)

2. **Fill in the form:**
   - **Monitor Type:** HTTP(s)
   - **Friendly Name:** NSE Stock Alerts
   - **URL:** Paste your Replit URL from Step 2.5
     - Example: `https://nse-stock-alerts.yourname.repl.co`
   - **Monitoring Interval:** 5 minutes (default)

3. **Click "Create Monitor"**

4. **Status should show green "Up"** within a minute

✅ **Your bot now runs 24/7 for FREE!**

---

## STEP 4: Your Dad Uses It on iPhone (2 minutes)

### 4.1 Download Telegram

1. **Open App Store on iPhone**
2. **Search:** "Telegram"
3. **Download** the app (blue paper airplane icon)
4. **Sign up/Log in** with phone number

### 4.2 Start Using the Bot

1. **Open Telegram app**

2. **Search for your bot:**
   - Tap the search icon (magnifying glass)
   - Type the bot username you created
   - Example: `@dadstockalerts_bot`

3. **Start the bot:**
   - Tap "START" button
   - Or type: `/start`

4. **Add first alert:**
   - Type: `/add ETERNAL 275 300`
   - Press send

5. **Bot confirms:**
   ```
   ✅ Alert Added!
   Stock: ETERNAL
   Current Price: ₹285
   Lower Limit: ₹275
   Upper Limit: ₹300
   
   You'll be notified when price breaches these limits.
   ```

### 4.3 Daily Usage

Your dad just needs to remember these 4 commands:

```
/add STOCK LOWER UPPER    → Add new alert
/update STOCK LOWER UPPER → Change limits
/list                     → See all alerts
/remove STOCK             → Delete alert
```

**Examples:**
```
/add RELIANCE 2400 2500
/update ETERNAL 270 305
/list
/remove RELIANCE
```

---

## 📱 How Alerts Look on iPhone

When a price breaches, your dad gets a notification on his iPhone:

```
🚨 PRICE ALERT - UPPER BREACH 🚨

Stock: ETERNAL
Current Price: ₹301.50
Upper Threshold: ₹300
Time: 2026-02-10 10:30:45
```

He can:
- ✅ See it in Notification Center
- ✅ See it in Telegram app
- ✅ Get sound/vibration alert
- ✅ Receive it even when phone is locked

---

## ⚙️ iPhone Notification Settings

### To ensure your dad gets alerts:

1. **Open iPhone Settings**
2. **Scroll to "Telegram"**
3. **Tap "Notifications"**
4. **Enable:**
   - ✅ Allow Notifications
   - ✅ Sounds
   - ✅ Badges
   - ✅ Show on Lock Screen
   - ✅ Show in Notification Center

5. **Notification Style:** Banners (stays on screen)

---

## 🔧 Troubleshooting

### Bot not responding to commands:

**Check 1:** Is Replit running?
- Go to https://replit.com
- Open your Repl
- Make sure it says "Running" (green indicator)
- If stopped, click "Run" again

**Check 2:** Is UptimeRobot active?
- Log into https://uptimerobot.com
- Check monitor shows green "Up"
- If down, check the Replit URL is correct

**Check 3:** Did your dad start the bot?
- He must send `/start` first time
- Search for the bot's username in Telegram

### Not getting price alerts:

**Check 1:** Stock symbol correct?
- Must be valid NSE symbol
- Examples: ETERNAL, RELIANCE, TCS, INFY
- Find symbols at: https://www.nseindia.com

**Check 2:** Is it market hours?
- NSE open: 9:15 AM - 3:30 PM IST (Mon-Fri)
- Bot checks prices during market hours

**Check 3:** Has price actually breached?
- Type `/list` to see current prices
- Make sure current price is beyond your limits

### Replit says "Always running limit reached":

This happens on free tier. Solutions:
- **Option 1:** Stop other Repls you have running
- **Option 2:** Upgrade to Replit Hacker plan ($7/month) for guaranteed uptime
- **Option 3:** Create new free Replit account

---

## 💰 Costs

### Completely FREE Option:
- Replit Free Tier: **$0**
- UptimeRobot Free: **$0**
- Telegram: **$0**
- **Total: $0/month** ✅

Limitations:
- May occasionally sleep if UptimeRobot fails
- Limited to 50 monitors on free UptimeRobot

### Reliable 24/7 Option:
- Replit Hacker Plan: **$7/month**
- Guaranteed always-on
- No sleep issues
- Worth it if your dad trades actively

---

## 🎯 Final Checklist

Before you hand it off to your dad:

- [ ] Bot created on Telegram (@BotFather)
- [ ] Code deployed to Replit
- [ ] Bot token added to code
- [ ] Replit is running (green indicator)
- [ ] UptimeRobot monitor created and showing "Up"
- [ ] Tested: Send `/start` to bot and get response
- [ ] Tested: Send `/add ETERNAL 275 300` and get confirmation
- [ ] Telegram installed on dad's iPhone
- [ ] Notifications enabled in iPhone settings
- [ ] Dad knows the 4 main commands

---

## 📖 Print This for Your Dad

```
┌─────────────────────────────────────────┐
│  TELEGRAM STOCK ALERTS - QUICK GUIDE    │
└─────────────────────────────────────────┘

Bot Username: @your_bot_username_here

COMMANDS:
─────────
/add ETERNAL 275 300     → Add alert
/update ETERNAL 270 305  → Change prices
/list                    → See all alerts
/remove ETERNAL          → Delete alert
/help                    → Show help

EXAMPLES:
─────────
Add Reliance alert:
/add RELIANCE 2400 2500

Change Eternal limits:
/update ETERNAL 270 310

See all your alerts:
/list

Remove Reliance alert:
/remove RELIANCE

WHEN YOU GET AN ALERT:
──────────────────────
🚨 Check the price
🚨 Decide if you want to trade
🚨 Update limits if needed with /update

NSE MARKET HOURS:
─────────────────
Monday - Friday
9:15 AM - 3:30 PM IST

NEED HELP?
──────────
Send: /help
Or call me!
```

---

## 🚀 Advanced: Running on Your Own Server

If you want to run this on your own computer/server 24/7:

1. **Install Python 3.7+**
2. **Run:**
   ```bash
   pip install yfinance requests
   python telegram_command_bot.py
   ```
3. **Keep terminal open**
4. **Use `screen` or `tmux` on Linux to run in background**

But Replit + UptimeRobot is easier!

---

## 📞 Support

If something breaks:

1. **Check Replit console** for error messages
2. **Restart the Repl** (Stop, then Run)
3. **Check bot token** is correct
4. **Verify stock symbols** are valid NSE symbols

---

## 🎉 You're Done!

Your dad now has a personal stock alert system that:
- ✅ Runs 24/7 automatically
- ✅ Works on his iPhone
- ✅ Requires no coding knowledge
- ✅ Costs $0 per month
- ✅ Sends instant Telegram alerts

He just texts the bot - that's it! 🚀
