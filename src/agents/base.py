"""
Base fractal agent class and orchestrator
"""

from typing import Dict, List, Optional, Any, TypedDict
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
import asyncio
from loguru import logger

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from config import (
    MAX_FRACTAL_DEPTH, CONFIDENCE_THRESHOLD, 
    SpecialtyType, DiagnosisType, RiskLevel
)
from data_loader import PatientData

@dataclass
class DiagnosisResult:
    """Result from an agent's analysis"""
    diagnosis: DiagnosisType
    confidence: float
    reasoning: str
    risk_level: RiskLevel
    recommendations: List[str]
    supporting_evidence: Dict[str, Any]
    agent_name: str
    depth: int
    children_results: List['DiagnosisResult'] = field(default_factory=list)

@dataclass
class AgentState:
    """State passed between agents in LangGraph"""
    patient_data: PatientData
    active_agents: List[str] = field(default_factory=list)
    diagnosis_results: List[DiagnosisResult] = field(default_factory=list)
    safety_alerts: List[str] = field(default_factory=list)
    confidence: float = 0.0
    current_depth: int = 0

class FractalAgent(ABC):
    """
    Base class for all fractal agents
    
    Each agent can:
    1. Analyze patient data
    2. Spawn child agents if uncertainty is high
    3. Synthesize results from children
    """
    
    def __init__(
        self, 
        specialty: SpecialtyType,
        name: str,
        depth: int = 0,
        max_depth: int = MAX_FRACTAL_DEPTH,
        confidence_threshold: float = CONFIDENCE_THRESHOLD
    ):
        self.specialty = specialty
        self.name = name
        self.depth = depth
        self.max_depth = max_depth
        self.confidence_threshold = confidence_threshold
        self.children: List['FractalAgent'] = []
        
        logger.info(f"Initialized {self.name} at depth {self.depth}")
    
    async def analyze(self, patient_data: PatientData) -> DiagnosisResult:
        """
        Main analysis method
        
        1. Generate hypotheses
        2. If uncertain, spawn children
        3. Synthesize results
        """
        logger.info(f"{self.name} analyzing patient {patient_data.patient_id}")
        
        # Generate initial hypotheses
        hypotheses = await self._generate_hypotheses(patient_data)
        
        # Calculate uncertainty (entropy)
        uncertainty = self._calculate_uncertainty(hypotheses)
        
        logger.debug(f"{self.name} uncertainty: {uncertainty:.2f}")
        
        # Spawn children if needed
        children_results = []
        if uncertainty > (1 - self.confidence_threshold) and self.depth < self.max_depth:
            children_results = await self._spawn_and_analyze_children(patient_data, hypotheses)
        
        # Synthesize final result
        final_result = await self._synthesize_results(hypotheses, children_results, patient_data)
        final_result.depth = self.depth
        final_result.children_results = children_results
        
        logger.info(
            f"{self.name} completed: {final_result.diagnosis} "
            f"(confidence: {final_result.confidence:.2f})"
        )
        
        return final_result
    
    @abstractmethod
    async def _generate_hypotheses(self, patient_data: PatientData) -> List[DiagnosisResult]:
        """Generate diagnostic hypotheses (specialty-specific)"""
        pass
    
    @abstractmethod
    async def _identify_subspecialties(self, hypotheses: List[DiagnosisResult]) -> List[str]:
        """Identify which sub-agents to spawn"""
        pass
    
    def _calculate_uncertainty(self, hypotheses: List[DiagnosisResult]) -> float:
        """
        Calculate diagnostic uncertainty using entropy
        
        Higher entropy = more uncertainty = need for sub-agents
        """
        if not hypotheses:
            return 1.0
        
        # Normalize confidences
        total_conf = sum(h.confidence for h in hypotheses)
        if total_conf == 0:
            return 1.0
        
        probs = [h.confidence / total_conf for h in hypotheses]
        
        # Calculate entropy
        import numpy as np
        entropy = -sum(p * np.log2(p + 1e-10) for p in probs if p > 0)
        
        # Normalize to [0, 1]
        max_entropy = np.log2(len(hypotheses)) if len(hypotheses) > 1 else 1
        normalized_entropy = entropy / max_entropy if max_entropy > 0 else 0
        
        return normalized_entropy
    
    async def _spawn_and_analyze_children(
        self, 
        patient_data: PatientData,
        hypotheses: List[DiagnosisResult]
    ) -> List[DiagnosisResult]:
        """Spawn child agents and gather their results"""
        
        subspecialties = await self._identify_subspecialties(hypotheses)
        
        logger.info(f"{self.name} spawning {len(subspecialties)} child agents")
        
        # Create child agents
        tasks = []
        for subspecialty_name in subspecialties:
            child_agent = self._create_child_agent(subspecialty_name)
            if child_agent:
                self.children.append(child_agent)
                tasks.append(child_agent.analyze(patient_data))
        
        # Run children in parallel
        if tasks:
            results = await asyncio.gather(*tasks, return_exceptions=True)
            # Filter out exceptions
            return [r for r in results if isinstance(r, DiagnosisResult)]
        
        return []
    
    @abstractmethod
    def _create_child_agent(self, subspecialty_name: str) -> Optional['FractalAgent']:
        """Factory method to create child agents"""
        pass
    
    @abstractmethod
    async def _synthesize_results(
        self,
        hypotheses: List[DiagnosisResult],
        children_results: List[DiagnosisResult],
        patient_data: PatientData
    ) -> DiagnosisResult:
        """Combine parent and children results into final diagnosis"""
        pass
    
    def get_tree_structure(self, indent: int = 0) -> str:
        """Get a string representation of the agent tree"""
        tree = "  " * indent + f"└─ {self.name} (depth={self.depth})\n"
        for child in self.children:
            tree += child.get_tree_structure(indent + 1)
        return tree


class MasterOrchestrator:
    """
    Top-level orchestrator that routes patients to appropriate specialty agents
    """
    
    def __init__(self):
        self.name = "Master Orchestrator"
        self.specialty_agents = {}
        logger.info("Initialized Master Orchestrator")
    
    def register_agent(self, specialty: SpecialtyType, agent: FractalAgent):
        """Register a specialty agent"""
        self.specialty_agents[specialty] = agent
        logger.info(f"Registered {agent.name} for {specialty}")
    
    async def orchestrate(self, patient_data: PatientData) -> AgentState:
        """
        Main orchestration logic
        
        1. Analyze patient data
        2. Route to appropriate specialty agents
        3. Collect and synthesize results
        """
        logger.info(f"Orchestrating diagnosis for patient {patient_data.patient_id}")
        
        # Initialize state
        state = AgentState(
            patient_data=patient_data,
            active_agents=[],
            diagnosis_results=[],
            safety_alerts=[],
            confidence=0.0,
            current_depth=0
        )
        
        # Determine which agents to activate
        agents_to_activate = self._route_patient(patient_data)
        
        logger.info(f"Activating {len(agents_to_activate)} specialty agents")
        
        # Run agents in parallel
        tasks = []
        for specialty in agents_to_activate:
            if specialty in self.specialty_agents:
                agent = self.specialty_agents[specialty]
                state.active_agents.append(agent.name)
                tasks.append(agent.analyze(patient_data))
        
        # Gather results
        if tasks:
            results = await asyncio.gather(*tasks, return_exceptions=True)
            state.diagnosis_results = [
                r for r in results if isinstance(r, DiagnosisResult)
            ]
        
        # Synthesize final diagnosis
        state = self._synthesize_final_diagnosis(state)
        
        logger.success(
            f"Orchestration complete for patient {patient_data.patient_id}. "
            f"Final confidence: {state.confidence:.2f}"
        )
        
        return state
    
    def _route_patient(self, patient_data: PatientData) -> List[SpecialtyType]:
        """
        Determine which specialty agents to activate based on presentation
        
        For chest pain, we typically consider:
        - Cardiology (always for chest pain)
        - Gastroenterology (if meal-related symptoms)
        - Pulmonology (if dyspnea)
        - MSK (if reproducible with palpation)
        - Psychiatry (if psych history)
        """
        agents = [SpecialtyType.CARDIOLOGY]  # Always check cardiac first
        
        # Add other specialties based on symptoms/history
        # In a full implementation, this would use NLP on chief complaint
        
        # For demo, activate multiple agents
        agents.extend([
            SpecialtyType.GASTROENTEROLOGY,
            SpecialtyType.PULMONOLOGY,
            SpecialtyType.MUSCULOSKELETAL
        ])
        
        return agents
    
    def _synthesize_final_diagnosis(self, state: AgentState) -> AgentState:
        """
        Synthesize results from all specialty agents
        
        Priority order:
        1. Highest risk level
        2. Highest confidence
        3. Most specific diagnosis
        """
        if not state.diagnosis_results:
            state.confidence = 0.0
            return state
        
        # Sort by risk level (descending) then confidence (descending)
        risk_priority = {
            RiskLevel.CRITICAL: 4,
            RiskLevel.HIGH: 3,
            RiskLevel.MODERATE: 2,
            RiskLevel.LOW: 1
        }
        
        sorted_results = sorted(
            state.diagnosis_results,
            key=lambda x: (risk_priority.get(x.risk_level, 0), x.confidence),
            reverse=True
        )
        
        # Top diagnosis
        state.confidence = sorted_results[0].confidence if sorted_results else 0.0
        
        return state
    
    def get_diagnosis_tree(self, state: AgentState) -> str:
        """Get a hierarchical view of all agent decisions"""
        tree = f"{self.name}\n"
        for result in state.diagnosis_results:
            tree += f"\n{result.agent_name}:\n"
            tree += f"  Diagnosis: {result.diagnosis}\n"
            tree += f"  Confidence: {result.confidence:.2f}\n"
            tree += f"  Risk: {result.risk_level}\n"
            
            if result.children_results:
                tree += "  Children:\n"
                for child in result.children_results:
                    tree += f"    - {child.agent_name}: {child.diagnosis} ({child.confidence:.2f})\n"
        
        return tree
