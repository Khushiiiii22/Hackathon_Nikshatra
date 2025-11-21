"""
Demo showing Cardiology and Gastroenterology agents working together
"""

import asyncio
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent / 'src'))

from loguru import logger
from src.config import LOG_FORMAT, LOG_LEVEL, SpecialtyType
from src.data_loader import PatientData
from src.agents.base import MasterOrchestrator
from src.agents.cardiology import CardiologyAgent
from src.agents.gastro import GastroenterologyAgent
from src.agents.safety import SafetyMonitorAgent

# Configure logging
logger.remove()
logger.add(
    "logs/mimiq_cardiac_gastro.log",
    format=LOG_FORMAT,
    level=LOG_LEVEL,
    rotation="10 MB"
)
logger.add(sys.stderr, format=LOG_FORMAT, level=LOG_LEVEL)


def create_cardiac_patient() -> PatientData:
    """Create test patient with cardiac chest pain (NSTEMI)"""
    from datetime import datetime
    return PatientData(
        patient_id='10001',
        hadm_id='20001',
        age=68,
        gender='M',
        chief_complaint='Chest pain',
        admission_time=datetime.now(),
        icd_codes=['41401', '4019'],  # CAD, HTN
        diagnoses=['Chest pain', 'CAD'],
        labs={
            'Troponin': [
                (datetime.now(), 0.05),  # Baseline elevated
                (datetime.now(), 0.15),  # Rising
                (datetime.now(), 0.35)   # Significantly elevated (NSTEMI)
            ],
            'WBC': [(datetime.now(), 8.5)],
            'Hemoglobin': [(datetime.now(), 14.2)],
            'Creatinine': [(datetime.now(), 1.1)]
        },
        vitals={
            'heart_rate': 88,
            'blood_pressure': 145,
            'blood_pressure_diastolic': 90,
            'respiratory_rate': 18,
            'oxygen_saturation': 97,
            'temperature': 98.6
        }
    )


def create_gerd_patient() -> PatientData:
    """Create test patient with GI chest pain (GERD)"""
    from datetime import datetime
    return PatientData(
        patient_id='10002',
        hadm_id='20002',
        age=52,
        gender='F',
        chief_complaint='Chest pain, burning',
        admission_time=datetime.now(),
        icd_codes=['5301', '78650'],  # GERD, chest pain
        diagnoses=['GERD', 'Chest pain'],
        labs={
            'Troponin': [
                (datetime.now(), 0.01),  # Normal
                (datetime.now(), 0.01),  # Still normal
                (datetime.now(), 0.02)   # Normal
            ],
            'WBC': [(datetime.now(), 7.2)],
            'Hemoglobin': [(datetime.now(), 13.5)],
            'ALT': [(datetime.now(), 28)],
            'AST': [(datetime.now(), 32)]
        },
        vitals={
            'heart_rate': 76,
            'blood_pressure': 128,
            'blood_pressure_diastolic': 82,
            'respiratory_rate': 16,
            'oxygen_saturation': 98,
            'temperature': 98.2
        }
    )


def create_mixed_patient() -> PatientData:
    """
    Create patient with borderline findings (could be cardiac OR GI)
    This tests how agents collaborate
    """
    from datetime import datetime
    return PatientData(
        patient_id='10003',
        hadm_id='20003',
        age=58,
        gender='M',
        chief_complaint='Chest discomfort',
        admission_time=datetime.now(),
        icd_codes=['78650', '5301', '4019'],  # Chest pain, GERD, HTN
        diagnoses=['Chest pain', 'GERD', 'HTN'],
        labs={
            'Troponin': [
                (datetime.now(), 0.04),  # Borderline
                (datetime.now(), 0.05),  # Minimally elevated
                (datetime.now(), 0.06)   # Stable minimal elevation
            ],
            'WBC': [(datetime.now(), 8.0)],
            'Lipase': [(datetime.now(), 65)],  # Normal
            'ALT': [(datetime.now(), 35)],
            'AST': [(datetime.now(), 40)]
        },
        vitals={
            'heart_rate': 72,
            'blood_pressure': 132,
            'blood_pressure_diastolic': 84,
            'respiratory_rate': 16,
            'oxygen_saturation': 98,
            'temperature': 98.4
        }
    )


def create_pancreatitis_patient() -> PatientData:
    """Create patient with pancreatitis (high-risk GI emergency)"""
    from datetime import datetime
    return PatientData(
        patient_id='10004',
        hadm_id='20004',
        age=45,
        gender='M',
        chief_complaint='Severe epigastric pain radiating to back',
        admission_time=datetime.now(),
        icd_codes=['5770', '78650'],  # Pancreatitis, chest pain
        diagnoses=['Pancreatitis', 'Abdominal pain'],
        labs={
            'Troponin': [(datetime.now(), 0.02)],  # Normal
            'Lipase': [(datetime.now(), 850)],  # Very high (>3x ULN)
            'Amylase': [(datetime.now(), 520)],  # Elevated
            'WBC': [(datetime.now(), 14.2)],  # Elevated
            'Glucose': [(datetime.now(), 145)],
            'Calcium': [(datetime.now(), 8.2)],
            'ALT': [(datetime.now(), 180)],
            'AST': [(datetime.now(), 220)]
        },
        vitals={
            'heart_rate': 105,
            'blood_pressure': 110,
            'blood_pressure_diastolic': 70,
            'respiratory_rate': 22,
            'oxygen_saturation': 95,
            'temperature': 99.8
        }
    )


async def run_patient_analysis(orchestrator: MasterOrchestrator, patient: PatientData, case_name: str):
    """Run analysis for a single patient"""
    
    print("\n" + "="*80)
    print(f"🏥 ANALYZING: {case_name}")
    print("="*80)
    print(f"Patient ID: {patient.patient_id}")
    print(f"Age: {patient.age}  Sex: {patient.gender}")
    print(f"ICD Codes: {patient.icd_codes}")
    print(f"\nVitals:")
    print(f"  HR: {patient.vitals.get('heart_rate')} bpm")
    print(f"  BP: {patient.vitals.get('blood_pressure')}/{patient.vitals.get('blood_pressure_diastolic')}")
    print(f"  O2: {patient.vitals.get('oxygen_saturation')}%")
    
    # Show key labs
    print(f"\nKey Labs:")
    if 'Troponin' in patient.labs:
        latest_trop = patient.labs['Troponin'][-1][1]
        print(f"  Troponin: {latest_trop} ng/mL")
    if 'Lipase' in patient.labs:
        latest_lipase = patient.labs['Lipase'][-1][1]
        print(f"  Lipase: {latest_lipase} U/L")
    
    print("\n" + "-"*80)
    print("🤖 MULTI-AGENT ANALYSIS IN PROGRESS...")
    print("-"*80)
    
    # Run orchestration
    state = await orchestrator.orchestrate(patient)
    
    # DEBUG: Print raw state
    print(f"\n[DEBUG] diagnosis_results count: {len(state.diagnosis_results)}")
    print(f"[DEBUG] active_agents: {state.active_agents}")
    print(f"[DEBUG] safety_alerts: {state.safety_alerts}")
    
    print("\n" + "="*80)
    print("📊 ANALYSIS RESULTS")
    print("="*80)
    
    # Show all agent results
    print(f"\n🔍 Agents Activated: {len(state.diagnosis_results)}")
    
    for i, result in enumerate(state.diagnosis_results, 1):
        print(f"\n{i}. {result.agent_name}")
        print(f"   Diagnosis: {result.diagnosis.value}")
        print(f"   Confidence: {result.confidence:.1%}")
        print(f"   Risk Level: {result.risk_level.value}")
        print(f"   Reasoning: {result.reasoning[:150]}...")
        
        if result.children_results:
            print(f"   └─ Spawned {len(result.children_results)} child agent(s)")
            for child in result.children_results:
                print(f"      └─ {child.agent_name}: {child.diagnosis.value} ({child.confidence:.1%})")
    
    # Show top diagnosis
    if state.diagnosis_results:
        top_diagnosis = max(state.diagnosis_results, key=lambda x: (
            4 if x.risk_level.value == "CRITICAL" else
            3 if x.risk_level.value == "HIGH" else
            2 if x.risk_level.value == "MODERATE" else 1,
            x.confidence
        ))
        
        print("\n" + "="*80)
        print("🎯 FINAL DIAGNOSIS")
        print("="*80)
        print(f"Diagnosis: {top_diagnosis.diagnosis.value}")
        print(f"Confidence: {top_diagnosis.confidence:.1%}")
        print(f"Risk: {top_diagnosis.risk_level.value}")
        print(f"\nReasoning:")
        print(top_diagnosis.reasoning)
        print(f"\n📋 Recommendations:")
        for rec in top_diagnosis.recommendations:
            print(f"  • {rec}")
    
    # Show safety alerts
    if state.safety_alerts:
        print("\n" + "="*80)
        print("⚠️  SAFETY ALERTS")
        print("="*80)
        for alert in state.safety_alerts:
            print(f"  ⚠️  {alert}")
    
    print("\n" + "="*80 + "\n")
    
    return state


async def main():
    """Main demo function"""
    
    print("""
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║   MIMIQ MULTI-AGENT DIAGNOSTIC SYSTEM                        ║
║   Cardiology + Gastroenterology Integration Demo            ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
    """)
    
    # Initialize orchestrator
    orchestrator = MasterOrchestrator()
    
    # Register agents
    print("🔧 Initializing agents...")
    safety_agent = SafetyMonitorAgent()
    cardiology_agent = CardiologyAgent()
    gastro_agent = GastroenterologyAgent()
    
    orchestrator.register_agent(SpecialtyType.SAFETY, safety_agent)
    orchestrator.register_agent(SpecialtyType.CARDIOLOGY, cardiology_agent)
    orchestrator.register_agent(SpecialtyType.GASTROENTEROLOGY, gastro_agent)
    
    print("✅ Agents initialized successfully!")
    print(f"   • Safety Monitor: {safety_agent.name}")
    print(f"   • Cardiology: {cardiology_agent.name}")
    print(f"   • Gastroenterology: {gastro_agent.name}")
    
    # Test Case 1: Clear Cardiac (NSTEMI)
    patient1 = create_cardiac_patient()
    await run_patient_analysis(orchestrator, patient1, "TEST CASE 1: Cardiac Chest Pain (NSTEMI)")
    
    # Test Case 2: Clear GI (GERD)
    patient2 = create_gerd_patient()
    await run_patient_analysis(orchestrator, patient2, "TEST CASE 2: GI Chest Pain (GERD)")
    
    # Test Case 3: Mixed/Borderline
    patient3 = create_mixed_patient()
    await run_patient_analysis(orchestrator, patient3, "TEST CASE 3: Borderline Case (Cardiac vs GI)")
    
    # Test Case 4: High-Risk GI (Pancreatitis)
    patient4 = create_pancreatitis_patient()
    await run_patient_analysis(orchestrator, patient4, "TEST CASE 4: Acute Pancreatitis")
    
    print("""
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║   ✅  ALL TEST CASES COMPLETED                               ║
║                                                              ║
║   Key Insights:                                              ║
║   • Both agents analyze each patient in parallel             ║
║   • Highest risk + confidence diagnosis prioritized          ║
║   • Cardiac and GI collaborate on borderline cases           ║
║   • Safety monitor always active                             ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
    """)


if __name__ == "__main__":
    asyncio.run(main())
