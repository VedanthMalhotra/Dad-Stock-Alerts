# 🚀 START HERE - Simple Setup Guide

## ❓ IMPORTANT: Who Does What?

### YOU (One-Time Setup - 15 min):
- ✅ Create the bot using BotFather on YOUR Telegram
- ✅ Upload code to Replit
- ✅ Setup 24/7 monitoring

### YOUR DAD (Daily Use):
- ✅ Just messages the bot on HIS Telegram
- ✅ Never touches BotFather or code
- ✅ Types commands like: /add ETERNAL 275 300

**The bot is like a separate person - you create it, he messages it!**

---

## 📋 STEP-BY-STEP DEPLOYMENT

### STEP 1: Create Bot (YOU do this - 5 min)

1. **Open Telegram on YOUR phone** (not dad's!)
   
2. **Search for:** @BotFather (blue checkmark, official bot)

3. **Send:** `/newbot`

4. **BotFather asks: "What's your bot's name?"**
   - Type: `Dad Stock Alerts`
   
5. **BotFather asks: "What's your bot's username?"**
   - Type: `dadstockalerts_bot`
   - (Must end with "bot", must be unique)
   - If taken, try: `mystockalerts_bot` or `stocknotify_bot`

6. **BotFather replies with a TOKEN:**
   ```
   Done! Your token is:
   1234567890:ABCdefGHIjklMNOpqrsTUVwxyz-123456
   ```

7. **COPY THIS TOKEN** and save it:
   - Paste in Notes app on your phone
   - Or email it to yourself
   - You'll need it in Step 2!

✅ **Bot created! Now deploy it...**

---

### STEP 2: Upload Code to Replit (YOU do this - 7 min)

1. **On your computer, go to:** https://replit.com

2. **Sign up:**
   - Click "Sign up"
   - Use Google login (easiest)
   - Free account is fine

3. **Create new Repl:**
   - Click "+ Create Repl"
   - Select template: **Python**
   - Title: `NSE Stock Alerts`
   - Click "Create Repl"

4. **Delete default code:**
   - You'll see a file called `main.py` with some code
   - Select all (Ctrl+A or Cmd+A)
   - Delete it (leave file empty)

5. **Add the bot code:**
   - Open the file: `telegram_command_bot.py` (from downloads)
   - Open it with Notepad/TextEdit
   - **FIND THIS LINE** (near the bottom, around line 380):
     ```python
     TELEGRAM_BOT_TOKEN = "YOUR_BOT_TOKEN_HERE"
     ```
   - **REPLACE WITH YOUR ACTUAL TOKEN:**
     ```python
     TELEGRAM_BOT_TOKEN = "1234567890:ABCdefGHIjklMNOpqrsTUVwxyz-123456"
     ```
     ⚠️ Keep the quotes! Just replace the text between them.
   
   - **Copy ALL the code** (Ctrl+A, Ctrl+C)
   - **Paste into Replit's main.py** (Ctrl+V)

6. **Add requirements file:**
   - In Replit, click the "Files" icon (left sidebar)
   - Click the 3-dot menu (•••)
   - Click "Upload file"
   - Select the file: `requirements.txt`
   - Click Open

7. **Run it!**
   - Click the big green **"Run"** button at the top
   - Wait 1-2 minutes (installing packages)
   - Look for: **"🤖 Bot started!"**

8. **Copy your Replit URL:**
   - At the top, you'll see a URL like:
   - `https://nse-stock-alerts.yourname.repl.co`
   - **COPY THIS URL** (you need it for Step 3)

✅ **Bot is running! But will sleep in 1 hour... let's fix that...**

---

### STEP 3: Keep It Running 24/7 (YOU do this - 3 min)

1. **Go to:** https://uptimerobot.com

2. **Sign up:**
   - Click "Sign Up Free"
   - Use email
   - Verify email
   - Login

3. **Add monitor:**
   - Click "+ Add New Monitor" (green button)
   - **Monitor Type:** HTTP(s)
   - **Friendly Name:** NSE Stock Alerts
   - **URL:** [Paste your Replit URL from Step 2]
   - **Monitoring Interval:** 5 minutes
   - Click "Create Monitor"

4. **Check status:**
   - Should show green "Up" within 1 minute

✅ **Bot now runs 24/7 for FREE!**

---

### STEP 4: Your Dad Uses It (HE does this - 2 min)

**On his iPhone:**

1. **Download Telegram app** (if not already installed)
   - Open App Store
   - Search: "Telegram"
   - Download (free)
   - Sign up with his phone number

2. **Find your bot:**
   - Open Telegram
   - Tap search icon (🔍)
   - Type: `@dadstockalerts_bot` (or whatever you named it)
   - Tap on the bot

3. **Start the bot:**
   - Tap "START" button
   - Bot says: "Welcome! Send /help to see commands"

4. **Add first alert:**
   - Type: `/add ETERNAL 275 300`
   - Press send
   - Bot confirms: ✅ Alert Added!

5. **See all alerts:**
   - Type: `/list`
   - Bot shows all active alerts

✅ **DONE! He's using it!**

---

## 📱 What Your Dad Does Daily

He just opens Telegram and types:

```
/add RELIANCE 2400 2500     → Add stock alert
/update RELIANCE 2350 2550  → Change prices
/list                       → See all alerts
/remove RELIANCE            → Delete alert
/help                       → Show commands
```

**When a price hits, he gets:**
```
🚨 PRICE ALERT - UPPER BREACH 🚨

Stock: RELIANCE
Current Price: ₹2501.20
Upper Threshold: ₹2500
Time: 2026-02-10 11:45:30
```

---

## 🎯 Quick Checklist

- [ ] YOU created bot on YOUR Telegram (@BotFather)
- [ ] YOU got bot token and saved it
- [ ] YOU created Replit account
- [ ] YOU uploaded code to Replit
- [ ] YOU added YOUR token to the code
- [ ] YOU clicked Run - shows "Bot started!"
- [ ] YOU copied Replit URL
- [ ] YOU created UptimeRobot account
- [ ] YOU added monitor with Replit URL
- [ ] DAD downloads Telegram on his iPhone
- [ ] DAD searches for bot by username
- [ ] DAD sends /start
- [ ] DAD sends /add ETERNAL 275 300
- [ ] DAD gets confirmation ✅

---

## 📂 Files You Need

**For Replit (upload these):**
1. `telegram_command_bot.py` - Main code
2. `requirements.txt` - Dependencies

**For Your Dad (print this):**
3. `PRINTABLE_REFERENCE_CARD.txt` - Command reference

**If You Get Stuck (read these):**
4. `COMPLETE_IPHONE_SETUP.md` - Detailed guide
5. `DEPLOYMENT_CHECKLIST.md` - Step-by-step checklist

---

## 🆘 Troubleshooting

**Bot not responding to dad's messages:**
- Did you click "Run" in Replit?
- Check Replit shows "Running" (green)
- Did dad send /start first?
- Is he searching for the right bot username?

**Can't find bot on Telegram:**
- Search for the EXACT username: `@dadstockalerts_bot`
- Make sure it starts with @ symbol
- Try searching from dad's phone

**Bot stopped working:**
- Check UptimeRobot shows "Up"
- Check Replit is still running
- Click "Run" again if needed

**Error: "Invalid stock symbol":**
- Use NSE symbols: RELIANCE, TCS, INFY, HDFCBANK
- Find symbols at: https://www.nseindia.com

---

## 💡 Key Points

1. **You create the bot ONCE on YOUR Telegram**
2. **Your dad never touches BotFather**
3. **He just messages the bot like a friend**
4. **Bot runs 24/7 for FREE**
5. **He controls everything via text commands**

---

## 💰 Cost

- Telegram: **FREE**
- Replit Free Tier: **FREE**
- UptimeRobot Free: **FREE**
- **Total: $0/month** ✅

---

## 📞 Need Help?

1. Read `COMPLETE_IPHONE_SETUP.md` for detailed steps
2. Check `DEPLOYMENT_CHECKLIST.md` for checkboxes
3. Print `PRINTABLE_REFERENCE_CARD.txt` for dad

---

**That's it! 15 minutes and your dad has a personal stock alert system!** 🎉
