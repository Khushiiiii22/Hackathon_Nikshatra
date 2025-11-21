"""
MIMIQ Demo - Test the neuro-fractal multi-agent system
"""

import asyncio
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from loguru import logger
from config import LOG_LEVEL, LOG_FORMAT, LOGS_DIR
from data_loader import MIMICDataLoader, format_patient_summary
from agents.base import MasterOrchestrator
from agents.cardiology import CardiologyAgent
from agents.safety import SafetyMonitorAgent

# Configure logging
logger.remove()
logger.add(sys.stderr, format=LOG_FORMAT, level=LOG_LEVEL)
logger.add(LOGS_DIR / "mimiq.log", format=LOG_FORMAT, level="DEBUG", rotation="10 MB")


async def main():
    """Main demo function"""
    
    logger.info("=" * 80)
    logger.info("MIMIQ - Medical Intelligence Multi-agent Inquiry Quest")
    logger.info("Neuro-Fractal Multi-Agent System for Chest Pain Diagnosis")
    logger.info("=" * 80)
    
    # Step 1: Load MIMIC-IV data
    logger.info("\n📊 Step 1: Loading MIMIC-IV dataset...")
    data_loader = MIMICDataLoader()
    data_loader.load_all()
    
    # Step 2: Get sample chest pain patients
    logger.info("\n🏥 Step 2: Filtering chest pain patients...")
    sample_patients = data_loader.get_sample_patients(n=3)
    
    if not sample_patients:
        logger.error("No chest pain patients found in dataset!")
        return
    
    logger.success(f"Found {len(sample_patients)} chest pain patients for analysis")
    
    # Step 3: Initialize agent system
    logger.info("\n🤖 Step 3: Initializing Multi-Agent System...")
    orchestrator = MasterOrchestrator()
    
    # Register specialty agents
    cardio_agent = CardiologyAgent(depth=0)
    safety_agent = SafetyMonitorAgent()
    
    orchestrator.register_agent("cardiology", cardio_agent)
    orchestrator.register_agent("safety", safety_agent)
    
    logger.success("Agent system initialized")
    
    # Step 4: Analyze patients
    logger.info("\n🔬 Step 4: Analyzing patients...")
    
    for i, patient in enumerate(sample_patients, 1):
        logger.info(f"\n{'='*80}")
        logger.info(f"PATIENT {i}/{len(sample_patients)}")
        logger.info(f"{'='*80}")
        
        # Print patient summary
        summary = format_patient_summary(patient)
        print(summary)
        
        # Safety check first
        logger.info("\n🚨 Running Safety Monitor...")
        safety_result = await safety_agent.analyze(patient)
        
        if safety_agent.has_critical_alerts():
            logger.critical(f"\n⚠️  CRITICAL ALERTS: {', '.join(safety_agent.get_alerts())}")
            logger.critical(f"Diagnosis: {safety_result.diagnosis}")
            logger.critical(f"Confidence: {safety_result.confidence:.1%}")
            logger.critical(f"Risk Level: {safety_result.risk_level}")
            logger.critical("\nRecommendations:")
            for rec in safety_result.recommendations:
                logger.critical(f"  • {rec}")
        else:
            logger.info("✓ No critical safety alerts")
        
        # Run orchestrator
        logger.info("\n🎯 Running Diagnostic Orchestration...")
        state = await orchestrator.orchestrate(patient)
        
        # Print results
        logger.info(f"\n📋 DIAGNOSTIC RESULTS")
        logger.info(f"{'─'*80}")
        
        if state.diagnosis_results:
            for result in sorted(state.diagnosis_results, key=lambda x: x.confidence, reverse=True):
                logger.info(f"\n{result.agent_name}:")
                logger.info(f"  Diagnosis: {result.diagnosis}")
                logger.info(f"  Confidence: {result.confidence:.1%}")
                logger.info(f"  Risk Level: {result.risk_level}")
                logger.info(f"  Reasoning: {result.reasoning}")
                logger.info(f"  Recommendations:")
                for rec in result.recommendations[:3]:
                    logger.info(f"    • {rec}")
                
                if result.children_results:
                    logger.info(f"  Sub-agent results:")
                    for child in result.children_results:
                        logger.info(f"    └─ {child.agent_name}: {child.diagnosis} ({child.confidence:.1%})")
        
        logger.info(f"\n{'─'*80}")
        logger.info(f"Final Confidence: {state.confidence:.1%}")
        logger.info(f"Active Agents: {', '.join(state.active_agents)}")
        
        # Print ground truth
        if patient.diagnoses:
            logger.info(f"\n📚 Ground Truth Diagnoses:")
            for dx in patient.diagnoses[:3]:
                logger.info(f"  • {dx}")
        
        # Print agent tree
        logger.info(f"\n🌳 Agent Execution Tree:")
        tree = orchestrator.get_diagnosis_tree(state)
        print(tree)
        
        logger.info(f"\n{'='*80}\n")
    
    logger.success("\n✅ Demo completed successfully!")
    logger.info("\nNext steps:")
    logger.info("  1. Review results in logs/mimiq.log")
    logger.info("  2. Tune confidence thresholds")
    logger.info("  3. Add more specialty agents")
    logger.info("  4. Implement SNN for EKG analysis")
    logger.info("  5. Deploy as MCP servers")


if __name__ == "__main__":
    asyncio.run(main())
