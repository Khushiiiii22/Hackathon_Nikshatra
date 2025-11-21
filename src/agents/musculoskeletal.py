"""
Musculoskeletal (MSK) specialty agent for chest wall pain
Includes costochondritis, muscle strain, rib fracture
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


class MusculoskeletalAgent(FractalAgent):
    """
    MSK agent for chest pain evaluation
    
    Can differentiate between:
    - Costochondritis (most common MSK chest pain)
    - Muscle strain (intercostal, pectoral)
    - Rib fracture
    - Herpes zoster (shingles - pre-rash phase)
    """
    
    def __init__(self, depth: int = 0):
        super().__init__(
            specialty=SpecialtyType.MUSCULOSKELETAL,
            name="Musculoskeletal Agent",
            depth=depth
        )
    
    async def _generate_hypotheses(self, patient_data: PatientData) -> List[DiagnosisResult]:
        """Generate MSK differential diagnoses for chest pain"""
        hypotheses = []
        
        # Extract MSK-relevant features
        msk_features = self._extract_msk_features(patient_data)
        
        # Costochondritis
        costo_score = self._calculate_costochondritis_score(msk_features, patient_data)
        if costo_score > 0.3:
            hypotheses.append(self._create_costochondritis_hypothesis(costo_score, msk_features))
        
        # Muscle strain
        strain_score = self._calculate_muscle_strain_score(msk_features, patient_data)
        if strain_score > 0.3:
            hypotheses.append(self._create_muscle_strain_hypothesis(strain_score, msk_features))
        
        # Rib fracture
        fracture_score = self._calculate_rib_fracture_score(msk_features, patient_data)
        if fracture_score > 0.3:
            hypotheses.append(self._create_rib_fracture_hypothesis(fracture_score, msk_features))
        
        # If no strong MSK hypothesis, return low-confidence default
        if not hypotheses:
            hypotheses.append(DiagnosisResult(
                diagnosis=DiagnosisType.NON_CARDIAC_CHEST_PAIN,
                confidence=0.15,
                reasoning="No strong MSK etiology identified - consider other causes",
                risk_level=RiskLevel.LOW,
                recommendations=["Rule out cardiac/pulmonary causes first", "Trial of NSAIDs if appropriate"],
                supporting_evidence={},
                agent_name=self.name,
                depth=self.depth
            ))
        
        return hypotheses
    
    def _extract_msk_features(self, patient_data: PatientData) -> Dict[str, Any]:
        """
        Extract MSK-relevant features from patient data
        
        Key MSK features:
        - Reproducible with palpation
        - Sharp/stabbing quality
        - Worse with movement/breathing
        - Point tenderness
        - Recent trauma/heavy lifting
        - Unilateral distribution
        """
        features = {
            "reproducible_with_palpation": False,
            "sharp_quality": False,
            "worse_with_movement": False,
            "worse_with_breathing": False,
            "point_tenderness": False,
            "recent_trauma": False,
            "recent_exertion": False,
            "unilateral": False,
            "dermatomal": False,  # For herpes zoster
            "swelling_visible": False,
            "young_age": patient_data.age < 40,
            "age": patient_data.age,
        }
        
        # Check ICD codes for MSK history
        msk_icd_codes = {
            '7330': 'osteoarthritis',
            '7242': 'lumbago',  # Back pain
            '8070': 'rib_fracture',
            '8071': 'multiple_rib_fractures',
            '7335': 'costochondritis',
            '7291': 'myalgia',  # Muscle pain
            '0539': 'herpes_zoster'
        }
        
        for icd in patient_data.icd_codes:
            if icd in msk_icd_codes:
                condition = msk_icd_codes[icd]
                if 'costochondritis' in condition:
                    features['point_tenderness'] = True
                    features['reproducible_with_palpation'] = True
                elif 'fracture' in condition:
                    features['recent_trauma'] = True
                    features['worse_with_breathing'] = True
                elif 'myalgia' in condition or 'lumbago' in condition:
                    features['worse_with_movement'] = True
                elif 'zoster' in condition:
                    features['dermatomal'] = True
                    features['unilateral'] = True
        
        # Infer from chief complaint if available
        if hasattr(patient_data, 'chief_complaint') and patient_data.chief_complaint:
            complaint = patient_data.chief_complaint.lower()
            if 'sharp' in complaint or 'stabbing' in complaint:
                features['sharp_quality'] = True
            if 'movement' in complaint or 'breathing' in complaint:
                features['worse_with_movement'] = True
                features['worse_with_breathing'] = True
            if 'tender' in complaint or 'touch' in complaint:
                features['point_tenderness'] = True
                features['reproducible_with_palpation'] = True
        
        # Check for normal cardiac biomarkers (suggests non-cardiac)
        if 'Troponin' in patient_data.labs:
            troponin_values = patient_data.labs['Troponin']
            latest_troponin = troponin_values[-1][1] if troponin_values else 0
            if latest_troponin < 0.04:  # Normal
                features['normal_troponin'] = True
        
        return features
    
    def _calculate_costochondritis_score(self, features: Dict, patient_data: PatientData) -> float:
        """
        Calculate likelihood of costochondritis
        
        Classic features:
        - Reproducible with palpation (most important)
        - Sharp, stabbing pain
        - Point tenderness over costochondral junctions
        - Worse with deep breathing or movement
        - Young to middle-aged adults
        - No cardiac risk factors
        """
        score = 0.0
        
        # Most important: reproducible with palpation
        if features.get('reproducible_with_palpation'):
            score += 0.40
        
        if features.get('point_tenderness'):
            score += 0.25
        
        if features.get('sharp_quality'):
            score += 0.15
        
        if features.get('worse_with_breathing'):
            score += 0.15
        
        if features.get('worse_with_movement'):
            score += 0.10
        
        # Age factor (more common in young adults)
        age = features.get('age', 50)
        if 20 <= age <= 40:
            score += 0.20
        elif 41 <= age <= 60:
            score += 0.10
        
        # Normal cardiac markers support MSK diagnosis
        if features.get('normal_troponin'):
            score += 0.15
        
        return min(score, 1.0)
    
    def _calculate_muscle_strain_score(self, features: Dict, patient_data: PatientData) -> float:
        """
        Calculate likelihood of muscle strain (intercostal or pectoral)
        
        Features:
        - Recent exertion or heavy lifting
        - Worse with specific movements
        - Sharp or aching pain
        - Unilateral often
        - Reproduced with stretching
        """
        score = 0.0
        
        if features.get('recent_exertion') or features.get('recent_trauma'):
            score += 0.35
        
        if features.get('worse_with_movement'):
            score += 0.30
        
        if features.get('reproducible_with_palpation'):
            score += 0.20
        
        if features.get('unilateral'):
            score += 0.15
        
        if features.get('sharp_quality'):
            score += 0.10
        
        # Younger patients more likely to have exertion-related strain
        if features.get('young_age'):
            score += 0.15
        
        if features.get('normal_troponin'):
            score += 0.10
        
        return min(score, 1.0)
    
    def _calculate_rib_fracture_score(self, features: Dict, patient_data: PatientData) -> float:
        """
        Calculate likelihood of rib fracture
        
        Features:
        - Recent trauma (fall, MVA, assault)
        - Severe pain with breathing
        - Point tenderness over rib
        - Worse with coughing/sneezing
        - Elderly (osteoporosis) or trauma history
        """
        score = 0.0
        
        # Recent trauma is key
        if features.get('recent_trauma'):
            score += 0.50
        
        if features.get('worse_with_breathing'):
            score += 0.25
        
        if features.get('point_tenderness'):
            score += 0.20
        
        if features.get('sharp_quality'):
            score += 0.15
        
        # Elderly or osteoporosis increases risk
        age = features.get('age', 50)
        if age >= 65:
            score += 0.20  # Osteoporosis risk
        
        if features.get('swelling_visible'):
            score += 0.15
        
        return min(score, 1.0)
    
    def _create_costochondritis_hypothesis(self, score: float, features: Dict) -> DiagnosisResult:
        """Create costochondritis diagnosis hypothesis"""
        confidence = score
        
        reasoning_parts = ["Costochondritis (chest wall inflammation) suggested by:"]
        if features.get('reproducible_with_palpation'):
            reasoning_parts.append("- Reproducible with palpation (diagnostic)")
        if features.get('point_tenderness'):
            reasoning_parts.append("- Point tenderness over costochondral junctions")
        if features.get('sharp_quality'):
            reasoning_parts.append("- Sharp, stabbing pain quality")
        if features.get('worse_with_breathing'):
            reasoning_parts.append("- Worse with deep breathing")
        
        reasoning = "\n".join(reasoning_parts)
        
        recommendations = [
            "NSAIDs: Ibuprofen 400-600mg PO TID or naproxen 500mg BID",
            "Local heat application",
            "Avoid aggravating activities",
            "Stretching exercises after acute phase",
            "If severe: consider lidocaine patch",
            "Rule out cardiac causes first (troponin, EKG)",
            "Reassure: benign, self-limited (2-12 weeks)",
            "Return if: worsening pain, fever, dyspnea"
        ]
        
        return DiagnosisResult(
            diagnosis=DiagnosisType.COSTOCHONDRITIS,
            confidence=confidence,
            reasoning=reasoning,
            risk_level=RiskLevel.LOW,
            recommendations=recommendations,
            supporting_evidence={
                "costochondritis_score": score,
                "reproducible": features.get('reproducible_with_palpation', False),
                "point_tenderness": features.get('point_tenderness', False)
            },
            agent_name=self.name,
            depth=self.depth
        )
    
    def _create_muscle_strain_hypothesis(self, score: float, features: Dict) -> DiagnosisResult:
        """Create muscle strain hypothesis"""
        return DiagnosisResult(
            diagnosis=DiagnosisType.MUSCLE_STRAIN,
            confidence=score,
            reasoning="Muscle strain (intercostal or pectoral) likely from recent exertion/trauma",
            risk_level=RiskLevel.LOW,
            recommendations=[
                "Rest from aggravating activities",
                "Ice in first 48 hours, then heat",
                "NSAIDs: Ibuprofen 400-600mg TID with food",
                "Gentle stretching after 48-72 hours",
                "Avoid heavy lifting for 1-2 weeks",
                "Progressive return to activity",
                "Consider physical therapy if prolonged",
                "Rule out cardiac causes first"
            ],
            supporting_evidence={
                "muscle_strain_score": score,
                "recent_exertion": features.get('recent_exertion', False),
                "worse_with_movement": features.get('worse_with_movement', False)
            },
            agent_name=self.name,
            depth=self.depth
        )
    
    def _create_rib_fracture_hypothesis(self, score: float, features: Dict) -> DiagnosisResult:
        """Create rib fracture hypothesis"""
        # Rib fracture can be higher risk if multiple or if complications
        risk = RiskLevel.MODERATE if score > 0.7 else RiskLevel.LOW
        
        return DiagnosisResult(
            diagnosis=DiagnosisType.RIB_FRACTURE,
            confidence=score,
            reasoning="Rib fracture suspected based on trauma history and severe pleuritic pain",
            risk_level=risk,
            recommendations=[
                "⚠️ Chest X-ray to confirm diagnosis and assess for complications",
                "Check for: pneumothorax, hemothorax, pulmonary contusion",
                "Pain control: Multimodal approach",
                "  - NSAIDs: Ibuprofen 600mg TID or ketorolac",
                "  - Consider short-course opioids if severe",
                "  - Avoid rib belts (increase pneumonia risk)",
                "Incentive spirometry to prevent pneumonia",
                "Cough and deep breathing exercises (despite pain)",
                "If multiple ribs or flail chest: ADMIT for monitoring",
                "If elderly: high risk of pneumonia, consider admission",
                "Return if: increasing dyspnea, fever, worsening pain"
            ],
            supporting_evidence={
                "rib_fracture_score": score,
                "recent_trauma": features.get('recent_trauma', False),
                "worse_with_breathing": features.get('worse_with_breathing', False)
            },
            agent_name=self.name,
            depth=self.depth
        )
    
    async def _identify_subspecialties(self, hypotheses: List[DiagnosisResult]) -> List[str]:
        """Identify if sub-agents needed (none for MSK in basic implementation)"""
        return []
    
    def _create_child_agent(self, subspecialty_name: str) -> Optional[FractalAgent]:
        """Create sub-specialty agents (placeholder for future)"""
        return None
    
    async def _synthesize_results(
        self,
        hypotheses: List[DiagnosisResult],
        children_results: List[DiagnosisResult],
        patient_data: PatientData
    ) -> DiagnosisResult:
        """Synthesize MSK diagnoses"""
        
        # Return best hypothesis
        if hypotheses:
            best_hypothesis = max(hypotheses, key=lambda x: x.confidence)
            
            # If multiple high-confidence hypotheses, note differential
            high_conf_hyps = [h for h in hypotheses if h.confidence > 0.5]
            if len(high_conf_hyps) > 1:
                best_hypothesis.reasoning += "\n\nDifferential diagnosis includes: " + \
                    ", ".join([f"{h.diagnosis.value} ({h.confidence:.0%})" for h in high_conf_hyps[1:]])
            
            return best_hypothesis
        
        # Fallback
        return DiagnosisResult(
            diagnosis=DiagnosisType.NON_CARDIAC_CHEST_PAIN,
            confidence=0.10,
            reasoning="MSK etiology possible but uncertain - consider other causes",
            risk_level=RiskLevel.LOW,
            recommendations=["Cardiac workup first", "If cardiac negative: trial of NSAIDs"],
            supporting_evidence={},
            agent_name=self.name,
            depth=self.depth
        )
