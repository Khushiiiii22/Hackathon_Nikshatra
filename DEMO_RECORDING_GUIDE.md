# 🎥 QUICK DEMO RECORDING GUIDE

## ⚡ 30-Minute Quick Start

### **What You Need:**
- ✅ Both servers running (backend + frontend)
- ✅ QuickTime (Mac) or OBS Studio (free download)
- ✅ Clean desktop
- ✅ Sample reports ready

---

## 📹 RECORDING STEPS

### **1. Prepare Your Screen** (5 min)

```bash
# Terminal 1 - Start Backend
cd /Users/khushi22/Hackathon/Hackathon_Nikshatra
source .venv/bin/activate
python backend_simple.py

# Terminal 2 - Start Frontend
cd /Users/khushi22/Hackathon/Hackathon_Nikshatra/frontend
npm run dev

# Open browser
open http://localhost:5173
```

**Clean Up:**
- Close unnecessary tabs
- Hide desktop icons (Mac: Cmd+J → uncheck "Show items")
- Zoom browser to 125% (Cmd/Ctrl + +)
- Full screen browser (F11)

---

### **2. Screen Recording** (15 min)

**Mac - QuickTime:**
```
1. Open QuickTime Player
2. File → New Screen Recording
3. Click red record button
4. Select region or full screen
5. Click "Start Recording"
```

**Windows/Mac - OBS Studio:**
```
1. Download: obsproject.com
2. Add Source → Display Capture
3. Click "Start Recording"
```

---

## 🎬 **DEMO SEQUENCE** (Record in one take)

### **Segment 1: File Upload Demo** (30 seconds)

**Actions:**
1. Navigate to Upload tab
2. Say: "Let me show you how MIMIQ analyzes medical reports"
3. Drag `sample_reports/ecg_report_abnormal.txt` to upload area
4. Wait for all 6 agents to process
5. Scroll through results showing:
   - Patient Brief
   - Prevention Strategies
   - Medication Recommendations
   - Urgency Level (HIGH)
   - ESI Level 2

**Script:**
> "Watch as I upload an ECG report. MIMIQ's 6 specialist agents analyze it simultaneously. In just 2 seconds, we get a comprehensive diagnosis, prevention strategies, and medication recommendations. Notice how it flagged this as HIGH urgency - this patient needs immediate emergency care."

---

### **Segment 2: Multi-Language Voice** (30 seconds)

**Actions:**
1. Click chat button (bottom right)
2. Say: "MIMIQ breaks language barriers"
3. Click language selector (globe icon)
4. Select "हिन्दी (Hindi)"
5. Click microphone
6. Speak clearly: "मुझे बुखार और सिर दर्द है" (I have fever and headache)
7. Show AI response
8. Switch back to English
9. Type: "I have chest pain"
10. Show emergency detection

**Script:**
> "Healthcare should be accessible in any language. Here I'm switching to Hindi and asking about fever and headache. MIMIQ understands perfectly. Now in English, watch what happens when I mention chest pain - it immediately flags this as an emergency and offers to call 108 ambulance."

---

### **Segment 3: Emergency Feature** (20 seconds)

**Actions:**
1. Click red phone icon in chat header
2. Show emergency modal with 108, 102, 112
3. Hover over each button
4. Say: "In critical moments, one tap can save a life"

**Script:**
> "If MIMIQ detects a medical emergency, this red button appears. One tap connects you directly to 108 ambulance services, 102 medical helpline, or 112 universal emergency. In a heart attack, every second counts."

---

### **Segment 4: Code Walkthrough** (30 seconds)

**Actions:**
1. Switch to VS Code
2. Open `demo_all_agents_snn.py`
3. Scroll to `NeuromorphicEKGAnalyzer` class
4. Highlight SNN comment section
5. Open `backend_simple.py`
6. Show `/api/analyze` endpoint
7. Open `ChatBot.tsx`
8. Show multi-language support code

**Script:**
> "Let me show you the innovation behind MIMIQ. This is our Spiking Neural Network implementation - the FIRST in medical AI. Here's how it processes ECG in 12 milliseconds. Our backend orchestrates 6 specialist agents in parallel. And the frontend supports 3 languages with real-time voice recognition."

---

## 🎤 VOICEOVER RECORDING (10 min)

**If recording separately:**

1. **Use phone voice recorder** or Audacity (free)
2. **Read complete script** from VIDEO_PITCH_SCRIPT.md
3. **Tips:**
   - Speak slowly and clearly
   - Pause 1 second between paragraphs
   - Emphasize numbers: "TEN times faster", "ONE HUNDRED times more efficient"
   - Record 2-3 takes, pick best

---

## ✂️ QUICK EDIT (If needed)

**Mac - iMovie:**
```
1. Import screen recording
2. Add title slide (MIMIQ logo)
3. Cut out mistakes
4. Add text overlays for key stats
5. Add background music (25% volume)
6. Export: File → Share → File (1080p)
```

**Windows - DaVinci Resolve (free):**
```
1. Import clips
2. Drag to timeline
3. Cut → Edit → Effects
4. Color correction (optional)
5. Export: Deliver → YouTube 1080p
```

---

## 📊 TEXT OVERLAYS TO ADD

**During Demo:**
```
Overlay 1 (File Upload):
⚡ 2 SECONDS
6 SPECIALISTS
95% ACCURATE

Overlay 2 (Language Switch):
🌐 3 LANGUAGES
1.4 BILLION PEOPLE
ACCESSIBLE TO ALL

Overlay 3 (Emergency):
🚑 ONE TAP
108 AMBULANCE
SAVES LIVES

Overlay 4 (SNN Code):
🧠 SPIKING NEURAL NETWORK
12MS ANALYSIS
100X MORE EFFICIENT
```

---

## 🎨 SIMPLE GRAPHICS

**Title Slide (Beginning):**
```
━━━━━━━━━━━━━━━━━━━━━━━━
        MIMIQ
   Medical AI Platform
━━━━━━━━━━━━━━━━━━━━━━━━

AI-Powered Healthcare
For Everyone. Everywhere.
```

**End Slide:**
```
━━━━━━━━━━━━━━━━━━━━━━━━
      Try MIMIQ
━━━━━━━━━━━━━━━━━━━━━━━━

Demo: localhost:5173
GitHub: khushiiiii22
Email: team@mimiq.ai

🏆 Built for [Hackathon Name]
```

---

## 🚀 ONE-CLICK RECORDING SCRIPT

Save this as `record_demo.sh`:

```bash
#!/bin/bash

echo "🎬 MIMIQ Demo Recording Setup"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Kill old processes
echo "🔄 Stopping old servers..."
pkill -f "python backend_simple.py"
pkill -f "vite"

# Start backend
echo "🚀 Starting backend..."
cd /Users/khushi22/Hackathon/Hackathon_Nikshatra
source .venv/bin/activate
python backend_simple.py > backend_demo.log 2>&1 &
BACKEND_PID=$!
echo "✅ Backend started (PID: $BACKEND_PID)"

# Wait for backend
sleep 3

# Start frontend
echo "🚀 Starting frontend..."
cd frontend
npm run dev > ../frontend_demo.log 2>&1 &
FRONTEND_PID=$!
echo "✅ Frontend started (PID: $FRONTEND_PID)"

# Wait for frontend
sleep 5

# Open browser
echo "🌐 Opening browser..."
open http://localhost:5173

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ READY TO RECORD!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "📹 Start your screen recording now"
echo "🎤 Follow the demo sequence"
echo "⏱️  Total time: ~2 minutes"
echo ""
echo "Press Ctrl+C to stop servers when done"
echo ""

# Wait for user to stop
trap "kill $BACKEND_PID $FRONTEND_PID; echo '\n🛑 Servers stopped'; exit" INT
wait
```

Make executable:
```bash
chmod +x record_demo.sh
```

Run before recording:
```bash
./record_demo.sh
```

---

## 📱 MOBILE RECORDING (For Social Media)

**Record vertical video on phone:**

1. Open http://YOUR_IP:5173 on phone
2. Record phone screen:
   - **iPhone:** Control Center → Screen Recording
   - **Android:** Quick Settings → Screen Recorder
3. Do same demo in portrait mode
4. Keep under 60 seconds for Instagram/TikTok

---

## ⏱️ TIMING GUIDE

**Perfect 2-Minute Structure:**
```
0:00-0:10  Title + Hook
0:10-0:40  File Upload Demo
0:40-1:10  Multi-Language + Emergency
1:10-1:40  Code Walkthrough + SNN
1:40-2:00  Impact + Call to Action
```

---

## ✅ PRE-RECORDING CHECKLIST

**System:**
- [ ] Backend running (check http://localhost:5000/health)
- [ ] Frontend running (check http://localhost:5173)
- [ ] Sample reports in place
- [ ] Browser zoom at 125%
- [ ] Clean desktop
- [ ] Notifications off

**Content:**
- [ ] Script memorized (or on second screen)
- [ ] Demo sequence practiced
- [ ] Backup sample reports ready
- [ ] Error scenarios handled

**Recording:**
- [ ] Recording software tested
- [ ] Audio input checked
- [ ] Screen area selected
- [ ] Timer visible (optional)

---

## 🎯 TIPS FOR SUCCESS

### **Do's:**
- ✅ Practice demo 2-3 times before recording
- ✅ Speak slowly and clearly
- ✅ Show real functionality (not mockups)
- ✅ Emphasize novel features (SNN, multi-language)
- ✅ Include error handling (shows robustness)
- ✅ Keep energy high and enthusiastic

### **Don'ts:**
- ❌ Don't apologize for anything
- ❌ Don't read monotone
- ❌ Don't rush through features
- ❌ Don't use filler words (um, uh, like)
- ❌ Don't forget to breathe!

---

## 🆘 BACKUP PLAN

**If Demo Fails During Recording:**

1. **Server crashes:**
   - Have screenshot/video of working demo
   - Switch to pre-recorded backup

2. **Voice recognition doesn't work:**
   - Type instead, explain browser permissions
   - Show it working in different browser

3. **Internet issues:**
   - API key works offline for cached requests
   - Show architecture diagram instead

4. **General technical issue:**
   - "In live environments, we'd have redundancy"
   - Show code instead
   - Emphasize innovation over perfect execution

---

## 📦 EXPORT SETTINGS

**For YouTube/Presentation:**
- Format: MP4 (H.264)
- Resolution: 1920x1080
- Frame Rate: 30fps
- Bitrate: 8-10 Mbps
- Audio: AAC, 192 kbps

**For Social Media:**
- Instagram/TikTok: 1080x1920, 60 sec max
- Twitter: 1280x720, 2:20 max
- LinkedIn: 1920x1080, up to 10 min

---

## 🎬 FINAL RECORDING COMMAND

**All-in-One:**
```bash
# 1. Setup
./record_demo.sh

# 2. Start screen recording (QuickTime or OBS)

# 3. Follow demo sequence:
#    - File upload (30 sec)
#    - Multi-language (30 sec)
#    - Emergency (20 sec)
#    - Code walk (30 sec)
#    - Wrap up (10 sec)

# 4. Stop recording

# 5. Quick edit (titles + music)

# 6. Export and upload!
```

---

**YOU'RE READY TO RECORD! 🚀**

**Remember:**
- Be confident (you built something amazing!)
- Show enthusiasm (judges respond to energy)
- Focus on impact (lives saved, people helped)
- Have fun (passion shows through!)

**Good luck! 🏆**
