"""
Triage Prioritization Agent
ESI (Emergency Severity Index) based triage with AI enhancement
"""

from typing import List, Dict, Any
from dataclasses import dataclass
from enum import Enum
from loguru import logger

from src.agents.base import FractalAgent, DiagnosisResult
from src.config import SpecialtyType, DiagnosisType, RiskLevel
from src.data_loader import PatientData


class ESILevel(Enum):
    """Emergency Severity Index Levels"""
    LEVEL_1 = 1  # Immediate - Life-threatening, requires resuscitation
    LEVEL_2 = 2  # Emergent - High risk, potentially life-threatening
    LEVEL_3 = 3  # Urgent - Stable but needs evaluation/treatment
    LEVEL_4 = 4  # Less urgent - Stable, minor problems
    LEVEL_5 = 5  # Non-urgent - Could be seen in clinic setting


@dataclass
class TriageScore:
    """Comprehensive triage assessment"""
    patient_id: int
    esi_level: ESILevel
    priority_score: float  # 0-100, higher = more urgent
    wait_time_target: str
    destination: str
    resources_needed: List[str]
    nursing_ratio: str
    monitoring_level: str
    rationale: str
    
    # Risk flags
    critical_flags: List[str]
    warning_flags: List[str]
    
    # Disposition
    recommended_disposition: str  # "Admit ICU", "Admit floor", "Observation", "Discharge"
    
    def format_triage(self) -> str:
        """Format triage assessment for display"""
        
        lines = []
        lines.append("╔" + "═"*78 + "╗")
        lines.append("║" + f"  TRIAGE ASSESSMENT - ESI Level {self.esi_level.value}".ljust(78) + "║")
        lines.append("║" + f"  Patient ID: {self.patient_id} | Priority Score: {self.priority_score:.1f}/100".ljust(78) + "║")
        lines.append("╚" + "═"*78 + "╝")
        
        # Critical Flags
        if self.critical_flags:
            lines.append("\n🚨 CRITICAL FLAGS:")
            lines.append("━" * 80)
            for flag in self.critical_flags:
                lines.append(f"  ⚠️  {flag}")
        
        # Priority Details
        lines.append(f"\n📊 PRIORITY DETAILS:")
        lines.append("━" * 80)
        lines.append(f"  ESI Level: {self.esi_level.value} - {self.esi_level.name.replace('_', ' ')}")
        lines.append(f"  Wait Time Target: {self.wait_time_target}")
        lines.append(f"  Priority Score: {self.priority_score:.1f}/100")
        
        # Disposition
        lines.append(f"\n🏥 DISPOSITION:")
        lines.append("━" * 80)
        lines.append(f"  Destination: {self.destination}")
        lines.append(f"  Recommended: {self.recommended_disposition}")
        lines.append(f"  Nursing Ratio: {self.nursing_ratio}")
        lines.append(f"  Monitoring: {self.monitoring_level}")
        
        # Resources
        if self.resources_needed:
            lines.append(f"\n🔧 RESOURCES REQUIRED:")
            lines.append("━" * 80)
            for resource in self.resources_needed:
                lines.append(f"  • {resource}")
        
        # Rationale
        lines.append(f"\n💡 RATIONALE:")
        lines.append("━" * 80)
        lines.append(f"  {self.rationale}")
        
        return "\n".join(lines)


class TriageAgent(FractalAgent):
    """
    Agent responsible for emergency triage prioritization
    Uses ESI (Emergency Severity Index) enhanced with AI
    """
    
    def __init__(self, depth: int = 0):
        super().__init__(
            specialty=SpecialtyType.TRIAGE,
            name="Triage Prioritization Agent",
            depth=depth
        )
    
    def calculate_priority(
        self,
        patient: PatientData,
        diagnosis: DiagnosisResult = None
    ) -> TriageScore:
        """
        Calculate comprehensive triage priority
        
        ESI Algorithm:
        - Level 1: Requires immediate life-saving intervention
        - Level 2: High-risk situation, confused/lethargic, severe pain/distress
        - Level 3: Needs ≥2 resources
        - Level 4: Needs 1 resource
        - Level 5: Needs 0 resources
        
        Enhanced with AI to predict resource needs and severity
        """
        
        logger.info(f"[{self.name}] Triaging patient {patient.patient_id}")
        
        # Initialize
        critical_flags = []
        warning_flags = []
        priority_score = 50.0  # Base score
        
        # Step 1: Check for immediate life-threats (ESI Level 1)
        if self._requires_immediate_intervention(patient, diagnosis):
            esi_level, rationale = self._assign_level_1(patient, diagnosis, critical_flags)
            priority_score = 100.0
        
        # Step 2: Check for high-risk situations (ESI Level 2)
        elif self._is_high_risk(patient, diagnosis):
            esi_level, rationale = self._assign_level_2(patient, diagnosis, critical_flags, warning_flags)
            priority_score = 85.0
        
        # Step 3-5: Resource-based assignment
        else:
            esi_level, rationale, priority_score = self._assign_by_resources(
                patient, diagnosis, warning_flags
            )
        
        # Calculate priority score with modifiers
        priority_score = self._calculate_priority_score(
            patient, diagnosis, esi_level, critical_flags, warning_flags
        )
        
        # Determine disposition
        destination, disposition = self._determine_disposition(
            patient, diagnosis, esi_level
        )
        
        # Determine resources needed
        resources = self._determine_resources(patient, diagnosis, esi_level)
        
        # Nursing ratio based on ESI level
        nursing_ratio = self._get_nursing_ratio(esi_level)
        
        # Monitoring level
        monitoring = self._get_monitoring_level(esi_level, diagnosis)
        
        # Wait time target
        wait_time = self._get_wait_time_target(esi_level)
        
        triage_score = TriageScore(
            patient_id=int(patient.patient_id),
            esi_level=esi_level,
            priority_score=priority_score,
            wait_time_target=wait_time,
            destination=destination,
            resources_needed=resources,
            nursing_ratio=nursing_ratio,
            monitoring_level=monitoring,
            rationale=rationale,
            critical_flags=critical_flags,
            warning_flags=warning_flags,
            recommended_disposition=disposition
        )
        
        logger.success(
            f"Triage complete: ESI Level {esi_level.value}, Priority {priority_score:.1f}"
        )
        
        return triage_score
    
    def _requires_immediate_intervention(
        self,
        patient: PatientData,
        diagnosis: DiagnosisResult = None
    ) -> bool:
        """Check if patient requires immediate life-saving intervention"""
        
        # Critical diagnoses
        if diagnosis and diagnosis.diagnosis in [
            DiagnosisType.STEMI,
            DiagnosisType.MASSIVE_PE
        ]:
            return True
        
        # Critical vitals
        if patient.vitals:
            # Severe hypotension
            if patient.vitals.get('sbp', 120) < 80:
                return True
            
            # Severe hypoxia
            if patient.vitals.get('spo2', 100) < 85:
                return True
            
            # Severe tachycardia or bradycardia
            hr = patient.vitals.get('heart_rate', 80)
            if hr < 40 or hr > 150:
                return True
        
        return False
    
    def _is_high_risk(
        self,
        patient: PatientData,
        diagnosis: DiagnosisResult = None
    ) -> bool:
        """Check if patient is in high-risk situation"""
        
        # High-risk diagnoses
        if diagnosis and diagnosis.risk_level == RiskLevel.HIGH:
            return True
        
        # High-risk vitals
        if patient.vitals:
            # Moderate hypotension
            if patient.vitals.get('sbp', 120) < 90:
                return True
            
            # Hypoxia
            if patient.vitals.get('spo2', 100) < 90:
                return True
            
            # Severe pain (chest pain with cardiac risk)
            if diagnosis and diagnosis.diagnosis in [
                DiagnosisType.NSTEMI,
                DiagnosisType.UNSTABLE_ANGINA
            ]:
                return True
        
        # Advanced age with acute symptoms
        if patient.age > 75 and diagnosis:
            return True
        
        return False
    
    def _assign_level_1(
        self,
        patient: PatientData,
        diagnosis: DiagnosisResult,
        critical_flags: List[str]
    ) -> tuple:
        """Assign ESI Level 1 (Immediate)"""
        
        critical_flags.append("IMMEDIATE LIFE-SAVING INTERVENTION REQUIRED")
        
        rationale_parts = []
        
        if diagnosis:
            if diagnosis.diagnosis == DiagnosisType.STEMI:
                critical_flags.append("STEMI - Cath lab activation required")
                rationale_parts.append("STEMI requiring emergent PCI")
            
            elif diagnosis.diagnosis == DiagnosisType.MASSIVE_PE:
                critical_flags.append("Massive PE - Consider thrombolysis")
                rationale_parts.append("Massive PE with hemodynamic instability")
        
        if patient.vitals:
            if patient.vitals.get('sbp', 120) < 80:
                critical_flags.append("Severe hypotension (SBP <80)")
                rationale_parts.append("Severe hypotension")
            
            if patient.vitals.get('spo2', 100) < 85:
                critical_flags.append("Critical hypoxia (SpO2 <85%)")
                rationale_parts.append("Critical hypoxia")
        
        rationale = f"ESI Level 1: {', '.join(rationale_parts) if rationale_parts else 'Critical condition requiring immediate intervention'}"
        
        return ESILevel.LEVEL_1, rationale
    
    def _assign_level_2(
        self,
        patient: PatientData,
        diagnosis: DiagnosisResult,
        critical_flags: List[str],
        warning_flags: List[str]
    ) -> tuple:
        """Assign ESI Level 2 (Emergent)"""
        
        rationale_parts = []
        
        if diagnosis:
            if diagnosis.diagnosis == DiagnosisType.NSTEMI:
                warning_flags.append("NSTEMI - High risk for progression")
                rationale_parts.append("NSTEMI requiring urgent cardiology evaluation")
            
            elif diagnosis.diagnosis == DiagnosisType.UNSTABLE_ANGINA:
                warning_flags.append("Unstable Angina - Monitor for MI")
                rationale_parts.append("Unstable angina with high-risk features")
            
            if diagnosis.risk_level == RiskLevel.HIGH:
                warning_flags.append("High-risk diagnosis")
                rationale_parts.append("High-risk condition")
        
        if patient.vitals:
            if patient.vitals.get('sbp', 120) < 90:
                warning_flags.append("Hypotension (SBP <90)")
                rationale_parts.append("Hypotension")
            
            if patient.vitals.get('spo2', 100) < 90:
                warning_flags.append("Hypoxia (SpO2 <90%)")
                rationale_parts.append("Hypoxia")
        
        if patient.age > 75:
            warning_flags.append("Geriatric patient with acute symptoms")
            rationale_parts.append("Advanced age with acute presentation")
        
        rationale = f"ESI Level 2: {', '.join(rationale_parts) if rationale_parts else 'High-risk situation requiring prompt evaluation'}"
        
        return ESILevel.LEVEL_2, rationale
    
    def _assign_by_resources(
        self,
        patient: PatientData,
        diagnosis: DiagnosisResult,
        warning_flags: List[str]
    ) -> tuple:
        """Assign ESI Level 3-5 based on resource needs"""
        
        # Predict resource needs
        resources_needed = self._determine_resources(patient, diagnosis, None)
        resource_count = len(resources_needed)
        
        if resource_count >= 2:
            # ESI Level 3: ≥2 resources
            rationale = f"ESI Level 3: Requires {resource_count} resources (stable but needs workup)"
            priority_score = 60.0
            return ESILevel.LEVEL_3, rationale, priority_score
        
        elif resource_count == 1:
            # ESI Level 4: 1 resource
            rationale = "ESI Level 4: Requires 1 resource (stable, minor intervention)"
            priority_score = 40.0
            return ESILevel.LEVEL_4, rationale, priority_score
        
        else:
            # ESI Level 5: 0 resources
            rationale = "ESI Level 5: No resources needed (could be seen in clinic)"
            priority_score = 20.0
            return ESILevel.LEVEL_5, rationale, priority_score
    
    def _determine_resources(
        self,
        patient: PatientData,
        diagnosis: DiagnosisResult,
        esi_level: ESILevel = None
    ) -> List[str]:
        """Determine resources needed"""
        
        resources = []
        
        # Diagnostic resources
        if diagnosis or patient.presenting_complaint == "chest pain":
            resources.extend([
                "12-lead ECG",
                "Cardiac biomarkers (troponin, BNP)",
                "Basic metabolic panel"
            ])
        
        # Level-specific resources
        if esi_level == ESILevel.LEVEL_1:
            resources.extend([
                "STAT Cardiology consultation",
                "Cath lab activation",
                "ICU bed",
                "Continuous hemodynamic monitoring",
                "Arterial line",
                "Two large-bore IV lines"
            ])
        
        elif esi_level == ESILevel.LEVEL_2:
            resources.extend([
                "Continuous telemetry monitoring",
                "Serial troponins",
                "Cardiology consultation (urgent)",
                "Chest X-ray",
                "Possible echocardiogram"
            ])
        
        elif esi_level == ESILevel.LEVEL_3:
            resources.extend([
                "Telemetry monitoring",
                "Basic labs",
                "Imaging as indicated"
            ])
        
        return list(set(resources))  # Remove duplicates
    
    def _calculate_priority_score(
        self,
        patient: PatientData,
        diagnosis: DiagnosisResult,
        esi_level: ESILevel,
        critical_flags: List[str],
        warning_flags: List[str]
    ) -> float:
        """Calculate refined priority score (0-100)"""
        
        # Base score from ESI level
        base_scores = {
            ESILevel.LEVEL_1: 100.0,
            ESILevel.LEVEL_2: 85.0,
            ESILevel.LEVEL_3: 60.0,
            ESILevel.LEVEL_4: 40.0,
            ESILevel.LEVEL_5: 20.0
        }
        
        score = base_scores[esi_level]
        
        # Modifiers
        
        # Age modifier (elderly = higher priority)
        if patient.age > 75:
            score += 5.0
        elif patient.age > 65:
            score += 2.0
        
        # Critical flags
        score += len(critical_flags) * 10.0
        
        # Warning flags
        score += len(warning_flags) * 5.0
        
        # Diagnosis confidence modifier
        if diagnosis and diagnosis.confidence > 0.8:
            score += 3.0
        
        # Cap at 100
        return min(score, 100.0)
    
    def _determine_disposition(
        self,
        patient: PatientData,
        diagnosis: DiagnosisResult,
        esi_level: ESILevel
    ) -> tuple:
        """Determine destination and recommended disposition"""
        
        if esi_level == ESILevel.LEVEL_1:
            destination = "Resuscitation Bay → ICU/Cath Lab"
            disposition = "Admit ICU (likely post-PCI)"
        
        elif esi_level == ESILevel.LEVEL_2:
            destination = "ED Bed with Telemetry"
            if diagnosis and diagnosis.diagnosis in [DiagnosisType.NSTEMI, DiagnosisType.UNSTABLE_ANGINA]:
                disposition = "Admit Telemetry Floor (likely)"
            else:
                disposition = "Admit vs Observation (pending workup)"
        
        elif esi_level == ESILevel.LEVEL_3:
            destination = "ED Bed"
            disposition = "Observation vs Discharge (pending results)"
        
        elif esi_level == ESILevel.LEVEL_4:
            destination = "ED Chair/Fast Track"
            disposition = "Likely discharge"
        
        else:  # Level 5
            destination = "Waiting Area → Fast Track"
            disposition = "Discharge"
        
        return destination, disposition
    
    def _get_nursing_ratio(self, esi_level: ESILevel) -> str:
        """Get recommended nurse-to-patient ratio"""
        ratios = {
            ESILevel.LEVEL_1: "1:1 (dedicated nurse)",
            ESILevel.LEVEL_2: "1:2-3",
            ESILevel.LEVEL_3: "1:4",
            ESILevel.LEVEL_4: "1:5-6",
            ESILevel.LEVEL_5: "1:6+"
        }
        return ratios[esi_level]
    
    def _get_monitoring_level(
        self,
        esi_level: ESILevel,
        diagnosis: DiagnosisResult = None
    ) -> str:
        """Get recommended monitoring level"""
        
        if esi_level == ESILevel.LEVEL_1:
            return "Continuous telemetry + invasive hemodynamic monitoring"
        elif esi_level == ESILevel.LEVEL_2:
            return "Continuous telemetry + frequent vitals (q15-30min)"
        elif esi_level == ESILevel.LEVEL_3:
            return "Intermittent telemetry + vitals q1-2h"
        elif esi_level == ESILevel.LEVEL_4:
            return "Vitals q2-4h"
        else:
            return "Vitals on arrival and discharge"
    
    def _get_wait_time_target(self, esi_level: ESILevel) -> str:
        """Get wait time target per ESI guidelines"""
        targets = {
            ESILevel.LEVEL_1: "0 minutes (immediate)",
            ESILevel.LEVEL_2: "<10 minutes",
            ESILevel.LEVEL_3: "10-60 minutes",
            ESILevel.LEVEL_4: "1-2 hours",
            ESILevel.LEVEL_5: "2-24 hours"
        }
        return targets[esi_level]
    
    def analyze(self, patient_data: PatientData, context: Dict = None) -> Dict:
        """Analyze patient for triage prioritization"""
        
        diagnosis = context.get('diagnosis') if context else None
        
        triage_score = self.calculate_priority(patient_data, diagnosis)
        
        return {
            'agent': self.name,
            'triage_score': triage_score,
            'confidence': 1.0  # Triage follows established protocols
        }
    
    # Abstract method implementations (Triage agent doesn't spawn children)
    def _identify_subspecialties(self, patient_data: Any) -> List[str]:
        """Triage agent doesn't identify subspecialties"""
        return []
    
    def _generate_hypotheses(self, patient_data: Any) -> List[str]:
        """Triage agent assigns priority, not hypotheses"""
        return []
    
    def _create_child_agent(self, subspecialty: str) -> 'FractalAgent':
        """Triage agent doesn't create children"""
        return None
    
    def _synthesize_results(self, child_results: List[Dict]) -> Dict:
        """Triage agent doesn't synthesize (no children)"""
        return {}


# Example usage
if __name__ == "__main__":
    from src.data_loader import MIMICDataLoader
    
    # Load patient
    loader = MIMICDataLoader()
    loader.load_all()
    patients = loader.filter_chest_pain_patients()
    
    if patients:
        patient = loader.get_patient_data(patients[0])
        
        # Simulate high-risk diagnosis
        diagnosis = DiagnosisResult(
            diagnosis=DiagnosisType.NSTEMI,
            confidence=0.85,
            risk_level=RiskLevel.HIGH,
            reasoning="Elevated troponin with rising trend",
            supporting_evidence={'troponin': 0.3}
        )
        
        # Triage
        triage_agent = TriageAgent()
        score = triage_agent.calculate_priority(patient, diagnosis)
        
        print(score.format_triage())
