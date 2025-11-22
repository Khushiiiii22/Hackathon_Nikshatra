# 📱 REAL-TIME PHONE DATA - QUICK START GUIDE

## 🎯 **30-SECOND SETUP**

### ✅ Your Backend is RUNNING!
- **URL:** `http://10.0.0.8:5000`
- **Status:** Gemini AI ✅ | Health Twin ✅
- **Ready:** Accepting real-time data from your phone!

---

## 📱 **USE YOUR PHONE NOW - 3 OPTIONS**

### **Option 1: Web Interface (FASTEST - Works on ANY phone!)**

**On your phone:**

1. **Connect to same WiFi** as your Mac
2. **Open Safari/Chrome** and go to:
   ```
   http://10.0.0.8:5000/phone_monitor.html
   ```
3. **Choose monitoring method:**
   - 📷 **Camera PPG** - Place finger on camera
   - ✋ **Manual Input** - Enter vitals manually

4. **Tap "START MONITORING"**

**That's it!** Real-time data flows: Phone → Flask → Gemini → Alerts

---

### **Option 2: iOS HealthKit App (Advanced - Requires Xcode)**

See: `docs/IPHONE_SWIFT_CODE.md`

1. Open Xcode → New iOS App
2. Copy Swift code from docs
3. Change URL to: `http://10.0.0.8:5000/api/vitals`
4. Run on real iPhone

---

### **Option 3: Quick Test via cURL**

```bash
# From your phone or computer
curl -X POST http://10.0.0.8:5000/api/vitals \
  -H "Content-Type: application/json" \
  -d '{
    "patient_id": "TEST_PHONE",
    "heart_rate": 85,
    "hrv_rmssd": 45,
    "spo2": 97,
    "data_source": "phone_test"
  }'
```

---

## 🎬 **DEMO - TRIGGER A CARDIAC EVENT**

### Using Web Interface:

1. Open: `http://10.0.0.8:5000/phone_monitor.html`
2. Switch to **Manual Input**
3. Enter these values:

**Scenario 1: Normal Vitals**
```
Heart Rate: 72
HRV: 65
SpO2: 98
```
Result: ✅ All normal

**Scenario 2: Developing Cardiac Event**
```
Heart Rate: 95
HRV: 38
SpO2: 94
```
Result: ⚠️ **ALERT!** Gemini detects Pre-NSTEMI

**Scenario 3: Critical Event**
```
Heart Rate: 115
HRV: 25
SpO2: 91
```
Result: 🚨 **EMERGENCY ALERT!** High risk cardiac event

---

## 🎥 **CAMERA PPG - HOW IT WORKS**

The web interface includes **Camera PPG (Photoplethysmography)**:

1. **Uses your phone's camera** as a sensor
2. **Place fingertip** over camera lens
3. **Measures blood flow** by detecting red light changes
4. **Calculates heart rate and HRV** in real-time
5. **Sends data** to backend every 5 seconds

**No wearable needed!** Works on iPhone, Android, any phone with camera.

---

## 📊 **WHAT YOU'LL SEE**

### On Your Phone:
```
╔══════════════════════════════╗
║      ❤️ MIMIQ                ║
║ Real-Time Cardiac Monitoring ║
║                              ║
║        72                    ║
║   Heart Rate (bpm)           ║
║                              ║
║        65                    ║
║      HRV (ms)                ║
║                              ║
║        98                    ║
║      SpO2 (%)                ║
║                              ║
║   [STOP MONITORING]          ║
║                              ║
║ Patient: PHONE_USER_A7F2     ║
║ Backend: Connected ✅        ║
╚══════════════════════════════╝
```

### In Your Terminal (Backend):
```
📊 Vitals received: PHONE_USER_A7F2 - HR=72, HRV=65
✅ Normal vitals

[30 seconds later]

📊 Vitals received: PHONE_USER_A7F2 - HR=95, HRV=38
⚠️  Anomaly detected!
🤖 Analyzing with Gemini AI...
📋 Diagnosis: Pre-NSTEMI (89% confidence)
🚨 ALERT SENT!
```

### On Phone (Alert):
```
⚠️ Cardiac Event Detected!
Diagnosis: Pre-NSTEMI
Risk Level: HIGH
Confidence: 89%
```

---

## 🔥 **FEATURES OF WEB INTERFACE**

✅ **Two Monitoring Methods:**
- Camera PPG (automatic detection)
- Manual input (for testing)

✅ **Real-Time Updates:**
- Data sent every 5 seconds
- Live heart rate display
- Live HRV display

✅ **Gemini AI Integration:**
- Automatic anomaly detection
- Medical diagnosis with confidence
- Risk level assessment

✅ **Alert System:**
- Visual alerts on phone
- Vibration feedback
- Auto-dismiss after 10 seconds

✅ **Beautiful UI:**
- Responsive design
- Gradient backgrounds
- Animated status indicators

---

## 🛠️ **TROUBLESHOOTING**

### "Cannot connect to backend"

1. **Check WiFi:** Phone and Mac on same network?
   ```bash
   # On Mac, verify IP:
   ifconfig | grep "inet " | grep -v 127.0.0.1
   ```

2. **Check backend running:**
   ```bash
   lsof -ti:5000  # Should show process ID
   ```

3. **Test from Safari:**
   - Open: `http://10.0.0.8:5000`
   - Should see MIMIQ dashboard

### "Camera not working"

1. **Allow camera permission** in browser
2. **Use Safari** (best compatibility on iOS)
3. **Try manual input** instead

### "No data showing"

1. **Check browser console:** F12 → Console
2. **Look for errors** in red
3. **Verify backend URL** in phone_monitor.html:
   ```javascript
   const BACKEND_URL = window.location.origin + '/api/vitals';
   ```

---

## 🌐 **ACCESS FROM ANYWHERE (Optional)**

### Use ngrok for internet access:

```bash
# Install ngrok
brew install ngrok

# Create tunnel
ngrok http 5000

# You'll get a URL like:
# https://abc123.ngrok.io
```

Then on phone: `https://abc123.ngrok.io/phone_monitor.html`

**Works from anywhere!** Perfect for demo day.

---

## 📁 **FILES CREATED**

1. **phone_monitor.html** - Web-based phone interface
2. **app_integrated.py** - Flask backend (running)
3. **docs/IPHONE_SWIFT_CODE.md** - iOS app code
4. **docs/IPHONE_API_CONNECTION.md** - Deployment guide

---

## 🎯 **RECOMMENDED FOR DEMO**

### **Best Setup:**

1. **Use web interface** (`phone_monitor.html`)
   - No app installation needed
   - Works on ANY phone
   - Instant setup

2. **Use Camera PPG** for live demo
   - Shows real sensor technology
   - No manual input needed
   - More impressive!

3. **Or use Manual Input** for controlled demo
   - Predictable results
   - Can trigger specific scenarios
   - Faster demonstration

---

## ✅ **SUMMARY**

You now have **3 ways** to get real-time data from your phone:

| Method | Setup Time | Pros | Use Case |
|--------|-----------|------|----------|
| **Web Interface** | 30 seconds | Works on any phone, no app needed | Best for demo! |
| **iOS HealthKit** | 30 minutes | Real health data, background monitoring | Production use |
| **cURL Test** | 10 seconds | Quick testing | Development |

**Start now:** Open your phone → Safari → `http://10.0.0.8:5000/phone_monitor.html`

---

## 🎬 **NEXT STEPS**

1. **Test web interface** on your phone
2. **Trigger some alerts** with abnormal vitals
3. **Show the demo** to judges
4. **Deploy to cloud** (optional, see docs/IPHONE_API_CONNECTION.md)

**Backend is running and waiting for data!** 🚀

---

*Last Updated: November 22, 2025*  
*Your IP: 10.0.0.8*  
*Backend: http://10.0.0.8:5000*
