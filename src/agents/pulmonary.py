"""
Pulmonary specialty agent for respiratory causes of chest pain
Includes PE, pneumonia, pneumothorax, pleuritis
"""

from typing import List, Optional, Dict, Any
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from config import (
    SpecialtyType, DiagnosisType, RiskLevel
)
from data_loader import PatientData
from src.agents.base import FractalAgent, DiagnosisResult
from loguru import logger


class PulmonaryAgent(FractalAgent):
    """
    Pulmonary agent for chest pain evaluation
    
    Can differentiate between:
    - Pulmonary Embolism (PE) - life-threatening
    - Pneumonia - infectious
    - Pneumothorax - mechanical
    - Pleuritis/Pleurisy - inflammatory
    - COPD exacerbation
    """
    
    def __init__(self, depth: int = 0):
        super().__init__(
            specialty=SpecialtyType.PULMONARY,
            name="Pulmonary Agent",
            depth=depth
        )
    
    async def _generate_hypotheses(self, patient_data: PatientData) -> List[DiagnosisResult]:
        """Generate pulmonary differential diagnoses for chest pain"""
        hypotheses = []
        
        # Extract pulmonary-relevant features
        pulm_features = self._extract_pulmonary_features(patient_data)
        
        # Pulmonary Embolism (CRITICAL - check first)
        pe_score = self._calculate_pe_score(pulm_features, patient_data)
        if pe_score > 0.3:
            hypotheses.append(self._create_pe_hypothesis(pe_score, pulm_features))
        
        # Pneumothorax
        ptx_score = self._calculate_pneumothorax_score(pulm_features, patient_data)
        if ptx_score > 0.3:
            hypotheses.append(self._create_pneumothorax_hypothesis(ptx_score, pulm_features))
        
        # Pneumonia
        pna_score = self._calculate_pneumonia_score(pulm_features, patient_data)
        if pna_score > 0.3:
            hypotheses.append(self._create_pneumonia_hypothesis(pna_score, pulm_features))
        
        # Pleuritis
        pleur_score = self._calculate_pleuritis_score(pulm_features, patient_data)
        if pleur_score > 0.25:
            hypotheses.append(self._create_pleuritis_hypothesis(pleur_score, pulm_features))
        
        # If no strong pulmonary hypothesis
        if not hypotheses:
            hypotheses.append(DiagnosisResult(
                diagnosis=DiagnosisType.NON_CARDIAC_CHEST_PAIN,
                confidence=0.10,
                reasoning="No strong pulmonary etiology identified",
                risk_level=RiskLevel.LOW,
                recommendations=["Rule out cardiac causes", "Consider GI or MSK etiology"],
                supporting_evidence={},
                agent_name=self.name,
                depth=self.depth
            ))
        
        return hypotheses
    
    def _extract_pulmonary_features(self, patient_data: PatientData) -> Dict[str, Any]:
        """Extract pulmonary-relevant features"""
        features = {
            "dyspnea": False,
            "pleuritic_pain": False,  # Sharp pain worse with breathing
            "cough": False,
            "hemoptysis": False,
            "fever": False,
            "tachypnea": False,
            "hypoxia": False,
            "unilateral_pain": False,
            "recent_surgery": False,
            "immobilization": False,
            "leg_swelling": False,  # DVT → PE
            "smoking_history": False,
            "sudden_onset": False,
            "age": patient_data.age,
        }
        
        # Check vitals
        rr = patient_data.vitals.get('respiratory_rate', 16)
        spo2 = patient_data.vitals.get('oxygen_saturation', 100)
        temp = patient_data.vitals.get('temperature', 98.6)
        
        features['tachypnea'] = rr > 20
        features['hypoxia'] = spo2 < 94
        features['fever'] = temp > 100.4
        
        # Check ICD codes
        pulm_icd_codes = {
            '4151': 'pulmonary_embolism',
            '5121': 'pneumothorax',
            '486': 'pneumonia',
            '487': 'influenza',
            '491': 'chronic_bronchitis',
            '492': 'emphysema',
            '493': 'asthma',
            '511': 'pleurisy',
            '5990': 'uti',  # Risk for sepsis
        }
        
        for icd in patient_data.icd_codes:
            if icd in pulm_icd_codes:
                condition = pulm_icd_codes[icd]
                if 'embolism' in condition:
                    features['recent_surgery'] = True  # Infer risk
                elif 'pneumothorax' in condition:
                    features['sudden_onset'] = True
                elif 'pneumonia' in condition or 'influenza' in condition:
                    features['cough'] = True
                    features['fever'] = True
                elif 'pleurisy' in condition:
                    features['pleuritic_pain'] = True
                elif 'bronchitis' in condition or 'emphysema' in condition:
                    features['smoking_history'] = True
        
        # Check labs
        if 'WBC' in patient_data.labs:
            wbc_values = patient_data.labs['WBC']
            latest_wbc = wbc_values[-1][1] if wbc_values else 7.5
            if latest_wbc > 12:  # Leukocytosis
                features['elevated_wbc'] = True
                features['infection_likely'] = True
        
        if 'D-dimer' in patient_data.labs:
            ddimer_values = patient_data.labs['D-dimer']
            latest_ddimer = ddimer_values[-1][1] if ddimer_values else 0
            if latest_ddimer > 500:  # Elevated
                features['elevated_ddimer'] = True
        
        # Infer from chief complaint
        if hasattr(patient_data, 'chief_complaint') and patient_data.chief_complaint:
            complaint = patient_data.chief_complaint.lower()
            if 'breath' in complaint or 'dyspnea' in complaint or 'sob' in complaint:
                features['dyspnea'] = True
            if 'cough' in complaint:
                features['cough'] = True
            if 'sudden' in complaint or 'acute' in complaint:
                features['sudden_onset'] = True
            if 'sharp' in complaint and 'breath' in complaint:
                features['pleuritic_pain'] = True
        
        return features
    
    def _calculate_pe_score(self, features: Dict, patient_data: PatientData) -> float:
        """
        Calculate likelihood of Pulmonary Embolism (PE)
        
        Uses modified Wells' Criteria:
        - Clinical signs of DVT (3.0)
        - PE most likely diagnosis (3.0)
        - Heart rate > 100 (1.5)
        - Immobilization/surgery (1.5)
        - Previous PE/DVT (1.5)
        - Hemoptysis (1.0)
        - Malignancy (1.0)
        
        Score > 4 = PE likely
        """
        score = 0.0
        
        # Clinical signs of DVT
        if features.get('leg_swelling'):
            score += 0.30
        
        # Tachycardia
        hr = patient_data.vitals.get('heart_rate', 70)
        if hr > 100:
            score += 0.20
        
        # Recent surgery or immobilization
        if features.get('recent_surgery') or features.get('immobilization'):
            score += 0.25
        
        # Hemoptysis
        if features.get('hemoptysis'):
            score += 0.15
        
        # Sudden onset dyspnea
        if features.get('dyspnea') and features.get('sudden_onset'):
            score += 0.25
        
        # Hypoxia (strong indicator)
        if features.get('hypoxia'):
            score += 0.30
        
        # Pleuritic pain
        if features.get('pleuritic_pain'):
            score += 0.15
        
        # Elevated D-dimer (if available)
        if features.get('elevated_ddimer'):
            score += 0.20
        
        # Age > 60 increases risk
        if features.get('age', 50) > 60:
            score += 0.10
        
        return min(score, 1.0)
    
    def _calculate_pneumothorax_score(self, features: Dict, patient_data: PatientData) -> float:
        """
        Calculate likelihood of pneumothorax
        
        Classic presentation:
        - Sudden onset sharp chest pain
        - Unilateral
        - Dyspnea
        - Decreased breath sounds (would need exam)
        - Tall, thin young males (spontaneous PTX)
        """
        score = 0.0
        
        # Sudden onset (key feature)
        if features.get('sudden_onset'):
            score += 0.35
        
        # Sharp, pleuritic pain
        if features.get('pleuritic_pain'):
            score += 0.25
        
        # Dyspnea
        if features.get('dyspnea'):
            score += 0.20
        
        # Unilateral
        if features.get('unilateral_pain'):
            score += 0.20
        
        # Young age (spontaneous PTX)
        age = features.get('age', 50)
        if 15 <= age <= 35:
            score += 0.15
        
        # Hypoxia (if tension PTX)
        if features.get('hypoxia'):
            score += 0.20
        
        # Tachypnea
        if features.get('tachypnea'):
            score += 0.15
        
        return min(score, 1.0)
    
    def _calculate_pneumonia_score(self, features: Dict, patient_data: PatientData) -> float:
        """
        Calculate likelihood of pneumonia
        
        CURB-65 criteria:
        - Confusion
        - Uremia (BUN > 20)
        - Respiratory rate ≥ 30
        - Blood pressure (SBP < 90 or DBP ≤ 60)
        - Age ≥ 65
        
        Also: fever, cough, dyspnea, elevated WBC
        """
        score = 0.0
        
        # Fever (classic)
        if features.get('fever'):
            score += 0.30
        
        # Cough
        if features.get('cough'):
            score += 0.25
        
        # Dyspnea
        if features.get('dyspnea'):
            score += 0.20
        
        # Elevated WBC
        if features.get('elevated_wbc'):
            score += 0.25
        
        # Tachypnea
        if features.get('tachypnea'):
            score += 0.15
        
        # Pleuritic pain (suggests bacterial)
        if features.get('pleuritic_pain'):
            score += 0.15
        
        # Age ≥ 65
        if features.get('age', 50) >= 65:
            score += 0.15
        
        # Hypoxia
        if features.get('hypoxia'):
            score += 0.20
        
        return min(score, 1.0)
    
    def _calculate_pleuritis_score(self, features: Dict, patient_data: PatientData) -> float:
        """
        Calculate likelihood of pleuritis/pleurisy
        
        Features:
        - Sharp, pleuritic chest pain (worse with breathing)
        - Unilateral often
        - Viral prodrome
        - No significant hypoxia
        - Friction rub on exam (cannot assess here)
        """
        score = 0.0
        
        # Pleuritic pain (key feature)
        if features.get('pleuritic_pain'):
            score += 0.40
        
        # Sharp quality
        if features.get('unilateral_pain'):
            score += 0.20
        
        # Dyspnea (mild)
        if features.get('dyspnea') and not features.get('hypoxia'):
            score += 0.15
        
        # Recent viral illness (infer from ICD codes)
        if features.get('fever') and not features.get('elevated_wbc'):
            score += 0.15  # Viral (low WBC)
        
        # No hypoxia (rules out PE, large PTX, severe PNA)
        if not features.get('hypoxia'):
            score += 0.10
        
        return min(score, 1.0)
    
    def _create_pe_hypothesis(self, score: float, features: Dict) -> DiagnosisResult:
        """Create PE hypothesis"""
        confidence = score
        
        # PE is CRITICAL risk
        risk = RiskLevel.CRITICAL if confidence > 0.6 else RiskLevel.HIGH
        
        reasoning_parts = ["Pulmonary Embolism (PE) suspected - CRITICAL:"]
        if features.get('dyspnea'):
            reasoning_parts.append("- Acute dyspnea")
        if features.get('sudden_onset'):
            reasoning_parts.append("- Sudden onset")
        if features.get('hypoxia'):
            reasoning_parts.append("- Hypoxia (SpO2 < 94%)")
        if features.get('leg_swelling'):
            reasoning_parts.append("- Clinical DVT signs")
        if features.get('elevated_ddimer'):
            reasoning_parts.append("- Elevated D-dimer")
        
        reasoning = "\n".join(reasoning_parts)
        
        recommendations = [
            "⚠️⚠️ CRITICAL: Pulmonary Embolism is LIFE-THREATENING",
            "IMMEDIATE actions:",
            "  1. STAT CT Pulmonary Angiography (CTPA) - GOLD STANDARD",
            "  2. If CTPA not available: V/Q scan",
            "  3. Check D-dimer if low-moderate probability",
            "  4. Oxygen therapy to maintain SpO2 > 94%",
            "  5. Anticoagulation if high suspicion (don't wait for imaging)",
            "     - Heparin bolus 80 units/kg IV, then 18 units/kg/hr",
            "     - OR Enoxaparin 1 mg/kg SQ BID",
            "  6. Hemodynamically unstable? → Thrombolytics (tPA)",
            "  7. Check troponin, BNP (RV strain)",
            "  8. Bilateral lower extremity Dopplers (DVT)",
            "  9. Admit to ICU if massive PE",
            "Risk factors: recent surgery, immobilization, cancer, hypercoagulable state",
            "DO NOT DISCHARGE - high mortality if untreated"
        ]
        
        return DiagnosisResult(
            diagnosis=DiagnosisType.PULMONARY_EMBOLISM,
            confidence=confidence,
            reasoning=reasoning,
            risk_level=risk,
            recommendations=recommendations,
            supporting_evidence={
                "pe_score": score,
                "hypoxia": features.get('hypoxia', False),
                "sudden_onset": features.get('sudden_onset', False)
            },
            agent_name=self.name,
            depth=self.depth
        )
    
    def _create_pneumothorax_hypothesis(self, score: float, features: Dict) -> DiagnosisResult:
        """Create pneumothorax hypothesis"""
        risk = RiskLevel.HIGH if score > 0.6 else RiskLevel.MODERATE
        
        return DiagnosisResult(
            diagnosis=DiagnosisType.PNEUMOTHORAX,
            confidence=score,
            reasoning="Pneumothorax suspected: sudden sharp chest pain, dyspnea, unilateral",
            risk_level=risk,
            recommendations=[
                "⚠️ Pneumothorax requires immediate imaging",
                "STAT Chest X-ray (upright PA if possible)",
                "  - Look for: visceral pleural line, absent lung markings",
                "If tension PTX suspected (hypotension, JVD, tracheal deviation):",
                "  → IMMEDIATE needle decompression (2nd ICS midclavicular line)",
                "  → Don't wait for CXR if unstable!",
                "Management based on size:",
                "  - Small (<2cm): Observation + O2 (accelerates reabsorption)",
                "  - Large (>2cm) or symptomatic: Chest tube (pigtail or large bore)",
                "  - Tension: Emergency needle decompression → chest tube",
                "Admit for monitoring",
                "Avoid air travel until resolved",
                "If recurrent: consider VATS pleurodesis"
            ],
            supporting_evidence={
                "ptx_score": score,
                "sudden_onset": features.get('sudden_onset', False),
                "pleuritic_pain": features.get('pleuritic_pain', False)
            },
            agent_name=self.name,
            depth=self.depth
        )
    
    def _create_pneumonia_hypothesis(self, score: float, features: Dict) -> DiagnosisResult:
        """Create pneumonia hypothesis"""
        risk = RiskLevel.MODERATE if score > 0.6 else RiskLevel.LOW
        
        return DiagnosisResult(
            diagnosis=DiagnosisType.PNEUMONIA,
            confidence=score,
            reasoning="Pneumonia likely: fever, cough, dyspnea, elevated WBC",
            risk_level=risk,
            recommendations=[
                "Chest X-ray (PA and lateral) to confirm diagnosis",
                "Labs: CBC, CMP, blood cultures × 2 if severe",
                "Sputum culture (if productive)",
                "Consider severity with CURB-65 or PSI score",
                "Antibiotics (empiric, based on severity):",
                "  Outpatient: Amoxicillin 1g TID or doxycycline 100mg BID",
                "  Inpatient: Ceftriaxone 1g IV daily + azithromycin 500mg IV daily",
                "  ICU: Ceftriaxone + azithromycin + vancomycin (MRSA coverage)",
                "Oxygen if SpO2 < 92%",
                "IV fluids if dehydrated",
                "Admission criteria: CURB-65 ≥ 2, hypoxia, unstable vitals",
                "Repeat CXR in 6 weeks to ensure resolution",
                "Pneumococcal and influenza vaccines after recovery"
            ],
            supporting_evidence={
                "pneumonia_score": score,
                "fever": features.get('fever', False),
                "elevated_wbc": features.get('elevated_wbc', False)
            },
            agent_name=self.name,
            depth=self.depth
        )
    
    def _create_pleuritis_hypothesis(self, score: float, features: Dict) -> DiagnosisResult:
        """Create pleuritis hypothesis"""
        return DiagnosisResult(
            diagnosis=DiagnosisType.PLEURITIS,
            confidence=score,
            reasoning="Pleuritis/pleurisy: sharp pleuritic chest pain, likely viral",
            risk_level=RiskLevel.LOW,
            recommendations=[
                "Chest X-ray to rule out pneumonia, pneumothorax, effusion",
                "NSAIDs for pain: Ibuprofen 600mg TID or indomethacin 50mg TID",
                "If large pleural effusion: thoracentesis (diagnostic + therapeutic)",
                "If viral: supportive care, resolves in 1-2 weeks",
                "If bacterial: treat underlying infection",
                "If autoimmune (SLE, RA): rheumatology consult",
                "Breathing exercises to prevent atelectasis",
                "Return if: worsening dyspnea, fever, hemoptysis",
                "Usually benign and self-limited"
            ],
            supporting_evidence={
                "pleuritis_score": score,
                "pleuritic_pain": features.get('pleuritic_pain', False)
            },
            agent_name=self.name,
            depth=self.depth
        )
    
    async def _identify_subspecialties(self, hypotheses: List[DiagnosisResult]) -> List[str]:
        """No sub-specialties needed"""
        return []
    
    def _create_child_agent(self, subspecialty_name: str) -> Optional[FractalAgent]:
        """No child agents"""
        return None
    
    async def _synthesize_results(
        self,
        hypotheses: List[DiagnosisResult],
        children_results: List[DiagnosisResult],
        patient_data: PatientData
    ) -> DiagnosisResult:
        """Synthesize pulmonary diagnoses"""
        
        if hypotheses:
            # Return highest confidence
            best = max(hypotheses, key=lambda x: x.confidence)
            
            # If PE suspected, always flag as critical
            pe_hyps = [h for h in hypotheses if h.diagnosis == DiagnosisType.PULMONARY_EMBOLISM]
            if pe_hyps and pe_hyps[0].confidence > 0.4:
                return pe_hyps[0]
            
            return best
        
        return DiagnosisResult(
            diagnosis=DiagnosisType.NON_CARDIAC_CHEST_PAIN,
            confidence=0.10,
            reasoning="No strong pulmonary etiology",
            risk_level=RiskLevel.LOW,
            recommendations=["Consider cardiac, GI, or MSK causes"],
            supporting_evidence={},
            agent_name=self.name,
            depth=self.depth
        )
