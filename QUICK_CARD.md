# 📱 QUICK REFERENCE CARD - PHONE MONITORING

## 🎯 **30-SECOND START**

**On your phone:** Open Safari/Chrome → Type:
```
http://10.0.0.8:5000/phone_monitor.html
```

**OR scan the QR code:** `phone_qr_code.png`

---

## 📊 **YOUR SYSTEM**

| Component | Status | URL |
|-----------|--------|-----|
| Backend API | ✅ RUNNING | http://10.0.0.8:5000 |
| Phone Interface | ✅ READY | http://10.0.0.8:5000/phone_monitor.html |
| Gemini AI | ✅ ENABLED | Integrated |
| Health Twin | ✅ ACTIVE | Baseline checking |
| Alerts | ✅ OPERATIONAL | SMS/Email/Push |

---

## 🎬 **DEMO SCENARIOS**

### **Normal Patient** ✅
```
HR: 72  |  HRV: 65  |  SpO2: 98
→ "Normal vitals"
```

### **Pre-NSTEMI** ⚠️
```
HR: 95  |  HRV: 38  |  SpO2: 94
→ "Pre-NSTEMI detected (89% confidence)"
```

### **Critical Event** 🆘
```
HR: 115  |  HRV: 25  |  SpO2: 91
→ "NSTEMI - CRITICAL"
```

---

## 🔧 **TROUBLESHOOTING**

| Problem | Solution |
|---------|----------|
| Can't connect | Check WiFi, verify: `lsof -ti:5000` |
| Camera not working | Use Manual Input mode |
| No alerts | Use exact values: HR=95, HRV=38 |

---

## 📁 **FILES**

- **Phone Interface:** `phone_monitor.html`
- **QR Code:** `phone_qr_code.png` 
- **Full Guide:** `README_PHONE.md`
- **Visual Guide:** `VISUAL_GUIDE.md`

---

## ⚡ **FEATURES**

✅ Camera PPG (no wearable!)  
✅ Real-time monitoring  
✅ AI diagnosis (Gemini)  
✅ Instant alerts  
✅ Works on any phone  

---

**READY? Open phone → Scan QR → Start monitoring!** 🚀
