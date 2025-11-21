"""
MIMIQ Medical AI Chatbot
Real-time Emergency Assessment with Voice Assistant

Author: Hackathon Nikshatra Team
Date: November 21, 2025
"""

import streamlit as st
import asyncio
from datetime import datetime
import sys
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent))

from src.agents.base import MasterOrchestrator
from src.agents.safety import SafetyMonitorAgent
from src.agents.cardiology import CardiologyAgent
from src.agents.gastro import GastroenterologyAgent
from src.agents.musculoskeletal import MusculoskeletalAgent
from src.agents.pulmonary import PulmonaryAgent
from src.agents.triage import TriageAgent
from src.data_loader import PatientData
from src.config import SpecialtyType, RiskLevel

# Page config
st.set_page_config(
    page_title="MIMIQ - Medical AI Assistant",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    /* Dark medical theme */
    .main {
        background-color: #0F172A;
        color: #FFFFFF;
    }
    
    /* Agent cards */
    .agent-card {
        background: linear-gradient(135deg, #1E293B 0%, #334155 100%);
        border-radius: 12px;
        padding: 20px;
        margin: 10px 0;
        border-left: 4px solid;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
    }
    
    .agent-card.safety { border-left-color: #DC2626; }
    .agent-card.cardiology { border-left-color: #B91C1C; }
    .agent-card.pulmonary { border-left-color: #0EA5E9; }
    .agent-card.gastro { border-left-color: #F97316; }
    .agent-card.msk { border-left-color: #10B981; }
    
    /* Risk levels */
    .risk-critical {
        background-color: #DC2626;
        color: white;
        padding: 15px;
        border-radius: 8px;
        font-size: 24px;
        font-weight: bold;
        text-align: center;
        animation: pulse 2s infinite;
    }
    
    .risk-high {
        background-color: #F59E0B;
        color: white;
        padding: 15px;
        border-radius: 8px;
        font-size: 20px;
        font-weight: bold;
        text-align: center;
    }
    
    .risk-moderate {
        background-color: #FCD34D;
        color: #1F2937;
        padding: 15px;
        border-radius: 8px;
        font-size: 18px;
        font-weight: bold;
        text-align: center;
    }
    
    .risk-low {
        background-color: #10B981;
        color: white;
        padding: 15px;
        border-radius: 8px;
        font-size: 16px;
        font-weight: bold;
        text-align: center;
    }
    
    @keyframes pulse {
        0%, 100% { opacity: 1; transform: scale(1); }
        50% { opacity: 0.8; transform: scale(1.02); }
    }
    
    /* ESI Levels */
    .esi-1 {
        background: linear-gradient(135deg, #DC2626 0%, #991B1B 100%);
        color: white;
        padding: 30px;
        border-radius: 12px;
        font-size: 48px;
        font-weight: 900;
        text-align: center;
        border: 4px solid #FCA5A5;
        animation: emergency-pulse 1s infinite;
    }
    
    .esi-2 {
        background: linear-gradient(135deg, #F59E0B 0%, #D97706 100%);
        color: white;
        padding: 25px;
        border-radius: 12px;
        font-size: 36px;
        font-weight: 800;
        text-align: center;
    }
    
    .esi-3 {
        background: linear-gradient(135deg, #FCD34D 0%, #F59E0B 100%);
        color: #1F2937;
        padding: 20px;
        border-radius: 12px;
        font-size: 28px;
        font-weight: 700;
        text-align: center;
    }
    
    @keyframes emergency-pulse {
        0%, 100% { box-shadow: 0 0 20px #DC2626; }
        50% { box-shadow: 0 0 40px #DC2626, 0 0 60px #DC2626; }
    }
    
    /* Chat bubbles */
    .chat-message {
        padding: 15px;
        border-radius: 12px;
        margin: 10px 0;
        max-width: 80%;
    }
    
    .chat-message.user {
        background: linear-gradient(135deg, #3B82F6 0%, #2563EB 100%);
        color: white;
        margin-left: auto;
        text-align: right;
    }
    
    .chat-message.assistant {
        background: linear-gradient(135deg, #6366F1 0%, #4F46E5 100%);
        color: white;
    }
    
    /* Confidence meter */
    .confidence-meter {
        height: 30px;
        background: #1E293B;
        border-radius: 15px;
        overflow: hidden;
        margin: 10px 0;
    }
    
    .confidence-fill {
        height: 100%;
        background: linear-gradient(90deg, #10B981 0%, #059669 100%);
        border-radius: 15px;
        transition: width 1s ease-out;
    }
    
    /* Vital signs */
    .vital-sign {
        background: #1E293B;
        border-radius: 8px;
        padding: 15px;
        text-align: center;
        margin: 5px;
    }
    
    .vital-value {
        font-size: 32px;
        font-weight: bold;
        font-family: 'Courier New', monospace;
    }
    
    .vital-label {
        font-size: 14px;
        color: #94A3B8;
        margin-top: 5px;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'orchestrator' not in st.session_state:
    st.session_state.orchestrator = None
    st.session_state.messages = []
    st.session_state.current_assessment = None
    st.session_state.patient_data = None
    st.session_state.agent_results = []

def initialize_agents():
    """Initialize the 5-agent system"""
    if st.session_state.orchestrator is None:
        orchestrator = MasterOrchestrator()
        
        # Register all 5 agents
        orchestrator.register_agent(SpecialtyType.SAFETY, SafetyMonitorAgent())
        orchestrator.register_agent(SpecialtyType.CARDIOLOGY, CardiologyAgent())
        orchestrator.register_agent(SpecialtyType.GASTROENTEROLOGY, GastroenterologyAgent())
        orchestrator.register_agent(SpecialtyType.MUSCULOSKELETAL, MusculoskeletalAgent())
        orchestrator.register_agent(SpecialtyType.PULMONARY, PulmonaryAgent())
        
        st.session_state.orchestrator = orchestrator
        st.session_state.triage_agent = TriageAgent()

def render_agent_card(agent_name, diagnosis, confidence, risk_level, reasoning):
    """Render individual agent analysis card"""
    agent_class = agent_name.lower().replace(" ", "_")
    
    # Map agent to icon
    icons = {
        "safety": "🛡️",
        "cardiology": "❤️",
        "pulmonary": "🫁",
        "gastroenterology": "🍽️",
        "musculoskeletal": "💪"
    }
    
    icon = icons.get(agent_class.split("_")[0], "🤖")
    
    st.markdown(f"""
    <div class="agent-card {agent_class.split('_')[0]}">
        <h3>{icon} {agent_name}</h3>
        <p><strong>Diagnosis:</strong> {diagnosis}</p>
        <p><strong>Confidence:</strong> {confidence:.0%}</p>
        <p><strong>Risk Level:</strong> {risk_level}</p>
        <div class="confidence-meter">
            <div class="confidence-fill" style="width: {confidence*100}%"></div>
        </div>
        <details>
            <summary>View Reasoning</summary>
            <p style="margin-top: 10px; color: #CBD5E1;">{reasoning[:200]}...</p>
        </details>
    </div>
    """, unsafe_allow_html=True)

def render_esi_level(esi_level, priority_score):
    """Render ESI triage level"""
    esi_class = f"esi-{esi_level}"
    
    level_names = {
        1: "RESUSCITATION - IMMEDIATE",
        2: "EMERGENT - <10 MIN",
        3: "URGENT - 10-60 MIN",
        4: "LESS URGENT - 1-2 HRS",
        5: "NON-URGENT - 2-24 HRS"
    }
    
    st.markdown(f"""
    <div class="{esi_class}">
        🚨 ESI LEVEL {esi_level}
        <br>
        <span style="font-size: 24px;">{level_names.get(esi_level, "")}</span>
        <br>
        <span style="font-size: 18px;">Priority: {priority_score:.0f}/100</span>
    </div>
    """, unsafe_allow_html=True)

def render_risk_badge(risk_level):
    """Render risk level badge"""
    risk_classes = {
        "CRITICAL": "risk-critical",
        "HIGH": "risk-high",
        "MODERATE": "risk-moderate",
        "LOW": "risk-low"
    }
    
    risk_class = risk_classes.get(risk_level, "risk-low")
    
    st.markdown(f"""
    <div class="{risk_class}">
        ⚠️ {risk_level} RISK
    </div>
    """, unsafe_allow_html=True)

async def run_assessment(patient_data):
    """Run the 5-agent assessment"""
    # Run orchestrator
    state = await st.session_state.orchestrator.orchestrate(patient_data)
    
    # Run triage
    triage_result = await st.session_state.triage_agent.calculate_priority(state)
    
    return state, triage_result

# Main UI
def main():
    # Header
    st.markdown("""
    <div style="text-align: center; padding: 30px 0;">
        <h1 style="font-size: 48px; margin: 0;">🧠 MIMIQ</h1>
        <p style="font-size: 24px; color: #94A3B8; margin: 10px 0;">Medical AI Assistant</p>
        <p style="font-size: 16px; color: #64748B;">Emergency Symptom Assessment • 5 AI Specialists • Real-time Analysis</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Initialize agents
    initialize_agents()
    
    # Sidebar - Patient Input
    with st.sidebar:
        st.markdown("### 📋 Patient Information")
        
        # Quick test cases
        test_case = st.selectbox(
            "Quick Test Cases",
            [
                "Custom Input",
                "Pulmonary Embolism (CRITICAL)",
                "Pneumonia (MODERATE)",
                "NSTEMI (HIGH)",
                "Costochondritis (LOW)"
            ]
        )
        
        if test_case != "Custom Input":
            st.info(f"Loading: {test_case}")
        
        st.markdown("---")
        
        # Patient demographics
        col1, col2 = st.columns(2)
        with col1:
            age = st.number_input("Age", 18, 120, 45)
        with col2:
            sex = st.selectbox("Sex", ["M", "F"])
        
        # Chief complaint
        st.markdown("### 🗣️ Chief Complaint")
        complaint = st.text_area(
            "Describe symptoms:",
            placeholder="e.g., Sudden chest pain and shortness of breath...",
            height=100
        )
        
        # Vital signs
        st.markdown("### 📊 Vital Signs")
        
        col1, col2 = st.columns(2)
        with col1:
            hr = st.number_input("Heart Rate (bpm)", 40, 200, 88)
            rr = st.number_input("Resp Rate", 8, 40, 18)
        with col2:
            bp_sys = st.number_input("BP Systolic", 60, 220, 145)
            bp_dia = st.number_input("BP Diastolic", 40, 140, 92)
        
        col1, col2 = st.columns(2)
        with col1:
            spo2 = st.number_input("SpO2 (%)", 70, 100, 97)
        with col2:
            temp = st.number_input("Temp (°F)", 95.0, 107.0, 98.6)
        
        # Labs (optional)
        with st.expander("🧪 Lab Values (Optional)"):
            troponin = st.number_input("Troponin (ng/mL)", 0.0, 10.0, 0.0, step=0.01)
            d_dimer = st.number_input("D-dimer (ng/mL)", 0, 5000, 0)
            wbc = st.number_input("WBC (K/μL)", 0.0, 50.0, 8.5)
        
        # Assess button
        st.markdown("---")
        assess_button = st.button("🚀 START ASSESSMENT", use_container_width=True, type="primary")
        
        if st.button("🆘 EMERGENCY: Call 911", use_container_width=True, type="secondary"):
            st.error("🚨 Calling 911... Stay on the line!")
    
    # Main content area
    if assess_button or test_case != "Custom Input":
        # Load test case data if selected
        if test_case == "Pulmonary Embolism (CRITICAL)":
            patient_data = PatientData(
                patient_id="TEST001",
                age=62,
                sex="F",
                chief_complaint="Sudden shortness of breath and chest pain",
                vital_signs={"hr": 115, "bp_sys": 95, "bp_dia": 65, "rr": 28, "spo2": 88, "temp": 98.9},
                labs={"d_dimer": 850, "troponin": 0.02},
                medications=[],
                history=[]
            )
        elif test_case == "Pneumonia (MODERATE)":
            patient_data = PatientData(
                patient_id="TEST002",
                age=68,
                sex="M",
                chief_complaint="Cough, fever, and chest discomfort for 3 days",
                vital_signs={"hr": 92, "bp_sys": 140, "bp_dia": 88, "rr": 22, "spo2": 93, "temp": 101.8},
                labs={"wbc": 16.5},
                medications=[],
                history=[]
            )
        elif test_case == "NSTEMI (HIGH)":
            patient_data = PatientData(
                patient_id="TEST003",
                age=58,
                sex="M",
                chief_complaint="Crushing chest pain radiating to left arm",
                vital_signs={"hr": 88, "bp_sys": 145, "bp_dia": 92, "rr": 18, "spo2": 97, "temp": 98.6},
                labs={"troponin": 0.28, "troponin_6h": 0.12},
                medications=[],
                history=[]
            )
        elif test_case == "Costochondritis (LOW)":
            patient_data = PatientData(
                patient_id="TEST004",
                age=35,
                sex="F",
                chief_complaint="Sharp chest pain, worse with deep breathing and touch",
                vital_signs={"hr": 75, "bp_sys": 118, "bp_dia": 72, "rr": 16, "spo2": 99, "temp": 98.4},
                labs={},
                medications=[],
                history=[]
            )
        else:
            # Custom input
            patient_data = PatientData(
                patient_id=f"CUSTOM_{datetime.now().strftime('%Y%m%d%H%M%S')}",
                age=age,
                sex=sex,
                chief_complaint=complaint,
                vital_signs={
                    "hr": hr,
                    "bp_sys": bp_sys,
                    "bp_dia": bp_dia,
                    "rr": rr,
                    "spo2": spo2,
                    "temp": temp
                },
                labs={
                    "troponin": troponin if troponin > 0 else None,
                    "d_dimer": d_dimer if d_dimer > 0 else None,
                    "wbc": wbc if wbc > 0 else None
                },
                medications=[],
                history=[]
            )
        
        # Display patient info
        st.markdown("## 👤 Patient Overview")
        col1, col2, col3, col4, col5, col6 = st.columns(6)
        
        with col1:
            st.markdown(f"""
            <div class="vital-sign">
                <div class="vital-value">{patient_data.vital_signs['hr']}</div>
                <div class="vital-label">HR (bpm)</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div class="vital-sign">
                <div class="vital-value">{patient_data.vital_signs['bp_sys']}/{patient_data.vital_signs['bp_dia']}</div>
                <div class="vital-label">BP (mmHg)</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown(f"""
            <div class="vital-sign">
                <div class="vital-value">{patient_data.vital_signs['rr']}</div>
                <div class="vital-label">RR (breaths)</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col4:
            spo2_color = "#DC2626" if patient_data.vital_signs['spo2'] < 90 else "#10B981"
            st.markdown(f"""
            <div class="vital-sign" style="background: {spo2_color};">
                <div class="vital-value">{patient_data.vital_signs['spo2']}%</div>
                <div class="vital-label">SpO2</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col5:
            temp_color = "#DC2626" if patient_data.vital_signs['temp'] > 100.4 else "#1E293B"
            st.markdown(f"""
            <div class="vital-sign" style="background: {temp_color};">
                <div class="vital-value">{patient_data.vital_signs['temp']}</div>
                <div class="vital-label">Temp (°F)</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col6:
            st.markdown(f"""
            <div class="vital-sign">
                <div class="vital-value">{patient_data.age}{patient_data.sex}</div>
                <div class="vital-label">Age/Sex</div>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown(f"**Chief Complaint:** {patient_data.chief_complaint}")
        
        # Run assessment
        st.markdown("---")
        st.markdown("## 🤖 AI Analysis in Progress...")
        
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        # Simulate agent processing
        status_text.text("⚡ Activating 5 specialty agents...")
        progress_bar.progress(20)
        
        # Run actual assessment
        with st.spinner("Analyzing..."):
            state, triage_result = asyncio.run(run_assessment(patient_data))
        
        progress_bar.progress(100)
        status_text.text("✅ Analysis complete!")
        
        st.markdown("---")
        
        # Display results
        if state.diagnosis_results:
            # Get top diagnosis
            top_diagnosis = state.diagnosis_results[0]
            
            # Critical alert if needed
            if top_diagnosis.risk_level in [RiskLevel.CRITICAL, RiskLevel.HIGH]:
                st.markdown("## 🚨 URGENT MEDICAL ATTENTION REQUIRED")
                render_risk_badge(top_diagnosis.risk_level.value)
                
                if top_diagnosis.risk_level == RiskLevel.CRITICAL:
                    st.error("""
                    ### ⚠️ IMMEDIATE ACTION REQUIRED
                    
                    **DO NOW:**
                    1. Call 911 immediately
                    2. Stay calm and sit down
                    3. Do NOT drive yourself
                    4. Stay on the line with 911
                    
                    This is a life-threatening emergency requiring immediate medical attention.
                    """)
                    
                    if st.button("📞 CALL 911 NOW", type="primary", use_container_width=True):
                        st.success("🚨 Initiating 911 call...")
            
            # ESI Triage Level
            st.markdown("## 🚨 Triage Priority")
            render_esi_level(triage_result.esi_level, triage_result.priority_score)
            
            # Final Diagnosis
            st.markdown("## 🎯 Primary Diagnosis")
            col1, col2 = st.columns([2, 1])
            
            with col1:
                st.markdown(f"""
                ### {top_diagnosis.diagnosis.value}
                **Confidence:** {top_diagnosis.confidence*100:.0f}%
                
                **Risk Level:** {top_diagnosis.risk_level.value}
                
                **Agent:** {top_diagnosis.agent_name}
                
                **Reasoning:**
                {top_diagnosis.reasoning}
                """)
            
            with col2:
                st.markdown("### 💡 Recommendations")
                for i, rec in enumerate(top_diagnosis.recommendations[:5], 1):
                    st.markdown(f"{i}. {rec}")
            
            # All Agent Analyses
            st.markdown("---")
            st.markdown("## 🤖 All Agent Analyses (5/5)")
            
            for result in state.diagnosis_results:
                render_agent_card(
                    result.agent_name,
                    result.diagnosis.value,
                    result.confidence,
                    result.risk_level.value,
                    result.reasoning
                )
            
            # Disposition
            st.markdown("---")
            st.markdown("## 🏥 Disposition & Next Steps")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown(f"""
                **Destination:** {triage_result.destination}
                
                **Recommended:** {triage_result.disposition}
                
                **Nursing Ratio:** {triage_result.nursing_ratio}
                
                **Monitoring:** {triage_result.monitoring_level}
                """)
            
            with col2:
                st.markdown("**Resources Required:**")
                for resource in triage_result.resources_needed:
                    st.markdown(f"• {resource}")
            
            # Export options
            st.markdown("---")
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                if st.button("💾 Save Report", use_container_width=True):
                    st.success("Report saved!")
            
            with col2:
                if st.button("📤 Share", use_container_width=True):
                    st.info("Share options...")
            
            with col3:
                if st.button("🔊 Read Aloud", use_container_width=True):
                    st.info("Voice output activated...")
            
            with col4:
                if st.button("🗺️ Find ER", use_container_width=True):
                    st.info("Opening maps...")
        
        else:
            st.error("No diagnosis results available. Please check patient data.")

# Run the app
if __name__ == "__main__":
    main()
