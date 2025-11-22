# 🎯 PATIENT-FRIENDLY UI - QUICK REFERENCE CARD

**For:** MIMIQ Medical AI Platform  
**Focus:** Make it easy for people in pain/distress to use  
**Date:** November 22, 2025

---

## 🚨 CRITICAL PATIENT-FRIENDLY PRINCIPLES

### **1. ONE TAP AWAY FROM HELP**
```
❌ BAD: Multiple steps to call 911
✅ GOOD: Giant red "CALL 911" button always visible
```

### **2. SPEAK, DON'T TYPE**
```
❌ BAD: Force typing when hands trembling
✅ GOOD: Large voice button + fallback to text
```

### **3. SIMPLE WORDS, NOT MEDICAL JARGON**
```
❌ BAD: "Acute coronary syndrome requires immediate intervention"
✅ GOOD: "Your heart needs help now. Call 911 immediately."
```

### **4. EMPATHY IN EVERY MESSAGE**
```
❌ BAD: "Symptom data logged. Proceeding."
✅ GOOD: "I understand you're in pain. I'm analyzing this right now to help you."
```

### **5. VISUAL FEEDBACK FOR EVERYTHING**
```
❌ BAD: Silent processing
✅ GOOD: 
  - Waveforms when listening
  - Pulsing icons when analyzing
  - Clear progress bars
```

---

## 🎤 VOICE FEATURES CHECKLIST

### **Must-Have Voice Capabilities:**

✅ **Large Voice Button**
- Minimum 80x80 pixels (120x120px recommended)
- Clear "Tap to Speak" label
- Green color (universally understood)
- Pulsing animation when active

✅ **Visual Feedback**
- Waveform animation while listening
- "I'm listening..." message
- Real-time transcription preview

✅ **Error Handling**
```typescript
// If microphone fails:
"Can't access microphone. No worries - you can type instead."

// If no speech detected:
"I didn't hear anything. Try speaking a bit louder, or type if easier."

// If network fails:
"Connection issue. Your message is saved and will send when back online."
```

✅ **Graceful Degradation**
```
Voice fails → Automatic fallback to large text input
Network fails → Save data locally, sync when online
Browser unsupported → Show typing interface immediately
```

---

## 💬 CHATBOT PERSONALITY GUIDE

### **Tone: Empathetic Medical Assistant**

```typescript
// Example chatbot responses:

User: "My chest hurts really bad"
MIMIQ: "I understand - chest pain can be scary. I'm here to help. 
        Can you tell me when it started? Just your best guess is fine."

User: "Like 30 minutes ago"
MIMIQ: "Thank you for telling me. Is the pain constant, or does it come and go?"

User: "Constant and getting worse"
MIMIQ: "This sounds urgent. I'm going to analyze this right now. 
        While I do that, if the pain gets severe, please call 911 immediately. 
        There's a red button on this screen if you need it. Okay?"

User: "Okay"
MIMIQ: "Starting analysis now. This will take about 30 seconds. 
        You're doing great - just breathe slowly."
```

### **Key Phrases to Use:**

✅ **Reassuring:**
- "I'm here to help"
- "You're doing great"
- "This will only take a moment"
- "I understand"

✅ **Clear Instructions:**
- "Call 911 now - don't wait"
- "Tap the red button if you need emergency help"
- "Just tell me in your own words"
- "Take your time"

✅ **Empathetic Acknowledgment:**
- "I know this is scary"
- "That must be very uncomfortable"
- "I understand you're in pain"
- "You made the right choice to get help"

---

## 🎨 UI DESIGN RULES

### **Button Sizes (Minimum):**
```css
.btn-primary {
  min-width: 120px;
  min-height: 60px;
  font-size: 18px;
}

.btn-voice {
  min-width: 120px;
  min-height: 120px;
  font-size: 20px;
}

.btn-emergency {
  width: 80px;
  height: 80px;
  position: fixed;
  bottom: 20px;
  right: 20px;
  z-index: 9999;
}
```

### **Color Coding:**
```
🔴 RED = Emergency / Critical
  - Call 911 button
  - Critical alerts
  - ESI Level 1-2

🟠 ORANGE = High Priority
  - Urgent care needed
  - ESI Level 2-3

🟡 YELLOW = Moderate
  - See doctor soon
  - ESI Level 3-4

🟢 GREEN = Safe / Low Priority
  - Voice input button
  - Success messages
  - ESI Level 4-5
```

### **Text Sizes (Minimum):**
```css
.text-heading {
  font-size: 32px;  /* Main headings */
  font-weight: bold;
}

.text-body {
  font-size: 18px;   /* Body text */
  line-height: 1.6;
}

.text-button {
  font-size: 20px;   /* Button labels */
  font-weight: bold;
}

.text-urgent {
  font-size: 24px;   /* Urgent messages */
  font-weight: bold;
  color: #F56565;
}
```

---

## 🚦 URGENCY INDICATORS

### **ESI Level Display:**

```
ESI 1 (CRITICAL)
┌──────────────────────────────────┐
│    🔴                            │
│    1                             │
│    LIFE-THREATENING              │
│    CALL 911 NOW                  │
│    [GIANT CALL 911 BUTTON]       │
└──────────────────────────────────┘

ESI 2 (HIGH)
┌──────────────────────────────────┐
│    🟠                            │
│    2                             │
│    URGENT CARE NEEDED            │
│    Go to ER immediately          │
│    [FIND NEAREST HOSPITAL]       │
└──────────────────────────────────┘

ESI 3 (MODERATE)
┌──────────────────────────────────┐
│    🟡                            │
│    3                             │
│    SEE DOCTOR SOON               │
│    Within 24 hours               │
│    [SCHEDULE APPOINTMENT]        │
└──────────────────────────────────┘
```

---

## 📱 MOBILE-FIRST DESIGN

### **Touch Targets:**
```
Minimum: 44x44 pixels (Apple guideline)
Recommended: 60x60 pixels (easier for trembling hands)
Voice button: 120x120 pixels (can't miss it!)
```

### **Spacing:**
```css
/* Space between interactive elements */
.btn + .btn {
  margin-top: 20px;  /* Prevent accidental taps */
}

/* Padding around tap areas */
.interactive-area {
  padding: 20px;
}
```

### **Scrolling:**
```
❌ BAD: Long forms requiring scroll
✅ GOOD: One question at a time, minimal scrolling
```

---

## 🎭 SCREEN-BY-SCREEN PATIENT EXPERIENCE

### **1. Landing Screen**
**Goal:** Make them feel safe, start assessment quickly

```
[LOGO: MIMIQ]

"Having chest pain or other symptoms?"

[GIANT BUTTON: Start Assessment Now]

"I'll ask a few simple questions to help you.
 You can speak or type - whatever's easier."

[Small text: About MIMIQ | Privacy]
```

### **2. Assessment Screen**
**Goal:** Collect symptoms without overwhelming them

```
[Voice Waveform Animation]

"I'm listening..."

[GIANT VOICE BUTTON]
Tap to Speak

OR

[Large Text Input]
Type your symptoms here

[Messages]
MIMIQ: "Can you tell me what you're feeling?"
You: "Chest pain and shortness of breath"
MIMIQ: "I understand. When did this start?"
```

### **3. Analysis Screen**
**Goal:** Show progress, keep them informed

```
"Analyzing Your Symptoms"

AI Specialists Reviewing Your Case:

[✓] Emergency Triage AI - Complete (98%)
[⏳] Heart Specialist AI - Analyzing...
[⏳] Lung Specialist AI - Waiting...
[⏳] Stomach Specialist AI - Waiting...
[⏳] Bone & Muscle AI - Waiting...
[⏳] Priority Assessment AI - Waiting...

"This takes about 30 seconds.
 You're doing great."

[EMERGENCY: Call 911 button always visible]
```

### **4. Results Screen**
**Goal:** Clear diagnosis, obvious next steps

```
⚠️ HIGH PRIORITY
ESI Level 2

"Your Heart May Need Urgent Care"

What This Means:
Your symptoms match patterns we see in serious
heart conditions. This needs immediate medical attention.

What To Do RIGHT NOW:
1. Call 911 - don't drive yourself
2. Chew an aspirin if you have one (and not allergic)
3. Stay calm and sit down
4. Have someone stay with you

[GIANT BUTTON: CALL 911 NOW]

[Download Report] [Share with Doctor]
```

---

## 🛠️ IMPLEMENTATION SHORTCUTS

### **Quick Wins (Do These First):**

1. **Large Voice Button** (30 min)
```typescript
<button className="w-32 h-32 rounded-full bg-green-500 text-white">
  🎤 Tap to Speak
</button>
```

2. **Emergency Button** (15 min)
```typescript
<button 
  className="fixed bottom-4 right-4 w-20 h-20 rounded-full bg-red-600"
  onClick={() => window.location.href = 'tel:911'}
>
  📞 911
</button>
```

3. **Simple Chatbot** (1 hour)
```typescript
const responses = {
  greeting: "Hi! I'm MIMIQ. I'm here to help. What symptoms are you experiencing?",
  acknowledge: "I understand. Let me ask a few more questions to help you.",
  urgent: "This sounds urgent. I'm analyzing this now. If pain gets worse, call 911 immediately."
};
```

4. **Patient-Friendly Language** (2 hours)
```python
def simplify_diagnosis(medical_term):
    translations = {
        'Acute Coronary Syndrome': 'Possible heart attack',
        'Pulmonary Embolism': 'Blood clot in lung',
        'GERD': 'Severe heartburn'
    }
    return translations.get(medical_term, medical_term)
```

---

## ✅ LAUNCH CHECKLIST

### **Before Showing to Patients:**

- [ ] **Voice input works on mobile**
- [ ] **Emergency button always visible**
- [ ] **All text is size 18px or larger**
- [ ] **Chatbot uses simple words (no jargon)**
- [ ] **Loading states have progress indicators**
- [ ] **Error messages are helpful, not technical**
- [ ] **Works in poor network conditions**
- [ ] **Tested with screen reader**
- [ ] **High contrast mode available**
- [ ] **Emergency info shows in <3 seconds**

---

## 🎯 SUCCESS METRICS

**Patient Can:**
1. Start assessment in 1 tap/click
2. Use voice without touching screen
3. Call 911 in 1 tap from any screen
4. Understand diagnosis without medical knowledge
5. Complete assessment while in pain/distress

**System Provides:**
1. Response to urgent symptoms in <5 seconds
2. Empathetic chatbot messages
3. Clear next steps (no ambiguity)
4. Visual progress for all operations
5. Graceful degradation when features fail

---

## 📞 SUPPORT MESSAGES

### **For Different Urgency Levels:**

**CRITICAL:**
```
"🚨 This is an emergency. Call 911 immediately.
Don't wait. Don't drive yourself.
Tap the red button below to call now."
```

**HIGH:**
```
"⚠️ This needs urgent medical care.
Go to the emergency room now.
Don't wait for an appointment."
```

**MODERATE:**
```
"📋 You should see a doctor soon.
Try to get an appointment within 24 hours.
Call your doctor or visit urgent care."
```

**LOW:**
```
"✅ Your symptoms don't seem urgent right now.
Schedule a regular appointment with your doctor.
Monitor how you feel."
```

---

**Remember:** If in doubt, err on the side of being MORE patient-friendly, MORE empathetic, and MORE clear about emergencies.

**NEVER:** Use medical jargon, assume technical knowledge, or make light of symptoms.

---

**END OF QUICK REFERENCE**

Use this as a checklist when implementing the UI!
