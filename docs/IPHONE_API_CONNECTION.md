# 📱 iPhone to API Connection Guide

**How to connect your iPhone to the MIMIQ backend API**

---

## 🎯 Quick Start (30 seconds)

### Step 1: Find Your Computer's IP Address

```bash
# On Mac, run this:
ipconfig getifaddress en0

# Example output: 192.168.1.105
```

### Step 2: Your API URL

```
http://YOUR_IP_ADDRESS:5000
Example: http://192.168.1.105:5000
```

### Step 3: Test from iPhone

1. Make sure iPhone and Mac are on **same WiFi**
2. Open Safari on iPhone
3. Go to: `http://192.168.1.105:5000` (use your IP)
4. You should see the MIMIQ dashboard!

---

## 📱 Method 1: Local Network (For Testing)

**Pros:** ✅ Free, ✅ Fast, ✅ No setup
**Cons:** ⚠️ Only works on same WiFi

### Setup:

1. **Get your Mac's IP:**
   ```bash
   ipconfig getifaddress en0
   # Output: 192.168.1.105 (example)
   ```

2. **API is already running at:**
   ```
   http://192.168.1.105:5000
   ```

3. **iPhone Swift code:**
   ```swift
   let backendURL = "http://192.168.1.105:5000/api/vitals"
   //                       ^^^^^^^^^^^^^^
   //                       Replace with YOUR IP
   ```

4. **Allow local network on Mac:**
   ```bash
   # API is already configured to accept connections from anywhere
   # Running on 0.0.0.0:5000 ✅
   ```

### Test It:

```bash
# From your iPhone Safari:
http://192.168.1.105:5000

# You should see the MIMIQ dashboard
```

---

## 🌐 Method 2: ngrok (Easiest Internet Access)

**Pros:** ✅ Works anywhere, ✅ Free tier available, ✅ 2-minute setup
**Cons:** ⚠️ URL changes on restart (free tier)

### Setup:

1. **Install ngrok:**
   ```bash
   brew install ngrok
   ```

2. **Sign up for free account:**
   ```bash
   # Go to: https://ngrok.com/
   # Create account (free)
   # Get auth token
   
   ngrok config add-authtoken YOUR_TOKEN
   ```

3. **Expose your API:**
   ```bash
   ngrok http 5000
   ```

4. **You'll get a public URL:**
   ```
   Forwarding: https://abc123.ngrok.io -> http://localhost:5000
   ```

5. **Use this URL in iPhone:**
   ```swift
   let backendURL = "https://abc123.ngrok.io/api/vitals"
   ```

### Start Script:

I'll create a script for you below!

---

## ☁️ Method 3: Deploy to Render (Free Cloud)

**Pros:** ✅ Permanent URL, ✅ Free tier, ✅ Works anywhere
**Cons:** ⚠️ Sleeps after 15 min inactivity (free tier)

### Setup:

1. **Create account:** https://render.com (free)

2. **Deploy:**
   - Click "New Web Service"
   - Connect GitHub repo
   - Settings:
     - Build Command: `pip install -r requirements.txt`
     - Start Command: `python app_integrated.py`
   - Add environment variable:
     - `GEMINI_API_KEY` = your key

3. **Get your URL:**
   ```
   https://mimiq-api.onrender.com
   ```

4. **Use in iPhone:**
   ```swift
   let backendURL = "https://mimiq-api.onrender.com/api/vitals"
   ```

I'll create deployment files below!

---

## 🚀 Recommended for Demo Day

**Use ngrok!** It's the fastest and works from anywhere.

```bash
# Terminal 1: Run API
python app_integrated.py

# Terminal 2: Expose with ngrok
ngrok http 5000

# Use the https URL in your iPhone app
```

---

## 📋 Complete Setup Commands

### Quick Start (Local Network):

```bash
# 1. Get your IP
IP=$(ipconfig getifaddress en0)
echo "Your API: http://$IP:5000"

# 2. API is already running!
# 3. Open on iPhone Safari: http://YOUR_IP:5000
```

### With ngrok (Internet Access):

```bash
# Install ngrok (one time)
brew install ngrok

# Sign up at ngrok.com and get auth token
ngrok config add-authtoken YOUR_TOKEN

# Run API
python app_integrated.py  # Terminal 1

# Expose API
ngrok http 5000           # Terminal 2

# Copy the https URL to iPhone app
```

---

## 🔧 Troubleshooting

### Can't connect from iPhone?

1. **Check same WiFi:**
   ```bash
   # Mac and iPhone must be on SAME network
   ```

2. **Check Mac firewall:**
   ```bash
   # System Settings > Network > Firewall
   # Allow Python to accept connections
   ```

3. **Test from Mac first:**
   ```bash
   curl http://localhost:5000/health
   # Should return: {"status": "healthy"}
   ```

4. **Check IP is correct:**
   ```bash
   ipconfig getifaddress en0
   # Use this exact IP
   ```

### ngrok not working?

1. **Free account limits:**
   - Max 1 tunnel at a time
   - URL changes on restart
   - Upgrade for static URL

2. **Check ngrok is running:**
   ```bash
   ngrok http 5000
   # Don't close this terminal!
   ```

---

## 📱 iPhone App Code

Complete Swift implementation coming in next file!

See: `docs/IPHONE_SWIFT_CODE.md`

---

## ✅ Summary

| Method | Speed | Cost | Works From | Best For |
|--------|-------|------|------------|----------|
| **Local Network** | ⚡ Instant | Free | Same WiFi | Development |
| **ngrok** | 🚀 2 min | Free | Anywhere | Demo Day |
| **Render** | 🐌 5 min | Free | Anywhere | Production |

**Recommendation:** Use ngrok for your hackathon demo!

---

## 🎬 Demo Day Setup

```bash
# 1 hour before demo:
ngrok http 5000

# Copy the https URL (e.g., https://abc123.ngrok.io)
# Paste in iPhone app
# Test once
# Done! 🎉
```

---

*Last Updated: November 22, 2025*  
*File: docs/IPHONE_API_CONNECTION.md*
