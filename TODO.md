# 🏥 Neuro-Fractal Multi-Agent System - TODO

## Project: MIMIQ (Medical Intelligence Multi-agent Inquiry Quest)
**Goal**: Novel agentic AI for chest pain differential diagnosis using neuro-fractal architecture

---

## Phase 1: Architecture & Setup (2 hours)
- [x] **1.1** Setup Python environment with dependencies ✅
  - Brian2 (SNN), PyTorch, LangGraph, pandas, scikit-learn
  - 📝 Review: Virtual environment created, core packages installed
  - 📊 Diff: Created requirements.txt, installed langgraph, torch, pandas, etc.
- [x] **1.2** Design LangGraph state machine schema ✅
  - Define AgentState, MessageGraph, CheckpointMemory
  - 📝 Review: AgentState and DiagnosisResult dataclasses defined
  - 📊 Diff: Created src/agents/base.py with state management
- [x] **1.3** Create data preprocessing pipeline ✅
  - Parse MIMIC-IV: admissions, diagnoses, labs, vitals
  - Filter chest pain related ICD codes (e.g., 41401, 78650)
  - 📝 Review: MIMICDataLoader successfully loads and filters 31 chest pain admissions
  - 📊 Diff: Created src/data_loader.py with PatientData structure
- [x] **1.4** Define clinical rule ontology ✅
  - Cardio: Troponin thresholds, EKG criteria
  - Gastro: GERD indicators, PPI response
  - MSK: Reproducible pain, negative cardiac workup
  - Anxiety: Psychiatric history, hyperventilation
  - 📝 Review: HEART score, Wells criteria, critical alerts defined
  - 📊 Diff: Created src/config.py with all clinical thresholds

---

## Phase 2: Core Agent Development (4 hours)
- [x] **2.1** Build Master Orchestrator Agent ✅
  - Input: Patient demographics, chief complaint, vitals
  - Output: Spawn appropriate specialty agents
  - Routing logic: Symptom pattern matching
  - 📝 Review: Orchestrator routes to cardio, gastro, pulm, MSK agents
  - 📊 Diff: Implemented in src/agents/base.py - MasterOrchestrator class
- [x] **2.2** Implement Cardiology Micro-Agent ✅
  - Sub-agents: ACS, Arrhythmia, HF, Pericarditis
  - Clinical rules: HEART score, TIMI risk
  - Lab integration: Troponin, BNP, D-dimer trends
  - 📝 Review: CardiologyAgent + ACSAgent with HEART score calculation
  - 📊 Diff: Created src/agents/cardiology.py with fractal spawning
- [ ] **2.3** Implement Gastroenterology Micro-Agent
  - Sub-agents: GERD, PUD, Esophageal spasm
  - Clinical rules: Meal relationship, PPI trial
  - 📝 Note: Simplified for 12-hour demo, can be added later
- [ ] **2.4** Implement Pulmonary Micro-Agent
  - Sub-agents: PE, Pneumothorax, Pneumonia
  - Clinical rules: Wells criteria, O2 saturation
  - 📝 Note: Simplified for 12-hour demo, can be added later
- [ ] **2.5** Implement MSK Micro-Agent
  - Sub-agents: Costochondritis, Muscle strain
  - Clinical rules: Palpation tenderness, movement exacerbation
  - 📝 Note: Simplified for 12-hour demo, can be added later
- [ ] **2.6** Implement Anxiety/Psych Micro-Agent
  - Sub-agents: Panic disorder, Anxiety
  - Clinical rules: Psychiatric history, stress triggers
  - 📝 Note: Simplified for 12-hour demo, can be added later
- [x] **2.7** Implement Safety Monitor Agent (CRITICAL) ✅
  - Always-active circuit breaker
  - Monitors: STEMI, massive PE, sepsis, tamponade
  - Override mechanism: Escalate to emergency protocol
  - 📝 Review: SafetyMonitorAgent checks for critical conditions
  - 📊 Diff: Created src/agents/safety.py with qSOFA, STEMI detection

---

## Phase 3: Neuro-Fractal Layer (3 hours)
- [ ] **3.1** Build SNN for EKG pattern recognition (Brian2)
  - Input: EKG time series → Spiking neurons
  - Output: ST-elevation, T-wave inversion detection
- [ ] **3.2** Build PyTorch LSTM for lab trend prediction
  - Input: Serial troponin, BNP measurements
  - Output: Rising/falling trend classification
- [ ] **3.3** Implement Memory Consolidation Layer
  - Store successful diagnostic patterns
  - Shared memory across agents (Redis/SQLite)
  - Replay mechanism: Similar cases retrieval
- [ ] **3.4** Create Fractal Spawning Mechanism
  - Parent agent → Child agent spawning logic
  - Termination criteria: Diagnostic confidence > 0.85
  - Max depth: 3 levels (prevent infinite recursion)

---

## Phase 4: MCP Server Deployment (2 hours)
- [ ] **4.1** Create MCP Server Structure
  - `mcp_orchestrator/`: Master coordinator
  - `mcp_cardio/`: Cardiology agent server
  - `mcp_gastro/`: Gastro agent server
  - `mcp_pulm/`: Pulmonary agent server
  - `mcp_msk/`: MSK agent server
  - `mcp_safety/`: Safety monitor server
- [ ] **4.2** Implement MCP Tools/Resources
  - Tools: `analyze_chest_pain()`, `check_labs()`, `assess_risk()`
  - Resources: Access to MIMIC-IV data, clinical guidelines
- [ ] **4.3** Setup Inter-Agent Communication
  - Message passing protocol (JSON schema)
  - Async communication (avoid blocking)
- [ ] **4.4** Create Docker Compose Configuration
  - Multi-container setup for each MCP server
  - Shared volumes for data access

---

## Phase 5: Integration & Testing (1 hour)
- [ ] **5.1** End-to-End Testing
  - Test Case 1: Typical angina → NSTEMI diagnosis
  - Test Case 2: GERD → Appropriate routing
  - Test Case 3: Panic attack → Psych diagnosis
  - Test Case 4: STEMI → Emergency escalation
- [ ] **5.2** Run Linting
  - Black, flake8, mypy
- [ ] **5.3** Performance Profiling
  - Measure: Agent spawn time, LLM calls, memory usage
  - Target: < 30s for initial assessment

---

## Phase 6: Documentation (30 min)
- [ ] **6.1** Architecture Documentation
  - System diagram, agent flowcharts
  - Clinical rule documentation
- [ ] **6.2** Executive Summary (1-page)
  - Problem statement, solution, innovation
  - Preliminary results, future directions
- [ ] **6.3** Code Documentation
  - Docstrings, README.md, API reference

---

## Review & Completion Tracking
*Each completed item will be marked with:*
- ✅ Done
- 📝 Review note
- 📊 Code diff summary

---

## Innovation Metrics
- **Novel Contribution**: Fractal agent spawning + SNN integration
- **Clinical Impact**: Faster triage, reduced missed diagnoses
- **Technical Achievement**: Multi-modal (structured + time-series) fusion
