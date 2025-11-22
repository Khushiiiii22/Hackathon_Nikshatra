"""
Centralized LLM Service using Google Gemini
Use this service everywhere in your application for AI analysis
"""

import os
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
import json
from loguru import logger
from dotenv import load_dotenv

try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False
    logger.warning("google-generativeai not installed. Run: pip install google-generativeai")

# Load environment variables
load_dotenv()

# Configuration
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
DEFAULT_MODEL = os.getenv('LLM_MODEL', 'gemini-2.5-flash')

# Multi-language support
LANGUAGE_PROMPTS = {
    'english': 'You are a professional medical doctor with extensive clinical experience. Provide medically accurate, evidence-based responses with proper clinical reasoning. Use medical terminology appropriately while ensuring patient understanding.'},
    'hindi': 'आप एक पेशेवर चिकित्सक हैं जो व्यापक नैदानिक अनुभव के साथ हैं। चिकित्सकीय रूप से सटीक, साक्ष्य-आधारित उत्तर उचित नैदानिक तर्क के साथ प्रदान करें। रोगी की समझ सुनिश्चित करते हुए चिकित्सा शब्दावली का उचित उपयोग करें।',
    'kannada': 'ನೀವು ವ್ಯಾಪಕ ಕ್ಲಿನಿಕಲ್ ಅನುಭವವನ್ನು ಹೊಂದಿರುವ ವೃತ್ತಿಪರ ವೈದ್ಯರು. ಸರಿಯಾದ ಕ್ಲಿನಿಕಲ್ ತರ್ಕದೊಂದಿಗೆ ವೈದ್ಯಕೀಯವಾಗಿ ನಿಖರವಾದ, ಸಾಕ್ಷ್ಯ-ಆಧಾರಿತ ಪ್ರತಿಕ್ರಿಯೆಗಳನ್ನು ಒದಗಿಸಿ. ರೋಗಿಯ ತಿಳುವಳಿಕೆಯನ್ನು ಖಚಿತಪಡಿಸುತ್ತಾ ವೈದ್ಯಕೀಯ ಪರಿಭಾಷೆಯನ್ನು ಸೂಕ್ತವಾಗಿ ಬಳಸಿ.'

}

class LLMService:
    """Centralized LLM Service for medical AI analysis"""
    
    def __init__(self, model: str = DEFAULT_MODEL):
        if not GEMINI_AVAILABLE:
            raise ImportError("google-generativeai is required. Install it with: pip install google-generativeai")
        
        if not GEMINI_API_KEY:
            raise ValueError("GEMINI_API_KEY not found in environment variables")
        
        genai.configure(api_key=GEMINI_API_KEY)
        self.model = genai.GenerativeModel(model)
        logger.info(f"LLM Service initialized with model: {model}")
    
    def chat(self, message: str, language: str = 'english') -> Dict[str, Any]:
        """Professional doctor-level medical chat with prevention tips"""
        try:
            # Get language-specific system prompt
            system_prompt = LANGUAGE_PROMPTS.get(language.lower(), LANGUAGE_PROMPTS['english'])
            
            # Construct full prompt with professional medical context
            full_prompt = f"{system_prompt}\n\nPatient Query: {message}\n\nProvide a comprehensive medical response that includes:\n1. Professional assessment\n2. Relevant symptoms or signs to monitor\n3. Prevention strategies and lifestyle recommendations\n4. When to seek medical attention\n\nResponse:"
            
            response = self.model.generate_content(full_prompt)
            
            return {
                'success': True,
                'response': response.text,
                'language': language
            }
            
        except Exception as e:
            logger.error(f"Chat error: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def analyze_report(self, report_data: str, patient_info: Optional[Dict] = None) -> Dict[str, Any]:
        """Comprehensive medical report analysis with symptoms and prevention strategies"""
        try:
            # Construct detailed medical analysis prompt
            analysis_prompt = f"""You are a professional medical doctor analyzing a patient's medical report. Provide a comprehensive clinical analysis.

Patient Information:
{patient_info if patient_info else 'Not provided'}

Medical Report Data:
{report_data}

Provide a detailed medical analysis in JSON format with the following structure:
{{
    "patient_brief": "A 2-3 sentence summary of the patient's overall health status and key concerns",
    "summary": "Brief overview of the report findings",
    "key_findings": ["List of main clinical findings"],
    "symptoms_detected": ["List of symptoms or clinical manifestations identified"],
    "abnormalities": ["List of any abnormal values or concerning findings"],
    "risk_assessment": {{
        "level": "low/moderate/high",
        "reasoning": "Clinical reasoning for the risk level"
    }},
    "clinical_recommendations": ["List of immediate medical recommendations"],
    "prevention_strategies": ["Detailed prevention tips and lifestyle modifications specific to the findings"],
    "follow_up": "Recommended follow-up timeline and actions"
}}

Ensure all analysis is medically accurate, evidence-based, and patient-friendly while maintaining professional medical standards.
"""
            
            response = self.model.generate_content(analysis_prompt)
            
            # Parse JSON response
            import json
            result = json.loads(response.text)
            
            return {
                'success': True,
                'analysis': result
            }
            
        except Exception as e:
            logger.error(f"Report analysis error: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
