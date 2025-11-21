# 🏗️ MIMIQ - Neuro-Fractal Multi-Agent Architecture

## Executive Summary

**MIMIQ (Medical Intelligence Multi-agent Inquiry Quest)** is a revolutionary diagnostic AI system that uses fractal agent decomposition and spiking neural networks to analyze chest pain presentations. Unlike traditional monolithic AI or simple multi-agent systems, MIMIQ dynamically spawns specialized micro-agents based on diagnostic uncertainty, mimicking the hierarchical reasoning of expert clinicians.

### Key Innovations
1. **Fractal Agent Spawning**: Parent agents spawn child agents recursively (e.g., Cardio → ACS → STEMI)
2. **SNN Temporal Processing**: Brian2-based spiking neural networks for EKG/vital sign analysis
3. **Safety-Critical Architecture**: Always-active safety monitor with override authority
4. **Memory Consolidation**: Shared diagnostic pattern memory across agents
5. **MCP-Native Design**: Each specialty as independent MCP server for modularity

---

## System Architecture

### High-Level Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                    MIMIQ SYSTEM BOUNDARY                         │
│                                                                   │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │              Master Orchestrator (LangGraph)              │   │
│  │  • Patient intake & triage                                │   │
│  │  • Agent routing & spawning                               │   │
│  │  • Diagnostic synthesis                                   │   │
│  └───────────────────────┬──────────────────────────────────┘   │
│                          │                                        │
│  ┌───────────────────────┴──────────────────────────────────┐   │
│  │            Safety Monitor (Always Active)                 │   │
│  │  • STEMI detection • Sepsis alert • PE risk               │   │
│  └──────────────────────────────────────────────────────────┘   │
│                          │                                        │
│       ┌──────────────────┼──────────────────┬────────────┐       │
│       ↓                  ↓                  ↓            ↓       │
│  ┌─────────┐       ┌─────────┐       ┌─────────┐  ┌─────────┐  │
│  │ Cardio  │       │ Gastro  │       │  Pulm   │  │   MSK   │  │
│  │  Agent  │       │  Agent  │       │  Agent  │  │  Agent  │  │
│  └────┬────┘       └─────────┘       └─────────┘  └─────────┘  │
│       │                                                          │
│  ┌────┴────┐  (Fractal Spawning)                                │
│  │   ACS   │                                                     │
│  │  Agent  │                                                     │
│  └────┬────┘                                                     │
│       │                                                          │
│  ┌────┴────┬─────────┐                                          │
│  │  STEMI  │ NSTEMI  │                                          │
│  │  Agent  │  Agent  │                                          │
│  └─────────┴─────────┘                                          │
│                                                                   │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │         Neuro-Fractal Processing Layer                    │   │
│  │  ┌─────────────┐  ┌──────────────┐  ┌─────────────────┐  │   │
│  │  │ SNN (Brian2)│  │ LSTM (PyTorch)│  │ Memory Store    │  │   │
│  │  │ EKG Pattern │  │ Lab Trends    │  │ (Redis/SQLite)  │  │   │
│  │  └─────────────┘  └──────────────┘  └─────────────────┘  │   │
│  └──────────────────────────────────────────────────────────┘   │
│                                                                   │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │                Data Layer (MIMIC-IV)                      │   │
│  │  • Admissions • Diagnoses • Labs • Vitals • EKG           │   │
│  └──────────────────────────────────────────────────────────┘   │
└───────────────────────────────────────────────────────────────────┘
```

---

## Component Specifications

### 1. Master Orchestrator Agent

**Technology**: LangGraph StateGraph
**Responsibilities**:
- Patient data intake (demographics, vitals, chief complaint)
- Initial symptom analysis and risk stratification
- Dynamic agent spawning based on symptom complexity
- Diagnostic synthesis from multiple agent outputs
- Final report generation

**State Schema**:
```python
class PatientState(TypedDict):
    patient_id: str
    age: int
    gender: str
    chief_complaint: str
    vitals: Dict[str, float]  # HR, BP, RR, O2sat, Temp
    labs: Dict[str, List[LabValue]]  # Serial measurements
    active_agents: List[str]
    diagnostic_hypotheses: List[Diagnosis]
    confidence_score: float
    safety_alerts: List[Alert]
```

**Routing Logic**:
```
IF chest_pain AND (troponin_elevated OR EKG_changes):
    spawn(CardioAgent, priority=HIGH)
IF chest_pain AND meal_related:
    spawn(GastroAgent, priority=MEDIUM)
IF chest_pain AND dyspnea AND hypoxia:
    spawn(PulmAgent, priority=HIGH)
IF chest_pain AND reproducible_palpation:
    spawn(MSKAgent, priority=LOW)
IF chest_pain AND psychiatric_history:
    spawn(AnxietyAgent, priority=MEDIUM)
```

---

### 2. Cardiology Micro-Agent

**Sub-Agents**: ACS, Arrhythmia, Heart Failure, Pericarditis, Valvular

#### 2.1 ACS Sub-Agent
**Clinical Rules**:
- **STEMI Criteria**: 
  - ST elevation ≥1mm in 2+ contiguous leads
  - New LBBB + symptoms
  - → Spawn STEMI agent (immediate cath lab alert)
  
- **NSTEMI Criteria**:
  - Troponin elevation (> 99th percentile)
  - ST depression or T-wave inversion
  - → Spawn NSTEMI agent (risk stratification)

- **Unstable Angina**:
  - Typical chest pain + negative biomarkers
  - → Conservative management pathway

**HEART Score Calculation**:
```
History: Highly suspicious (2), Moderately (1), Slightly (0)
EKG: ST changes (2), Non-specific (1), Normal (0)
Age: ≥65 (2), 45-64 (1), <45 (0)
Risk Factors: ≥3 (2), 1-2 (1), 0 (0)
Troponin: ≥3x normal (2), 1-3x (1), Normal (0)

Score 0-3: Low risk (2% MACE)
Score 4-6: Moderate risk (12% MACE)
Score 7-10: High risk (65% MACE)
```

**MCP Tools**:
- `assess_acs_risk(troponin, ekg, age, risk_factors) -> RiskLevel`
- `calculate_heart_score(patient_data) -> int`
- `recommend_intervention(risk_level) -> Treatment`

---

### 3. Gastroenterology Micro-Agent

**Sub-Agents**: GERD, PUD, Esophageal Spasm, Biliary Colic

**Clinical Rules**:
- **GERD**:
  - Burning chest pain
  - Worse after meals, lying down
  - Relief with antacids
  - → PPI trial recommendation

- **PUD**:
  - Epigastric pain
  - Relief with food (duodenal) or worse (gastric)
  - → H. pylori testing

**MCP Tools**:
- `assess_gi_etiology(symptoms, meal_relationship) -> Diagnosis`
- `recommend_ppi_trial() -> Treatment`

---

### 4. Pulmonary Micro-Agent

**Sub-Agents**: Pulmonary Embolism, Pneumothorax, Pneumonia, Pleurisy

**Clinical Rules**:
- **PE (Wells Score)**:
  ```
  Clinical signs of DVT: 3 points
  PE most likely diagnosis: 3 points
  HR > 100: 1.5 points
  Immobilization ≥3 days or surgery: 1.5 points
  Previous PE/DVT: 1.5 points
  Hemoptysis: 1 point
  Cancer: 1 point
  
  Score ≥4: High probability → D-dimer + CTA
  ```

- **Pneumothorax**:
  - Sudden onset pleuritic pain
  - Decreased breath sounds
  - → Chest X-ray

**MCP Tools**:
- `calculate_wells_score(patient_data) -> float`
- `assess_pe_risk(wells_score, d_dimer) -> RiskLevel`

---

### 5. MSK Micro-Agent

**Sub-Agents**: Costochondritis, Muscle Strain, Rib Fracture

**Clinical Rules**:
- **Costochondritis**:
  - Sharp, localized pain
  - Reproducible with palpation
  - No cardiac biomarkers
  - → NSAIDs recommendation

**MCP Tools**:
- `assess_msk_etiology(palpation_tenderness) -> Diagnosis`

---

### 6. Anxiety/Psych Micro-Agent

**Sub-Agents**: Panic Disorder, GAD, Somatic Symptom Disorder

**Clinical Rules**:
- **Panic Attack**:
  - Sudden onset chest tightness
  - Palpitations, dyspnea, dizziness
  - Psychiatric history
  - Negative cardiac workup
  - → Psychiatric referral + CBT

**MCP Tools**:
- `assess_anxiety_disorder(symptoms, psych_history) -> Diagnosis`

---

### 7. Safety Monitor Agent (Critical)

**Always Active - Highest Priority**

**Critical Alerts**:
```python
STEMI_CRITERIA = {
    "ST_elevation": ">1mm in 2+ leads",
    "action": "IMMEDIATE_CATH_LAB"
}

MASSIVE_PE_CRITERIA = {
    "hypotension": "SBP < 90",
    "hypoxia": "O2sat < 90%",
    "action": "THROMBOLYTICS/EMBOLECTOMY"
}

SEPSIS_CRITERIA = {
    "qSOFA": "≥2 (RR≥22, SBP≤100, altered mental status)",
    "action": "SEPSIS_BUNDLE"
}

CARDIAC_TAMPONADE = {
    "beck_triad": "hypotension + JVD + muffled heart sounds",
    "action": "PERICARDIOCENTESIS"
}
```

**Override Authority**: Can interrupt any agent and escalate to emergency protocol

---

## Neuro-Fractal Processing Layer

### Spiking Neural Network (Brian2)

**Purpose**: Real-time EKG pattern recognition

**Architecture**:
```
Input Layer: 12-lead EKG (digitized @ 500Hz)
         ↓
Leaky Integrate-and-Fire Neurons (1000 neurons)
         ↓
STDP Learning (Spike-Timing-Dependent Plasticity)
         ↓
Output: ST-elevation, T-wave inversion, QRS widening
```

**Implementation**:
```python
from brian2 import *

# EKG spiking encoder
ekg_neurons = NeuronGroup(1000, 
    '''dv/dt = (ge - v) / tau : volt
       dge/dt = -ge/tau_e : volt
       tau : second
       tau_e : second''',
    threshold='v > -50*mV',
    reset='v = -70*mV')

# STDP learning for pattern recognition
stdp = Synapses(input_layer, ekg_neurons,
    '''w : volt
       dapre/dt = -apre/tau_pre : volt
       dapost/dt = -apost/tau_post : volt''',
    on_pre='''ge += w
              apre += A_pre
              w = clip(w + apost, 0, w_max)''',
    on_post='''apost += A_post
               w = clip(w + apre, 0, w_max)''')
```

---

### LSTM Lab Trend Predictor (PyTorch)

**Purpose**: Predict troponin/BNP trends from serial measurements

**Architecture**:
```
Input: [time, troponin_value, BNP_value, creatinine]
         ↓
LSTM (2 layers, 128 hidden units)
         ↓
Attention Mechanism (focus on recent values)
         ↓
Output: [rising_trend_prob, falling_trend_prob, stable_prob]
```

**Training Data**: MIMIC-IV patients with serial troponin measurements

---

### Memory Consolidation Layer

**Purpose**: Store and retrieve successful diagnostic patterns

**Implementation**: 
- **Vector Database**: ChromaDB/Pinecone for semantic search
- **Storage**: Patient features + diagnosis + outcome
- **Retrieval**: K-nearest neighbors based on symptom embedding
- **Replay**: Show similar cases to agents for learning

**Schema**:
```python
class DiagnosticMemory:
    patient_embedding: np.array  # 512-dim vector
    symptoms: List[str]
    labs: Dict[str, float]
    final_diagnosis: str
    confidence: float
    outcome: str  # "correct", "missed", "false_positive"
    timestamp: datetime
```

---

## Fractal Spawning Mechanism

**Concept**: Agents spawn child agents when encountering sub-problems

**Spawning Logic**:
```python
class FractalAgent:
    def __init__(self, specialty, depth=0, max_depth=3):
        self.specialty = specialty
        self.depth = depth
        self.max_depth = max_depth
        self.children = []
    
    def analyze(self, patient_state):
        # Perform specialty-specific analysis
        hypotheses = self.generate_hypotheses(patient_state)
        
        # If uncertainty is high and depth allows, spawn children
        if self.uncertainty > 0.5 and self.depth < self.max_depth:
            for hypothesis in hypotheses:
                child = self.spawn_child(hypothesis.subspecialty)
                child_result = child.analyze(patient_state)
                self.children.append(child_result)
        
        # Synthesize results from children
        return self.synthesize(hypotheses, self.children)
    
    def spawn_child(self, subspecialty):
        return FractalAgent(subspecialty, 
                           depth=self.depth + 1, 
                           max_depth=self.max_depth)
```

**Example**:
```
CardioAgent (depth=0, uncertainty=0.7)
    ↓ spawns
ACSAgent (depth=1, uncertainty=0.6)
    ↓ spawns
STEMIAgent (depth=2, uncertainty=0.2) ← High confidence, stops
NSTEMIAgent (depth=2, uncertainty=0.3) ← High confidence, stops
```

**Termination Criteria**:
1. Diagnostic confidence > 0.85
2. Max depth reached (3 levels)
3. No relevant sub-agents available
4. Safety monitor override

---

## MCP Server Deployment

### Server Structure

```
mcp_servers/
├── orchestrator/
│   ├── server.py
│   ├── tools.py (route_patient, synthesize_diagnosis)
│   └── prompts.py
├── cardio/
│   ├── server.py
│   ├── tools.py (assess_acs, calculate_heart_score)
│   ├── models/
│   │   └── troponin_lstm.pth
│   └── clinical_rules.yaml
├── gastro/
│   ├── server.py
│   └── tools.py (assess_gerd, assess_pud)
├── pulm/
│   ├── server.py
│   └── tools.py (calculate_wells, assess_pe)
├── msk/
│   ├── server.py
│   └── tools.py (assess_costochondritis)
├── safety/
│   ├── server.py
│   └── tools.py (check_stemi, check_sepsis)
└── docker-compose.yml
```

### MCP Tool Specification

**Example: Cardio Server**

```python
# mcp_servers/cardio/tools.py
from mcp import Tool

@Tool(
    name="assess_acs_risk",
    description="Assesses acute coronary syndrome risk using HEART score",
    parameters={
        "troponin": {"type": "number", "description": "Troponin level (ng/mL)"},
        "ekg_findings": {"type": "string", "enum": ["normal", "non_specific", "st_changes"]},
        "age": {"type": "integer"},
        "risk_factors": {"type": "array", "items": {"type": "string"}},
    },
    required=["troponin", "ekg_findings", "age"]
)
def assess_acs_risk(troponin, ekg_findings, age, risk_factors=[]):
    heart_score = calculate_heart_score(troponin, ekg_findings, age, risk_factors)
    
    if heart_score <= 3:
        return {"risk": "LOW", "recommendation": "Discharge with outpatient follow-up"}
    elif heart_score <= 6:
        return {"risk": "MODERATE", "recommendation": "Observation + serial troponins"}
    else:
        return {"risk": "HIGH", "recommendation": "Admission + cardiology consult"}
```

### Inter-Server Communication

**Message Protocol** (JSON):
```json
{
    "sender": "orchestrator",
    "recipient": "cardio_agent",
    "message_type": "analysis_request",
    "patient_id": "10004235",
    "data": {
        "vitals": {"HR": 110, "BP": "140/90"},
        "labs": {"troponin": 0.5},
        "symptoms": ["chest pain", "dyspnea"]
    },
    "priority": "HIGH",
    "timestamp": "2025-11-21T10:30:00Z"
}
```

---

## Data Flow Example

**Patient Presentation**: 65yo male with substernal chest pain x 2 hours

```
1. Master Orchestrator receives patient
   ├─ Vital signs: HR 95, BP 150/85, O2 98%
   ├─ Chief complaint: "crushing chest pain"
   └─ Risk factors: DM, HTN, smoker

2. Safety Monitor: No immediate critical alerts

3. Orchestrator spawns Cardio Agent (high priority)
   └─ Cardio Agent analyzes:
      ├─ Symptom pattern: Typical angina (score: 0.9)
      ├─ Labs: Troponin 0.05 (normal), awaiting repeat
      └─ EKG: Non-specific ST changes

4. Cardio Agent spawns ACS Sub-Agent
   └─ ACS Agent:
      ├─ HEART score calculation: 6 (moderate risk)
      ├─ Recommendation: Serial troponins, observation
      └─ Does NOT spawn STEMI/NSTEMI (low confidence)

5. Orchestrator also spawns Gastro Agent (medium priority)
   └─ Gastro Agent:
      ├─ Meal relationship: None reported
      ├─ Antacid response: Not tried
      └─ Confidence: 0.3 (low)

6. 3-hour troponin returns: 0.15 (elevated)
   ├─ Safety Monitor: NSTEMI alert!
   ├─ Cardio Agent confidence now 0.95
   └─ ACS Agent spawns NSTEMI Sub-Agent
      └─ NSTEMI Agent:
         ├─ Risk stratification: TIMI score 4
         ├─ Recommendation: Cath lab within 24hr
         └─ Treatment: Dual antiplatelet + anticoagulation

7. Final Synthesis:
   └─ Orchestrator combines:
      ├─ Primary: NSTEMI (confidence 0.95)
      ├─ Secondary: Rule out GERD (confidence 0.3)
      └─ Action: Admit to cardiology, cath lab scheduled
```

---

## Performance Metrics

**Target Metrics**:
- **Latency**: < 30 seconds for initial triage
- **Accuracy**: > 90% concordance with discharge diagnoses
- **Safety**: 100% sensitivity for STEMI/massive PE/sepsis
- **Scalability**: Handle 100 concurrent patients
- **Explainability**: Traceable decision paths

**Evaluation Dataset**:
- MIMIC-IV chest pain admissions (N ≈ 500)
- Ground truth: ICD-9/10 discharge diagnoses
- Metrics: Precision, Recall, F1, AUC-ROC

---

## Novel Contributions

1. **First fractal multi-agent medical AI**: Hierarchical agent spawning
2. **SNN integration for EKG**: Neuromorphic computing in clinical AI
3. **Safety-critical architecture**: Dedicated override agent
4. **MCP-native clinical agents**: Modular, interoperable specialty servers
5. **Memory consolidation**: Cross-agent learning from past cases

---

## Future Enhancements

1. **Federated Learning**: Train on multi-hospital data while preserving privacy
2. **Reinforcement Learning**: Agents learn from outcomes (reward = correct diagnosis)
3. **Multimodal Fusion**: Integrate chest X-ray/CT with structured data
4. **Natural Language Reports**: Generate human-readable diagnostic narratives
5. **Real-time Streaming**: Process continuous EKG/vital sign streams

---

## Regulatory Considerations

**Current Status**: Research prototype (not FDA-approved)

**Path to Clinical Deployment**:
1. **Validation Study**: Prospective trial comparing MIMIQ vs. physician diagnosis
2. **Safety Audit**: Independent review of safety monitor logic
3. **FDA 510(k)**: Clinical decision support software (Class II device)
4. **HIPAA Compliance**: De-identification, encryption, access controls
5. **Continuous Monitoring**: Post-deployment performance tracking

---

## Technology Stack Summary

| Component | Technology | Purpose |
|-----------|-----------|---------|
| Agent Orchestration | LangGraph | State management, routing |
| LLM Backend | OpenAI/Anthropic/Local | Natural language reasoning |
| SNN Framework | Brian2 | EKG pattern recognition |
| Deep Learning | PyTorch | Lab trend prediction |
| Vector DB | ChromaDB | Memory consolidation |
| MCP Servers | FastAPI + MCP SDK | Modular agent deployment |
| Data Storage | PostgreSQL | MIMIC-IV structured data |
| Time-Series DB | InfluxDB (optional) | Vitals streaming |
| Deployment | Docker Compose | Multi-container orchestration |
| Testing | pytest + hypothesis | Unit + property-based tests |
| Monitoring | Prometheus + Grafana | System health metrics |

---

**Version**: 1.0  
**Last Updated**: 2025-11-21  
**Authors**: MIMIQ Development Team  
**License**: MIT (for research purposes)
