"""
Centralized LLM Service using Google Gemini
"""

import os
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from loguru import logger
from dotenv import load_dotenv

try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False
    logger.warning("google-generativeai not installed")

load_dotenv()

GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
DEFAULT_MODEL = os.getenv('LLM_MODEL', 'gemini-2.5-flash')

LANGUAGE_PROMPTS = {
    'english': 'You are a professional medical doctor with extensive clinical experience.',
    'hindi': 'आप एक पेशेवर चिकित्सक हैं।',
    'kannada': 'ನೀವು ವೃತ್ತಿಪರ ವೈದ್ಯರು.'
}

@dataclass
class LLMResponse:
    text: str
    success: bool
    model: str = ""
    error: Optional[str] = None
    metadata: Dict[str, Any] = None

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}

class GeminiService:
    def __init__(self, api_key: Optional[str] = None, model: str = DEFAULT_MODEL):
        self.api_key = api_key or GEMINI_API_KEY
        self.model_name = model
        
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY not found")
        
        if not GEMINI_AVAILABLE:
            raise ImportError("google-generativeai not installed")
        
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel(self.model_name)
        logger.info(f"✅ Gemini configured: {self.model_name}")
    
    def analyze(self, prompt: str, temperature: float = 0.3, max_tokens: int = 2000, language: str = 'english') -> LLMResponse:
        try:
            system_prompt = LANGUAGE_PROMPTS.get(language, LANGUAGE_PROMPTS['english'])
            full_prompt = f"{system_prompt}\n\n{prompt}"
            
            response = self.model.generate_content(
                full_prompt,
                generation_config=genai.GenerationConfig(
                    temperature=temperature,
                    max_output_tokens=max_tokens
                )
            )
            
            return LLMResponse(
                text=response.text,
                success=True,
                model=self.model_name,
                metadata={'language': language}
            )
        except Exception as e:
            logger.error(f"Gemini error: {str(e)}")
            return LLMResponse(text="", success=False, error=str(e), model=self.model_name)
    
    def chat(self, messages: List[Dict[str, str]], temperature: float = 0.7) -> LLMResponse:
        try:
            chat = self.model.start_chat(history=[])
            
            for msg in messages[:-1]:
                if msg['role'] == 'user':
                    chat.send_message(msg['content'])
            
            response = chat.send_message(
                messages[-1]['content'],
                generation_config=genai.GenerationConfig(temperature=temperature)
            )
            
            return LLMResponse(text=response.text, success=True, model=self.model_name)
        except Exception as e:
            logger.error(f"Chat error: {str(e)}")
            return LLMResponse(text="", success=False, error=str(e), model=self.model_name)
