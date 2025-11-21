"""
Data preprocessing and loading utilities for MIMIC-IV dataset
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple
from pathlib import Path
from loguru import logger
from dataclasses import dataclass
from datetime import datetime
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from config import (
    ADMISSIONS_CSV, PATIENTS_CSV, DIAGNOSES_CSV, LABEVENTS_CSV,
    D_ICD_DIAGNOSES_CSV, ICUSTAYS_CSV, CHEST_PAIN_ICD9_CODES
)

@dataclass
class PatientData:
    """Structured patient data"""
    patient_id: str
    hadm_id: str
    age: int
    gender: str
    chief_complaint: str
    admission_time: datetime
    vitals: Dict[str, float]
    labs: Dict[str, List[Tuple[datetime, float]]]  # Lab name -> [(time, value)]
    diagnoses: List[str]
    icd_codes: List[str]
    
class MIMICDataLoader:
    """Load and preprocess MIMIC-IV data for chest pain patients"""
    
    def __init__(self):
        self.admissions = None
        self.patients = None
        self.diagnoses = None
        self.labevents = None
        self.d_icd = None
        self.icustays = None
        
        logger.info("Initializing MIMIC-IV data loader")
        
    def load_all(self):
        """Load all required MIMIC-IV tables"""
        logger.info("Loading MIMIC-IV datasets...")
        
        try:
            self.admissions = pd.read_csv(ADMISSIONS_CSV)
            logger.info(f"Loaded {len(self.admissions)} admissions")
            
            self.patients = pd.read_csv(PATIENTS_CSV)
            logger.info(f"Loaded {len(self.patients)} patients")
            
            self.diagnoses = pd.read_csv(DIAGNOSES_CSV)
            logger.info(f"Loaded {len(self.diagnoses)} diagnoses")
            
            # Load lab events (may be large)
            logger.info("Loading lab events (this may take a moment)...")
            self.labevents = pd.read_csv(LABEVENTS_CSV)
            logger.info(f"Loaded {len(self.labevents)} lab events")
            
            self.d_icd = pd.read_csv(D_ICD_DIAGNOSES_CSV)
            logger.info(f"Loaded {len(self.d_icd)} ICD diagnosis codes")
            
            self.icustays = pd.read_csv(ICUSTAYS_CSV)
            logger.info(f"Loaded {len(self.icustays)} ICU stays")
            
            logger.success("All datasets loaded successfully")
            
        except Exception as e:
            logger.error(f"Error loading datasets: {e}")
            raise
    
    def filter_chest_pain_patients(self) -> pd.DataFrame:
        """Filter patients with chest pain related diagnoses"""
        if self.diagnoses is None:
            raise ValueError("Diagnoses not loaded. Call load_all() first.")
        
        # Filter by ICD codes related to chest pain
        chest_pain_codes = list(CHEST_PAIN_ICD9_CODES.keys())
        chest_pain_dx = self.diagnoses[
            self.diagnoses['icd_code'].isin(chest_pain_codes)
        ]
        
        logger.info(f"Found {len(chest_pain_dx)} chest pain diagnoses")
        
        # Get unique admissions
        chest_pain_hadm_ids = chest_pain_dx['hadm_id'].unique()
        
        # Get admission details
        chest_pain_admissions = self.admissions[
            self.admissions['hadm_id'].isin(chest_pain_hadm_ids)
        ]
        
        logger.info(f"Found {len(chest_pain_admissions)} chest pain admissions")
        
        return chest_pain_admissions
    
    def get_patient_data(self, hadm_id: int) -> Optional[PatientData]:
        """Get comprehensive data for a specific admission"""
        try:
            # Get admission info
            admission = self.admissions[self.admissions['hadm_id'] == hadm_id].iloc[0]
            subject_id = admission['subject_id']
            
            # Get patient demographics
            patient = self.patients[self.patients['subject_id'] == subject_id].iloc[0]
            
            # Calculate age at admission
            anchor_age = patient['anchor_age']
            anchor_year = patient['anchor_year']
            admit_year = pd.to_datetime(admission['admittime']).year
            age = anchor_age + (admit_year - anchor_year)
            
            # Get diagnoses
            patient_dx = self.diagnoses[self.diagnoses['hadm_id'] == hadm_id]
            icd_codes = patient_dx['icd_code'].tolist()
            
            # Map ICD codes to descriptions
            dx_descriptions = []
            for code in icd_codes:
                dx_info = self.d_icd[self.d_icd['icd_code'] == code]
                if not dx_info.empty:
                    dx_descriptions.append(dx_info.iloc[0]['long_title'])
            
            # Get lab values
            labs = self._get_lab_values(subject_id, hadm_id)
            
            # Create structured patient data
            patient_data = PatientData(
                patient_id=str(subject_id),
                hadm_id=str(hadm_id),
                age=int(age),
                gender=patient['gender'],
                chief_complaint="chest pain",  # Inferred from diagnosis codes
                admission_time=pd.to_datetime(admission['admittime']),
                vitals=self._simulate_vitals(),  # MIMIC demo may not have all vitals
                labs=labs,
                diagnoses=dx_descriptions,
                icd_codes=icd_codes
            )
            
            return patient_data
            
        except Exception as e:
            logger.error(f"Error getting patient data for hadm_id {hadm_id}: {e}")
            return None
    
    def _get_lab_values(self, subject_id: int, hadm_id: int) -> Dict[str, List[Tuple[datetime, float]]]:
        """Extract lab values for a patient"""
        patient_labs = self.labevents[
            (self.labevents['subject_id'] == subject_id) &
            (self.labevents['hadm_id'] == hadm_id)
        ]
        
        labs_dict = {}
        
        # Key lab tests
        important_labs = {
            51222: 'Hemoglobin',
            51265: 'Platelet Count',
            50912: 'Creatinine',
            50902: 'Chloride',
            50971: 'Potassium',
            50983: 'Sodium',
            50931: 'Glucose',
            50878: 'AST',
            50861: 'ALT',
            51237: 'INR',
            51274: 'PT',
            51275: 'PTT',
        }
        
        # Note: MIMIC demo may not have troponin/BNP
        # In production, itemid for troponin would be ~51003
        
        for itemid, lab_name in important_labs.items():
            lab_values = patient_labs[patient_labs['itemid'] == itemid]
            if not lab_values.empty:
                values = []
                for _, row in lab_values.iterrows():
                    if pd.notna(row['valuenum']):
                        time = pd.to_datetime(row['charttime'])
                        values.append((time, float(row['valuenum'])))
                
                if values:
                    labs_dict[lab_name] = sorted(values, key=lambda x: x[0])
        
        # Simulate troponin for demo purposes (in real MIMIC-IV full version, this exists)
        labs_dict['Troponin'] = self._simulate_troponin()
        labs_dict['BNP'] = self._simulate_bnp()
        
        return labs_dict
    
    def _simulate_vitals(self) -> Dict[str, float]:
        """Simulate vital signs (demo dataset may not have all)"""
        # In production, these would come from chartevents
        return {
            'heart_rate': np.random.randint(60, 120),
            'systolic_bp': np.random.randint(100, 160),
            'diastolic_bp': np.random.randint(60, 100),
            'respiratory_rate': np.random.randint(12, 24),
            'o2_saturation': np.random.randint(92, 100),
            'temperature': round(np.random.uniform(36.5, 38.5), 1)
        }
    
    def _simulate_troponin(self) -> List[Tuple[datetime, float]]:
        """Simulate serial troponin measurements"""
        now = datetime.now()
        
        # Simulate 3 serial troponins
        baseline = np.random.choice([0.02, 0.03, 0.04, 0.08, 0.15, 0.5])
        
        if baseline < 0.05:  # Normal
            return [
                (now, baseline),
                (now, baseline + np.random.uniform(-0.01, 0.01)),
                (now, baseline + np.random.uniform(-0.01, 0.01))
            ]
        else:  # Elevated - simulate rising trend
            return [
                (now, baseline),
                (now, baseline * 1.5),
                (now, baseline * 2.0)
            ]
    
    def _simulate_bnp(self) -> List[Tuple[datetime, float]]:
        """Simulate BNP measurement"""
        now = datetime.now()
        bnp_value = np.random.choice([50, 100, 200, 500, 1000])
        return [(now, bnp_value)]
    
    def get_sample_patients(self, n: int = 10) -> List[PatientData]:
        """Get a sample of chest pain patients for testing"""
        chest_pain_admissions = self.filter_chest_pain_patients()
        
        sample_hadm_ids = chest_pain_admissions['hadm_id'].sample(
            min(n, len(chest_pain_admissions))
        ).tolist()
        
        patients = []
        for hadm_id in sample_hadm_ids:
            patient_data = self.get_patient_data(hadm_id)
            if patient_data:
                patients.append(patient_data)
        
        logger.info(f"Loaded {len(patients)} sample patients")
        return patients

# Utility functions
def format_patient_summary(patient: PatientData) -> str:
    """Format patient data as a readable summary"""
    summary = f"""
Patient ID: {patient.patient_id}
Admission ID: {patient.hadm_id}
Demographics: {patient.age}yo {patient.gender}
Chief Complaint: {patient.chief_complaint}
Admission Time: {patient.admission_time}

Vital Signs:
- Heart Rate: {patient.vitals.get('heart_rate', 'N/A')} bpm
- Blood Pressure: {patient.vitals.get('systolic_bp', 'N/A')}/{patient.vitals.get('diastolic_bp', 'N/A')} mmHg
- Respiratory Rate: {patient.vitals.get('respiratory_rate', 'N/A')} /min
- O2 Saturation: {patient.vitals.get('o2_saturation', 'N/A')}%
- Temperature: {patient.vitals.get('temperature', 'N/A')}°C

Key Labs:
"""
    
    for lab_name, values in patient.labs.items():
        if values:
            latest_value = values[-1][1]
            summary += f"- {lab_name}: {latest_value}\n"
    
    summary += f"\nFinal Diagnoses: {', '.join(patient.diagnoses[:3])}\n"
    
    return summary

def calculate_troponin_trend(troponin_values: List[Tuple[datetime, float]]) -> str:
    """Determine if troponin is rising, falling, or stable"""
    if len(troponin_values) < 2:
        return "insufficient_data"
    
    values = [v[1] for v in troponin_values]
    
    # Check trend
    first_half = np.mean(values[:len(values)//2])
    second_half = np.mean(values[len(values)//2:])
    
    if second_half > first_half * 1.2:
        return "rising"
    elif second_half < first_half * 0.8:
        return "falling"
    else:
        return "stable"
