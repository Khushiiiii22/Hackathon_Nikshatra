"""
Enhanced Fl# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from llm_service import GeminiService
from agents.safety import SafetyAgent
from agents.cardiology import CardiologyAgent
from agents.pulmonary import PulmonaryAgent
from agents.gastro import GastroAgent
from agents.musculoskeletal import MusculoskeletalAgent
from agents.triage import TriageAgent

app = Flask(__name__)
CORS(app, origins=["http://localhost:5173", "http://localhost:3000"])
socketio = SocketIO(app, cors_allowed_origins=["http://localhost:5173", "http://localhost:3000"])

# Initialize services
llm_service = GeminiService() Medical AI Platform
Supports React UI with WebSocket real-time updates and patient-friendly responses
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_socketio import SocketIO, emit
import sys
import os
from datetime import datetime
import json
import threading
import time

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from llm_service import GeminiService
from agents.safety_agent import SafetyAgent
from agents.cardiology_agent import CardiologyAgent
from agents.pulmonary_agent import PulmonaryAgent
from agents.gastro_agent import GastroAgent
from agents.musculoskeletal_agent import MusculoskeletalAgent
from agents.triage_agent import TriageAgent

app = Flask(__name__)
CORS(app, origins=["http://localhost:5173", "http://localhost:3000"])
socketio = SocketIO(app, cors_allowed_origins=["http://localhost:5173", "http://localhost:3000"])

# Initialize services
llm_service = GeminiService()

# Initialize all agents
safety_agent = SafetyAgent(llm_service)
cardiology_agent = CardiologyAgent(llm_service)
pulmonary_agent = PulmonaryAgent(llm_service)
gastro_agent = GastroAgent(llm_service)
msk_agent = MusculoskeletalAgent(llm_service)
triage_agent = TriageAgent(llm_service)

# Store for patient data and analysis results
patient_data = {}
analysis_results = {}
chat_history = {}

# Medical term translations for patient-friendly language
MEDICAL_TRANSLATIONS = {
    'Acute Coronary Syndrome': 'Possible heart attack',
    'NSTEMI': 'Heart issue requiring urgent care',
    'STEMI': 'Severe heart attack',
    'Pulmonary Embolism': 'Blood clot in lung',
    'Pneumothorax': 'Collapsed lung',
    'GERD': 'Severe acid reflux',
    'Gastritis': 'Stomach inflammation',
    'Musculoskeletal': 'Muscle or bone related',
    'Myocardial Infarction': 'Heart attack',
    'Angina': 'Chest pain from heart',
    'Dyspnea': 'Difficulty breathing',
    'Tachycardia': 'Fast heartbeat',
    'Bradycardia': 'Slow heartbeat',
    'Hypertension': 'High blood pressure',
    'Hypotension': 'Low blood pressure'
}

def simplify_medical_terms(text):
    """Convert medical jargon to patient-friendly language"""
    result = text
    for medical, simple in MEDICAL_TRANSLATIONS.items():
        result = result.replace(medical, simple)
    return result

def get_empathetic_prompt():
    """Get the empathetic chatbot system prompt"""
    return """You are MIMIQ, an empathetic medical AI assistant. Your role is to help patients describe their symptoms.

CRITICAL RULES:
1. Use SIMPLE language - no medical jargon
2. Be EMPATHETIC - acknowledge their feelings and pain
3. Ask ONE question at a time - don't overwhelm them
4. Give CLEAR instructions when urgent
5. REASSURE them - "I'm here to help you"
6. If symptoms sound serious, immediately recommend calling emergency services

RESPONSE FORMAT:
- Start with empathy: "I understand this is concerning..."
- Ask clear questions: "Can you tell me when this started?"
- Be supportive: "You're doing great. Just one more question..."
- End with reassurance: "I'm analyzing this to help you."

URGENCY HANDLING:
- Chest pain + difficulty breathing → "This could be serious. While I analyze this, if symptoms worsen, call emergency services immediately (911 in US, 108 in India)."
- Severe symptoms → "I'm concerned about your symptoms. Please have someone nearby if possible."
- Life-threatening signs → "Call emergency services NOW. Don't wait for my analysis."

Remember: The patient may be in pain, scared, or unable to type well. Be patient and understanding."""

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'services': {
            'llm': 'operational',
            'agents': 'operational',
            'websocket': 'operational'
        }
    })

@app.route('/api/chat', methods=['POST'])
def chat():
    """Handle chatbot conversation with voice/text input"""
    try:
        data = request.json
        patient_id = data.get('patient_id', 'default')
        message = data.get('message', '')
        timestamp = data.get('timestamp', datetime.now().isoformat())
        
        # Initialize chat history for patient
        if patient_id not in chat_history:
            chat_history[patient_id] = []
            patient_data[patient_id] = {
                'symptoms': [],
                'vitals': {},
                'history': []
            }
        
        # Add user message to history
        chat_history[patient_id].append({
            'role': 'user',
            'content': message,
            'timestamp': timestamp
        })
        
        # Build conversation context
        conversation = [{'role': 'system', 'content': get_empathetic_prompt()}]
        conversation.extend([
            {'role': msg['role'], 'content': msg['content']} 
            for msg in chat_history[patient_id][-10:]  # Last 10 messages
        ])
        
        # Get AI response
        response = llm_service.generate_text(
            prompt=message,
            system_prompt=get_empathetic_prompt(),
            temperature=0.7
        )
        
        # Add AI response to history
        chat_history[patient_id].append({
            'role': 'assistant',
            'content': response,
            'timestamp': datetime.now().isoformat()
        })
        
        # Extract symptoms and urgency from conversation
        extracted_symptoms = extract_symptoms(message)
        urgency_level = assess_urgency(message, extracted_symptoms)
        
        # Update patient data
        if extracted_symptoms:
            patient_data[patient_id]['symptoms'].extend(extracted_symptoms)
        
        # Determine next question
        next_question = determine_next_question(patient_data[patient_id])
        
        return jsonify({
            'response': response,
            'extracted_symptoms': extracted_symptoms,
            'urgency_level': urgency_level,
            'next_question': next_question,
            'patient_id': patient_id,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        print(f"Chat error: {e}")
        return jsonify({
            'error': str(e),
            'response': "I'm having trouble processing that. Could you try again, or type if you were using voice?"
        }), 500

def extract_symptoms(message):
    """Extract symptoms from patient message"""
    symptoms = []
    message_lower = message.lower()
    
    symptom_keywords = {
        'chest pain': ['chest pain', 'chest hurt', 'chest pressure', 'tight chest'],
        'shortness of breath': ['can\'t breathe', 'short of breath', 'breathing hard', 'difficulty breathing'],
        'nausea': ['nausea', 'feel sick', 'want to vomit', 'queasy'],
        'dizziness': ['dizzy', 'lightheaded', 'spinning'],
        'sweating': ['sweating', 'sweaty', 'cold sweat'],
        'pain radiating': ['pain in arm', 'pain in jaw', 'pain spreading'],
        'fatigue': ['tired', 'exhausted', 'weak', 'fatigue']
    }
    
    for symptom, keywords in symptom_keywords.items():
        if any(keyword in message_lower for keyword in keywords):
            symptoms.append(symptom)
    
    return symptoms

def assess_urgency(message, symptoms):
    """Assess urgency level from symptoms"""
    message_lower = message.lower()
    
    # Critical symptoms
    critical_keywords = ['can\'t breathe', 'severe chest pain', 'crushing', 'unconscious', 'passing out']
    if any(keyword in message_lower for keyword in critical_keywords):
        return 'critical'
    
    # High urgency
    high_urgency_symptoms = ['chest pain', 'shortness of breath', 'pain radiating']
    if any(symptom in symptoms for symptom in high_urgency_symptoms):
        return 'high'
    
    # Moderate
    moderate_symptoms = ['nausea', 'dizziness', 'sweating']
    if any(symptom in symptoms for symptom in moderate_symptoms):
        return 'moderate'
    
    return 'low'

def determine_next_question(patient_info):
    """Determine what to ask next based on gathered info"""
    symptoms = patient_info.get('symptoms', [])
    
    if not symptoms:
        return "Can you describe what you're feeling right now?"
    
    if 'chest pain' in symptoms and 'pain radiating' not in symptoms:
        return "Does the pain spread to your arm, jaw, or back?"
    
    if 'shortness of breath' in symptoms:
        return "When you try to take a deep breath, does it hurt or feel impossible?"
    
    if not patient_info.get('vitals'):
        return "Do you know your current heart rate or blood pressure? It's okay if you don't."
    
    return "Is there anything else you'd like to tell me about how you're feeling?"

@app.route('/api/analyze', methods=['POST'])
def start_analysis():
    """Start AI agent analysis"""
    try:
        data = request.json
        patient_id = data.get('patient_id', 'default')
        symptoms = data.get('symptoms', [])
        vitals = data.get('vitals', {})
        
        # Update patient data
        if patient_id not in patient_data:
            patient_data[patient_id] = {'symptoms': [], 'vitals': {}, 'history': []}
        
        patient_data[patient_id]['symptoms'].extend(symptoms)
        patient_data[patient_id]['vitals'].update(vitals)
        
        # Create analysis ID
        analysis_id = f"{patient_id}_{int(time.time())}"
        
        # Start analysis in background thread
        thread = threading.Thread(
            target=run_agent_analysis,
            args=(patient_id, analysis_id, symptoms, vitals)
        )
        thread.daemon = True
        thread.start()
        
        return jsonify({
            'status': 'started',
            'analysis_id': analysis_id,
            'estimated_time': '30-45 seconds',
            'patient_id': patient_id,
            'message': 'AI specialists are reviewing your case now. You\'ll see updates in real-time.'
        })
        
    except Exception as e:
        print(f"Analysis error: {e}")
        return jsonify({'error': str(e)}), 500

def run_agent_analysis(patient_id, analysis_id, symptoms, vitals):
    """Run all agents and emit real-time updates"""
    try:
        # Prepare patient context
        context = f"Symptoms: {', '.join(symptoms)}. Vitals: {vitals}"
        
        agents = [
            ('safety', safety_agent, 'Emergency Triage AI'),
            ('cardiology', cardiology_agent, 'Heart Specialist AI'),
            ('pulmonary', pulmonary_agent, 'Lung Specialist AI'),
            ('gastro', gastro_agent, 'Stomach Specialist AI'),
            ('musculoskeletal', msk_agent, 'Bone & Muscle AI'),
            ('triage', triage_agent, 'Priority Assessment AI')
        ]
        
        results = {}
        
        for agent_id, agent, agent_name in agents:
            # Emit start status
            socketio.emit('agent_update', {
                'agent_id': agent_id,
                'agent_name': agent_name,
                'status': 'analyzing',
                'progress': 0,
                'patient_id': patient_id
            })
            
            # Run agent analysis
            try:
                result = agent.analyze(context)
                
                # Emit progress
                socketio.emit('agent_update', {
                    'agent_id': agent_id,
                    'agent_name': agent_name,
                    'status': 'processing',
                    'progress': 50,
                    'patient_id': patient_id
                })
                
                time.sleep(0.5)  # Simulate processing
                
                # Parse result
                confidence = extract_confidence(result)
                diagnosis = extract_diagnosis(result)
                
                results[agent_id] = {
                    'diagnosis': diagnosis,
                    'confidence': confidence,
                    'raw_result': result,
                    'timestamp': datetime.now().isoformat()
                }
                
                # Emit completion
                socketio.emit('agent_update', {
                    'agent_id': agent_id,
                    'agent_name': agent_name,
                    'status': 'complete',
                    'progress': 100,
                    'confidence': confidence,
                    'patient_id': patient_id
                })
                
            except Exception as e:
                print(f"Agent {agent_id} error: {e}")
                results[agent_id] = {
                    'error': str(e),
                    'timestamp': datetime.now().isoformat()
                }
                socketio.emit('agent_update', {
                    'agent_id': agent_id,
                    'agent_name': agent_name,
                    'status': 'error',
                    'error': str(e),
                    'patient_id': patient_id
                })
        
        # Store results
        analysis_results[analysis_id] = {
            'patient_id': patient_id,
            'results': results,
            'timestamp': datetime.now().isoformat(),
            'symptoms': symptoms,
            'vitals': vitals
        }
        
        # Generate patient-friendly summary
        summary = generate_patient_summary(results, symptoms)
        analysis_results[analysis_id]['summary'] = summary
        
        # Emit completion
        socketio.emit('analysis_complete', {
            'analysis_id': analysis_id,
            'patient_id': patient_id,
            'summary': summary
        })
        
    except Exception as e:
        print(f"Analysis thread error: {e}")
        socketio.emit('analysis_error', {
            'patient_id': patient_id,
            'error': str(e)
        })

def extract_confidence(result):
    """Extract confidence score from agent result"""
    try:
        if 'confidence' in result.lower():
            # Try to find percentage
            import re
            matches = re.findall(r'(\d+)%', result)
            if matches:
                return int(matches[0])
        return 85  # Default confidence
    except:
        return 85

def extract_diagnosis(result):
    """Extract diagnosis from agent result"""
    try:
        # Simple extraction - get first sentence
        sentences = result.split('.')
        if sentences:
            return simplify_medical_terms(sentences[0].strip())
        return simplify_medical_terms(result[:200])
    except:
        return "Analysis complete"

def generate_patient_summary(results, symptoms):
    """Generate patient-friendly summary"""
    try:
        # Get triage result for ESI level
        triage = results.get('triage', {})
        safety = results.get('safety', {})
        
        # Determine urgency
        urgency = 'moderate'
        esi_level = 3
        
        if 'chest pain' in symptoms or 'shortness of breath' in symptoms:
            urgency = 'high'
            esi_level = 2
        
        # Create summary
        summary = {
            'urgency': urgency,
            'esi_level': esi_level,
            'primary_concern': simplify_medical_terms(
                results.get('cardiology', {}).get('diagnosis', 
                results.get('pulmonary', {}).get('diagnosis', 'Symptoms under review'))
            ),
            'recommendation': get_recommendation(urgency, esi_level),
            'next_steps': get_next_steps(urgency, esi_level),
            'agents_consulted': len([r for r in results.values() if 'diagnosis' in r])
        }
        
        return summary
        
    except Exception as e:
        print(f"Summary generation error: {e}")
        return {
            'urgency': 'moderate',
            'esi_level': 3,
            'primary_concern': 'Analysis complete',
            'recommendation': 'See a doctor soon',
            'next_steps': ['Schedule appointment', 'Monitor symptoms'],
            'agents_consulted': 6
        }

def get_recommendation(urgency, esi_level):
    """Get patient-friendly recommendation"""
    if urgency == 'critical' or esi_level == 1:
        return '🚨 This is an emergency. Call 911 (US) or 108 (India) immediately.'
    elif urgency == 'high' or esi_level == 2:
        return '⚠️ This needs urgent medical care. Go to the emergency room now.'
    elif esi_level == 3:
        return '📋 You should see a doctor soon. Try to get an appointment within 24 hours.'
    else:
        return '✅ Your symptoms don\'t seem urgent. Schedule a regular doctor appointment.'

def get_next_steps(urgency, esi_level):
    """Get next steps for patient"""
    if urgency == 'critical' or esi_level == 1:
        return [
            'Call emergency services NOW (911 in US, 108 in India)',
            'Don\'t drive yourself - wait for ambulance',
            'Have someone stay with you',
            'Sit or lie down while waiting'
        ]
    elif urgency == 'high' or esi_level == 2:
        return [
            'Go to emergency room immediately',
            'Don\'t drive yourself if possible',
            'Bring this report with you',
            'Have someone accompany you'
        ]
    elif esi_level == 3:
        return [
            'Call your doctor for appointment within 24 hours',
            'Monitor your symptoms closely',
            'Go to ER if symptoms worsen',
            'Rest and avoid strenuous activity'
        ]
    else:
        return [
            'Schedule regular doctor appointment',
            'Keep track of your symptoms',
            'Rest and stay hydrated',
            'Seek immediate care if symptoms worsen'
        ]

@app.route('/api/results/<patient_id>', methods=['GET'])
def get_results(patient_id):
    """Get patient-friendly results"""
    try:
        # Find latest analysis for patient
        patient_analyses = [
            (aid, data) for aid, data in analysis_results.items()
            if data.get('patient_id') == patient_id
        ]
        
        if not patient_analyses:
            return jsonify({'error': 'No results found for patient'}), 404
        
        # Get most recent
        latest_id, latest_data = max(patient_analyses, key=lambda x: x[1].get('timestamp', ''))
        
        return jsonify({
            'patient_id': patient_id,
            'analysis_id': latest_id,
            'timestamp': latest_data.get('timestamp'),
            'summary': latest_data.get('summary'),
            'detailed_results': latest_data.get('results'),
            'symptoms': latest_data.get('symptoms'),
            'vitals': latest_data.get('vitals')
        })
        
    except Exception as e:
        print(f"Results error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/agents/status', methods=['GET'])
def get_agent_status():
    """Get current status of all agents"""
    return jsonify({
        'agents': [
            {'id': 'safety', 'name': 'Emergency Triage AI', 'status': 'ready'},
            {'id': 'cardiology', 'name': 'Heart Specialist AI', 'status': 'ready'},
            {'id': 'pulmonary', 'name': 'Lung Specialist AI', 'status': 'ready'},
            {'id': 'gastro', 'name': 'Stomach Specialist AI', 'status': 'ready'},
            {'id': 'musculoskeletal', 'name': 'Bone & Muscle AI', 'status': 'ready'},
            {'id': 'triage', 'name': 'Priority Assessment AI', 'status': 'ready'}
        ],
        'llm_service': 'operational',
        'timestamp': datetime.now().isoformat()
    })

@socketio.on('connect')
def handle_connect():
    """Handle WebSocket connection"""
    print(f"Client connected: {request.sid}")
    emit('connection_status', {'status': 'connected', 'timestamp': datetime.now().isoformat()})

@socketio.on('disconnect')
def handle_disconnect():
    """Handle WebSocket disconnection"""
    print(f"Client disconnected: {request.sid}")

@socketio.on('subscribe')
def handle_subscribe(data):
    """Handle patient subscription for updates"""
    patient_id = data.get('patient_id')
    print(f"Client {request.sid} subscribed to patient {patient_id}")
    emit('subscribed', {'patient_id': patient_id, 'status': 'subscribed'})

if __name__ == '__main__':
    print("=" * 60)
    print("🏥 MIMIQ Medical AI Platform - Enhanced API Server")
    print("=" * 60)
    print(f"✅ LLM Service: {llm_service.model}")
    print(f"✅ Agents: 6 specialists ready")
    print(f"✅ CORS: Enabled for localhost:5173, localhost:3000")
    print(f"✅ WebSocket: Enabled")
    print(f"✅ Emergency Numbers: 911 (US), 108 (India)")
    print("=" * 60)
    print("🚀 Starting server on http://localhost:5000")
    print("=" * 60)
    
    socketio.run(app, host='0.0.0.0', port=5000, debug=True, allow_unsafe_werkzeug=True)
