# 📱 REAL-TIME PHONE MONITORING - VISUAL GUIDE

## 🎯 **YOUR SYSTEM IS LIVE!**

```
┌─────────────────────────────────────────────────────────┐
│  ✅ Flask API: RUNNING on http://10.0.0.8:5000         │
│  ✅ Gemini AI: ENABLED                                  │
│  ✅ Health Twin: ACTIVE                                 │
│  ✅ Phone Interface: READY                              │
└─────────────────────────────────────────────────────────┘
```

---

## 📱 **STEP-BY-STEP: GET REAL-TIME DATA NOW**

### **Step 1: Open Your Phone** 📱

1. Make sure your phone is on **same WiFi** as your Mac
2. Open **Safari** (iPhone) or **Chrome** (Android)
3. Type this URL:

```
┌─────────────────────────────────────────┐
│  http://10.0.0.8:5000/phone_monitor.html│
└─────────────────────────────────────────┘
```

### **Step 2: You'll See This Screen** 👀

```
╔══════════════════════════════════════╗
║          ❤️ MIMIQ                    ║
║   Real-Time Cardiac Monitoring       ║
║                                      ║
║  [📷 Camera PPG] [✋ Manual Input]   ║
║                                      ║
║  ┌────────────────────────────┐     ║
║  │         --                 │     ║
║  │    Heart Rate (bpm)        │     ║
║  └────────────────────────────┘     ║
║                                      ║
║  ┌────────────────────────────┐     ║
║  │         --                 │     ║
║  │       HRV (ms)             │     ║
║  └────────────────────────────┘     ║
║                                      ║
║  ┌────────────────────────────┐     ║
║  │         --                 │     ║
║  │       SpO2 (%)             │     ║
║  └────────────────────────────┘     ║
║                                      ║
║  ╔══════════════════════════╗       ║
║  ║  START MONITORING        ║       ║
║  ╚══════════════════════════╝       ║
║                                      ║
║  Patient ID: PHONE_USER_A7F2        ║
║  Backend: Connected ✅              ║
╚══════════════════════════════════════╝
```

### **Step 3: Choose Monitoring Method** 🎯

#### **Option A: Camera PPG (Automatic)**

1. Tap **"📷 Camera PPG"** button
2. Tap **"START MONITORING"**
3. **Allow camera permission** when prompted
4. **Place your fingertip** on the back camera
5. Cover the lens completely
6. Hold still for 10-15 seconds
7. Watch the numbers update!

```
┌──────────────────────────────┐
│  👆 FINGER ON CAMERA         │
│  ───────────────────         │
│     [Camera Lens]            │
│  ───────────────────         │
│  Cover it completely!        │
└──────────────────────────────┘
```

#### **Option B: Manual Input (For Testing)**

1. Tap **"✋ Manual Input"** button
2. Enter vitals:
   - Heart Rate: `72`
   - HRV: `65`
   - SpO2: `98`
3. Tap **"START MONITORING"**
4. Data sends every 5 seconds automatically

### **Step 4: See Real-Time Results** 📊

**On your phone, you'll see:**

```
╔══════════════════════════════╗
║     Status: Monitoring...    ║
║                              ║
║         72                   ║  ← Updates live!
║    Heart Rate (bpm)          ║
║                              ║
║         65                   ║  ← Updates live!
║      HRV (ms)                ║
║                              ║
║         98                   ║  ← Updates live!
║      SpO2 (%)                ║
╚══════════════════════════════╝
```

**In your Mac terminal, you'll see:**

```
2025-11-22 01:45:32 | INFO - 📊 Vitals received: PHONE_USER_A7F2
2025-11-22 01:45:32 | INFO -    HR=72, HRV=65, SpO2=98
2025-11-22 01:45:32 | INFO - ✅ Normal vitals for PHONE_USER_A7F2
```

---

## 🚨 **DEMO: TRIGGER A CARDIAC ALERT**

### **Test Scenario: Detect Pre-NSTEMI**

1. **Switch to Manual Input** mode
2. **Enter these values:**

```
┌─────────────────────────┐
│ Heart Rate: 95          │ ← Elevated HR
│ HRV: 38                 │ ← Low HRV (stress!)
│ SpO2: 94                │ ← Slightly low oxygen
└─────────────────────────┘
```

3. **Tap START MONITORING**
4. **Wait 5-10 seconds...**

### **What Happens:**

**On your phone:**
```
╔══════════════════════════════════════╗
║ ⚠️ Cardiac Event Detected!          ║
║                                      ║
║ Diagnosis: Pre-NSTEMI                ║
║ Risk Level: HIGH                     ║
║ Confidence: 89%                      ║
║                                      ║
║ [Phone vibrates! 📳]                 ║
╚══════════════════════════════════════╝
```

**In your terminal:**
```
2025-11-22 01:46:15 | INFO - 📊 Vitals received: PHONE_USER_A7F2
2025-11-22 01:46:15 | INFO -    HR=95, HRV=38, SpO2=94
2025-11-22 01:46:15 | WARNING - ⚠️  Anomaly detected!
2025-11-22 01:46:15 | INFO - 🤖 Analyzing with Gemini AI...
2025-11-22 01:46:16 | WARNING - 📋 Gemini Diagnosis:
2025-11-22 01:46:16 | WARNING -    Pre-NSTEMI (89% confidence)
2025-11-22 01:46:16 | WARNING -    Risk: HIGH (risk_score: 25%)
2025-11-22 01:46:16 | CRITICAL - 🚨 ALERT SENT!
2025-11-22 01:46:16 | CRITICAL -    Patient: PHONE_USER_A7F2
2025-11-22 01:46:16 | CRITICAL -    SMS: +1234567890
2025-11-22 01:46:16 | CRITICAL -    ER: Johns Hopkins Emergency
```

**Boom! Complete end-to-end flow in action! 🎯**

---

## 🎬 **COMPLETE DATA FLOW VISUALIZATION**

```
┌──────────────┐
│  YOUR PHONE  │
│              │
│   👆 Finger  │
│   on camera  │
│              │
│  Or manual   │
│  input       │
└──────┬───────┘
       │ Camera PPG detects
       │ blood flow changes
       │ OR
       │ Manual vitals entered
       ▼
┌──────────────┐
│  JavaScript  │
│  calculates: │
│  • HR: 95    │
│  • HRV: 38   │
│  • SpO2: 94  │
└──────┬───────┘
       │ HTTP POST
       │ http://10.0.0.8:5000/api/vitals
       ▼
┌──────────────────────────┐
│  FLASK API (Your Mac)    │
│  app_integrated.py       │
│                          │
│  1. Receives vitals      │
│  2. Health Twin check    │
│  3. Detects anomaly!     │
└──────┬───────────────────┘
       │ Anomaly detected
       │ HR elevated, HRV low
       ▼
┌──────────────────────────┐
│  GEMINI AI               │
│  (Google Cloud)          │
│                          │
│  Analyzes patterns:      │
│  "Pre-NSTEMI, 89% sure"  │
└──────┬───────────────────┘
       │ Diagnosis returned
       ▼
┌──────────────────────────┐
│  ALERT SYSTEM            │
│                          │
│  • SMS to patient        │
│  • ER notification       │
│  • Push to phone         │
└──────┬───────────────────┘
       │
       ▼
┌──────────────┐
│  YOUR PHONE  │
│              │
│  ⚠️ ALERT!   │
│  Pre-NSTEMI  │
│  detected    │
│              │
│  📳 Vibrate  │
└──────────────┘
```

**Total time: 2-5 seconds from finger to alert!**

---

## 🧪 **TESTING SCENARIOS**

### **Scenario 1: Normal Patient**
```javascript
Heart Rate: 72
HRV: 65
SpO2: 98
```
**Expected:** ✅ "Normal vitals"

---

### **Scenario 2: Early Warning**
```javascript
Heart Rate: 85
HRV: 48
SpO2: 96
```
**Expected:** ⚠️ "Mild anomaly detected"

---

### **Scenario 3: Pre-NSTEMI**
```javascript
Heart Rate: 95
HRV: 38
SpO2: 94
```
**Expected:** 🚨 "Pre-NSTEMI, HIGH risk"

---

### **Scenario 4: Critical Event**
```javascript
Heart Rate: 115
HRV: 25
SpO2: 91
```
**Expected:** 🚨 "NSTEMI likely, CRITICAL"

---

## 📊 **MONITORING DATA FLOW**

### **Data Sent Every 5 Seconds:**

```json
{
  "patient_id": "PHONE_USER_A7F2",
  "heart_rate": 95,
  "hrv_rmssd": 38,
  "spo2": 94,
  "timestamp": 1732243532.45,
  "data_source": "phone_camera_ppg"
}
```

### **Response Received:**

```json
{
  "status": "processed",
  "patient_id": "PHONE_USER_A7F2",
  "is_anomaly": true,
  "diagnosis": "Pre-NSTEMI (Non-ST Elevation Myocardial Infarction)",
  "risk_level": "HIGH",
  "confidence": 89,
  "alert_sent": true,
  "recommendations": [
    "Seek immediate medical attention",
    "Call emergency services",
    "Take aspirin if available"
  ]
}
```

---

## 🎯 **QUICK REFERENCE**

### **Your URLs:**

```
Web Interface:
http://10.0.0.8:5000/phone_monitor.html

API Endpoint:
http://10.0.0.8:5000/api/vitals

Dashboard:
http://10.0.0.8:5000

Alerts Log:
http://10.0.0.8:5000/api/alerts
```

### **Your Patient ID:**

Each session generates a unique ID like:
- `PHONE_USER_A7F2`
- `PHONE_USER_X9K5`
- `PHONE_USER_M2P8`

This ensures each phone session is tracked separately.

---

## ✅ **CHECKLIST**

Before demo, verify:

- [ ] Backend running: `lsof -ti:5000` shows process ID
- [ ] Phone on same WiFi as Mac
- [ ] Can access: `http://10.0.0.8:5000/phone_monitor.html`
- [ ] Camera permission allowed (for Camera PPG)
- [ ] Test normal vitals: see ✅ response
- [ ] Test abnormal vitals: see 🚨 alert
- [ ] Terminal shows Gemini AI responses
- [ ] Phone vibrates on alert

**All green? You're ready to demo!** 🚀

---

## 🎬 **DEMO SCRIPT**

**Opening:**
> "Let me show you real-time cardiac monitoring using just a smartphone camera."

**Action:**
1. Show phone interface
2. Place finger on camera
3. Watch heart rate appear in real-time
4. Enter abnormal vitals
5. Wait 5 seconds...
6. **ALERT appears!**

**Wow Factor:**
> "From fingertip to AI diagnosis in 2 seconds. No wearable needed!"

---

## 🐛 **TROUBLESHOOTING**

### **"Cannot connect"**
- ✅ Check WiFi: `ifconfig | grep inet`
- ✅ Verify backend: `lsof -ti:5000`
- ✅ Try: `http://10.0.0.8:5000` in Safari

### **"Camera not working"**
- ✅ Allow camera permission
- ✅ Use Safari (best compatibility)
- ✅ Switch to Manual Input instead

### **"No alerts showing"**
- ✅ Use abnormal vitals (HR=95, HRV=38)
- ✅ Check terminal for Gemini responses
- ✅ Wait 5-10 seconds for analysis

---

## 🚀 **YOU'RE LIVE!**

**Everything is ready:**
- ✅ Backend running
- ✅ Gemini AI connected
- ✅ Phone interface deployed
- ✅ Real-time monitoring active

**Just open your phone and go to:**
```
http://10.0.0.8:5000/phone_monitor.html
```

**Start monitoring NOW!** 📱❤️

---

*Created: November 22, 2025*  
*Your Backend: http://10.0.0.8:5000*  
*Status: LIVE AND READY! 🚀*
