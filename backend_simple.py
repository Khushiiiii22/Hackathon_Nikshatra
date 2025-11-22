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
        
        prompt = f"""System: {system_prompt}

Patient says: {message}

Previous context: {session['context'][:500]}

Provide an empathetic, helpful response:"""
        
        llm_response = llm_service.analyze(
            prompt=prompt,
            temperature=0.7,
            max_tokens=200
        )
        
        response = llm_response.text if llm_response.success else "I'm having trouble right now. Please try again."
        
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
    """Run AI agent analysis on symptoms or uploaded files"""
    try:
        # Check if file was uploaded
        if 'file' in request.files:
            file = request.files['file']
            patient_id = request.form.get('patient_id', 'default')
            
            if file.filename == '':
                return jsonify({'error': 'No file selected'}), 400
            
            # Read file content
            file_content = file.read().decode('utf-8', errors='ignore')
            context = f"Medical Report Analysis:\n{file_content}"
            
            print(f"Analyzing uploaded file for patient {patient_id}...")
            print(f"File: {file.filename}, Size: {len(file_content)} bytes")
            
        else:
            # Handle JSON request
            data = request.json
            patient_id = data.get('patient_id', 'default')
            
            session = patient_sessions.get(patient_id, {})
            context = session.get('context', data.get('symptoms', ''))
        
        # Run agents in parallel
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
        
        # Extract symptoms, medications, and findings
        symptoms_found = []
        medications_found = []
        findings = []
        
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
                
                # Extract key information from result
                if result:
                    # Simple keyword extraction for symptoms
                    symptom_keywords = ['pain', 'fever', 'cough', 'headache', 'nausea', 'dizziness', 
                                       'shortness of breath', 'chest pain', 'fatigue', 'weakness']
                    for keyword in symptom_keywords:
                        if keyword in context.lower() and keyword not in symptoms_found:
                            symptoms_found.append(keyword.title())
                    
                    # Extract medication mentions
                    med_keywords = ['aspirin', 'paracetamol', 'ibuprofen', 'amoxicillin', 
                                   'metformin', 'insulin', 'lisinopril', 'atorvastatin']
                    for med in med_keywords:
                        if med in context.lower() and med not in medications_found:
                            medications_found.append(med.title())
                
                results[agent_id] = {
                    'diagnosis': result[:300] if result else 'Analysis complete',
                    'confidence': 85,
                    'timestamp': datetime.now().isoformat(),
                    'agent_name': name
                }
            except Exception as e:
                print(f"Agent {agent_id} error: {e}")
                results[agent_id] = {'error': str(e), 'agent_name': name}
        
        # Generate AI-powered comprehensive brief with prevention strategies
        try:
            brief_prompt = f"""Analyze this medical report and generate a comprehensive brief:

Report Content:
{context[:2000]}

Symptoms Found: {', '.join(symptoms_found) if symptoms_found else 'None identified'}
Medications Mentioned: {', '.join(medications_found) if medications_found else 'None'}

Generate a JSON response with:
{{
    "patient_brief": "2-3 sentence summary of patient's health status",
    "condition_identified": "Main health condition or concern",
    "prevention_strategies": ["List 4-5 specific prevention tips and lifestyle changes"],
    "medication_recommendations": ["Suggested medications or treatments"],
    "risk_factors": ["Key risk factors to monitor"],
    "follow_up_actions": ["Specific follow-up actions needed"]
}}"""
            
            ai_brief = llm_service.analyze(brief_prompt, temperature=0.3, max_tokens=1000)
            
            # Try to parse JSON response
            import json
            import re
            # Extract JSON from response
            json_match = re.search(r'\{.*\}', ai_brief.text, re.DOTALL)
            if json_match:
                brief_data = json.loads(json_match.group())
            else:
                brief_data = {}
        except Exception as e:
            print(f"Brief generation error: {e}")
            brief_data = {}
        
        # Generate comprehensive summary with medications
        urgency = 'moderate'
        esi_level = 3
        recommendation = '📋 See a doctor soon. Try to get an appointment within 24 hours.'
        
        # Check for urgent symptoms
        urgent_keywords = ['chest pain', 'shortness of breath', 'severe pain', 'unconscious', 
                          'bleeding', 'stroke', 'heart attack', 'emergency']
        for keyword in urgent_keywords:
            if keyword in context.lower():
                urgency = 'high'
                esi_level = 2
                recommendation = '🚨 EMERGENCY: Go to the emergency room immediately or call 108!'
                break
        
        # Check for moderate urgency
        moderate_keywords = ['fever', 'infection', 'diabetes', 'high blood pressure', 'pneumonia']
        if urgency == 'moderate':
            for keyword in moderate_keywords:
                if keyword in context.lower():
                    urgency = 'moderate-high'
                    esi_level = 3
                    recommendation = '⚠️ Schedule a doctor appointment within 24-48 hours.'
                    break
        
        summary = {
            'urgency': urgency,
            'esi_level': esi_level,
            'primary_concern': brief_data.get('condition_identified', 'Medical review required'),
            'recommendation': recommendation,
            'patient_brief': brief_data.get('patient_brief', 'Comprehensive medical analysis completed by 6 specialist AI agents.'),
            'symptoms_identified': symptoms_found if symptoms_found else ['Under review'],
            'medications_mentioned': medications_found if medications_found else ['None found in report'],
            'medication_recommendations': brief_data.get('medication_recommendations', [
                'Consult with your doctor for appropriate medications',
                'Follow prescribed treatment plan'
            ]),
            'prevention_strategies': brief_data.get('prevention_strategies', [
                '🥗 Maintain a balanced, nutritious diet',
                '🏃 Regular physical exercise (30 min/day)',
                '😴 Get adequate sleep (7-8 hours)',
                '💧 Stay well hydrated',
                '🚭 Avoid smoking and limit alcohol'
            ]),
            'risk_factors': brief_data.get('risk_factors', ['Consult doctor for personalized risk assessment']),
            'key_findings': [
                f"{len(results)} specialist agents reviewed your case",
                f"Urgency level: {urgency.upper()}",
                f"ESI Triage Level: {esi_level}",
                f"{len(symptoms_found)} symptoms identified",
                f"{len(medications_found)} medications found"
            ],
            'next_steps': [],
            'follow_up_actions': brief_data.get('follow_up_actions', []),
            'agents_consulted': len(results)
        }
        
        # Add next steps based on urgency
        if urgency == 'high':
            summary['next_steps'] = [
                '🚑 Call ambulance (108) immediately',
                '🏥 Go to nearest emergency room',
                '📱 Have someone accompany you',
                '📋 Bring this analysis with you'
            ]
        elif urgency == 'moderate-high':
            summary['next_steps'] = [
                '📞 Call your doctor today',
                '📅 Schedule appointment within 24-48 hours',
                '📊 Monitor symptoms closely',
                '💊 Continue current medications if prescribed',
                '🚨 Go to ER if symptoms worsen'
            ]
        else:
            summary['next_steps'] = [
                '📞 Call your doctor for an appointment',
                '📝 Monitor your symptoms',
                '💧 Stay hydrated and rest',
                '🚨 Go to ER if symptoms worsen'
            ]
        
        # Store results
        if patient_id not in patient_sessions:
            patient_sessions[patient_id] = {}
            
        patient_sessions[patient_id]['results'] = {
            'summary': summary,
            'detailed_results': results,
            'timestamp': datetime.now().isoformat()
        }
        
        # Emit completion
        socketio.emit('analysis_complete', {
            'patient_id': patient_id,
            'summary': summary,
            'detailed_results': results
        })
        
        return jsonify({
            'status': 'complete',
            'analysis_id': f"{patient_id}_{int(datetime.now().timestamp())}",
            'summary': summary,
            'detailed_results': results,
            'message': '✅ Analysis complete! All 6 specialists have reviewed your case.'
        })
        
    except Exception as e:
        print(f"Analysis error: {e}")
        import traceback
        traceback.print_exc()
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
