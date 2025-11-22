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
