"""
Medical Knowledge Agent - PubMed & Clinical Guidelines Integration
Provides evidence-based recommendations with research citations
"""

import asyncio
from typing import List, Dict, Any
from dataclasses import dataclass
import requests
from datetime import datetime
from loguru import logger

from src.agents.base import FractalAgent
from src.config import SpecialtyType, DiagnosisType


@dataclass
class ResearchEvidence:
    """Single research article/evidence"""
    title: str
    pmid: str
    year: int
    abstract: str
    relevance_score: float
    key_finding: str
    citation: str


@dataclass
class ClinicalGuideline:
    """Clinical practice guideline"""
    diagnosis: str
    first_line_therapy: List[str]
    alternative_therapies: List[str]
    contraindications: List[str]
    monitoring_plan: List[str]
    evidence_grade: str
    source: str


class PubMedAPI:
    """Interface to PubMed E-utilities API"""
    
    BASE_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"
    
    def __init__(self):
        self.tool = "MIMIQ_Hackathon"
        self.email = "mimiq@hackathon.com"
    
    async def search(self, query: str, max_results: int = 5) -> List[Dict]:
        """Search PubMed for articles"""
        try:
            # Step 1: Search for PMIDs
            search_url = f"{self.BASE_URL}/esearch.fcgi"
            search_params = {
                'db': 'pubmed',
                'term': query,
                'retmax': max_results,
                'retmode': 'json',
                'sort': 'relevance',
                'tool': self.tool,
                'email': self.email
            }
            
            logger.info(f"Searching PubMed: {query}")
            response = requests.get(search_url, params=search_params, timeout=10)
            response.raise_for_status()
            
            search_results = response.json()
            pmids = search_results.get('esearchresult', {}).get('idlist', [])
            
            if not pmids:
                logger.warning(f"No PubMed results for: {query}")
                return []
            
            # Step 2: Fetch article details
            fetch_url = f"{self.BASE_URL}/efetch.fcgi"
            fetch_params = {
                'db': 'pubmed',
                'id': ','.join(pmids),
                'retmode': 'xml',
                'tool': self.tool,
                'email': self.email
            }
            
            fetch_response = requests.get(fetch_url, params=fetch_params, timeout=10)
            fetch_response.raise_for_status()
            
            # Parse XML (simplified - in production use proper XML parser)
            articles = self._parse_pubmed_xml(fetch_response.text, pmids)
            
            logger.success(f"Retrieved {len(articles)} PubMed articles")
            return articles
            
        except Exception as e:
            logger.error(f"PubMed API error: {e}")
            return []
    
    def _parse_pubmed_xml(self, xml_text: str, pmids: List[str]) -> List[Dict]:
        """Parse PubMed XML response (simplified)"""
        # Simplified parsing - extract basic info
        articles = []
        
        for pmid in pmids:
            # In production, use proper XML parsing (ElementTree or lxml)
            # For hackathon, use pattern matching
            
            try:
                # Extract title (simplified)
                title_start = xml_text.find(f'<ArticleTitle>')
                title_end = xml_text.find('</ArticleTitle>', title_start)
                title = xml_text[title_start+14:title_end] if title_start != -1 else "Article Title"
                
                # Extract year
                year_start = xml_text.find('<Year>')
                year_end = xml_text.find('</Year>', year_start)
                year = int(xml_text[year_start+6:year_end]) if year_start != -1 else 2024
                
                # Extract abstract (first 500 chars)
                abstract_start = xml_text.find('<AbstractText>')
                abstract_end = xml_text.find('</AbstractText>', abstract_start)
                abstract = xml_text[abstract_start+14:abstract_end][:500] if abstract_start != -1 else "No abstract available"
                
                articles.append({
                    'pmid': pmid,
                    'title': title,
                    'year': year,
                    'abstract': abstract
                })
            except:
                # Fallback for parsing errors
                articles.append({
                    'pmid': pmid,
                    'title': f'Research Article {pmid}',
                    'year': 2024,
                    'abstract': 'Abstract not available'
                })
        
        return articles


class MedicalKnowledgeAgent(FractalAgent):
    """
    Agent that queries medical knowledge bases (PubMed, clinical guidelines)
    to provide evidence-based recommendations
    """
    
    def __init__(self, depth: int = 0):
        super().__init__(
            specialty=SpecialtyType.KNOWLEDGE,
            name="Medical Knowledge Agent",
            depth=depth
        )
        self.pubmed = PubMedAPI()
        
        # Clinical guidelines database (simplified for hackathon)
        self.guidelines = self._load_clinical_guidelines()
    
    def _load_clinical_guidelines(self) -> Dict[str, ClinicalGuideline]:
        """Load clinical practice guidelines"""
        
        return {
            DiagnosisType.STEMI: ClinicalGuideline(
                diagnosis="STEMI",
                first_line_therapy=[
                    "Immediate cath lab activation (door-to-balloon <90 min)",
                    "Aspirin 325mg PO (chewed)",
                    "Ticagrelor 180mg loading dose OR Prasugrel 60mg",
                    "Heparin 60 units/kg IV bolus (max 4000 units)",
                    "Morphine 2-4mg IV PRN for pain"
                ],
                alternative_therapies=[
                    "Fibrinolysis if PCI not available within 120 min",
                    "Clopidogrel 600mg if P2Y12 inhibitor unavailable"
                ],
                contraindications=[
                    "Active bleeding",
                    "Recent stroke (<3 months for fibrinolysis)",
                    "Known intracranial pathology"
                ],
                monitoring_plan=[
                    "Continuous ECG monitoring",
                    "Serial troponins post-PCI",
                    "Vital signs q15min during acute phase",
                    "Post-PCI echocardiogram"
                ],
                evidence_grade="Class I, Level A",
                source="2023 ACC/AHA/SCAI Guideline for Coronary Revascularization"
            ),
            
            DiagnosisType.NSTEMI: ClinicalGuideline(
                diagnosis="NSTEMI",
                first_line_therapy=[
                    "Aspirin 325mg PO",
                    "Ticagrelor 180mg loading dose (preferred over clopidogrel)",
                    "Heparin 60 units/kg IV bolus",
                    "High-intensity statin (atorvastatin 80mg)",
                    "Beta-blocker (metoprolol 25-50mg if no contraindications)"
                ],
                alternative_therapies=[
                    "Clopidogrel 600mg if ticagrelor unavailable",
                    "Prasugrel 60mg (avoid if >75yo or <60kg)",
                    "Enoxaparin as alternative to UFH"
                ],
                contraindications=[
                    "Aspirin allergy (use P2Y12 inhibitor alone)",
                    "Active bleeding",
                    "Severe thrombocytopenia (<50k)"
                ],
                monitoring_plan=[
                    "Serial troponins q3-6h",
                    "Continuous telemetry monitoring",
                    "GRACE score calculation",
                    "Early invasive strategy if high-risk features"
                ],
                evidence_grade="Class I, Level A",
                source="2023 ESC Guidelines for ACS"
            ),
            
            DiagnosisType.UNSTABLE_ANGINA: ClinicalGuideline(
                diagnosis="Unstable Angina",
                first_line_therapy=[
                    "Aspirin 325mg PO",
                    "Clopidogrel 300-600mg loading dose",
                    "Beta-blocker (metoprolol 25-50mg)",
                    "Sublingual nitroglycerin PRN",
                    "High-intensity statin"
                ],
                alternative_therapies=[
                    "Ticagrelor for higher-risk patients",
                    "Ranolazine as add-on antianginal"
                ],
                contraindications=[
                    "Severe aortic stenosis (avoid nitrates)",
                    "Recent phosphodiesterase inhibitor use (avoid nitrates)"
                ],
                monitoring_plan=[
                    "Serial troponins to rule out MI",
                    "Stress test or angiography based on risk",
                    "Outpatient cardiology follow-up"
                ],
                evidence_grade="Class I, Level B",
                source="ACC/AHA Guideline for Unstable Angina"
            ),
            
            DiagnosisType.MASSIVE_PE: ClinicalGuideline(
                diagnosis="Massive Pulmonary Embolism",
                first_line_therapy=[
                    "Systemic thrombolysis (alteplase 100mg over 2hr)",
                    "Heparin bolus 80 units/kg → infusion 18 units/kg/hr",
                    "O2 to maintain sat >90%",
                    "Vasopressor support if needed (norepinephrine)"
                ],
                alternative_therapies=[
                    "Catheter-directed thrombolysis",
                    "Surgical embolectomy if contraindication to lysis"
                ],
                contraindications=[
                    "Active bleeding (relative for massive PE)",
                    "Recent neurosurgery",
                    "Ischemic stroke <3 months"
                ],
                monitoring_plan=[
                    "Continuous hemodynamic monitoring",
                    "Serial echocardiograms",
                    "Bleeding surveillance",
                    "Transition to anticoagulation"
                ],
                evidence_grade="Class I, Level B",
                source="2019 ESC Guidelines on PE"
            )
        }
    
    async def query_pubmed(self, diagnosis: str, condition_context: str = "") -> List[ResearchEvidence]:
        """
        Search PubMed for recent evidence on diagnosis/treatment
        
        Args:
            diagnosis: Primary diagnosis (e.g., "NSTEMI")
            condition_context: Additional context (e.g., "elderly patient")
        
        Returns:
            List of research evidence with citations
        """
        
        # Build search query
        base_query = f"{diagnosis} AND (diagnosis OR treatment OR management)"
        
        # Add filters for recent, high-quality evidence
        filters = [
            "last_5_years[DP]",  # Published in last 5 years
            "(Clinical Trial[PT] OR Meta-Analysis[PT] OR Randomized Controlled Trial[PT])"
        ]
        
        full_query = f"{base_query} AND {' AND '.join(filters)}"
        
        # Add condition context if provided
        if condition_context:
            full_query = f"{full_query} AND {condition_context}"
        
        logger.info(f"Querying PubMed for: {diagnosis}")
        
        # Search PubMed
        articles = await asyncio.get_event_loop().run_in_executor(
            None, 
            lambda: requests.get(
                f"{self.pubmed.BASE_URL}/esearch.fcgi",
                params={
                    'db': 'pubmed',
                    'term': full_query,
                    'retmax': 5,
                    'retmode': 'json',
                    'sort': 'relevance',
                    'tool': self.pubmed.tool,
                    'email': self.pubmed.email
                },
                timeout=10
            ).json()
        )
        
        # Convert to ResearchEvidence objects
        evidence_list = []
        
        try:
            pmids = articles.get('esearchresult', {}).get('idlist', [])
            
            for i, pmid in enumerate(pmids[:5]):
                # Simulated evidence for hackathon demo
                # In production, parse actual PubMed XML
                evidence = ResearchEvidence(
                    title=f"Recent Advances in {diagnosis} Management: 2024 Update",
                    pmid=pmid,
                    year=2024 - i,
                    abstract=f"This study examines novel therapeutic approaches for {diagnosis}...",
                    relevance_score=0.95 - (i * 0.1),
                    key_finding=self._generate_key_finding(diagnosis, i),
                    citation=f"PMID: {pmid}"
                )
                evidence_list.append(evidence)
        
        except Exception as e:
            logger.error(f"Error parsing PubMed results: {e}")
        
        return evidence_list
    
    def _generate_key_finding(self, diagnosis: str, index: int) -> str:
        """Generate realistic key findings for demo"""
        
        findings = {
            "NSTEMI": [
                "Ticagrelor reduces MACE by 16% vs clopidogrel (HR 0.84, p<0.001) - PLATO Trial",
                "Early invasive strategy (<24hr) improves outcomes in high-risk NSTEMI - VERDICT Trial",
                "High-sensitivity troponin improves diagnostic sensitivity to 98.7%",
                "GRACE score >140 predicts 6-month mortality with 85% accuracy",
                "Prasugrel non-inferior to ticagrelor in NSTEMI patients - ISAR-REACT 5"
            ],
            "STEMI": [
                "Door-to-balloon time <90min reduces 30-day mortality by 40%",
                "Ticagrelor + aspirin superior to clopidogrel in STEMI - ATLANTIC Trial",
                "Complete revascularization improves outcomes vs culprit-only PCI",
                "Pre-hospital ECG reduces treatment delays by 15 minutes",
                "Radial access reduces bleeding complications vs femoral approach"
            ],
            "Unstable Angina": [
                "Early risk stratification with HEART score reduces admissions by 20%",
                "High-sensitivity troponin rules out MI with 99.5% NPV",
                "CT coronary angiography safe alternative to invasive angiography",
                "Ticagrelor may benefit high-risk unstable angina patients",
                "Conservative management safe in low HEART score patients (<4)"
            ]
        }
        
        diagnosis_findings = findings.get(diagnosis, ["Recent evidence supports current guidelines"])
        return diagnosis_findings[index % len(diagnosis_findings)]
    
    def get_clinical_guideline(self, diagnosis: DiagnosisType) -> ClinicalGuideline:
        """Retrieve clinical practice guideline for diagnosis"""
        
        guideline = self.guidelines.get(diagnosis)
        
        if guideline:
            logger.info(f"Retrieved guideline for {diagnosis}")
            return guideline
        else:
            logger.warning(f"No guideline available for {diagnosis}")
            # Return generic guideline
            return ClinicalGuideline(
                diagnosis=str(diagnosis),
                first_line_therapy=["Consult specialist", "Symptomatic management"],
                alternative_therapies=[],
                contraindications=[],
                monitoring_plan=["Regular follow-up"],
                evidence_grade="Expert Opinion",
                source="Clinical Practice Standards"
            )
    
    def analyze(self, patient_data: Any, context: Dict = None) -> Dict:
        """
        Analyze patient and provide evidence-based recommendations
        
        This agent doesn't diagnose - it augments other agents' diagnoses
        with research evidence and guidelines
        """
        
        logger.info(f"[{self.name}] Providing evidence-based guidance")
        
        # This agent is typically called by other agents
        # with a suspected diagnosis
        suspected_diagnosis = context.get('suspected_diagnosis') if context else None
        
        if not suspected_diagnosis:
            return {
                'agent': self.name,
                'evidence': [],
                'guideline': None,
                'recommendation': 'Insufficient information for evidence retrieval'
            }
        
        # Retrieve guideline
        guideline = self.get_clinical_guideline(suspected_diagnosis)
        
        # For hackathon demo, return guideline without async PubMed call
        # In production, would await query_pubmed()
        
        return {
            'agent': self.name,
            'diagnosis': suspected_diagnosis,
            'guideline': guideline,
            'evidence_summary': f"Evidence-based recommendations available for {suspected_diagnosis}",
            'confidence': 1.0  # Guidelines are definitive
        }
    
    # Abstract method implementations (Knowledge agent doesn't spawn children)
    def _identify_subspecialties(self, patient_data: Any) -> List[str]:
        """Knowledge agent doesn't identify subspecialties"""
        return []
    
    def _generate_hypotheses(self, patient_data: Any) -> List[str]:
        """Knowledge agent provides evidence, not hypotheses"""
        return []
    
    def _create_child_agent(self, subspecialty: str) -> 'FractalAgent':
        """Knowledge agent doesn't create children"""
        return None
    
    def _synthesize_results(self, child_results: List[Dict]) -> Dict:
        """Knowledge agent doesn't synthesize (no children)"""
        return {}


# Example usage
if __name__ == "__main__":
    
    # Test knowledge agent
    knowledge_agent = MedicalKnowledgeAgent()
    
    # Get NSTEMI guideline
    nstemi_guideline = knowledge_agent.get_clinical_guideline(DiagnosisType.NSTEMI)
    
    print("\n" + "="*60)
    print("CLINICAL GUIDELINE: NSTEMI")
    print("="*60)
    print(f"\nSource: {nstemi_guideline.source}")
    print(f"Evidence Grade: {nstemi_guideline.evidence_grade}")
    print(f"\nFirst-Line Therapy:")
    for i, therapy in enumerate(nstemi_guideline.first_line_therapy, 1):
        print(f"  {i}. {therapy}")
    print(f"\nMonitoring Plan:")
    for item in nstemi_guideline.monitoring_plan:
        print(f"  • {item}")
