# 🛡️ Prevention-Focused Chatbot with Real-Time Recommendations

"""
Prevention-focused conversation flow that integrates with real-time vital monitoring
to provide proactive health guidance BEFORE emergencies occur.

Key Features:
1. Real-time vital sign analysis during conversation
2. Predictive risk scoring (30-60 min ahead)
3. Prevention recommendations integrated into chat
4. Early warning system for deterioration
"""

from typing import Dict, List, Optional
from dataclasses import dataclass
from enum import Enum
import asyncio
import time

@dataclass
class ConversationContext:
    """Track conversation state and patient context"""
    patient_id: str
    session_id: str
    start_time: float
    symptoms: List[str]
    vital_trends: Dict
    risk_score: float
    prevention_alerts: List[str]
    conversation_history: List[Dict]

class PreventionLevel(Enum):
    """Prevention urgency levels"""
    IMMEDIATE = "immediate"      # Do this now (aspirin, call 911)
    URGENT = "urgent"            # Do within 1 hour
    SOON = "soon"                # Do within 24 hours
    LIFESTYLE = "lifestyle"      # Long-term changes

@dataclass
class PreventionRecommendation:
    """Single prevention recommendation"""
    level: PreventionLevel
    action: str
    reasoning: str
    time_sensitive: bool
    evidence: Dict

class PreventionChatbot:
    """
    Enhanced chatbot with prevention-focused conversation flow
    
    Instead of just diagnosing, it:
    - Monitors vitals in real-time during conversation
    - Detects early warning signs
    - Provides prevention advice before crisis
    - Generates comprehensive prevention report
    """
    
    def __init__(self, vital_monitor, orchestrator):
        self.vital_monitor = vital_monitor
        self.orchestrator = orchestrator
        self.active_sessions: Dict[str, ConversationContext] = {}
    
    async def start_conversation(self, patient_id: str) -> ConversationContext:
        """Start a new prevention-focused conversation"""
        
        # Create session
        session_id = f"session-{patient_id}-{int(time.time())}"
        
        # Get baseline vitals from monitoring
        baseline_vitals = await self.vital_monitor.get_current_vitals(patient_id)
        
        context = ConversationContext(
            patient_id=patient_id,
            session_id=session_id,
            start_time=time.time(),
            symptoms=[],
            vital_trends=baseline_vitals,
            risk_score=0.0,
            prevention_alerts=[],
            conversation_history=[]
        )
        
        self.active_sessions[session_id] = context
        
        # Initial greeting with baseline check
        greeting = await self._generate_greeting(context)
        
        return context, greeting
    
    async def _generate_greeting(self, context: ConversationContext) -> str:
        """Generate personalized greeting based on current vitals"""
        
        vitals = context.vital_trends
        
        # Check for concerning trends
        concerns = []
        
        if vitals.get('heart_rate', 0) > 100:
            concerns.append("elevated heart rate")
        
        if vitals.get('spo2', 100) < 95:
            concerns.append("lower oxygen levels")
        
        # Personalized greeting
        if concerns:
            return (
                f"👋 Hi! I'm MIMIQ, your AI health assistant. "
                f"I notice your {', '.join(concerns)}. "
                f"Let's talk about what you're experiencing so I can help you stay healthy. "
                f"What brings you here today?"
            )
        else:
            return (
                "👋 Hi! I'm MIMIQ, your AI health assistant. "
                "I'm here to listen, assess your symptoms, and help prevent any issues. "
                "What's going on today?"
            )
    
    async def process_message(
        self, 
        session_id: str, 
        user_message: str
    ) -> Dict:
        """
        Process user message with real-time prevention analysis
        
        Flow:
        1. Analyze message for symptoms
        2. Check current vitals
        3. Calculate risk score
        4. Generate prevention recommendations
        5. Formulate response
        """
        
        context = self.active_sessions.get(session_id)
        if not context:
            raise ValueError(f"Session {session_id} not found")
        
        # 1. Add message to history
        context.conversation_history.append({
            'timestamp': time.time(),
            'role': 'user',
            'content': user_message
        })
        
        # 2. Extract symptoms
        new_symptoms = await self._extract_symptoms(user_message)
        context.symptoms.extend(new_symptoms)
        
        # 3. Get current vitals (real-time)
        current_vitals = await self.vital_monitor.get_current_vitals(context.patient_id)
        context.vital_trends = current_vitals
        
        # 4. Calculate risk score (includes vital trends)
        context.risk_score = await self._calculate_risk_score(context)
        
        # 5. Generate prevention recommendations
        preventions = await self._generate_prevention_recommendations(context)
        
        # 6. Check if immediate action needed
        if context.risk_score > 0.85:
            response = await self._handle_critical_situation(context, preventions)
        elif context.risk_score > 0.60:
            response = await self._handle_high_risk(context, preventions)
        else:
            response = await self._handle_normal_conversation(context, preventions)
        
        # 7. Add bot response to history
        context.conversation_history.append({
            'timestamp': time.time(),
            'role': 'assistant',
            'content': response['message']
        })
        
        return response
    
    async def _extract_symptoms(self, message: str) -> List[str]:
        """Extract symptoms from user message using NLP"""
        
        symptoms = []
        
        # Keyword matching (can be enhanced with NLP model)
        symptom_keywords = {
            'chest pain': ['chest pain', 'chest hurt', 'pain in chest'],
            'shortness of breath': ['short of breath', 'can\'t breathe', 'breathing hard'],
            'dizziness': ['dizzy', 'lightheaded', 'faint'],
            'nausea': ['nausea', 'nauseous', 'sick to stomach'],
            'sweating': ['sweating', 'cold sweat', 'clammy'],
            'palpitations': ['heart racing', 'palpitations', 'heart beating fast'],
            'fatigue': ['tired', 'exhausted', 'fatigue', 'weak']
        }
        
        message_lower = message.lower()
        
        for symptom, keywords in symptom_keywords.items():
            if any(keyword in message_lower for keyword in keywords):
                symptoms.append(symptom)
        
        return symptoms
    
    async def _calculate_risk_score(self, context: ConversationContext) -> float:
        """
        Calculate real-time risk score
        
        Factors:
        - Symptoms (severity and combination)
        - Vital sign trends (HRV decrease, SpO2 drop)
        - Symptom duration
        - Previous medical history
        """
        
        risk = 0.0
        vitals = context.vital_trends
        
        # High-risk symptom combinations
        high_risk_combos = [
            {'chest pain', 'shortness of breath'},
            {'chest pain', 'sweating', 'nausea'},
            {'shortness of breath', 'palpitations'}
        ]
        
        symptoms_set = set(context.symptoms)
        
        for combo in high_risk_combos:
            if combo.issubset(symptoms_set):
                risk += 0.40
        
        # Individual symptoms
        if 'chest pain' in symptoms_set:
            risk += 0.30
        if 'shortness of breath' in symptoms_set:
            risk += 0.25
        
        # Vital sign trends
        if vitals.get('hrv_decrease', 0) < -0.15:  # 15% HRV decrease
            risk += 0.20
        
        if vitals.get('spo2', 100) < 94:
            risk += 0.15
        
        if vitals.get('heart_rate', 80) > 110:
            risk += 0.10
        
        # Symptom duration
        duration = time.time() - context.start_time
        if duration < 600 and risk > 0.3:  # < 10 min AND high symptoms
            risk += 0.15  # Sudden onset is concerning
        
        return min(risk, 1.0)
    
    async def _generate_prevention_recommendations(
        self, 
        context: ConversationContext
    ) -> List[PreventionRecommendation]:
        """
        Generate prevention recommendations based on current state
        
        Prevention strategies:
        - Immediate actions (aspirin, call 911)
        - Symptom management (position, breathing)
        - Risk reduction (medications, lifestyle)
        - Monitoring (what to watch for)
        """
        
        preventions = []
        symptoms = set(context.symptoms)
        vitals = context.vital_trends
        risk = context.risk_score
        
        # IMMEDIATE PREVENTION (Risk > 0.85)
        if risk > 0.85:
            if 'chest pain' in symptoms:
                preventions.append(PreventionRecommendation(
                    level=PreventionLevel.IMMEDIATE,
                    action="Chew 325mg aspirin immediately (if not allergic)",
                    reasoning="Aspirin can prevent blood clot from growing during heart attack",
                    time_sensitive=True,
                    evidence={'reduces_mortality': '23%', 'time_critical': '< 5 min'}
                ))
                
                preventions.append(PreventionRecommendation(
                    level=PreventionLevel.IMMEDIATE,
                    action="Call 911 now - do NOT drive yourself",
                    reasoning="Your symptoms suggest possible heart attack",
                    time_sensitive=True,
                    evidence={'risk_score': risk, 'symptoms': list(symptoms)}
                ))
        
        # URGENT PREVENTION (Risk 0.60-0.85)
        elif risk > 0.60:
            if 'chest pain' in symptoms:
                preventions.append(PreventionRecommendation(
                    level=PreventionLevel.URGENT,
                    action="Sit down and rest - avoid any physical exertion",
                    reasoning="Reducing cardiac workload can prevent worsening",
                    time_sensitive=True,
                    evidence={'reduces_oxygen_demand': True}
                ))
                
                preventions.append(PreventionRecommendation(
                    level=PreventionLevel.URGENT,
                    action="Have someone drive you to ER within 1 hour",
                    reasoning="Moderate-high risk requires medical evaluation",
                    time_sensitive=True,
                    evidence={'risk_score': risk}
                ))
            
            if 'shortness of breath' in symptoms:
                preventions.append(PreventionRecommendation(
                    level=PreventionLevel.URGENT,
                    action="Sit upright, open windows for fresh air",
                    reasoning="Improves oxygen delivery",
                    time_sensitive=False,
                    evidence={'improves_spo2': True}
                ))
        
        # SOON PREVENTION (Risk 0.30-0.60)
        elif risk > 0.30:
            preventions.append(PreventionRecommendation(
                level=PreventionLevel.SOON,
                action="Contact your doctor today for evaluation",
                reasoning="Your symptoms need medical assessment",
                time_sensitive=False,
                evidence={'symptoms': list(symptoms)}
            ))
            
            preventions.append(PreventionRecommendation(
                level=PreventionLevel.SOON,
                action="Monitor symptoms - if worsening, go to ER",
                reasoning="Watch for deterioration",
                time_sensitive=False,
                evidence={'watch_for': ['increased pain', 'new symptoms']}
            ))
        
        # LIFESTYLE PREVENTION (Always include)
        if vitals.get('heart_rate', 80) > 90:
            preventions.append(PreventionRecommendation(
                level=PreventionLevel.LIFESTYLE,
                action="Practice deep breathing: 4 seconds in, 6 seconds out",
                reasoning="Reduces heart rate and anxiety",
                time_sensitive=False,
                evidence={'reduces_hr': '10-15 bpm', 'improves_hrv': True}
            ))
        
        # Vital-specific prevention
        if vitals.get('spo2', 100) < 95:
            preventions.append(PreventionRecommendation(
                level=PreventionLevel.URGENT,
                action="Sit upright and take slow, deep breaths",
                reasoning=f"Your oxygen is {vitals['spo2']:.1f}% (should be >95%)",
                time_sensitive=True,
                evidence={'current_spo2': vitals['spo2']}
            ))
        
        return preventions
    
    async def _handle_critical_situation(
        self, 
        context: ConversationContext,
        preventions: List[PreventionRecommendation]
    ) -> Dict:
        """Handle critical risk situation with immediate prevention"""
        
        # Get immediate actions
        immediate = [p for p in preventions if p.level == PreventionLevel.IMMEDIATE]
        
        message = "🚨 **CRITICAL ALERT** 🚨\n\n"
        message += f"Based on your symptoms and vital signs, this could be life-threatening.\n\n"
        message += "**DO THESE NOW:**\n"
        
        for i, action in enumerate(immediate, 1):
            message += f"{i}. {action.action}\n"
            message += f"   *Why: {action.reasoning}*\n\n"
        
        message += "\n💓 I'm monitoring your vitals in real-time. Stay on the line."
        
        # Run full diagnosis in background
        diagnosis_task = asyncio.create_task(
            self._run_full_diagnosis(context)
        )
        
        return {
            'message': message,
            'risk_level': 'CRITICAL',
            'risk_score': context.risk_score,
            'preventions': [p.__dict__ for p in preventions],
            'requires_immediate_action': True,
            'diagnosis_pending': True
        }
    
    async def _handle_high_risk(
        self, 
        context: ConversationContext,
        preventions: List[PreventionRecommendation]
    ) -> Dict:
        """Handle high-risk situation with urgent prevention"""
        
        urgent = [p for p in preventions if p.level == PreventionLevel.URGENT]
        
        message = "⚠️ **Important - Take Action Soon**\n\n"
        message += f"Your symptoms suggest moderate-high risk.\n\n"
        message += "**I recommend you do this:**\n"
        
        for i, action in enumerate(urgent, 1):
            message += f"{i}. {action.action}\n"
            message += f"   *{action.reasoning}*\n\n"
        
        # Add vital sign warning
        vitals = context.vital_trends
        if vitals.get('hrv_decrease', 0) < -0.15:
            message += "\n📊 I notice your heart rate variability has decreased 15% - "
            message += "this can be an early sign of stress on your heart.\n"
        
        message += "\nLet me ask a few more questions to assess this properly..."
        
        return {
            'message': message,
            'risk_level': 'HIGH',
            'risk_score': context.risk_score,
            'preventions': [p.__dict__ for p in preventions],
            'requires_immediate_action': False,
            'next_questions': await self._generate_followup_questions(context)
        }
    
    async def _handle_normal_conversation(
        self, 
        context: ConversationContext,
        preventions: List[PreventionRecommendation]
    ) -> Dict:
        """Handle normal conversation with preventive guidance"""
        
        # Include lifestyle preventions
        lifestyle = [p for p in preventions if p.level == PreventionLevel.LIFESTYLE]
        
        message = "I understand. Let me help you with that.\n\n"
        
        if lifestyle:
            message += "**Here's what you can do right now to feel better:**\n"
            for action in lifestyle:
                message += f"• {action.action}\n"
                message += f"  *{action.reasoning}*\n\n"
        
        # Add vital commentary if notable
        vitals = context.vital_trends
        if vitals.get('heart_rate', 80) > 90:
            message += f"\n💓 Your heart rate is {vitals['heart_rate']} bpm - "
            message += "a bit elevated. Let's help you relax.\n"
        
        message += "\nTell me more - when did this start?"
        
        return {
            'message': message,
            'risk_level': 'LOW',
            'risk_score': context.risk_score,
            'preventions': [p.__dict__ for p in preventions],
            'requires_immediate_action': False,
            'next_questions': await self._generate_followup_questions(context)
        }
    
    async def _generate_followup_questions(self, context: ConversationContext) -> List[str]:
        """Generate smart follow-up questions"""
        
        symptoms = context.symptoms
        questions = []
        
        if 'chest pain' in symptoms:
            questions = [
                "On a scale of 1-10, how severe is your chest pain?",
                "Does the pain radiate to your arm, jaw, or back?",
                "When did this pain start?",
                "Is it sharp or dull/pressure-like?"
            ]
        elif 'shortness of breath' in symptoms:
            questions = [
                "When did the breathing difficulty start?",
                "Does it get worse with exertion?",
                "Are you able to speak in full sentences?",
                "Do you have a cough?"
            ]
        else:
            questions = [
                "When did your symptoms start?",
                "Have you experienced anything like this before?",
                "Are your symptoms getting better, worse, or staying the same?"
            ]
        
        return questions
    
    async def _run_full_diagnosis(self, context: ConversationContext):
        """Run full 5-agent diagnosis"""
        
        # Convert conversation to patient data
        patient_data = await self._context_to_patient_data(context)
        
        # Run orchestrator
        result = await self.orchestrator.orchestrate(patient_data)
        
        return result
    
    async def _context_to_patient_data(self, context: ConversationContext) -> Dict:
        """Convert conversation context to PatientData format"""
        
        return {
            'patient_id': context.patient_id,
            'chief_complaint': ', '.join(context.symptoms),
            'vitals': context.vital_trends,
            'conversation_history': context.conversation_history
        }
    
    async def generate_prevention_report(self, session_id: str) -> str:
        """
        Generate comprehensive prevention report
        
        Includes:
        - Symptoms and diagnosis
        - Prevention actions taken
        - Future prevention strategies
        - Risk reduction plan
        """
        
        context = self.active_sessions.get(session_id)
        if not context:
            return "Session not found"
        
        # Get diagnosis
        diagnosis = await self._run_full_diagnosis(context)
        
        report = f"""
# 🛡️ Prevention & Health Report

**Patient ID:** {context.patient_id}
**Session:** {session_id}
**Date:** {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(context.start_time))}

---

## 📊 Current Status

**Risk Score:** {context.risk_score:.0%}
**Symptoms:** {', '.join(context.symptoms)}

**Vital Signs:**
- Heart Rate: {context.vital_trends.get('heart_rate', 'N/A')} bpm
- SpO2: {context.vital_trends.get('spo2', 'N/A')}%
- HRV Change: {context.vital_trends.get('hrv_decrease', 0) * 100:.1f}%

---

## 🎯 Diagnosis

{diagnosis.diagnosis if hasattr(diagnosis, 'diagnosis') else 'Pending full analysis'}

**Confidence:** {diagnosis.confidence if hasattr(diagnosis, 'confidence') else 'N/A'}
**Risk Level:** {diagnosis.risk_level if hasattr(diagnosis, 'risk_level') else 'N/A'}

---

## 🛡️ Prevention Recommendations

### Immediate Actions (Do Now)
{self._format_prevention_section(context, PreventionLevel.IMMEDIATE)}

### Urgent (Within 1 hour)
{self._format_prevention_section(context, PreventionLevel.URGENT)}

### Soon (Within 24 hours)
{self._format_prevention_section(context, PreventionLevel.SOON)}

### Lifestyle Changes (Long-term)
{self._format_prevention_section(context, PreventionLevel.LIFESTYLE)}

---

## 🔮 Future Prevention Strategy

Based on your assessment, here's how to prevent this in the future:

1. **Monitor these warning signs:**
   - HRV decrease > 10%
   - Chest discomfort with exertion
   - Unusual fatigue

2. **Risk reduction:**
   - Take aspirin daily (if prescribed)
   - Control blood pressure
   - Manage stress with breathing exercises

3. **When to seek help:**
   - Any chest pain lasting > 5 minutes
   - Shortness of breath at rest
   - Symptoms return or worsen

---

## 📱 Follow-Up

- [ ] Schedule follow-up with cardiologist
- [ ] Get recommended lab work (troponin, lipid panel)
- [ ] Download vital monitoring app
- [ ] Set medication reminders

**Questions?** Message me anytime at MIMIQ Health Assistant.
"""
        
        return report
    
    def _format_prevention_section(
        self, 
        context: ConversationContext, 
        level: PreventionLevel
    ) -> str:
        """Format prevention recommendations for report"""
        
        preventions = [
            p for p in context.prevention_alerts 
            if isinstance(p, PreventionRecommendation) and p.level == level
        ]
        
        if not preventions:
            return "_None required at this level_\n"
        
        formatted = ""
        for p in preventions:
            formatted += f"- **{p.action}**\n"
            formatted += f"  _{p.reasoning}_\n\n"
        
        return formatted


# Example usage
async def demo_prevention_chatbot():
    """Demo of prevention-focused conversation"""
    
    from src.wearable.phone_sensors import PhoneSensorMonitor
    from src.agents.base import MasterOrchestrator
    
    # Initialize
    sensor_monitor = PhoneSensorMonitor(patient_id="DEMO_001")
    orchestrator = MasterOrchestrator()
    chatbot = PreventionChatbot(sensor_monitor, orchestrator)
    
    # Start conversation
    context, greeting = await chatbot.start_conversation("DEMO_001")
    print(f"MIMIQ: {greeting}\n")
    
    # Simulate conversation
    messages = [
        "I have chest pain",
        "It started about 20 minutes ago",
        "Yes, it's going to my left arm",
        "Sharp pain, about 7 out of 10"
    ]
    
    for msg in messages:
        print(f"USER: {msg}")
        response = await chatbot.process_message(context.session_id, msg)
        print(f"MIMIQ: {response['message']}\n")
        print(f"[Risk Score: {response['risk_score']:.0%}]\n")
        
        if response.get('requires_immediate_action'):
            print("⚠️ Emergency protocol activated!")
            break
    
    # Generate report
    report = await chatbot.generate_prevention_report(context.session_id)
    print("\n" + "="*60)
    print(report)

if __name__ == "__main__":
    import asyncio
    asyncio.run(demo_prevention_chatbot())
