"""
Treatment Recommendation Agent
Generates comprehensive treatment plans with medications, monitoring, and follow-up
"""

from typing import List, Dict, Any
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from loguru import logger

from src.agents.base import FractalAgent, DiagnosisResult
from src.agents.knowledge import MedicalKnowledgeAgent
from src.config import SpecialtyType, DiagnosisType, RiskLevel
from src.data_loader import PatientData


@dataclass
class Medication:
    """Single medication with dosing instructions"""
    name: str
    dose: str
    frequency: str
    route: str = "PO"  # PO, IV, SQ, etc.
    duration: str = "ongoing"
    rationale: str = ""
    evidence: str = ""
    contraindications: List[str] = field(default_factory=list)
    monitoring: List[str] = field(default_factory=list)
    
    def __str__(self):
        return f"{self.name} {self.dose} {self.route} {self.frequency}"


@dataclass
class TreatmentPlan:
    """Comprehensive treatment plan"""
    diagnosis: DiagnosisResult
    patient_id: int
    created_at: datetime = field(default_factory=datetime.now)
    
    # Immediate actions
    immediate_actions: List[str] = field(default_factory=list)
    
    # Medications
    medications: List[Medication] = field(default_factory=list)
    
    # Monitoring plan
    monitoring_plan: Dict[str, List[str]] = field(default_factory=dict)
    
    # Follow-up schedule
    followup_schedule: List[Dict] = field(default_factory=list)
    
    # Patient education
    patient_education: Dict[str, List[str]] = field(default_factory=dict)
    
    # Evidence base
    evidence_citations: List[str] = field(default_factory=list)
    
    def format_plan(self) -> str:
        """Format treatment plan for display"""
        
        lines = []
        lines.append("╔" + "═"*78 + "╗")
        lines.append("║" + f"  TREATMENT PLAN - {self.diagnosis.diagnosis}".ljust(78) + "║")
        lines.append("║" + f"  Patient ID: {self.patient_id} | Risk: {self.diagnosis.risk_level}".ljust(78) + "║")
        lines.append("╚" + "═"*78 + "╝")
        
        # Immediate Actions
        if self.immediate_actions:
            lines.append("\n🚨 IMMEDIATE ACTIONS (within 1 hour):")
            lines.append("━" * 80)
            for action in self.immediate_actions:
                lines.append(f"  ✓ {action}")
        
        # Medications
        if self.medications:
            lines.append("\n💊 ONGOING MEDICATIONS:")
            lines.append("━" * 80)
            for i, med in enumerate(self.medications, 1):
                lines.append(f"  {i}. {med.name} {med.dose} {med.route} {med.frequency}")
                if med.rationale:
                    lines.append(f"     └─ Rationale: {med.rationale}")
                if med.evidence:
                    lines.append(f"     └─ Evidence: {med.evidence}")
                if med.duration != "ongoing":
                    lines.append(f"     └─ Duration: {med.duration}")
                if med.monitoring:
                    lines.append(f"     └─ Monitoring: {', '.join(med.monitoring)}")
                lines.append("")
        
        # Monitoring Plan
        if self.monitoring_plan:
            lines.append("📊 MONITORING PLAN:")
            lines.append("━" * 80)
            for timeframe, items in self.monitoring_plan.items():
                lines.append(f"  {timeframe}:")
                for item in items:
                    lines.append(f"    • {item}")
                lines.append("")
        
        # Follow-up
        if self.followup_schedule:
            lines.append("📅 FOLLOW-UP SCHEDULE:")
            lines.append("━" * 80)
            for followup in self.followup_schedule:
                lines.append(f"  {followup['timeframe']}: {followup['provider']} - {followup['purpose']}")
        
        # Patient Education
        if self.patient_education:
            lines.append("\n📚 PATIENT EDUCATION:")
            lines.append("━" * 80)
            for category, items in self.patient_education.items():
                lines.append(f"  {category}:")
                for item in items:
                    lines.append(f"    • {item}")
                lines.append("")
        
        # Evidence
        if self.evidence_citations:
            lines.append("📖 EVIDENCE BASE:")
            lines.append("━" * 80)
            for citation in self.evidence_citations:
                lines.append(f"  • {citation}")
        
        return "\n".join(lines)


class TreatmentAgent(FractalAgent):
    """
    Agent responsible for generating comprehensive treatment plans
    based on diagnosis and patient characteristics
    """
    
    def __init__(self, depth: int = 0):
        super().__init__(
            specialty=SpecialtyType.TREATMENT,
            name="Treatment Planning Agent",
            depth=depth
        )
        self.knowledge_agent = MedicalKnowledgeAgent()
    
    def recommend_treatment(
        self,
        diagnosis: DiagnosisResult,
        patient: PatientData
    ) -> TreatmentPlan:
        """
        Generate comprehensive treatment plan
        
        Args:
            diagnosis: Diagnostic result from specialist agent
            patient: Patient data including demographics, labs, vitals
        
        Returns:
            Complete treatment plan with medications, monitoring, follow-up
        """
        
        logger.info(f"[{self.name}] Generating treatment plan for {diagnosis.diagnosis}")
        
        # Get evidence-based guideline
        guideline = self.knowledge_agent.get_clinical_guideline(diagnosis.diagnosis)
        
        # Initialize treatment plan
        plan = TreatmentPlan(
            diagnosis=diagnosis,
            patient_id=int(patient.patient_id)
        )
        
        # Check for contraindications
        contraindications = self._check_contraindications(patient)
        
        # Generate components based on diagnosis
        plan.immediate_actions = self._generate_immediate_actions(
            diagnosis, patient, guideline
        )
        
        plan.medications = self._prescribe_medications(
            diagnosis, patient, guideline, contraindications
        )
        
        plan.monitoring_plan = self._create_monitoring_plan(
            diagnosis, patient, guideline
        )
        
        plan.followup_schedule = self._create_followup_schedule(
            diagnosis, patient
        )
        
        plan.patient_education = self._create_patient_education(
            diagnosis, patient
        )
        
        plan.evidence_citations = [
            guideline.source,
            f"Evidence Grade: {guideline.evidence_grade}"
        ]
        
        logger.success(f"Treatment plan generated with {len(plan.medications)} medications")
        
        return plan
    
    def _check_contraindications(self, patient: PatientData) -> List[str]:
        """Check for medication contraindications"""
        contraindications = []
        
        # Check age
        if patient.age > 75:
            contraindications.append("advanced_age")
        
        # Check renal function (if creatinine available)
        if patient.labs and patient.labs.get('creatinine', 0) > 2.0:
            contraindications.append("renal_impairment")
        
        # Check platelets
        if patient.labs and patient.labs.get('platelets', 200) < 50:
            contraindications.append("severe_thrombocytopenia")
        
        # Check blood pressure
        if patient.vitals and patient.vitals.get('sbp', 120) < 90:
            contraindications.append("hypotension")
        
        return contraindications
    
    def _generate_immediate_actions(
        self,
        diagnosis: DiagnosisResult,
        patient: PatientData,
        guideline: Any
    ) -> List[str]:
        """Generate time-critical interventions"""
        
        actions = []
        
        if diagnosis.diagnosis == DiagnosisType.STEMI:
            actions.extend([
                "🚨 ACTIVATE CATH LAB IMMEDIATELY (Door-to-balloon goal: <90 min)",
                "Aspirin 325mg PO (chewed) - give immediately",
                "Ticagrelor 180mg PO loading dose",
                "Heparin 60 units/kg IV bolus (max 4000 units)",
                "Morphine 2-4mg IV PRN for chest pain",
                "Oxygen if SpO2 <90%",
                "Continuous ECG monitoring",
                "Two large-bore IV lines"
            ])
        
        elif diagnosis.diagnosis == DiagnosisType.NSTEMI:
            actions.extend([
                "Aspirin 325mg PO immediately (unless contraindicated)",
                "Ticagrelor 180mg PO loading dose OR Clopidogrel 600mg",
                "Heparin 60 units/kg IV bolus (max 4000 units) → infusion 12 units/kg/hr",
                "Beta-blocker: Metoprolol 25-50mg PO (if SBP >100, HR >60)",
                "High-intensity statin: Atorvastatin 80mg PO",
                "Sublingual nitroglycerin 0.4mg q5min x3 PRN chest pain",
                "Continuous telemetry monitoring",
                "Cardiology consultation STAT"
            ])
        
        elif diagnosis.diagnosis == DiagnosisType.UNSTABLE_ANGINA:
            actions.extend([
                "Aspirin 325mg PO",
                "Sublingual nitroglycerin 0.4mg PRN chest pain",
                "Beta-blocker: Metoprolol 25mg PO",
                "Telemetry monitoring",
                "Serial troponins q3h x 2 (to rule out MI)",
                "Cardiology consultation"
            ])
        
        elif diagnosis.diagnosis == DiagnosisType.MASSIVE_PE:
            actions.extend([
                "🚨 CRITICAL - Consider systemic thrombolysis",
                "Alteplase 100mg IV over 2 hours (if no contraindications)",
                "Heparin 80 units/kg IV bolus → 18 units/kg/hr infusion",
                "Oxygen to maintain SpO2 >90%",
                "Hemodynamic monitoring (consider ICU)",
                "Pulmonology/Interventional Radiology consultation STAT"
            ])
        
        return actions
    
    def _prescribe_medications(
        self,
        diagnosis: DiagnosisResult,
        patient: PatientData,
        guideline: Any,
        contraindications: List[str]
    ) -> List[Medication]:
        """Generate ongoing medication regimen"""
        
        medications = []
        
        # ACS medications (STEMI, NSTEMI, Unstable Angina)
        if diagnosis.diagnosis in [DiagnosisType.STEMI, DiagnosisType.NSTEMI, DiagnosisType.UNSTABLE_ANGINA]:
            
            # Aspirin
            if "aspirin_allergy" not in contraindications:
                medications.append(Medication(
                    name="Aspirin",
                    dose="81mg",
                    frequency="daily",
                    route="PO",
                    duration="indefinite",
                    rationale="Antiplatelet therapy for secondary prevention of MI",
                    evidence="Class I, Level A recommendation (ACC/AHA)",
                    monitoring=["GI symptoms", "bleeding"]
                ))
            
            # P2Y12 inhibitor
            medications.append(Medication(
                name="Ticagrelor",
                dose="90mg",
                frequency="BID",
                route="PO",
                duration="12 months minimum",
                rationale="Superior to clopidogrel in reducing MACE (PLATO trial: 16% reduction)",
                evidence="PMID: 20816798 - PLATO trial",
                contraindications=["active bleeding", "intracranial hemorrhage history"],
                monitoring=["bleeding", "dyspnea (common side effect)"]
            ))
            
            # Statin
            if "severe_liver_disease" not in contraindications:
                medications.append(Medication(
                    name="Atorvastatin",
                    dose="80mg",
                    frequency="daily at bedtime",
                    route="PO",
                    duration="indefinite",
                    rationale="High-intensity statin for plaque stabilization and LDL reduction",
                    evidence="PROVE-IT TIMI 22 trial - intensive statin superior to moderate",
                    monitoring=["LFTs at baseline and 12 weeks", "Lipid panel q3 months", "Myalgias"]
                ))
            
            # Beta-blocker
            if "asthma" not in contraindications and "hypotension" not in contraindications:
                medications.append(Medication(
                    name="Metoprolol succinate",
                    dose="25mg (titrate to 200mg)",
                    frequency="daily",
                    route="PO",
                    duration="indefinite",
                    rationale="Reduces recurrent MI and mortality post-ACS",
                    evidence="Class I recommendation - multiple RCTs",
                    monitoring=["HR (target 60-70)", "BP", "Signs of HF decompensation"]
                ))
            
            # ACE inhibitor (if LV dysfunction or diabetes)
            if patient.age < 75 or "renal_impairment" not in contraindications:
                medications.append(Medication(
                    name="Lisinopril",
                    dose="2.5mg (titrate to 10mg)",
                    frequency="daily",
                    route="PO",
                    duration="indefinite",
                    rationale="Reduces remodeling post-MI, especially if LVEF <40%",
                    evidence="HOPE, EUROPA, PEACE trials",
                    contraindications=["pregnancy", "bilateral renal artery stenosis", "angioedema history"],
                    monitoring=["K+ and Cr at 1-2 weeks", "BP", "Cough"]
                ))
        
        # PE anticoagulation
        elif diagnosis.diagnosis in [DiagnosisType.MASSIVE_PE, DiagnosisType.PE]:
            medications.append(Medication(
                name="Apixaban",
                dose="10mg BID x 7 days, then 5mg BID",
                frequency="BID → then BID",
                route="PO",
                duration="3-6 months (reassess)",
                rationale="Direct oral anticoagulant for PE treatment",
                evidence="AMPLIFY trial - non-inferior to warfarin with less bleeding",
                contraindications=["active bleeding", "severe renal impairment (CrCl <15)"],
                monitoring=["Bleeding symptoms", "Renal function q3-6 months"]
            ))
        
        return medications
    
    def _create_monitoring_plan(
        self,
        diagnosis: DiagnosisResult,
        patient: PatientData,
        guideline: Any
    ) -> Dict[str, List[str]]:
        """Create monitoring schedule"""
        
        plan = {}
        
        if diagnosis.diagnosis in [DiagnosisType.STEMI, DiagnosisType.NSTEMI]:
            plan["Immediate (First 24 hours)"] = [
                "Continuous ECG telemetry monitoring",
                "Serial troponins q3-6h until plateau/decline",
                "Vital signs q1h x 4, then q4h if stable",
                "Oxygen saturation continuous monitoring",
                "Strict I/O monitoring"
            ]
            
            plan["Daily (During Admission)"] = [
                "12-lead ECG daily",
                "Basic metabolic panel (assess renal function for medication dosing)",
                "CBC (monitor for bleeding)",
                "Lipid panel (fasting) - assess statin need",
                "HbA1c (screen for diabetes)",
                "Echocardiogram (assess LV function, wall motion abnormalities)"
            ]
            
            plan["Pre-Discharge"] = [
                "Lipid panel confirmed",
                "Echocardiogram completed",
                "Cardiac rehabilitation referral",
                "Medication reconciliation",
                "Education on warning signs"
            ]
            
            plan["Outpatient Follow-up"] = [
                "Week 1: Cardiology clinic visit",
                "Week 4: Primary care - medication review",
                "Month 3: Cardiology + lipid panel (assess statin efficacy)",
                "Month 6: Cardiology + repeat echo if initial LVEF abnormal",
                "Month 12: Consider stress test for risk stratification"
            ]
        
        return plan
    
    def _create_followup_schedule(
        self,
        diagnosis: DiagnosisResult,
        patient: PatientData
    ) -> List[Dict]:
        """Create follow-up appointment schedule"""
        
        schedule = []
        
        if diagnosis.diagnosis in [DiagnosisType.STEMI, DiagnosisType.NSTEMI]:
            schedule = [
                {
                    'timeframe': 'Week 1',
                    'provider': 'Cardiology',
                    'purpose': 'Post-discharge check, medication review'
                },
                {
                    'timeframe': 'Week 4',
                    'provider': 'Primary Care',
                    'purpose': 'Medication reconciliation, lifestyle counseling'
                },
                {
                    'timeframe': 'Month 3',
                    'provider': 'Cardiology',
                    'purpose': 'Lipid panel review, titrate medications'
                },
                {
                    'timeframe': 'Month 6',
                    'provider': 'Cardiology',
                    'purpose': 'Repeat echo if indicated, assess cardiac rehab progress'
                },
                {
                    'timeframe': 'Month 12',
                    'provider': 'Cardiology',
                    'purpose': 'Annual review, consider stress test'
                }
            ]
        
        return schedule
    
    def _create_patient_education(
        self,
        diagnosis: DiagnosisResult,
        patient: PatientData
    ) -> Dict[str, List[str]]:
        """Generate patient education materials"""
        
        education = {}
        
        if diagnosis.diagnosis in [DiagnosisType.STEMI, DiagnosisType.NSTEMI]:
            education["Warning Signs - When to Call 911"] = [
                "🚨 Chest pain that returns or worsens",
                "🚨 Severe shortness of breath",
                "🚨 Fainting or severe dizziness",
                "🚨 Rapid or irregular heartbeat with symptoms"
            ]
            
            education["Medication Adherence"] = [
                "⚠️  NEVER stop aspirin or ticagrelor without discussing with cardiologist",
                "Stopping antiplatelet therapy early increases risk of stent thrombosis (can be fatal)",
                "Take atorvastatin at bedtime for best effect",
                "If you miss a dose, take it as soon as you remember (unless almost time for next dose)"
            ]
            
            education["Lifestyle Modifications"] = [
                "🚭 Smoking cessation is CRITICAL - increases heart attack risk 2-4x",
                "Referral to smoking cessation program provided",
                "🥗 Heart-healthy diet: Mediterranean diet recommended",
                "Reduce sodium <2000mg/day",
                "Increase fruits, vegetables, whole grains, fish",
                "🏃 Exercise: Cardiac rehabilitation strongly recommended (improves outcomes 25%)",
                "Start with walking 10-15 min daily, gradually increase",
                "Avoid strenuous activity for 2-4 weeks post-MI"
            ]
            
            education["Cardiac Rehabilitation"] = [
                "Supervised exercise program - STRONGLY RECOMMENDED",
                "Reduces mortality by 25% after heart attack",
                "Most insurance covers 36 sessions",
                "Enrollment information provided at discharge"
            ]
        
        return education
    
    def analyze(self, patient_data: PatientData, context: Dict = None) -> Dict:
        """
        Analyze patient and generate treatment plan
        Typically called after diagnosis is established
        """
        
        # Need diagnosis from context
        diagnosis = context.get('diagnosis') if context else None
        
        if not diagnosis:
            return {
                'agent': self.name,
                'error': 'No diagnosis provided - treatment agent requires diagnosis'
            }
        
        # Generate treatment plan
        treatment_plan = self.recommend_treatment(diagnosis, patient_data)
        
        return {
            'agent': self.name,
            'treatment_plan': treatment_plan,
            'confidence': 1.0  # Treatment follows evidence-based guidelines
        }
    
    # Abstract method implementations (Treatment agent doesn't spawn children)
    def _identify_subspecialties(self, patient_data: Any) -> List[str]:
        """Treatment agent doesn't identify subspecialties"""
        return []
    
    def _generate_hypotheses(self, patient_data: Any) -> List[str]:
        """Treatment agent provides treatment, not hypotheses"""
        return []
    
    def _create_child_agent(self, subspecialty: str) -> 'FractalAgent':
        """Treatment agent doesn't create children"""
        return None
    
    def _synthesize_results(self, child_results: List[Dict]) -> Dict:
        """Treatment agent doesn't synthesize (no children)"""
        return {}


# Example usage
if __name__ == "__main__":
    from src.data_loader import MIMICDataLoader
    
    # Load patient data
    loader = MIMICDataLoader()
    loader.load_all()
    patients = loader.filter_chest_pain_patients()
    
    if patients:
        patient = loader.get_patient_data(patients[0])
        
        # Simulate diagnosis
        diagnosis = DiagnosisResult(
            diagnosis=DiagnosisType.NSTEMI,
            confidence=0.85,
            risk_level=RiskLevel.HIGH,
            reasoning="Elevated troponin 0.3 ng/mL with rising trend, HEART score 6",
            supporting_evidence={'troponin': 0.3, 'heart_score': 6}
        )
        
        # Generate treatment plan
        treatment_agent = TreatmentAgent()
        plan = treatment_agent.recommend_treatment(diagnosis, patient)
        
        # Display
        print(plan.format_plan())
