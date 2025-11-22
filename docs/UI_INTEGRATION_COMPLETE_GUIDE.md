# 🎨 COMPLETE UI INTEGRATION GUIDE
## MIMIQ - Patient-Friendly Medical AI Platform

**Created:** November 22, 2025  
**Purpose:** Integrate React/TypeScript frontend with Python Flask backend  
**Focus:** Patient-friendly, voice-enabled, pain-tolerant interface

---

## 📋 TABLE OF CONTENTS

1. [Architecture Overview](#architecture-overview)
2. [Folder Structure](#folder-structure)
3. [API Endpoints Mapping](#api-endpoints-mapping)
4. [Data Flow](#data-flow)
5. [Patient-Friendly Features](#patient-friendly-features)
6. [Real-Time Updates](#real-time-updates)
7. [Implementation Steps](#implementation-steps)
8. [Testing Strategy](#testing-strategy)

---

## 🏗️ ARCHITECTURE OVERVIEW

```
┌─────────────────────────────────────────────────────────────────┐
│                    PATIENT INTERFACE                            │
│  (Phone, Tablet, Desktop - Accessible anywhere)                 │
└────────────────┬────────────────────────────────────────────────┘
                 │
                 │ REST API + WebSocket
                 ▼
┌─────────────────────────────────────────────────────────────────┐
│               REACT FRONTEND (Port 5173)                        │
│  • Voice Input (Speech-to-Text)                                 │
│  • Chatbot Interface                                            │
│  • Real-time Agent Visualization                                │
│  • Pain-Tolerant UI (Large buttons, simple language)            │
└────────────────┬────────────────────────────────────────────────┘
                 │
                 │ HTTP/WebSocket
                 ▼
┌─────────────────────────────────────────────────────────────────┐
│               FLASK API (Port 5000)                             │
│  • /api/chat - Chatbot endpoint                                 │
│  • /api/analyze - Real-time analysis                            │
│  • /api/agents/status - Agent updates                           │
│  • /ws/realtime - WebSocket for live updates                    │
└────────────────┬────────────────────────────────────────────────┘
                 │
                 │
      ┌──────────┴──────────┬──────────────┬───────────────┐
      ▼                     ▼              ▼               ▼
┌──────────┐      ┌──────────────┐  ┌──────────┐   ┌──────────┐
│ Gemini   │      │ AI Agents    │  │ Health   │   │ Prevention│
│ LLM      │      │ (6 specialist)│  │ Twin     │   │ Alerts   │
│ Service  │      │              │  │          │   │          │
└──────────┘      └──────────────┘  └──────────┘   └──────────┘
```

---

## 📁 FOLDER STRUCTURE

### **Recommended Layout:**

```
/Users/khushi22/Hackathon/Hackathon_Nikshatra/
│
├── frontend/                          # NEW - React TypeScript UI
│   ├── src/
│   │   ├── components/
│   │   │   ├── screens/
│   │   │   │   ├── LandingScreen.tsx       # Hero page
│   │   │   │   ├── AssessmentScreen.tsx    # Voice + Chat interface
│   │   │   │   ├── AnalysisScreen.tsx      # Real-time agent processing
│   │   │   │   ├── ResultsScreen.tsx       # Diagnosis results
│   │   │   │   ├── DashboardScreen.tsx     # Patient history
│   │   │   │   ├── HospitalPortalScreen.tsx # Hospital bulk upload
│   │   │   │   └── ...
│   │   │   ├── ui/
│   │   │   │   ├── Button.tsx
│   │   │   │   ├── Card.tsx
│   │   │   │   ├── Input.tsx
│   │   │   │   └── ...
│   │   │   ├── AgentCard.tsx          # Individual agent status
│   │   │   ├── VoicePanel.tsx         # Voice input component
│   │   │   ├── ChatBot.tsx            # Chatbot interface
│   │   │   └── TopBar.tsx
│   │   ├── stores/
│   │   │   └── appStore.ts            # Zustand state management
│   │   ├── services/
│   │   │   ├── api.ts                 # REST API client
│   │   │   ├── websocket.ts           # WebSocket client
│   │   │   └── voice.ts               # Voice recognition
│   │   ├── types/
│   │   │   └── index.ts               # TypeScript interfaces
│   │   ├── utils/
│   │   │   ├── patientFriendly.ts     # Simplify medical terms
│   │   │   └── accessibility.ts       # A11y helpers
│   │   ├── App.tsx
│   │   └── main.tsx
│   ├── public/
│   ├── package.json
│   ├── tsconfig.json
│   ├── vite.config.ts
│   └── tailwind.config.js
│
├── src/                               # EXISTING - Python backend
│   ├── agents/
│   │   ├── cardiology.py
│   │   ├── gastro.py
│   │   ├── pulmonary.py
│   │   ├── musculoskeletal.py
│   │   ├── safety.py
│   │   └── triage.py
│   ├── llm_service.py                 # Gemini AI
│   └── ...
│
├── app_integrated.py                  # EXISTING - Flask API
├── app_with_ui_support.py             # NEW - Enhanced Flask with UI endpoints
├── requirements.txt
└── ...
```

---

## 🔌 API ENDPOINTS MAPPING

### **Patient Flow → API Endpoints**

#### **1. ASSESSMENT FLOW (Patient Input)**

```typescript
// UI Screen: AssessmentScreen.tsx
// Patient speaks or types symptoms

┌─────────────────────────────────────────────────────────────────┐
│ PATIENT ACTION: "I have chest pain and shortness of breath"    │
└───────────────────────────┬─────────────────────────────────────┘
                            │
                            ▼
                    Voice Recognition
                    (Browser Web Speech API)
                            │
                            ▼
┌───────────────────────────────────────────────────────────────────┐
│ POST /api/chat                                                    │
│ {                                                                 │
│   "message": "I have chest pain and shortness of breath",        │
│   "patient_id": "PT-ABC123",                                      │
│   "timestamp": "2025-11-22T10:30:00Z"                            │
│ }                                                                 │
└───────────────────────────┬───────────────────────────────────────┘
                            │
                            ▼
                    Gemini AI Chatbot
                    (src/llm_service.py)
                            │
                            ▼
┌───────────────────────────────────────────────────────────────────┐
│ RESPONSE:                                                         │
│ {                                                                 │
│   "response": "I understand. Can you tell me when this started?",│
│   "extracted_symptoms": ["chest pain", "shortness of breath"],   │
│   "urgency_level": "HIGH",                                        │
│   "next_question": "When did the pain start?"                    │
│ }                                                                 │
└───────────────────────────────────────────────────────────────────┘
```

**Backend Implementation:**
```python
# app_with_ui_support.py

@app.route('/api/chat', methods=['POST'])
def chat_endpoint():
    """
    Patient-friendly chatbot endpoint
    - Accepts voice or text input
    - Returns simple, empathetic responses
    - Extracts symptoms for analysis
    """
    data = request.json
    message = data.get('message')
    patient_id = data.get('patient_id')
    
    # Use Gemini AI for empathetic conversation
    from src.llm_service import chat_medical
    
    response = chat_medical(
        message=message,
        context={
            'patient_id': patient_id,
            'tone': 'empathetic',  # Patient-friendly
            'language': 'simple'    # Avoid medical jargon
        }
    )
    
    # Extract symptoms for later analysis
    symptoms = extract_symptoms(message)
    
    # Store conversation history
    store_conversation(patient_id, message, response)
    
    return jsonify({
        'response': response,
        'extracted_symptoms': symptoms,
        'urgency_level': assess_urgency(symptoms),
        'next_question': generate_followup_question(symptoms)
    })
```

---

#### **2. ANALYSIS FLOW (AI Agent Processing)**

```typescript
// UI Screen: AnalysisScreen.tsx
// Shows 6 agents processing in real-time

┌─────────────────────────────────────────────────────────────────┐
│ TRIGGER: Patient completes symptom input                       │
└───────────────────────────┬─────────────────────────────────────┘
                            │
                            ▼
┌───────────────────────────────────────────────────────────────────┐
│ POST /api/analyze                                                 │
│ {                                                                 │
│   "patient_id": "PT-ABC123",                                      │
│   "symptoms": ["chest pain", "shortness of breath"],             │
│   "vitals": {                                                     │
│     "heart_rate": 88,                                             │
│     "blood_pressure": "145/92",                                   │
│     "spo2": 96                                                    │
│   }                                                               │
│ }                                                                 │
└───────────────────────────┬───────────────────────────────────────┘
                            │
                            ▼
                  Launch All 6 Agents in Parallel
                            │
        ┌───────────────────┴───────────────────┐
        ▼                   ▼                   ▼
    Safety AI          Cardiology AI      Pulmonary AI
        │                   │                   │
        └───────────────────┴───────────────────┘
                            │
                            ▼
┌───────────────────────────────────────────────────────────────────┐
│ WebSocket Updates (Real-time)                                    │
│ ws://localhost:5000/ws/realtime                                   │
│                                                                   │
│ Message 1: { "agent": "safety", "status": "processing" }         │
│ Message 2: { "agent": "safety", "status": "complete",            │
│              "confidence": 98 }                                   │
│ Message 3: { "agent": "cardiology", "status": "processing" }     │
│ ...                                                               │
└───────────────────────────────────────────────────────────────────┘
```

**Backend Implementation:**
```python
# app_with_ui_support.py

from flask_socketio import SocketIO, emit
from threading import Thread

socketio = SocketIO(app, cors_allowed_origins="*")

@app.route('/api/analyze', methods=['POST'])
def analyze_patient():
    """
    Trigger AI agent analysis
    - Launches all 6 agents in parallel
    - Sends real-time updates via WebSocket
    - Patient-friendly progress indicators
    """
    data = request.json
    patient_id = data.get('patient_id')
    symptoms = data.get('symptoms')
    vitals = data.get('vitals')
    
    # Start analysis in background thread
    thread = Thread(target=run_analysis, args=(patient_id, symptoms, vitals))
    thread.start()
    
    return jsonify({
        'status': 'started',
        'analysis_id': generate_analysis_id(),
        'estimated_time': '30-60 seconds'
    })

def run_analysis(patient_id, symptoms, vitals):
    """
    Run all agents and send real-time updates
    """
    from src.agents.base import MasterOrchestrator
    from src.agents.cardiology import CardiologyAgent
    from src.agents.safety import SafetyMonitorAgent
    # ... import all agents
    
    orchestrator = MasterOrchestrator()
    
    # Register agents
    agents = [
        SafetyMonitorAgent(),
        CardiologyAgent(),
        PulmonaryAgent(),
        GastroenterologyAgent(),
        MusculoskeletalAgent(),
        TriageAgent()
    ]
    
    for agent in agents:
        orchestrator.register_agent(agent.specialty, agent)
        
        # Send "processing" status
        socketio.emit('agent_update', {
            'agent_id': agent.specialty.value.lower(),
            'status': 'processing',
            'timestamp': datetime.now().isoformat()
        })
    
    # Create patient data
    patient_data = create_patient_data(symptoms, vitals)
    
    # Run analysis
    results = await orchestrator.analyze_patient(patient_data)
    
    # Send completion updates
    for result in results:
        socketio.emit('agent_update', {
            'agent_id': result.agent_name.lower(),
            'status': 'complete',
            'confidence': int(result.confidence * 100),
            'diagnosis': simplify_medical_term(result.diagnosis),
            'analysis': result.reasoning,
            'timestamp': datetime.now().isoformat()
        })
    
    # Send final results
    socketio.emit('analysis_complete', {
        'patient_id': patient_id,
        'results': format_patient_friendly_results(results)
    })
```

---

#### **3. RESULTS FLOW (Patient-Friendly Diagnosis)**

```typescript
// UI Screen: ResultsScreen.tsx
// Shows diagnosis in simple, non-scary language

┌───────────────────────────────────────────────────────────────────┐
│ GET /api/results/{patient_id}                                     │
└───────────────────────────┬───────────────────────────────────────┘
                            │
                            ▼
┌───────────────────────────────────────────────────────────────────┐
│ RESPONSE (Patient-Friendly):                                      │
│ {                                                                 │
│   "primary_diagnosis": {                                          │
│     "condition": "Possible heart issue",                          │
│     "simple_explanation": "Your heart may need medical attention",│
│     "urgency": "HIGH",                                            │
│     "esi_level": 2,                                               │
│     "what_to_do": [                                               │
│       "Call 911 right now - don't wait",                          │
│       "Don't drive yourself",                                     │
│       "Chew an aspirin if you have one"                           │
│     ]                                                             │
│   },                                                              │
│   "agent_findings": [                                             │
│     {                                                             │
│       "agent": "Heart Specialist AI",                             │
│       "found": "Signs that need urgent care",                     │
│       "confidence": "94% sure",                                   │
│       "plain_english": "Your symptoms match serious heart issues" │
│     }                                                             │
│   ],                                                              │
│   "nearby_hospitals": [...]                                       │
│ }                                                                 │
└───────────────────────────────────────────────────────────────────┘
```

**Backend Implementation:**
```python
# app_with_ui_support.py

@app.route('/api/results/<patient_id>', methods=['GET'])
def get_patient_results(patient_id):
    """
    Return diagnosis in patient-friendly language
    - Avoid medical jargon
    - Use simple, clear instructions
    - Emphasize urgency with empathy
    """
    results = get_analysis_results(patient_id)
    
    # Simplify medical terminology
    patient_friendly = {
        'primary_diagnosis': {
            'condition': simplify_diagnosis(results.primary_diagnosis),
            'simple_explanation': explain_in_plain_english(results),
            'urgency': results.urgency_level,
            'esi_level': results.esi_level,
            'what_to_do': generate_simple_instructions(results)
        },
        'agent_findings': [
            {
                'agent': humanize_agent_name(finding.agent),
                'found': simplify_finding(finding.diagnosis),
                'confidence': f"{int(finding.confidence * 100)}% sure",
                'plain_english': translate_medical_jargon(finding.reasoning)
            }
            for finding in results.agent_results
        ],
        'nearby_hospitals': get_nearby_hospitals(),
        'support_message': get_empathetic_message(results.urgency_level)
    }
    
    return jsonify(patient_friendly)

def simplify_diagnosis(diagnosis):
    """
    Convert medical terminology to patient-friendly language
    """
    translations = {
        'Acute Coronary Syndrome': 'Possible heart attack',
        'NSTEMI': 'Heart issue needing urgent care',
        'Pulmonary Embolism': 'Blood clot in lung',
        'Pneumonia': 'Lung infection',
        'GERD': 'Acid reflux / heartburn',
        'Costochondritis': 'Chest wall inflammation (not heart-related)'
    }
    return translations.get(diagnosis, diagnosis)
```

---

## 🎤 PATIENT-FRIENDLY FEATURES

### **1. Voice Input (Speech-to-Text)**

**Frontend Implementation:**
```typescript
// frontend/src/services/voice.ts

export class VoiceService {
  private recognition: SpeechRecognition | null = null;
  
  constructor() {
    if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
      const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
      this.recognition = new SpeechRecognition();
      
      // Patient-friendly settings
      this.recognition.continuous = true;  // Don't stop listening
      this.recognition.interimResults = true;  // Show partial results
      this.recognition.lang = 'en-US';
      
      // Handle results
      this.recognition.onresult = (event) => {
        const transcript = Array.from(event.results)
          .map(result => result[0].transcript)
          .join('');
        
        this.onTranscript(transcript);
      };
      
      // Handle errors gracefully
      this.recognition.onerror = (event) => {
        console.error('Voice recognition error:', event.error);
        this.showPatientFriendlyError(event.error);
      };
    }
  }
  
  start() {
    if (this.recognition) {
      this.recognition.start();
      console.log('🎤 Listening...');
    }
  }
  
  stop() {
    if (this.recognition) {
      this.recognition.stop();
      console.log('🔇 Stopped listening');
    }
  }
  
  showPatientFriendlyError(error: string) {
    const errorMessages = {
      'no-speech': 'I didn\'t hear anything. Please try speaking again.',
      'audio-capture': 'Microphone not found. Please check your device.',
      'not-allowed': 'Please allow microphone access to use voice input.',
      'network': 'Internet connection issue. Please check your connection.'
    };
    
    const message = errorMessages[error] || 'Voice input not available. Please type instead.';
    alert(message);
  }
}
```

**Usage in AssessmentScreen.tsx:**
```typescript
// frontend/src/components/screens/AssessmentScreen.tsx

export function AssessmentScreen() {
  const [isListening, setIsListening] = useState(false);
  const voiceService = useRef(new VoiceService());
  
  const handleVoiceToggle = () => {
    if (isListening) {
      voiceService.current.stop();
      setIsListening(false);
    } else {
      voiceService.current.start();
      setIsListening(true);
    }
  };
  
  return (
    <div>
      {/* Large, easy-to-tap voice button */}
      <button
        onClick={handleVoiceToggle}
        className="w-32 h-32 rounded-full bg-gradient-to-br from-green-500 to-blue-500 
                   text-white text-xl font-bold shadow-2xl hover:scale-110 transition-all"
        aria-label={isListening ? "Stop recording" : "Start recording"}
      >
        {isListening ? (
          <>
            <MicOffIcon className="h-16 w-16" />
            <div className="text-sm mt-2">Tap to Stop</div>
          </>
        ) : (
          <>
            <MicIcon className="h-16 w-16" />
            <div className="text-sm mt-2">Tap to Speak</div>
          </>
        )}
      </button>
      
      {/* Visual feedback while listening */}
      {isListening && (
        <div className="mt-4 flex items-center gap-2">
          <div className="w-2 h-8 bg-green-500 rounded animate-wave" />
          <div className="w-2 h-12 bg-green-500 rounded animate-wave" style={{ animationDelay: '0.1s' }} />
          <div className="w-2 h-10 bg-green-500 rounded animate-wave" style={{ animationDelay: '0.2s' }} />
          <div className="w-2 h-14 bg-green-500 rounded animate-wave" style={{ animationDelay: '0.3s' }} />
          <div className="w-2 h-8 bg-green-500 rounded animate-wave" style={{ animationDelay: '0.4s' }} />
        </div>
      )}
    </div>
  );
}
```

---

### **2. Empathetic Chatbot**

**Gemini AI System Prompt (Patient-Friendly):**
```python
# src/llm_service.py - Enhanced for patients

PATIENT_FRIENDLY_PROMPT = """
You are MIMIQ, a caring medical AI assistant helping someone who may be in pain or distress.

IMPORTANT RULES:
1. Use SIMPLE language - no medical jargon
2. Be EMPATHETIC - acknowledge their feelings
3. Ask ONE question at a time - they may be struggling
4. Give CLEAR instructions - "Call 911 now" not "Seek emergency care"
5. REASSURE them - "I'm here to help" / "You're doing great"
6. If CRITICAL symptoms → Immediately tell them to call 911
7. Use SHORT sentences - easier to read when stressed

EXAMPLES:

❌ BAD: "Your symptoms suggest possible acute coronary syndrome. Immediate medical evaluation is recommended."
✅ GOOD: "Your chest pain sounds serious. Please call 911 right now. Don't wait."

❌ BAD: "Can you describe the onset, duration, and character of your pain?"
✅ GOOD: "When did the pain start? Just give me your best guess."

❌ BAD: "Noted. Proceeding with differential diagnosis."
✅ GOOD: "Thank you for telling me. I'm analyzing this now to help you."

Always end responses with:
- What you're doing next
- Reassurance
- Clear action if urgent
"""

def chat_medical(message: str, context: dict = None) -> str:
    """
    Patient-friendly medical chat
    """
    llm = get_llm_service()
    
    # Build empathetic prompt
    full_prompt = f"{PATIENT_FRIENDLY_PROMPT}\n\nPatient says: {message}\n\nYour response:"
    
    response = llm.analyze(full_prompt, temperature=0.7)
    
    # Ensure response is simple
    if len(response.text) > 200:
        # Too long - simplify
        response = llm.analyze(f"Simplify this for someone in pain: {response.text}", temperature=0.5)
    
    return response.text
```

---

### **3. Large, Accessible UI Elements**

**CSS/Tailwind for Pain-Tolerant Design:**
```css
/* frontend/src/index.css */

/* All interactive elements MUST be large enough for trembling hands */
.btn-primary {
  min-height: 60px;
  min-width: 120px;
  font-size: 20px;
  font-weight: bold;
  padding: 20px 40px;
  border-radius: 12px;
  
  /* High contrast for visibility */
  background: linear-gradient(135deg, #48BB78 0%, #38A169 100%);
  color: white;
  
  /* Obvious hover state */
  transition: all 0.3s ease;
}

.btn-primary:hover {
  transform: scale(1.1);
  box-shadow: 0 10px 40px rgba(72, 187, 120, 0.5);
}

/* Emergency button - ALWAYS visible */
.btn-emergency {
  position: fixed;
  bottom: 20px;
  right: 20px;
  width: 80px;
  height: 80px;
  background: linear-gradient(135deg, #F56565 0%, #C53030 100%);
  border-radius: 50%;
  z-index: 9999;
  animation: pulse 2s infinite;
}

/* Text must be LARGE and CLEAR */
.text-symptom {
  font-size: 18px;
  line-height: 1.8;
  color: #F7FAFC;
}

/* Input fields - easy to tap */
input[type="text"],
textarea {
  min-height: 60px;
  font-size: 18px;
  padding: 20px;
  border: 3px solid #667EEA;
  border-radius: 12px;
}

/* Voice waveform - visual feedback */
@keyframes wave {
  0%, 100% { transform: scaleY(1); }
  50% { transform: scaleY(1.5); }
}

.animate-wave {
  animation: wave 1.2s ease-in-out infinite;
}
```

---

## 🔄 REAL-TIME UPDATES (WebSocket)

### **WebSocket Flow:**

```
┌──────────────┐                    ┌──────────────┐
│   Frontend   │                    │   Backend    │
│ (React App)  │                    │ (Flask API)  │
└──────┬───────┘                    └──────┬───────┘
       │                                   │
       │ 1. Connect WebSocket              │
       │──────────────────────────────────>│
       │                                   │
       │ 2. Connection Established         │
       │<──────────────────────────────────│
       │                                   │
       │ 3. POST /api/analyze              │
       │──────────────────────────────────>│
       │                                   │
       │                                   │ 4. Start Agents
       │                                   │────┐
       │                                   │    │
       │ 5. Agent Update: Safety (processing)  │
       │<──────────────────────────────────│<───┘
       │                                   │
       │ 6. Agent Update: Safety (complete)    │
       │<──────────────────────────────────│
       │                                   │
       │ 7. Agent Update: Cardiology (processing)
       │<──────────────────────────────────│
       │                                   │
       │ ... (continue for all 6 agents)   │
       │                                   │
       │ 8. Analysis Complete              │
       │<──────────────────────────────────│
       │                                   │
```

### **Backend WebSocket Setup:**

```python
# app_with_ui_support.py

from flask import Flask
from flask_socketio import SocketIO, emit
from flask_cors import CORS

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "http://localhost:5173"}})
socketio = SocketIO(app, cors_allowed_origins="http://localhost:5173")

# WebSocket event handlers
@socketio.on('connect')
def handle_connect():
    print('✅ Frontend connected')
    emit('connection_status', {'status': 'connected'})

@socketio.on('disconnect')
def handle_disconnect():
    print('❌ Frontend disconnected')

@socketio.on('request_agent_update')
def handle_agent_request(data):
    patient_id = data.get('patient_id')
    # Send current agent status
    status = get_agent_status(patient_id)
    emit('agent_update', status)

# Run with WebSocket support
if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)
```

### **Frontend WebSocket Client:**

```typescript
// frontend/src/services/websocket.ts

import { io, Socket } from 'socket.io-client';

class WebSocketService {
  private socket: Socket | null = null;
  private callbacks: Map<string, Function> = new Map();
  
  connect() {
    this.socket = io('http://localhost:5000', {
      transports: ['websocket'],
      reconnection: true,
      reconnectionDelay: 1000,
      reconnectionAttempts: 5
    });
    
    this.socket.on('connect', () => {
      console.log('✅ Connected to backend');
    });
    
    this.socket.on('disconnect', () => {
      console.log('❌ Disconnected from backend');
    });
    
    this.socket.on('agent_update', (data) => {
      // Update agent status in UI
      const callback = this.callbacks.get('agent_update');
      if (callback) callback(data);
    });
    
    this.socket.on('analysis_complete', (data) => {
      const callback = this.callbacks.get('analysis_complete');
      if (callback) callback(data);
    });
  }
  
  on(event: string, callback: Function) {
    this.callbacks.set(event, callback);
  }
  
  emit(event: string, data: any) {
    if (this.socket) {
      this.socket.emit(event, data);
    }
  }
  
  disconnect() {
    if (this.socket) {
      this.socket.disconnect();
    }
  }
}

export const wsService = new WebSocketService();
```

**Usage in React Component:**
```typescript
// frontend/src/components/screens/AnalysisScreen.tsx

import { wsService } from '../../services/websocket';
import { useAppStore } from '../../stores/appStore';

export function AnalysisScreen() {
  const { updateAgentStatus, setAnalysisProgress } = useAppStore();
  
  useEffect(() => {
    // Connect to WebSocket
    wsService.connect();
    
    // Listen for agent updates
    wsService.on('agent_update', (data) => {
      updateAgentStatus(
        data.agent_id,
        data.status,
        data.confidence
      );
    });
    
    // Listen for completion
    wsService.on('analysis_complete', (data) => {
      setAnalysisProgress(100);
      setTimeout(() => {
        setCurrentScreen('results');
      }, 1000);
    });
    
    return () => {
      wsService.disconnect();
    };
  }, []);
  
  return (
    <div>
      {/* Agent status cards update in real-time */}
      {agents.map(agent => (
        <AgentCard key={agent.id} agent={agent} />
      ))}
    </div>
  );
}
```

---

## 📊 DATA TRANSFORMATION LAYER

### **Backend → Frontend Mapping:**

```python
# app_with_ui_support.py

def format_agent_result_for_ui(result: DiagnosisResult) -> dict:
    """
    Transform Python DiagnosisResult → TypeScript Agent format
    """
    # Map agent names
    agent_id_map = {
        'Cardiology Agent': 'cardiology',
        'Safety Monitor Agent': 'safety',
        'Pulmonary Agent': 'pulmonary',
        'Gastroenterology Agent': 'gastro',
        'Musculoskeletal Agent': 'musculoskeletal',
        'Triage Agent': 'triage'
    }
    
    # Map risk levels to urgency
    urgency_map = {
        RiskLevel.CRITICAL: 'CRITICAL',
        RiskLevel.HIGH: 'HIGH',
        RiskLevel.MODERATE: 'MODERATE',
        RiskLevel.LOW: 'LOW'
    }
    
    return {
        'id': agent_id_map.get(result.agent_name, 'unknown'),
        'name': humanize_agent_name(result.agent_name),
        'specialty': get_specialty_description(result.agent_name),
        'status': 'complete',
        'confidence': int(result.confidence * 100),  # 0-1 → 0-100
        'color': get_agent_color(result.agent_name),
        'analysis': simplify_medical_language(result.reasoning)
    }

def humanize_agent_name(agent_name: str) -> str:
    """
    Convert agent name to patient-friendly version
    """
    names = {
        'Cardiology Agent': 'Heart Specialist AI',
        'Safety Monitor Agent': 'Emergency Triage AI',
        'Pulmonary Agent': 'Lung Specialist AI',
        'Gastroenterology Agent': 'Stomach Specialist AI',
        'Musculoskeletal Agent': 'Bone & Muscle AI',
        'Triage Agent': 'Priority Assessment AI'
    }
    return names.get(agent_name, agent_name)
```

---

## 🚀 IMPLEMENTATION STEPS

### **Phase 1: Setup (30 minutes)**

1. **Create Frontend Folder:**
```bash
cd /Users/khushi22/Hackathon/Hackathon_Nikshatra
mkdir frontend
cd frontend

# Initialize React + TypeScript + Vite
npm create vite@latest . -- --template react-ts

# Install dependencies
npm install
npm install zustand lucide-react recharts canvas-confetti
npm install @radix-ui/react-accordion @radix-ui/react-progress
npm install socket.io-client axios
npm install -D tailwindcss postcss autoprefixer tailwindcss-animate
npx tailwindcss init -p
```

2. **Configure Vite for API Proxy:**
```typescript
// frontend/vite.config.ts
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import path from 'path'

export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },
  server: {
    port: 5173,
    proxy: {
      '/api': {
        target: 'http://localhost:5000',
        changeOrigin: true
      },
      '/ws': {
        target: 'ws://localhost:5000',
        ws: true
      }
    }
  }
})
```

3. **Copy UI Components:**
```bash
# Copy all provided UI files to frontend/src/
cp -r [path_to_ui_files]/components frontend/src/
cp -r [path_to_ui_files]/stores frontend/src/
# ... etc
```

---

### **Phase 2: Backend Enhancement (1 hour)**

1. **Create Enhanced Flask API:**
```bash
cd /Users/khushi22/Hackathon/Hackathon_Nikshatra

# Create new file
touch app_with_ui_support.py
```

2. **Install Flask-SocketIO:**
```bash
.venv/bin/pip install flask-socketio python-socketio
```

3. **Implement API endpoints** (see detailed code below)

---

### **Phase 3: Integration (1-2 hours)**

1. **Create API Service Layer:**
```typescript
// frontend/src/services/api.ts
import axios from 'axios';

const api = axios.create({
  baseURL: '/api',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json'
  }
});

export const chatAPI = {
  sendMessage: async (message: string, patientId: string) => {
    const response = await api.post('/chat', {
      message,
      patient_id: patientId,
      timestamp: new Date().toISOString()
    });
    return response.data;
  }
};

export const analysisAPI = {
  startAnalysis: async (patientId: string, symptoms: string[], vitals: any) => {
    const response = await api.post('/analyze', {
      patient_id: patientId,
      symptoms,
      vitals
    });
    return response.data;
  },
  
  getResults: async (patientId: string) => {
    const response = await api.get(`/results/${patientId}`);
    return response.data;
  }
};
```

2. **Connect Components to API:**
```typescript
// frontend/src/components/screens/AssessmentScreen.tsx

const handleSendMessage = async () => {
  if (!input.trim()) return;
  
  // Add user message to UI
  addMessage({ sender: 'user', text: input, timestamp: new Date() });
  setInput('');
  setIsTyping(true);
  
  try {
    // Call backend
    const response = await chatAPI.sendMessage(input, patientId);
    
    // Add MIMIQ response
    addMessage({
      sender: 'mimiq',
      text: response.response,
      timestamp: new Date()
    });
    
    // Check if ready to analyze
    if (response.urgency_level === 'HIGH' || response.urgency_level === 'CRITICAL') {
      // Show urgent care message
      addMessage({
        sender: 'mimiq',
        text: 'Based on your symptoms, I recommend starting an urgent analysis now. Ready?',
        timestamp: new Date()
      });
    }
  } catch (error) {
    console.error('Chat error:', error);
    addMessage({
      sender: 'mimiq',
      text: 'Sorry, I had trouble connecting. Please try again or type your symptoms.',
      timestamp: new Date()
    });
  } finally {
    setIsTyping(false);
  }
};
```

---

### **Phase 4: Testing (30 minutes)**

1. **Start Backend:**
```bash
cd /Users/khushi22/Hackathon/Hackathon_Nikshatra
.venv/bin/python app_with_ui_support.py
# Should start on http://localhost:5000
```

2. **Start Frontend:**
```bash
cd frontend
npm run dev
# Should start on http://localhost:5173
```

3. **Test Flow:**
   - Open http://localhost:5173
   - Click "Start Assessment"
   - Use voice or type symptoms
   - Verify chatbot responds
   - Complete assessment
   - Verify agents process in real-time
   - Check final results

---

## 🧪 TESTING CHECKLIST

### **Voice Input:**
- [ ] Microphone permission requested
- [ ] Voice recognized correctly
- [ ] Visual feedback (waveform) appears
- [ ] Graceful fallback to text if voice fails

### **Chatbot:**
- [ ] Empathetic responses
- [ ] Simple language (no jargon)
- [ ] Appropriate urgency detection
- [ ] Clear next steps

### **Agent Analysis:**
- [ ] All 6 agents start processing
- [ ] Real-time status updates
- [ ] Progress bar accurate
- [ ] Confidence scores display

### **Results:**
- [ ] Patient-friendly diagnosis
- [ ] Clear urgency indicators
- [ ] Simple action steps
- [ ] Nearby hospital info

### **Accessibility:**
- [ ] All buttons large enough (60px+ height)
- [ ] High contrast text
- [ ] Works on mobile
- [ ] Emergency button always visible

---

## 📝 NEXT STEPS

1. **Review this document** - Understand the architecture
2. **Set up frontend folder** - Follow Phase 1 steps
3. **Create enhanced Flask API** - Implement Phase 2
4. **Test integration** - Follow Phase 4
5. **Iterate based on testing** - Improve patient experience

---

## 🆘 TROUBLESHOOTING

### **CORS Issues:**
```python
# app_with_ui_support.py
from flask_cors import CORS

app = Flask(__name__)
CORS(app, resources={
    r"/*": {
        "origins": ["http://localhost:5173"],
        "methods": ["GET", "POST", "OPTIONS"],
        "allow_headers": ["Content-Type"]
    }
})
```

### **WebSocket Not Connecting:**
```typescript
// frontend/src/services/websocket.ts

// Try different transport
const socket = io('http://localhost:5000', {
  transports: ['polling', 'websocket'],  // Try polling first
  reconnection: true
});
```

### **Voice Not Working:**
```typescript
// Check browser support
if (!('webkitSpeechRecognition' in window)) {
  alert('Voice input not supported. Please use Chrome, Edge, or Safari.');
}
```

---

**END OF INTEGRATION GUIDE**

This document provides a complete blueprint for integrating the React UI with your Python backend while maintaining a patient-friendly, accessible experience. 

**Ready to implement?** Start with Phase 1 and let me know if you need help with any specific part!
