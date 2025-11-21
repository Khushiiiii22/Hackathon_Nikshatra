"""
Cardiology specialty agent with sub-agents for ACS, STEMI, NSTEMI
"""

from typing import List, Optional, Dict, Any
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from config import (
    SpecialtyType, DiagnosisType, RiskLevel,
    HEART_SCORE_HISTORY, HEART_SCORE_EKG, HEART_SCORE_AGE,
    HEART_SCORE_RISK_FACTORS, HEART_SCORE_TROPONIN,
    TROPONIN_NORMAL, TROPONIN_ELEVATED, TROPONIN_HIGH
)
from data_loader import PatientData, calculate_troponin_trend
from agents.base import FractalAgent, DiagnosisResult
from loguru import logger


class CardiologyAgent(FractalAgent):
    """Main cardiology agent - can spawn ACS, HF, Pericarditis sub-agents"""
    
    def __init__(self, depth: int = 0):
        super().__init__(
            specialty=SpecialtyType.CARDIOLOGY,
            name="Cardiology Agent",
            depth=depth
        )
    
    async def _generate_hypotheses(self, patient_data: PatientData) -> List[DiagnosisResult]:
        """Generate cardiac differential diagnoses"""
        hypotheses = []
        
        # Get troponin values
        troponin_values = patient_data.labs.get('Troponin', [])
        latest_troponin = troponin_values[-1][1] if troponin_values else 0.04
        
        # Check for ACS (acute coronary syndrome)
        if latest_troponin >= TROPONIN_ELEVATED:
            acs_hypothesis = DiagnosisResult(
                diagnosis=DiagnosisType.NSTEMI,
                confidence=0.7 if latest_troponin >= TROPONIN_HIGH else 0.5,
                reasoning=f"Elevated troponin ({latest_troponin} ng/mL) suggests myocardial injury",
                risk_level=RiskLevel.HIGH,
                recommendations=[
                    "Serial troponins",
                    "EKG monitoring",
                    "Cardiology consult",
                    "Consider cath lab"
                ],
                supporting_evidence={
                    "troponin": latest_troponin,
                    "trend": calculate_troponin_trend(troponin_values)
                },
                agent_name=self.name,
                depth=self.depth
            )
            hypotheses.append(acs_hypothesis)
        else:
            # Consider stable angina or non-cardiac
            angina_hypothesis = DiagnosisResult(
                diagnosis=DiagnosisType.STABLE_ANGINA,
                confidence=0.3,
                reasoning="Normal troponin but chest pain warrants evaluation",
                risk_level=RiskLevel.MODERATE,
                recommendations=[
                    "Stress test",
                    "Outpatient cardiology follow-up"
                ],
                supporting_evidence={"troponin": latest_troponin},
                agent_name=self.name,
                depth=self.depth
            )
            hypotheses.append(angina_hypothesis)
        
        return hypotheses
    
    async def _identify_subspecialties(self, hypotheses: List[DiagnosisResult]) -> List[str]:
        """Determine if we need ACS sub-agent"""
        subspecialties = []
        
        for hyp in hypotheses:
            if hyp.diagnosis in [DiagnosisType.NSTEMI, DiagnosisType.UNSTABLE_ANGINA]:
                if hyp.confidence < 0.85:  # Uncertainty threshold
                    subspecialties.append("ACS")
                    break
        
        return subspecialties
    
    def _create_child_agent(self, subspecialty_name: str) -> Optional[FractalAgent]:
        """Create ACS sub-agent"""
        if subspecialty_name == "ACS":
            return ACSAgent(depth=self.depth + 1)
        return None
    
    async def _synthesize_results(
        self,
        hypotheses: List[DiagnosisResult],
        children_results: List[DiagnosisResult],
        patient_data: PatientData
    ) -> DiagnosisResult:
        """Combine parent and children diagnoses"""
        
        # If children provided high-confidence results, use those
        if children_results:
            best_child = max(children_results, key=lambda x: x.confidence)
            if best_child.confidence > 0.8:
                return best_child
        
        # Otherwise, use best parent hypothesis
        if hypotheses:
            best_hypothesis = max(hypotheses, key=lambda x: x.confidence)
            return best_hypothesis
        
        # Fallback
        return DiagnosisResult(
            diagnosis=DiagnosisType.UNKNOWN,
            confidence=0.1,
            reasoning="Insufficient data for cardiac diagnosis",
            risk_level=RiskLevel.MODERATE,
            recommendations=["Further evaluation needed"],
            supporting_evidence={},
            agent_name=self.name,
            depth=self.depth
        )


class ACSAgent(FractalAgent):
    """
    Acute Coronary Syndrome sub-agent
    Can spawn STEMI or NSTEMI agents
    """
    
    def __init__(self, depth: int = 1):
        super().__init__(
            specialty=SpecialtyType.CARDIOLOGY,
            name="ACS Agent",
            depth=depth
        )
    
    async def _generate_hypotheses(self, patient_data: PatientData) -> List[DiagnosisResult]:
        """Differentiate between STEMI, NSTEMI, and unstable angina"""
        hypotheses = []
        
        # Calculate HEART score
        heart_score = self._calculate_heart_score(patient_data)
        
        troponin_values = patient_data.labs.get('Troponin', [])
        latest_troponin = troponin_values[-1][1] if troponin_values else 0.04
        troponin_trend = calculate_troponin_trend(troponin_values)
        
        # NSTEMI: Elevated troponin without ST elevation
        if latest_troponin >= TROPONIN_ELEVATED:
            nstemi_confidence = 0.85 if troponin_trend == "rising" else 0.7
            
            nstemi_hypothesis = DiagnosisResult(
                diagnosis=DiagnosisType.NSTEMI,
                confidence=nstemi_confidence,
                reasoning=f"HEART score: {heart_score}, Troponin: {latest_troponin} ({troponin_trend})",
                risk_level=RiskLevel.HIGH if heart_score >= 7 else RiskLevel.MODERATE,
                recommendations=[
                    "Admit to cardiology",
                    "Serial troponins q3h",
                    "Aspirin + P2Y12 inhibitor",
                    "Heparin",
                    "Consider early cath (<24hr)" if heart_score >= 7 else "Consider delayed cath (<72hr)"
                ],
                supporting_evidence={
                    "heart_score": heart_score,
                    "troponin": latest_troponin,
                    "troponin_trend": troponin_trend
                },
                agent_name=self.name,
                depth=self.depth
            )
            hypotheses.append(nstemi_hypothesis)
        else:
            # Unstable angina
            ua_hypothesis = DiagnosisResult(
                diagnosis=DiagnosisType.UNSTABLE_ANGINA,
                confidence=0.6,
                reasoning=f"HEART score: {heart_score}, Normal troponin",
                risk_level=RiskLevel.MODERATE,
                recommendations=[
                    "Serial troponins",
                    "Observation",
                    "Antiplatelet therapy",
                    "Risk stratification"
                ],
                supporting_evidence={"heart_score": heart_score},
                agent_name=self.name,
                depth=self.depth
            )
            hypotheses.append(ua_hypothesis)
        
        return hypotheses
    
    def _calculate_heart_score(self, patient_data: PatientData) -> int:
        """
        Calculate HEART score for ACS risk stratification
        
        History (0-2) + EKG (0-2) + Age (0-2) + Risk Factors (0-2) + Troponin (0-2)
        Score interpretation:
        0-3: Low risk (2% MACE)
        4-6: Moderate risk (12% MACE)
        7-10: High risk (65% MACE)
        """
        score = 0
        
        # History (simplified - in production, use NLP on chief complaint)
        score += 2  # Assume highly suspicious for chest pain presentation
        
        # EKG (simplified - in production, parse actual EKG)
        # Assume normal for demo
        score += 0
        
        # Age
        age = patient_data.age
        if age >= 65:
            score += 2
        elif age >= 45:
            score += 1
        
        # Risk factors (count: HTN, DM, smoking, family history, hyperlipidemia)
        # Simplified: estimate from ICD codes
        risk_factors = 0
        for icd in patient_data.icd_codes:
            if icd in ['4019', '25000', '25001', '25002']:  # HTN, DM codes
                risk_factors += 1
        
        if risk_factors >= 3:
            score += 2
        elif risk_factors >= 1:
            score += 1
        
        # Troponin
        troponin_values = patient_data.labs.get('Troponin', [])
        latest_troponin = troponin_values[-1][1] if troponin_values else 0.04
        
        if latest_troponin >= (3 * TROPONIN_NORMAL):
            score += 2
        elif latest_troponin >= TROPONIN_NORMAL:
            score += 1
        
        logger.debug(f"Calculated HEART score: {score}")
        return score
    
    async def _identify_subspecialties(self, hypotheses: List[DiagnosisResult]) -> List[str]:
        """Potentially spawn STEMI or NSTEMI specific agents"""
        # For 12-hour implementation, we'll keep this simple
        # In production, would spawn STEMIAgent or NSTEMIAgent
        return []
    
    def _create_child_agent(self, subspecialty_name: str) -> Optional[FractalAgent]:
        """Could create STEMI/NSTEMI agents"""
        # Placeholder for future expansion
        return None
    
    async def _synthesize_results(
        self,
        hypotheses: List[DiagnosisResult],
        children_results: List[DiagnosisResult],
        patient_data: PatientData
    ) -> DiagnosisResult:
        """Return best hypothesis"""
        if hypotheses:
            return max(hypotheses, key=lambda x: x.confidence)
        
        return DiagnosisResult(
            diagnosis=DiagnosisType.UNKNOWN,
            confidence=0.1,
            reasoning="Unable to determine ACS type",
            risk_level=RiskLevel.MODERATE,
            recommendations=["Cardiology evaluation"],
            supporting_evidence={},
            agent_name=self.name,
            depth=self.depth
        )
