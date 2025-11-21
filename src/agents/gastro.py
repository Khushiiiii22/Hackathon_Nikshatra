"""
Gastroenterology specialty agent for GI-related chest pain
Includes GERD, esophageal spasm, PUD, biliary colic, pancreatitis
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


class GastroenterologyAgent(FractalAgent):
    """
    Main GI agent for chest pain evaluation
    
    Can differentiate between:
    - GERD (most common GI cause of chest pain)
    - Esophageal spasm
    - Peptic ulcer disease
    - Biliary colic
    - Pancreatitis
    - Esophageal rupture (Boerhaave syndrome)
    """
    
    def __init__(self, depth: int = 0):
        super().__init__(
            specialty=SpecialtyType.GASTROENTEROLOGY,
            name="Gastroenterology Agent",
            depth=depth
        )
    
    async def _generate_hypotheses(self, patient_data: PatientData) -> List[DiagnosisResult]:
        """Generate GI differential diagnoses for chest pain"""
        hypotheses = []
        
        # Extract relevant clinical features
        clinical_features = self._extract_gi_features(patient_data)
        
        # GERD / Esophageal reflux
        gerd_score = self._calculate_gerd_score(clinical_features, patient_data)
        if gerd_score > 0:
            hypotheses.append(self._create_gerd_hypothesis(gerd_score, clinical_features))
        
        # Esophageal spasm
        spasm_score = self._calculate_spasm_score(clinical_features, patient_data)
        if spasm_score > 0:
            hypotheses.append(self._create_spasm_hypothesis(spasm_score, clinical_features))
        
        # Peptic ulcer disease
        pud_score = self._calculate_pud_score(clinical_features, patient_data)
        if pud_score > 0:
            hypotheses.append(self._create_pud_hypothesis(pud_score, clinical_features))
        
        # Biliary colic
        biliary_score = self._calculate_biliary_score(clinical_features, patient_data)
        if biliary_score > 0:
            hypotheses.append(self._create_biliary_hypothesis(biliary_score, clinical_features))
        
        # Pancreatitis
        pancreatitis_score = self._calculate_pancreatitis_score(clinical_features, patient_data)
        if pancreatitis_score > 0:
            hypotheses.append(self._create_pancreatitis_hypothesis(pancreatitis_score, clinical_features))
        
        # If no strong GI hypothesis, return low-confidence default
        if not hypotheses:
            hypotheses.append(DiagnosisResult(
                diagnosis=DiagnosisType.NON_CARDIAC_CHEST_PAIN,
                confidence=0.2,
                reasoning="No strong GI etiology identified",
                risk_level=RiskLevel.LOW,
                recommendations=["Consider other causes", "Outpatient GI follow-up if symptoms persist"],
                supporting_evidence={},
                agent_name=self.name,
                depth=self.depth
            ))
        
        return hypotheses
    
    def _extract_gi_features(self, patient_data: PatientData) -> Dict[str, Any]:
        """
        Extract GI-relevant features from patient data
        
        In production, this would parse:
        - Chief complaint text (NLP for keywords)
        - Medication history (PPIs, H2 blockers)
        - Past medical history (GERD, PUD, cholecystitis)
        - Physical exam findings
        
        For demo, we'll infer from available data
        """
        features = {
            "meal_related": False,
            "burning_quality": False,
            "positional": False,
            "relieved_by_antacids": False,
            "epigastric_pain": False,
            "right_upper_quadrant_pain": False,
            "back_radiation": False,
            "nausea_vomiting": False,
            "dysphagia": False,
            "history_gerd": False,
            "history_pud": False,
            "history_gallstones": False,
            "alcohol_use": False,
            "nsaid_use": False,
            "age": patient_data.age,
            "female": patient_data.gender.lower() == 'f',
        }
        
        # Check ICD codes for GI history
        gi_icd_codes = {
            '5300': 'esophagitis',
            '5301': 'gerd',
            '5310': 'gastric_ulcer',
            '5311': 'duodenal_ulcer',
            '5750': 'cholecystitis',
            '5751': 'cholelithiasis',
            '5770': 'pancreatitis'
        }
        
        for icd in patient_data.icd_codes:
            if icd in gi_icd_codes:
                condition = gi_icd_codes[icd]
                if 'gerd' in condition or 'esophagitis' in condition:
                    features['history_gerd'] = True
                    features['burning_quality'] = True
                    features['positional'] = True
                elif 'ulcer' in condition:
                    features['history_pud'] = True
                    features['epigastric_pain'] = True
                elif 'chole' in condition or 'gall' in condition:
                    features['history_gallstones'] = True
                    features['right_upper_quadrant_pain'] = True
                elif 'pancreatitis' in condition:
                    features['epigastric_pain'] = True
                    features['back_radiation'] = True
        
        # Check labs for GI-relevant markers
        if 'Lipase' in patient_data.labs:
            lipase_values = patient_data.labs['Lipase']
            latest_lipase = lipase_values[-1][1] if lipase_values else 0
            if latest_lipase > 180:  # > 3x ULN suggests pancreatitis
                features['elevated_lipase'] = latest_lipase
        
        if 'Amylase' in patient_data.labs:
            amylase_values = patient_data.labs['Amylase']
            latest_amylase = amylase_values[-1][1] if amylase_values else 0
            if latest_amylase > 300:
                features['elevated_amylase'] = latest_amylase
        
        if 'ALT' in patient_data.labs or 'AST' in patient_data.labs:
            alt_values = patient_data.labs.get('ALT', [(0, 0)])
            ast_values = patient_data.labs.get('AST', [(0, 0)])
            latest_alt = alt_values[-1][1] if alt_values else 0
            latest_ast = ast_values[-1][1] if ast_values else 0
            
            if latest_alt > 200 or latest_ast > 200:
                features['transaminitis'] = True
        
        return features
    
    def _calculate_gerd_score(self, features: Dict, patient_data: PatientData) -> float:
        """
        Calculate likelihood of GERD/esophageal reflux
        
        Risk factors:
        - Burning/retrosternal quality
        - Worse after meals
        - Worse lying down
        - Relieved by antacids
        - History of GERD
        - Obesity
        """
        score = 0.0
        
        if features.get('burning_quality'):
            score += 0.25
        if features.get('meal_related'):
            score += 0.20
        if features.get('positional'):
            score += 0.20
        if features.get('relieved_by_antacids'):
            score += 0.25
        if features.get('history_gerd'):
            score += 0.30
        
        # Age factor (GERD more common in middle age)
        age = features.get('age', 50)
        if 40 <= age <= 70:
            score += 0.10
        
        return min(score, 1.0)
    
    def _calculate_spasm_score(self, features: Dict, patient_data: PatientData) -> float:
        """
        Esophageal spasm likelihood
        
        Features:
        - Severe squeezing chest pain
        - Can mimic cardiac pain
        - May be triggered by hot/cold foods
        - Dysphagia
        """
        score = 0.0
        
        if features.get('dysphagia'):
            score += 0.35
        if features.get('burning_quality'):
            score += 0.15
        
        # If cardiac workup negative, consider esophageal
        troponin_values = patient_data.labs.get('Troponin', [])
        if troponin_values:
            latest_troponin = troponin_values[-1][1]
            if latest_troponin < 0.04:  # Normal troponin
                score += 0.20
        
        return min(score, 0.7)  # Max 70% without manometry
    
    def _calculate_pud_score(self, features: Dict, patient_data: PatientData) -> float:
        """
        Peptic ulcer disease likelihood
        
        Risk factors:
        - Epigastric pain
        - Burning/gnawing quality
        - Meal-related (gastric ulcer: worse with food, duodenal: better with food)
        - NSAID use
        - H. pylori history
        """
        score = 0.0
        
        if features.get('epigastric_pain'):
            score += 0.30
        if features.get('burning_quality'):
            score += 0.20
        if features.get('history_pud'):
            score += 0.35
        if features.get('nsaid_use'):
            score += 0.25
        
        # Nausea/vomiting
        if features.get('nausea_vomiting'):
            score += 0.15
        
        return min(score, 1.0)
    
    def _calculate_biliary_score(self, features: Dict, patient_data: PatientData) -> float:
        """
        Biliary colic / cholecystitis likelihood
        
        Risk factors (5 F's):
        - Female
        - Forty (age 40+)
        - Fertile (reproductive age)
        - Fat (obesity)
        - Fair (Caucasian)
        
        Plus:
        - RUQ pain
        - Postprandial (after fatty meals)
        - Radiation to back/right shoulder
        """
        score = 0.0
        
        if features.get('right_upper_quadrant_pain'):
            score += 0.35
        if features.get('female'):
            score += 0.15
        if features.get('age', 0) >= 40:
            score += 0.10
        if features.get('meal_related'):
            score += 0.25
        if features.get('back_radiation'):
            score += 0.20
        if features.get('history_gallstones'):
            score += 0.40
        
        # Check for Murphy's sign in physical exam (if available)
        # Check for elevated WBC (cholecystitis)
        if 'WBC' in patient_data.labs:
            wbc_values = patient_data.labs['WBC']
            latest_wbc = wbc_values[-1][1] if wbc_values else 0
            if latest_wbc > 11:
                score += 0.15
        
        return min(score, 1.0)
    
    def _calculate_pancreatitis_score(self, features: Dict, patient_data: PatientData) -> float:
        """
        Pancreatitis likelihood
        
        Diagnostic criteria (2 of 3):
        1. Epigastric pain radiating to back
        2. Lipase > 3x ULN
        3. Imaging findings
        
        Risk factors:
        - Alcohol use
        - Gallstones
        - Hypertriglyceridemia
        """
        score = 0.0
        criteria_met = 0
        
        # Criterion 1: Classic pain pattern
        if features.get('epigastric_pain') and features.get('back_radiation'):
            criteria_met += 1
            score += 0.35
        
        # Criterion 2: Elevated lipase/amylase
        if 'elevated_lipase' in features:
            lipase = features['elevated_lipase']
            if lipase > 180:  # > 3x ULN (normal ~60)
                criteria_met += 1
                score += 0.50
        elif 'elevated_amylase' in features:
            amylase = features['elevated_amylase']
            if amylase > 300:  # > 3x ULN
                criteria_met += 1
                score += 0.45
        
        # Risk factors
        if features.get('alcohol_use'):
            score += 0.20
        if features.get('history_gallstones'):
            score += 0.25
        
        # Need at least 1 criterion
        if criteria_met == 0:
            return 0.0
        
        return min(score, 1.0)
    
    def _create_gerd_hypothesis(self, score: float, features: Dict) -> DiagnosisResult:
        """Create GERD diagnosis hypothesis"""
        confidence = score
        
        # Determine risk level (GERD is typically low risk but can have complications)
        if confidence > 0.7:
            risk = RiskLevel.LOW
        else:
            risk = RiskLevel.LOW
        
        reasoning_parts = ["GERD/Esophageal reflux suggested by:"]
        if features.get('burning_quality'):
            reasoning_parts.append("- Burning retrosternal pain")
        if features.get('positional'):
            reasoning_parts.append("- Positional component (worse lying down)")
        if features.get('meal_related'):
            reasoning_parts.append("- Postprandial symptoms")
        if features.get('history_gerd'):
            reasoning_parts.append("- Known GERD history")
        
        reasoning = "\n".join(reasoning_parts)
        
        recommendations = [
            "Trial of PPI (omeprazole 20mg BID or pantoprazole 40mg daily)",
            "Lifestyle modifications: avoid large meals, elevate head of bed, avoid late-night eating",
            "Avoid triggers: caffeine, alcohol, chocolate, fatty foods, citrus",
            "If symptoms persist: upper endoscopy (EGD) to rule out Barrett's/stricture",
            "Consider H. pylori testing"
        ]
        
        # Add alarm features check
        if features.get('dysphagia') or features.get('age', 0) > 60:
            recommendations.insert(0, "⚠️ ALARM FEATURES: Urgent EGD recommended")
            risk = RiskLevel.MODERATE
        
        return DiagnosisResult(
            diagnosis=DiagnosisType.GERD,
            confidence=confidence,
            reasoning=reasoning,
            risk_level=risk,
            recommendations=recommendations,
            supporting_evidence={
                "gerd_score": score,
                "features": {k: v for k, v in features.items() if v and k != 'age'}
            },
            agent_name=self.name,
            depth=self.depth
        )
    
    def _create_spasm_hypothesis(self, score: float, features: Dict) -> DiagnosisResult:
        """Create esophageal spasm hypothesis"""
        return DiagnosisResult(
            diagnosis=DiagnosisType.ESOPHAGEAL_SPASM,
            confidence=score,
            reasoning="Esophageal spasm possible (requires manometry for diagnosis)",
            risk_level=RiskLevel.LOW,
            recommendations=[
                "Rule out cardiac causes first (troponin, EKG, stress test)",
                "If cardiac negative: esophageal manometry",
                "Trial of calcium channel blocker (diltiazem 30mg QID)",
                "Trial of nitrates (nitroglycerin SL PRN)",
                "Avoid triggers: hot/cold foods, rapid eating",
                "GI referral for definitive diagnosis"
            ],
            supporting_evidence={"spasm_score": score, "dysphagia": features.get('dysphagia', False)},
            agent_name=self.name,
            depth=self.depth
        )
    
    def _create_pud_hypothesis(self, score: float, features: Dict) -> DiagnosisResult:
        """Create peptic ulcer disease hypothesis"""
        risk = RiskLevel.MODERATE if features.get('history_pud') else RiskLevel.LOW
        
        return DiagnosisResult(
            diagnosis=DiagnosisType.PEPTIC_ULCER,
            confidence=score,
            reasoning="Peptic ulcer disease (gastric or duodenal ulcer) possible",
            risk_level=risk,
            recommendations=[
                "PPI therapy: pantoprazole 40mg BID or omeprazole 20mg BID",
                "Discontinue NSAIDs if using",
                "H. pylori testing (stool antigen or urea breath test)",
                "If H. pylori positive: triple therapy (PPI + clarithromycin + amoxicillin) x 14 days",
                "EGD if alarm features (age >60, bleeding, anemia, dysphagia, weight loss)",
                "Repeat EGD in 8-12 weeks to confirm healing if gastric ulcer"
            ],
            supporting_evidence={
                "pud_score": score,
                "epigastric_pain": features.get('epigastric_pain', False),
                "nsaid_use": features.get('nsaid_use', False)
            },
            agent_name=self.name,
            depth=self.depth
        )
    
    def _create_biliary_hypothesis(self, score: float, features: Dict) -> DiagnosisResult:
        """Create biliary colic/cholecystitis hypothesis"""
        # Higher risk if signs of cholecystitis (fever, elevated WBC)
        risk = RiskLevel.MODERATE
        
        reasoning_parts = ["Biliary colic/cholecystitis suggested by:"]
        if features.get('right_upper_quadrant_pain'):
            reasoning_parts.append("- Right upper quadrant pain")
        if features.get('meal_related'):
            reasoning_parts.append("- Postprandial (after fatty meals)")
        if features.get('female'):
            reasoning_parts.append("- Female sex (risk factor)")
        
        return DiagnosisResult(
            diagnosis=DiagnosisType.BILIARY_COLIC,
            confidence=score,
            reasoning="\n".join(reasoning_parts),
            risk_level=risk,
            recommendations=[
                "Right upper quadrant ultrasound (assess for gallstones, wall thickening)",
                "Labs: CBC, LFTs (ALT, AST, Alk Phos, bilirubin)",
                "If cholecystitis: NPO, IV fluids, IV antibiotics (ceftriaxone + metronidazole)",
                "Surgical consult for cholecystectomy",
                "If biliary colic (uncomplicated): elective cholecystectomy within 6 weeks",
                "Pain control: ketorolac or opioids"
            ],
            supporting_evidence={
                "biliary_score": score,
                "ruq_pain": features.get('right_upper_quadrant_pain', False),
                "history_gallstones": features.get('history_gallstones', False)
            },
            agent_name=self.name,
            depth=self.depth
        )
    
    def _create_pancreatitis_hypothesis(self, score: float, features: Dict) -> DiagnosisResult:
        """Create pancreatitis hypothesis"""
        # Pancreatitis is moderate-high risk
        risk = RiskLevel.HIGH if score > 0.7 else RiskLevel.MODERATE
        
        lipase = features.get('elevated_lipase', 'elevated')
        
        return DiagnosisResult(
            diagnosis=DiagnosisType.PANCREATITIS,
            confidence=score,
            reasoning=f"Pancreatitis likely: epigastric pain + elevated lipase ({lipase})",
            risk_level=risk,
            recommendations=[
                "⚠️ ADMIT TO HOSPITAL - Moderate to high risk condition",
                "NPO (nothing by mouth)",
                "IV fluid resuscitation (aggressive: 250-500 mL/hr LR)",
                "Pain control (IV opioids)",
                "CT abdomen with contrast (if diagnosis uncertain or severe disease)",
                "Ranson's criteria or BISAP score for severity assessment",
                "Check triglycerides, calcium",
                "RUQ ultrasound to rule out gallstone pancreatitis",
                "If gallstone pancreatitis: ERCP + cholecystectomy",
                "Monitor for complications: necrosis, pseudocyst, organ failure"
            ],
            supporting_evidence={
                "pancreatitis_score": score,
                "lipase": features.get('elevated_lipase'),
                "amylase": features.get('elevated_amylase'),
                "epigastric_pain": features.get('epigastric_pain', False)
            },
            agent_name=self.name,
            depth=self.depth
        )
    
    async def _identify_subspecialties(self, hypotheses: List[DiagnosisResult]) -> List[str]:
        """
        Identify if sub-agents needed
        
        Could spawn:
        - Hepatology agent (for liver disease)
        - Pancreatic agent (for complex pancreatitis)
        - IBD agent (for inflammatory bowel disease)
        
        For 12-hour hackathon, keep simple
        """
        subspecialties = []
        
        # If high suspicion of pancreatitis, could spawn pancreatic specialist
        for hyp in hypotheses:
            if hyp.diagnosis == DiagnosisType.PANCREATITIS and hyp.confidence > 0.7:
                # Could spawn PancreatitisAgent for severity assessment
                # subspecialties.append("Pancreatitis")
                pass
        
        return subspecialties
    
    def _create_child_agent(self, subspecialty_name: str) -> Optional[FractalAgent]:
        """Create sub-specialty agents"""
        # Placeholder for future expansion
        # if subspecialty_name == "Pancreatitis":
        #     return PancreatitisAgent(depth=self.depth + 1)
        return None
    
    async def _synthesize_results(
        self,
        hypotheses: List[DiagnosisResult],
        children_results: List[DiagnosisResult],
        patient_data: PatientData
    ) -> DiagnosisResult:
        """Synthesize GI diagnoses"""
        
        # If children provided results, consider them
        if children_results:
            best_child = max(children_results, key=lambda x: x.confidence)
            if best_child.confidence > 0.8:
                return best_child
        
        # Return best parent hypothesis
        if hypotheses:
            # Sort by confidence
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
            confidence=0.15,
            reasoning="GI etiology possible but uncertain - consider other causes",
            risk_level=RiskLevel.LOW,
            recommendations=["Cardiac workup first", "Outpatient GI evaluation if symptoms persist"],
            supporting_evidence={},
            agent_name=self.name,
            depth=self.depth
        )


class GERDAgent(FractalAgent):
    """
    Specialized GERD/Esophageal sub-agent
    
    Can differentiate between:
    - Uncomplicated GERD
    - Erosive esophagitis
    - Barrett's esophagus
    - Esophageal stricture
    """
    
    def __init__(self, depth: int = 1):
        super().__init__(
            specialty=SpecialtyType.GASTROENTEROLOGY,
            name="GERD Specialist Agent",
            depth=depth
        )
    
    async def _generate_hypotheses(self, patient_data: PatientData) -> List[DiagnosisResult]:
        """Detailed GERD evaluation"""
        # Placeholder - would implement detailed GERD subtyping
        return []
    
    async def _identify_subspecialties(self, hypotheses: List[DiagnosisResult]) -> List[str]:
        return []
    
    def _create_child_agent(self, subspecialty_name: str) -> Optional[FractalAgent]:
        return None
    
    async def _synthesize_results(
        self,
        hypotheses: List[DiagnosisResult],
        children_results: List[DiagnosisResult],
        patient_data: PatientData
    ) -> DiagnosisResult:
        """Synthesize GERD results"""
        if hypotheses:
            return max(hypotheses, key=lambda x: x.confidence)
        
        return DiagnosisResult(
            diagnosis=DiagnosisType.GERD,
            confidence=0.5,
            reasoning="GERD evaluation incomplete",
            risk_level=RiskLevel.LOW,
            recommendations=["EGD for definitive diagnosis"],
            supporting_evidence={},
            agent_name=self.name,
            depth=self.depth
        )
