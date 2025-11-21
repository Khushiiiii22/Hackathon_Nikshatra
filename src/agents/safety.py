"""
Safety Monitor Agent - Always active, highest priority
Monitors for life-threatening conditions
"""

from typing import List, Optional
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from config import (
    SpecialtyType, DiagnosisType, RiskLevel,
    TROPONIN_HIGH, CRITICAL_ALERTS
)
from data_loader import PatientData, calculate_troponin_trend
from src.agents.base import FractalAgent, DiagnosisResult
from loguru import logger


class SafetyMonitorAgent(FractalAgent):
    """
    Always-active safety monitor
    Checks for critical diagnoses that require immediate intervention
    """
    
    def __init__(self):
        super().__init__(
            specialty=SpecialtyType.SAFETY,
            name="Safety Monitor",
            depth=0
        )
        self.critical_alerts = []
    
    async def _generate_hypotheses(self, patient_data: PatientData) -> List[DiagnosisResult]:
        """Check for life-threatening conditions"""
        hypotheses = []
        
        # Check for STEMI (ST-elevation MI)
        stemi_result = self._check_stemi(patient_data)
        if stemi_result:
            hypotheses.append(stemi_result)
            self.critical_alerts.append("STEMI_ALERT")
        
        # Check for massive PE
        pe_result = self._check_massive_pe(patient_data)
        if pe_result:
            hypotheses.append(pe_result)
            self.critical_alerts.append("MASSIVE_PE_ALERT")
        
        # Check for sepsis
        sepsis_result = self._check_sepsis(patient_data)
        if sepsis_result:
            hypotheses.append(sepsis_result)
            self.critical_alerts.append("SEPSIS_ALERT")
        
        return hypotheses
    
    def _check_stemi(self, patient_data: PatientData) -> Optional[DiagnosisResult]:
        """
        Check for STEMI criteria:
        - Markedly elevated troponin
        - Chest pain
        - (In production: ST elevation on EKG)
        """
        troponin_values = patient_data.labs.get('Troponin', [])
        if not troponin_values:
            return None
        
        latest_troponin = troponin_values[-1][1]
        troponin_trend = calculate_troponin_trend(troponin_values)
        
        # STEMI if very high troponin + rising
        if latest_troponin >= TROPONIN_HIGH and troponin_trend == "rising":
            logger.critical(f"⚠️  STEMI ALERT for patient {patient_data.patient_id}")
            
            return DiagnosisResult(
                diagnosis=DiagnosisType.STEMI,
                confidence=0.95,
                reasoning=f"CRITICAL: Very high troponin ({latest_troponin}) with rising trend",
                risk_level=RiskLevel.CRITICAL,
                recommendations=[
                    "🚨 IMMEDIATE CATH LAB ACTIVATION",
                    "Aspirin 325mg",
                    "P2Y12 inhibitor (ticagrelor/prasugrel)",
                    "Heparin bolus",
                    "Beta-blocker if not contraindicated",
                    "Target door-to-balloon time <90 minutes"
                ],
                supporting_evidence={
                    "troponin": latest_troponin,
                    "trend": troponin_trend,
                    "alert_type": "STEMI"
                },
                agent_name=self.name,
                depth=self.depth
            )
        
        return None
    
    def _check_massive_pe(self, patient_data: PatientData) -> Optional[DiagnosisResult]:
        """
        Check for massive PE:
        - Hypotension (SBP < 90)
        - Hypoxia (O2 sat < 90%)
        - Tachycardia
        """
        vitals = patient_data.vitals
        
        sbp = vitals.get('systolic_bp', 120)
        o2_sat = vitals.get('o2_saturation', 98)
        hr = vitals.get('heart_rate', 70)
        
        # Massive PE criteria
        if sbp < 90 and o2_sat < 90:
            logger.critical(f"⚠️  MASSIVE PE ALERT for patient {patient_data.patient_id}")
            
            return DiagnosisResult(
                diagnosis=DiagnosisType.PE,
                confidence=0.85,
                reasoning=f"CRITICAL: Hypotension (SBP {sbp}) + Hypoxia (O2 {o2_sat}%)",
                risk_level=RiskLevel.CRITICAL,
                recommendations=[
                    "🚨 MASSIVE PE PROTOCOL",
                    "CTA pulmonary angiography",
                    "Consider thrombolytics (tPA)",
                    "ICU admission",
                    "Cardiothoracic surgery consult",
                    "Anticoagulation (heparin drip)"
                ],
                supporting_evidence={
                    "sbp": sbp,
                    "o2_sat": o2_sat,
                    "hr": hr,
                    "alert_type": "MASSIVE_PE"
                },
                agent_name=self.name,
                depth=self.depth
            )
        
        return None
    
    def _check_sepsis(self, patient_data: PatientData) -> Optional[DiagnosisResult]:
        """
        Check for sepsis using qSOFA:
        - RR >= 22
        - SBP <= 100
        - Altered mental status (not directly measurable in this data)
        """
        vitals = patient_data.vitals
        
        rr = vitals.get('respiratory_rate', 16)
        sbp = vitals.get('systolic_bp', 120)
        temp = vitals.get('temperature', 37.0)
        
        qsofa_score = 0
        if rr >= 22:
            qsofa_score += 1
        if sbp <= 100:
            qsofa_score += 1
        
        # Also consider fever/hypothermia
        if temp >= 38.3 or temp <= 36.0:
            qsofa_score += 0.5
        
        if qsofa_score >= 2:
            logger.critical(f"⚠️  SEPSIS ALERT for patient {patient_data.patient_id}")
            
            return DiagnosisResult(
                diagnosis=DiagnosisType.UNKNOWN,  # Would be specific infection
                confidence=0.75,
                reasoning=f"CRITICAL: qSOFA score {qsofa_score} suggests sepsis",
                risk_level=RiskLevel.CRITICAL,
                recommendations=[
                    "🚨 SEPSIS BUNDLE",
                    "Blood cultures x2 before antibiotics",
                    "Broad-spectrum antibiotics within 1 hour",
                    "Lactate measurement",
                    "30 mL/kg crystalloid bolus",
                    "ICU consult"
                ],
                supporting_evidence={
                    "qsofa": qsofa_score,
                    "rr": rr,
                    "sbp": sbp,
                    "temp": temp,
                    "alert_type": "SEPSIS"
                },
                agent_name=self.name,
                depth=self.depth
            )
        
        return None
    
    async def _identify_subspecialties(self, hypotheses: List[DiagnosisResult]) -> List[str]:
        """Safety monitor doesn't spawn children"""
        return []
    
    def _create_child_agent(self, subspecialty_name: str) -> Optional[FractalAgent]:
        """Safety monitor doesn't spawn children"""
        return None
    
    async def _synthesize_results(
        self,
        hypotheses: List[DiagnosisResult],
        children_results: List[DiagnosisResult],
        patient_data: PatientData
    ) -> DiagnosisResult:
        """Return highest priority critical alert"""
        if hypotheses:
            # Return most critical
            return max(hypotheses, key=lambda x: x.confidence)
        
        # No critical alerts
        return DiagnosisResult(
            diagnosis=DiagnosisType.UNKNOWN,
            confidence=0.0,
            reasoning="No critical safety alerts",
            risk_level=RiskLevel.LOW,
            recommendations=["Continue standard workup"],
            supporting_evidence={},
            agent_name=self.name,
            depth=self.depth
        )
    
    def has_critical_alerts(self) -> bool:
        """Check if any critical alerts were raised"""
        return len(self.critical_alerts) > 0
    
    def get_alerts(self) -> List[str]:
        """Get list of critical alerts"""
        return self.critical_alerts.copy()
