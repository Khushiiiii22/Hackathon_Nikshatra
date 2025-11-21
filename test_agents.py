"""Quick test of all new features"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from src.data_loader import MIMICDataLoader
from src.agents.knowledge import MedicalKnowledgeAgent
from src.agents.treatment import TreatmentAgent
from src.agents.triage import TriageAgent
from src.agents.base import DiagnosisResult
from src.config import DiagnosisType, RiskLevel

print("🧪 Testing new agents...")

# Load data
loader = MIMICDataLoader()
loader.load_all()
patients = loader.filter_chest_pain_patients()
patient = loader.get_patient_data(patients[0])

print(f"\n✅ Loaded patient {patient.patient_id} (Age: {patient.age}, Gender: {patient.gender})")

# Test Knowledge Agent
print("\n📚 Testing Knowledge Agent...")
knowledge = MedicalKnowledgeAgent()
guideline = knowledge.get_clinical_guideline(DiagnosisType.NSTEMI)
print(f"✅ Retrieved guideline: {guideline.source}")
print(f"   Evidence Grade: {guideline.evidence_grade}")
print(f"   First-line: {guideline.first_line_therapy[0]}")

# Test Treatment Agent
print("\n💊 Testing Treatment Agent...")
treatment = TreatmentAgent()
diagnosis = DiagnosisResult(
    diagnosis=DiagnosisType.NSTEMI,
    confidence=0.85,
    risk_level=RiskLevel.HIGH,
    reasoning="Test diagnosis with elevated troponin",
    recommendations=["Serial troponins", "Cardiology consult"],
    supporting_evidence={'troponin': 0.3, 'heart_score': 6},
    agent_name="Test Agent",
    depth=0
)
plan = treatment.recommend_treatment(diagnosis, patient)
print(f"✅ Generated treatment plan")
print(f"   Immediate actions: {len(plan.immediate_actions)}")
print(f"   Medications: {len(plan.medications)}")
print(f"   First action: {plan.immediate_actions[0]}")

# Test Triage Agent
print("\n🏥 Testing Triage Agent...")
triage = TriageAgent()
score = triage.calculate_priority(patient, diagnosis)
print(f"✅ Calculated triage priority")
print(f"   ESI Level: {score.esi_level.value}")
print(f"   Priority Score: {score.priority_score:.1f}/100")
print(f"   Destination: {score.destination}")

print("\n✅ ✅ ✅ ALL AGENTS WORKING! ✅ ✅ ✅")
