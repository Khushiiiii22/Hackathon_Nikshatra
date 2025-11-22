# 🎯 QUICK TESTING GUIDE - MIMIQ MEDICAL AI

## ⚡ 30-SECOND FEATURE TEST

### 1. Test Chatbot (10 seconds)
```
1. Open http://localhost:5173
2. Click "Chat with AI" button (top-right)
3. Type: "I have chest pain and shortness of breath"
4. Press Enter
5. ✅ Verify AI responds with empathetic message
```

### 2. Test Voice Assistant (10 seconds)
```
1. In chat window, click microphone icon 🎤
2. Allow browser microphone permission
3. Speak clearly: "I feel very dizzy"
4. ✅ Verify text appears in input field
5. Click send
6. ✅ Verify AI responds
```

### 3. Test 6 AI Agents (10 seconds)
```
1. Click "Dashboard" in navigation
2. Scroll to "AI Specialist Agents" section
3. ✅ Verify 6 cards showing:
   - 🚨 Safety Agent (Active)
   - ❤️ Cardiology (Active)
   - 🫁 Pulmonary (Active)
   - 🔬 Gastro (Active)
   - 🦴 MSK (Active)
   - 🎯 Triage (Ready)
4. ✅ Green pulse indicators visible
```

---

## 🧪 BROWSER CONSOLE TESTS

### Test Backend Connection:
```javascript
// Open browser console (F12)
fetch('http://localhost:5000/health')
  .then(r => r.json())
  .then(d => console.log('✅ Backend:', d));
// Expected: {"status":"healthy","timestamp":"..."}
```

### Test Chat API:
```javascript
fetch('http://localhost:5000/api/chat', {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({
    patient_id: 'test_123',
    message: 'I have severe chest pain'
  })
})
.then(r => r.json())
.then(d => console.log('✅ Chat Response:', d));
// Check for: response, extracted_symptoms, urgency_level
```

### Test Agent Analysis:
```javascript
fetch('http://localhost:5000/api/analyze', {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({
    patient_id: 'test_123',
    symptoms: 'chest pain, shortness of breath'
  })
})
.then(r => r.json())
.then(d => console.log('✅ Analysis Started:', d));
// Expected: analysis_id, estimated_time
```

### Access Test Screen:
```javascript
// Navigate to system diagnostics
useAppStore.getState().setCurrentScreen('test');
```

---

## 📋 VERIFICATION CHECKLIST

### Before Demo:
- [ ] Backend running: `lsof -i:5000` shows process
- [ ] Frontend running: `lsof -i:5173` shows process
- [ ] Browser open to http://localhost:5173
- [ ] Console shows no errors (F12)
- [ ] Microphone permission allowed

### During Demo:
- [ ] Homepage loads with dark theme
- [ ] Chat button clickable
- [ ] AI responds to messages
- [ ] Voice button works (if browser supports)
- [ ] Dashboard shows 6 agents
- [ ] Navigation between screens works
- [ ] Upload page accepts files

### If Something Breaks:
1. **Backend not responding:**
   ```bash
   cd /Users/khushi22/Hackathon/Hackathon_Nikshatra
   source .venv/bin/activate
   python backend_simple.py
   ```

2. **Frontend errors:**
   ```bash
   cd frontend
   npm run dev
   ```

3. **Port conflicts:**
   ```bash
   # Kill process on port 5000
   lsof -ti:5000 | xargs kill -9
   # Kill process on port 5173
   lsof -ti:5173 | xargs kill -9
   ```

---

## 🎤 DEMO SCRIPT (2 Minutes)

### Slide 1: Homepage (15s)
**Say:** "MIMIQ is a complete medical AI platform powered by Google Gemini and 6 specialist AI agents."
**Do:** Point to homepage stats (99.2% accuracy, <1s response, 24/7)

### Slide 2: Chatbot Demo (30s)
**Say:** "Let's test our empathetic AI chatbot."
**Do:** 
1. Click "Chat with AI"
2. Type: "I have severe chest pain and can't breathe properly"
3. Show AI's empathetic, patient-friendly response
4. Highlight urgency detection (will flag as high priority)

### Slide 3: Voice Assistant (20s)
**Say:** "We also have hands-free voice input for accessibility."
**Do:**
1. Click microphone button
2. Speak: "I feel very dizzy and nauseous"
3. Show transcription appear
4. Send message

### Slide 4: 6 AI Agents (20s)
**Say:** "Behind the scenes, 6 specialist AI agents work in parallel:"
**Do:** Navigate to Dashboard
**Point to:**
- Safety Monitor (emergency detection)
- Cardiology (heart specialist)
- Pulmonary (lung specialist)
- Gastroenterology (digestive system)
- Musculoskeletal (bones & muscles)
- Triage (priority assessment)

### Slide 5: Real-time Features (15s)
**Say:** "All agents analyze in under 1 second with real-time WebSocket updates."
**Do:** Show dashboard health metrics
**Highlight:**
- Heart rate: 86 BPM
- Heart score: 94%
- All agents: Active status

### Slide 6: Emergency Triage (20s)
**Say:** "Our ESI triage system automatically prioritizes cases from level 1 (immediate) to level 5 (non-urgent)."
**Do:** Show previous chat with chest pain
**Explain:** "Chest pain symptoms = ESI level 2 = urgent care needed within 10 minutes"

---

## 🏆 KEY SELLING POINTS

1. **🤖 Advanced AI**
   - Gemini 2.5 Flash (latest Google AI)
   - 6 independent specialist agents
   - Parallel processing

2. **🎤 Accessibility**
   - Voice recognition
   - Hands-free operation
   - Patient-friendly language

3. **⚡ Speed**
   - <1 second response time
   - Real-time WebSocket updates
   - Immediate emergency detection

4. **🎨 User Experience**
   - Beautiful medical UI
   - Glass-morphism design
   - Mobile responsive

5. **🏥 Medical Accuracy**
   - ESI triage system (hospital standard)
   - Symptom extraction engine
   - Emergency detection algorithm

6. **📊 Scalability**
   - Modular architecture
   - Easy to add more agents
   - Production-ready code

---

## 🔍 TROUBLESHOOTING

### Voice Not Working?
- Use Chrome or Edge browser
- Check microphone permission
- Look for red 'x' on browser tab

### Chat Not Responding?
- Check backend terminal for errors
- Verify Gemini API key is set
- Test with: `curl http://localhost:5000/health`

### UI Not Loading?
- Clear browser cache (Cmd+Shift+R)
- Check frontend terminal for errors
- Verify port 5173 is not blocked

### Agents Not Showing?
- Backend must be running
- Check terminal output for "6 specialists ready"
- Navigate to Dashboard page

---

## 📞 EMERGENCY COMMANDS

```bash
# Restart everything quickly
cd /Users/khushi22/Hackathon/Hackathon_Nikshatra

# Terminal 1: Backend
source .venv/bin/activate && python backend_simple.py

# Terminal 2: Frontend (in separate terminal)
cd frontend && npm run dev
```

**Verify both running:**
- Backend: http://localhost:5000/health
- Frontend: http://localhost:5173

---

**Last Updated:** Nov 22, 2025 at 9:40 AM
**Status:** ✅ Ready to Demo
**All Features:** Working
