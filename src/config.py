"""
MIMIQ - Medical Intelligence Multi-agent Inquiry Quest
Core configuration and constants
"""

import os
from pathlib import Path
from typing import Dict, List
from enum import Enum

# Project paths
PROJECT_ROOT = Path(__file__).parent.parent
DATA_DIR = PROJECT_ROOT / "datasets" / "mimic-iv-clinical-database-demo-2.2"
MODELS_DIR = PROJECT_ROOT / "models"
LOGS_DIR = PROJECT_ROOT / "logs"

# Create directories
MODELS_DIR.mkdir(exist_ok=True)
LOGS_DIR.mkdir(exist_ok=True)

# LLM Configuration
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "openai")  # openai, anthropic, local
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
LLM_MODEL = os.getenv("LLM_MODEL", "gpt-4-turbo-preview")
LLM_TEMPERATURE = 0.3  # Lower for more deterministic medical decisions

# Agent Configuration
MAX_FRACTAL_DEPTH = 3
CONFIDENCE_THRESHOLD = 0.85
SAFETY_OVERRIDE_PRIORITY = 1000

# Clinical Thresholds
TROPONIN_NORMAL = 0.04  # ng/mL
TROPONIN_ELEVATED = 0.05
TROPONIN_HIGH = 0.5

# ICD-9 Codes for Chest Pain Related Diagnoses
CHEST_PAIN_ICD9_CODES = {
    "41401": "Coronary atherosclerosis of native coronary artery",
    "41071": "Subendocardial infarction, initial episode of care",
    "78650": "Chest pain, unspecified",
    "78651": "Precordial pain",
    "41189": "Other acute and subacute forms of ischemic heart disease",
    "5329": "Unspecified gastroesophageal reflux",
    "5121": "Acute gastric ulcer with perforation",
    "4151": "Pulmonary embolism and infarction",
    "7330": "Osteoarthritis, generalized",
    "3000": "Anxiety state, unspecified",
}

# MIMIC-IV Data Paths
MIMIC_HOSP_DIR = DATA_DIR / "hosp"
MIMIC_ICU_DIR = DATA_DIR / "icu"

ADMISSIONS_CSV = MIMIC_HOSP_DIR / "admissions.csv"
PATIENTS_CSV = MIMIC_HOSP_DIR / "patients.csv"
DIAGNOSES_CSV = MIMIC_HOSP_DIR / "diagnoses_icd.csv"
LABEVENTS_CSV = MIMIC_HOSP_DIR / "labevents.csv"
D_ICD_DIAGNOSES_CSV = MIMIC_HOSP_DIR / "d_icd_diagnoses.csv"
ICUSTAYS_CSV = MIMIC_ICU_DIR / "icustays.csv"

class RiskLevel(str, Enum):
    """Risk stratification levels"""
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MODERATE = "MODERATE"
    LOW = "LOW"

class SpecialtyType(str, Enum):
    """Medical specialties"""
    CARDIOLOGY = "cardiology"
    GASTROENTEROLOGY = "gastroenterology"
    PULMONOLOGY = "pulmonology"
    MUSCULOSKELETAL = "musculoskeletal"
    PSYCHIATRY = "psychiatry"
    SAFETY = "safety"
    KNOWLEDGE = "knowledge"
    TREATMENT = "treatment"
    TRIAGE = "triage"

class DiagnosisType(str, Enum):
    """Diagnosis categories"""
    # Cardiac
    STEMI = "STEMI"
    NSTEMI = "NSTEMI"
    UNSTABLE_ANGINA = "Unstable Angina"
    STABLE_ANGINA = "Stable Angina"
    PERICARDITIS = "Pericarditis"
    MYOCARDITIS = "Myocarditis"
    
    # GI
    GERD = "GERD"
    PUD = "Peptic Ulcer Disease"
    ESOPHAGEAL_SPASM = "Esophageal Spasm"
    
    # Pulmonary
    PE = "Pulmonary Embolism"
    MASSIVE_PE = "Massive Pulmonary Embolism"
    PNEUMOTHORAX = "Pneumothorax"
    PNEUMONIA = "Pneumonia"
    PLEURISY = "Pleurisy"
    
    # MSK
    COSTOCHONDRITIS = "Costochondritis"
    MUSCLE_STRAIN = "Muscle Strain"
    RIB_FRACTURE = "Rib Fracture"
    
    # Psych
    PANIC_ATTACK = "Panic Attack"
    ANXIETY = "Anxiety Disorder"
    
    # Other
    UNKNOWN = "Unknown"

# HEART Score Components
HEART_SCORE_HISTORY = {
    "highly_suspicious": 2,
    "moderately_suspicious": 1,
    "slightly_suspicious": 0
}

HEART_SCORE_EKG = {
    "significant_st_depression": 2,
    "nonspecific_repolarization": 1,
    "normal": 0
}

HEART_SCORE_AGE = {
    ">=65": 2,
    "45-64": 1,
    "<45": 0
}

HEART_SCORE_RISK_FACTORS = {
    ">=3": 2,
    "1-2": 1,
    "0": 0
}

HEART_SCORE_TROPONIN = {
    ">=3x_normal": 2,
    "1-3x_normal": 1,
    "normal": 0
}

# Wells Score for PE
WELLS_CRITERIA = {
    "clinical_dvt": 3.0,
    "pe_most_likely": 3.0,
    "hr_gt_100": 1.5,
    "immobilization_surgery": 1.5,
    "previous_pe_dvt": 1.5,
    "hemoptysis": 1.0,
    "malignancy": 1.0
}

# Safety Monitor Critical Criteria
CRITICAL_ALERTS = {
    "STEMI": {
        "st_elevation": ">= 1mm in 2+ contiguous leads",
        "new_lbbb": "with symptoms",
        "action": "IMMEDIATE_CATH_LAB"
    },
    "MASSIVE_PE": {
        "hypotension": "SBP < 90",
        "hypoxia": "O2sat < 90%",
        "action": "THROMBOLYTICS/EMBOLECTOMY"
    },
    "SEPSIS": {
        "qsofa": ">= 2 (RR>=22, SBP<=100, AMS)",
        "action": "SEPSIS_BUNDLE"
    },
    "TAMPONADE": {
        "beck_triad": "hypotension + JVD + muffled sounds",
        "action": "PERICARDIOCENTESIS"
    }
}

# Logging Configuration
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_FORMAT = "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan> - <level>{message}</level>"
