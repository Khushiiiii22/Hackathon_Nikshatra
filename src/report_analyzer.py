"""
Comprehensive Medical Report Analyzer
Analyzes medical reports using all 6 specialist agents and LLM service
"""

import json
from typing import Dict, List, Any, Optional
from loguru import logger

from src.llm_service import LLMService
from src.agents.base import MasterOrchestrator
from src.agents.cardiology import CardiologyAgent
from src.agents.gastro import GastroenterologyAgent
from src.agents.musculoskeletal import MusculoskeletalAgent
from src.agents.pulmonary import PulmonaryAgent
from src.agents.triage import TriageAgent
from src.agents.safety import SafetyMonitorAgent


class ComprehensiveReportAnalyzer:
    """Analyzes medical reports using all specialist agents and generates comprehensive doctor-level summary"""
    
    def __init__(self):
        # Initialize LLM service
        self.llm_service = LLMService()
        
        # Initialize all 6 specialist agents
        self.agents = {
            'cardiology': CardiologyAgent(),
            'gastroenterology': GastroenterologyAgent(),
            'musculoskeletal': MusculoskeletalAgent(),
            'pulmonary': PulmonaryAgent(),
            'triage': TriageAgent(),
            'safety': SafetyMonitorAgent()
        }
        
        # Initialize orchestrator
        self.orchestrator = MasterOrchestrator(
            cardiology=self.agents['cardiology'],
            gastro=self.agents['gastroenterology'],
            msk=self.agents['musculoskeletal'],
            pulmonary=self.agents['pulmonary'],
            triage=self.agents['triage'],
            safety=self.agents['safety']
        )
        
        logger.info("ComprehensiveReportAnalyzer initialized with 6 specialist agents")
    
    def analyze_all_reports(self, reports: List[Dict[str, Any]], patient_info: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Analyze all uploaded medical reports comprehensively
        
        Args:
            reports: List of report dictionaries with 'filename', 'content', and 'type'
            patient_info: Optional patient information
        
        Returns:
            Comprehensive analysis with all agent results and doctor summary
        """
        try:
            logger.info(f"Analyzing {len(reports)} reports with all 6 specialist agents")
            
            # Collect all report contents
            all_report_data = "\n\n=== COMBINED MEDICAL REPORTS ===\n\n"
            for i, report in enumerate(reports, 1):
                all_report_data += f"\n--- Report {i}: {report.get('filename', 'Unknown')} ---\n"
                all_report_data += report.get('content', '')
                all_report_data += "\n"
            
            # Step 1: Run through all specialist agents
            logger.info("Step 1: Running specialist agent analysis...")
            agent_results = {}
            
            for agent_name, agent in self.agents.items():
                try:
                    logger.info(f"Running {agent_name} agent...")
                    # Each agent analyzes the combined reports
                    result = agent.analyze(all_report_data, patient_info=patient_info)
                    agent_results[agent_name] = result
                except Exception as e:
                    logger.error(f"Error in {agent_name} agent: {str(e)}")
                    agent_results[agent_name] = {
                        'error': str(e),
                        'status': 'failed'
                    }
            
            # Step 2: Use LLM service for comprehensive medical analysis
            logger.info("Step 2: Generating comprehensive medical analysis...")
            llm_analysis = self.llm_service.analyze_report(
                report_data=all_report_data,
                patient_info=patient_info
            )
            
            # Step 3: Combine all insights into doctor-level summary
            logger.info("Step 3: Creating comprehensive doctor summary...")
            comprehensive_summary = self._create_doctor_summary(
                agent_results=agent_results,
                llm_analysis=llm_analysis,
                reports_count=len(reports)
            )
            
            return {
                'success': True,
                'reports_analyzed': len(reports),
                'agent_results': agent_results,
                'llm_analysis': llm_analysis.get('analysis', {}) if llm_analysis.get('success') else {},
                'comprehensive_summary': comprehensive_summary,
                'timestamp': self._get_timestamp()
            }
            
        except Exception as e:
            logger.error(f"Error in comprehensive analysis: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'reports_analyzed': 0
            }
    
    def _create_doctor_summary(self, agent_results: Dict, llm_analysis: Dict, reports_count: int) -> Dict[str, Any]:
        """
        Create a comprehensive doctor-level summary combining all agent insights
        """
        try:
            # Extract key information from LLM analysis
            analysis_data = llm_analysis.get('analysis', {}) if llm_analysis.get('success') else {}
            
            # Compile symptoms from all agents and LLM
            all_symptoms = []
            if 'symptoms_detected' in analysis_data:
                all_symptoms.extend(analysis_data['symptoms_detected'])
            
            # Compile prevention strategies
            all_prevention_tips = []
            if 'prevention_strategies' in analysis_data:
                all_prevention_tips.extend(analysis_data['prevention_strategies'])
            
            # Extract findings from each specialist agent
            specialist_findings = {}
            for agent_name, result in agent_results.items():
                if result.get('status') != 'failed':
                    specialist_findings[agent_name] = {
                        'assessment': result.get('assessment', 'No specific findings'),
                        'recommendations': result.get('recommendations', []),
                        'risk_level': result.get('risk_level', 'unknown')
                    }
            
            # Create comprehensive summary
            summary = {
                'patient_brief': analysis_data.get('patient_brief', f"Comprehensive analysis of {reports_count} medical report(s) completed by 6 specialist AI agents acting as professional doctors."),
                'overall_summary': analysis_data.get('summary', 'Medical reports have been analyzed by cardiology, gastroenterology, musculoskeletal, pulmonary, triage, and safety specialists.'),
                'key_findings': analysis_data.get('key_findings', []),
                'symptoms_identified': all_symptoms if all_symptoms else ['Please refer to specialist findings'],
                'abnormalities_detected': analysis_data.get('abnormalities', []),
                'risk_assessment': analysis_data.get('risk_assessment', {'level': 'unknown', 'reasoning': 'Refer to specialist assessments'}),
                'specialist_insights': specialist_findings,
                'clinical_recommendations': analysis_data.get('clinical_recommendations', []),
                'prevention_strategies': all_prevention_tips if all_prevention_tips else [
                    "Maintain regular health checkups",
                    "Follow prescribed medications",
                    "Adopt healthy lifestyle habits",
                    "Monitor symptoms regularly",
                    "Consult healthcare provider for any concerns"
                ],
                'follow_up_advice': analysis_data.get('follow_up', 'Schedule follow-up appointment with your healthcare provider to discuss these findings.'),
                'reports_analyzed_count': reports_count,
                'specialists_consulted': list(self.agents.keys())
            }
            
            return summary
            
        except Exception as e:
            logger.error(f"Error creating doctor summary: {str(e)}")
            return {
                'error': 'Error generating summary',
                'details': str(e)
            }
    
    def _get_timestamp(self) -> str:
        """Get current timestamp"""
        from datetime import datetime
        return datetime.now().isoformat()


# Convenience function for quick analysis
def analyze_medical_reports(reports: List[Dict[str, Any]], patient_info: Optional[Dict] = None) -> Dict[str, Any]:
    """
    Convenience function to analyze medical reports
    
    Args:
        reports: List of report dictionaries
        patient_info: Optional patient information
    
    Returns:
        Comprehensive analysis results
    """
    analyzer = ComprehensiveReportAnalyzer()
    return analyzer.analyze_all_reports(reports, patient_info)
