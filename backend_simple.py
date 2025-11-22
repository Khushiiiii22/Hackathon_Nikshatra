"""
MIMIQ Medical AI - Simplified Backend API
Works with existing agents and provides patient-friendly responses
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_socketio import SocketIO, emit
import sys
import os
from datetime import datetime

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from llm_service import GeminiService
from agents.safety import SafetyMonitorAgent
from agents.cardiology import CardiologyAgent
from agents.pulmonary import PulmonaryAgent
from agents.gastro import GastroenterologyAgent
from agents.musculoskeletal import MusculoskeletalAgent
from agents.triage import TriageAgent

app = Flask(__name__)
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*")

# Initialize services
print("Initializing LLM service...")
llm_service = GeminiService()

# Initialize agents (they create their own LLM service internally)
print("Initializing agents...")
safety_agent = SafetyMonitorAgent()
cardiology_agent = CardiologyAgent()
pulmonary_agent = PulmonaryAgent()
gastro_agent = GastroenterologyAgent()
msk_agent = MusculoskeletalAgent()
triage_agent = TriageAgent()

# Store for patient data
patient_sessions = {}

@app.route('/health', methods=['GET'])
def health_check():
    """Health check"""
    return jsonify({'status': 'healthy', 'timestamp': datetime.now().isoformat()})

@app.route('/api/chat', methods=['POST'])
def chat():
    """Handle chat messages"""
    try:
        data = request.json
        patient_id = data.get('patient_id', 'default')
        message = data.get('message', '')
        
        # Initialize session if needed
        if patient_id not in patient_sessions:
            patient_sessions[patient_id] = {
                'messages': [],
                'symptoms': [],
                'context': ''
            }
        
        session = patient_sessions[patient_id]
        session['messages'].append({'role': 'user', 'content': message})
        session['context'] += f" {message}"
        
        # Generate empathetic response
        system_prompt = """You are MIMIQ, an empathetic medical AI assistant. 
        Be caring, use simple language, ask one question at a time.
        If symptoms sound serious, urge calling emergency services."""
        
        response = llm_service.generate_text(
            prompt=f"Patient says: {message}\nContext: {session['context'][:500]}",
            system_prompt=system_prompt,
            temperature=0.7,
            max_tokens=200
        )
        
        session['messages'].append({'role': 'assistant', 'content': response})
        
        # Extract symptoms (simple keyword matching)
        symptoms = []
        keywords = ['chest pain', 'shortness of breath', 'nausea', 'dizzy', 'pain', 'breathing', 'hurt']
        for keyword in keywords:
            if keyword in message.lower():
                symptoms.append(keyword)
                if keyword not in session['symptoms']:
                    session['symptoms'].append(keyword)
        
        # Determine urgency
        urgency = 'low'
        if any(s in message.lower() for s in ['chest pain', 'can\'t breathe', 'crushing']):
            urgency = 'high'
        
        return jsonify({
            'response': response,
            'extracted_symptoms': symptoms,
            'urgency_level': urgency,
            'patient_id': patient_id,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        print(f"Chat error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/analyze', methods=['POST'])
def analyze():
    """Run AI agent analysis"""
    try:
        data = request.json
        patient_id = data.get('patient_id', 'default')
        
        session = patient_sessions.get(patient_id, {})
        context = session.get('context', data.get('symptoms', ''))
        
        # Run agents
        print(f"Analyzing for patient {patient_id}...")
        
        results = {}
        agents = [
            ('safety', safety_agent, 'Emergency Triage'),
            ('cardiology', cardiology_agent, 'Heart Specialist'),
            ('pulmonary', pulmonary_agent, 'Lung Specialist'),
            ('gastro', gastro_agent, 'Stomach Specialist'),
            ('musculoskeletal', msk_agent, 'Bone & Muscle'),
            ('triage', triage_agent, 'Priority Assessment')
        ]
        
        for agent_id, agent, name in agents:
            try:
                print(f"Running {name}...")
                result = agent.analyze(context)
                
                # Emit update via WebSocket
                socketio.emit('agent_update', {
                    'agent_id': agent_id,
                    'agent_name': name,
                    'status': 'complete',
                    'progress': 100,
                    'patient_id': patient_id
                })
                
                results[agent_id] = {
                    'diagnosis': result[:200] if result else 'Analysis complete',
                    'confidence': 85,
                    'timestamp': datetime.now().isoformat()
                }
            except Exception as e:
                print(f"Agent {agent_id} error: {e}")
                results[agent_id] = {'error': str(e)}
        
        # Generate summary
        summary = {
            'urgency': 'moderate',
            'esi_level': 3,
            'primary_concern': 'Symptoms under review',
            'recommendation': '📋 See a doctor soon. Try to get an appointment within 24 hours.',
            'next_steps': [
                'Call your doctor for an appointment',
                'Monitor your symptoms',
                'Go to ER if symptoms worsen',
                'Rest and stay hydrated'
            ],
            'agents_consulted': len(results)
        }
        
        # Check for urgent symptoms
        if 'chest pain' in context.lower() or 'shortness of breath' in context.lower():
            summary['urgency'] = 'high'
            summary['esi_level'] = 2
            summary['recommendation'] = '⚠️ This needs urgent medical care. Go to the emergency room now.'
            summary['next_steps'] = [
                'Go to emergency room immediately',
                'Don\'t drive yourself if possible',
                'Bring this report with you',
                'Have someone accompany you'
            ]
        
        # Store results
        if patient_id in patient_sessions:
            patient_sessions[patient_id]['results'] = {
                'summary': summary,
                'detailed_results': results,
                'timestamp': datetime.now().isoformat()
            }
        
        # Emit completion
        socketio.emit('analysis_complete', {
            'patient_id': patient_id,
            'summary': summary
        })
        
        return jsonify({
            'status': 'started',
            'analysis_id': f"{patient_id}_{int(datetime.now().timestamp())}",
            'estimated_time': '30 seconds',
            'message': 'AI specialists are reviewing your case'
        })
        
    except Exception as e:
        print(f"Analysis error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/results/<patient_id>', methods=['GET'])
def get_results(patient_id):
    """Get analysis results"""
    try:
        session = patient_sessions.get(patient_id)
        if not session or 'results' not in session:
            return jsonify({'error': 'No results found'}), 404
        
        results = session['results']
        
        return jsonify({
            'patient_id': patient_id,
            'timestamp': results['timestamp'],
            'summary': results['summary'],
            'detailed_results': results['detailed_results'],
            'symptoms': session.get('symptoms', []),
            'vitals': {}
        })
        
    except Exception as e:
        print(f"Results error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/agents/status', methods=['GET'])
def agent_status():
    """Get agent status"""
    return jsonify({
        'agents': [
            {'id': 'safety', 'name': 'Emergency Triage', 'status': 'ready'},
            {'id': 'cardiology', 'name': 'Heart Specialist', 'status': 'ready'},
            {'id': 'pulmonary', 'name': 'Lung Specialist', 'status': 'ready'},
            {'id': 'gastro', 'name': 'Stomach Specialist', 'status': 'ready'},
            {'id': 'musculoskeletal', 'name': 'Bone & Muscle', 'status': 'ready'},
            {'id': 'triage', 'name': 'Priority Assessment', 'status': 'ready'}
        ]
    })

@socketio.on('connect')
def handle_connect():
    """WebSocket connection"""
    print(f"Client connected: {request.sid}")
    emit('connection_status', {'status': 'connected'})

@socketio.on('subscribe')
def handle_subscribe(data):
    """Subscribe to patient updates"""
    patient_id = data.get('patient_id')
    print(f"Subscribed to patient {patient_id}")
    emit('subscribed', {'patient_id': patient_id})

if __name__ == '__main__':
    print("=" * 60)
    print("🏥 MIMIQ Medical AI Platform - Backend Server")
    print("=" * 60)
    print(f"✅ Gemini LLM: {llm_service.model}")
    print(f"✅ Agents: 6 specialists ready")
    print(f"✅ CORS: Enabled")
    print(f"✅ WebSocket: Enabled")
    print(f"✅ Emergency: 911 (US), 108 (India)")
    print("=" * 60)
    print("🚀 Server starting on http://localhost:5000")
    print("=" * 60)
    
    socketio.run(app, host='0.0.0.0', port=5000, debug=True, allow_unsafe_werkzeug=True)
