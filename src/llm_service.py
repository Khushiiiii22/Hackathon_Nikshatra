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
    'english': 'Respond in English with clear, empathetic medical explanations.',
    'hindi': 'जवाब हिंदी में दें। स्पष्ट और सहानुभूतिपूर्ण चिकित्सा व्याख्या दें। (Respond in Hindi with clear explanations)',
    'kannada': 'ಕನ್ನಡದಲ್ಲಿ ಉತ್ತರಿಸಿ. ಸ್ಪಷ್ಟ ಮತ್ತು ಸಹಾನುಭೂತಿಯ ವೈದ್ಯಕೀಯ ವಿವರಣೆಗಳನ್ನು ನೀಡಿ। (Respond in Kannada with clear explanations)'
}

DEFAULT_LANGUAGE = 'english'


@dataclass
class LLMResponse:
    """Standardized LLM response"""
    success: bool
    text: str
    confidence: Optional[float] = None
    metadata: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


class GeminiService:
    """
    Centralized Gemini LLM Service
    
    Use this class everywhere you need AI:
    - Medical diagnosis
    - Data analysis
    - Pattern recognition
    - Natural language processing
    - Risk assessment
    """
    
    def __init__(self, model_name: str = DEFAULT_MODEL):
        """Initialize Gemini service"""
        self.model_name = model_name
        self.is_configured = False
        
        if not GEMINI_AVAILABLE:
            logger.error("❌ Gemini not available - install google-generativeai")
            return
        
        if not GEMINI_API_KEY:
            logger.warning("⚠️  GEMINI_API_KEY not found - running in simulation mode")
            return
        
        try:
            genai.configure(api_key=GEMINI_API_KEY)
            self.model = genai.GenerativeModel(model_name)
            self.is_configured = True
            logger.info(f"✅ Gemini configured with model: {model_name}")
        except Exception as e:
            logger.error(f"❌ Failed to configure Gemini: {e}")
    
    def analyze(self, prompt: str, **kwargs) -> LLMResponse:
        """
        Generic analysis method - use for any AI task
        
        Args:
            prompt: The prompt to send to Gemini
            **kwargs: Additional parameters (temperature, max_tokens, etc.)
        
        Returns:
            LLMResponse with result
        """
        if not self.is_configured:
            return self._simulate_response(prompt)
        
        try:
            # Generate response with safety settings
            safety_settings = {
                'HARM_CATEGORY_HARASSMENT': 'BLOCK_NONE',
                'HARM_CATEGORY_HATE_SPEECH': 'BLOCK_NONE',
                'HARM_CATEGORY_SEXUALLY_EXPLICIT': 'BLOCK_NONE',
                'HARM_CATEGORY_DANGEROUS_CONTENT': 'BLOCK_NONE',
            }
            
            response = self.model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=kwargs.get('temperature', 0.7),
                    max_output_tokens=kwargs.get('max_tokens', 1024),
                ),
                safety_settings=safety_settings
            )
            
            return LLMResponse(
                success=True,
                text=response.text,
                metadata={'model': self.model_name}
            )
            
        except Exception as e:
            logger.error(f"❌ Gemini analysis failed: {e}")
            return LLMResponse(
                success=False,
                text="",
                error=str(e)
            )
    
    def analyze_medical_vitals(
        self,
        heart_rate: int,
        hrv: float,
        spo2: int,
        patient_history: Optional[str] = None
    ) -> LLMResponse:
        """
        Analyze medical vitals and provide diagnosis
        
        Args:
            heart_rate: Heart rate in BPM
            hrv: Heart rate variability in ms
            spo2: Blood oxygen saturation percentage
            patient_history: Optional patient medical history
        
        Returns:
            LLMResponse with medical diagnosis
        """
        prompt = f"""You are a cardiologist AI assistant. Analyze these vital signs:

**Patient Vitals:**
- Heart Rate: {heart_rate} BPM
- HRV (RMSSD): {hrv} ms
- SpO2: {spo2}%
{f"- Medical History: {patient_history}" if patient_history else ""}

**Task:**
Provide a medical analysis in JSON format with:
1. diagnosis: Brief diagnosis (e.g., "Normal", "Pre-NSTEMI", "Unstable Angina")
2. confidence: Confidence percentage (0-100)
3. risk_level: LOW, MEDIUM, HIGH, or CRITICAL
4. reasoning: Brief clinical reasoning
5. recommendations: List of immediate actions

**Clinical Context:**
- Normal HR: 60-100 BPM
- Normal HRV: 50-100 ms (higher is better)
- Normal SpO2: 95-100%
- Low HRV + elevated HR = possible cardiac ischemia
- Very low HRV (<30ms) = high cardiac risk

Respond ONLY with valid JSON, no markdown or explanations."""

        response = self.analyze(prompt, temperature=0.3)
        
        if not response.success:
            return response
        
        try:
            # Parse JSON from response
            result = json.loads(response.text)
            response.metadata = result
            response.confidence = result.get('confidence', 0) / 100.0
        except json.JSONDecodeError:
            # Try to extract JSON from markdown
            text = response.text
            if "```json" in text:
                text = text.split("```json")[1].split("```")[0].strip()
            elif "```" in text:
                text = text.split("```")[1].split("```")[0].strip()
            
            try:
                result = json.loads(text)
                response.metadata = result
                response.confidence = result.get('confidence', 0) / 100.0
            except:
                logger.warning("⚠️  Could not parse JSON from Gemini response")
        
        return response
    
    def analyze_trend(
        self,
        vitals_history: List[Dict[str, Any]],
        time_window: str = "last hour"
    ) -> LLMResponse:
        """
        Analyze trends in vital signs over time
        
        Args:
            vitals_history: List of vital sign readings
            time_window: Time window description
        
        Returns:
            LLMResponse with trend analysis
        """
        prompt = f"""You are a cardiologist analyzing patient trends.

**Vitals History ({time_window}):**
{json.dumps(vitals_history, indent=2)}

**Task:**
Analyze the trend and provide:
1. Is the patient's condition improving, stable, or deteriorating?
2. What patterns do you see?
3. What is the risk trajectory?
4. Should any alerts be raised?

Respond in JSON format with:
{{
  "trend": "improving/stable/deteriorating",
  "key_patterns": ["pattern1", "pattern2"],
  "risk_trajectory": "increasing/stable/decreasing",
  "alert_needed": true/false,
  "reasoning": "brief explanation"
}}"""

        response = self.analyze(prompt, temperature=0.4)
        
        if response.success:
            try:
                text = response.text
                if "```json" in text:
                    text = text.split("```json")[1].split("```")[0].strip()
                result = json.loads(text)
                response.metadata = result
            except:
                pass
        
        return response
    
    def predict_risk(
        self,
        current_vitals: Dict[str, Any],
        recent_history: List[Dict[str, Any]],
        time_horizon: str = "next 24 hours"
    ) -> LLMResponse:
        """
        Predict cardiac event risk
        
        Args:
            current_vitals: Current vital signs
            recent_history: Recent vital sign history
            time_horizon: Prediction time window
        
        Returns:
            LLMResponse with risk prediction
        """
        prompt = f"""You are a predictive cardiology AI.

**Current Vitals:**
{json.dumps(current_vitals, indent=2)}

**Recent History:**
{json.dumps(recent_history, indent=2)}

**Task:**
Predict the risk of cardiac events in the {time_horizon}.

Respond in JSON format:
{{
  "risk_score": 0-100,
  "risk_level": "LOW/MEDIUM/HIGH/CRITICAL",
  "likely_events": ["event1", "event2"],
  "confidence": 0-100,
  "key_indicators": ["indicator1", "indicator2"],
  "recommendations": ["action1", "action2"]
}}"""

        response = self.analyze(prompt, temperature=0.3)
        
        if response.success:
            try:
                text = response.text
                if "```json" in text:
                    text = text.split("```json")[1].split("```")[0].strip()
                result = json.loads(text)
                response.metadata = result
                response.confidence = result.get('confidence', 0) / 100.0
            except:
                pass
        
        return response
    
    def explain_diagnosis(self, diagnosis: str, for_patient: bool = True) -> LLMResponse:
        """
        Generate patient-friendly explanation of diagnosis
        
        Args:
            diagnosis: Medical diagnosis
            for_patient: If True, use simple language
        
        Returns:
            LLMResponse with explanation
        """
        audience = "patient (use simple, non-technical language)" if for_patient else "medical professional"
        
        prompt = f"""Explain this medical diagnosis to a {audience}:

**Diagnosis:** {diagnosis}

Provide:
1. What it means in simple terms
2. Why it matters
3. What to do next

Keep it brief (2-3 sentences) and reassuring."""

        return self.analyze(prompt, temperature=0.7)
    
    def generate_recommendations(
        self,
        diagnosis: str,
        vitals: Dict[str, Any],
        context: Optional[str] = None
    ) -> LLMResponse:
        """
        Generate personalized recommendations
        
        Args:
            diagnosis: Medical diagnosis
            vitals: Current vital signs
            context: Additional context
        
        Returns:
            LLMResponse with recommendations
        """
        prompt = f"""Based on this diagnosis and vitals, provide recommendations:

**Diagnosis:** {diagnosis}
**Vitals:** {json.dumps(vitals)}
{f"**Context:** {context}" if context else ""}

Provide 3-5 specific, actionable recommendations in JSON format:
{{
  "immediate_actions": ["action1", "action2"],
  "lifestyle_changes": ["change1", "change2"],
  "monitoring_needed": ["what to monitor"],
  "followup": "when to follow up"
}}"""

        response = self.analyze(prompt, temperature=0.6)
        
        if response.success:
            try:
                text = response.text
                if "```json" in text:
                    text = text.split("```json")[1].split("```")[0].strip()
                result = json.loads(text)
                response.metadata = result
            except:
                pass
        
        return response
    
    def chat(self, message: str, conversation_history: Optional[List[Dict]] = None) -> LLMResponse:
        """
        Chat interface for medical Q&A
        
        Args:
            message: User message
            conversation_history: Previous conversation
        
        Returns:
            LLMResponse with chat response
        """
        context = ""
        if conversation_history:
            context = "Previous conversation:\n"
            for msg in conversation_history[-5:]:  # Last 5 messages
                role = msg.get('role', 'user')
                content = msg.get('content', '')
                context += f"{role}: {content}\n"
        
        prompt = f"""You are a helpful medical AI assistant for cardiac health.

{context}

User: {message}

Provide a helpful, accurate response. If medical emergency, advise to call 911."""

        return self.analyze(prompt, temperature=0.8)
    
    def _simulate_response(self, prompt: str) -> LLMResponse:
        """Simulation mode when Gemini not available"""
        logger.warning("🔄 Running in simulation mode")
        
        # Simple rule-based simulation
        if "heart rate" in prompt.lower() or "vitals" in prompt.lower():
            simulated = {
                "diagnosis": "Simulated diagnosis (Gemini not configured)",
                "confidence": 0,
                "risk_level": "MEDIUM",
                "reasoning": "This is a simulation. Configure GEMINI_API_KEY for real analysis.",
                "recommendations": ["Configure Gemini API key", "Install google-generativeai"]
            }
            
            return LLMResponse(
                success=True,
                text=json.dumps(simulated),
                confidence=0.0,
                metadata=simulated
            )
        
        return LLMResponse(
            success=True,
            text="Simulation mode active. Configure GEMINI_API_KEY for real AI analysis.",
            confidence=0.0
        )


# Global singleton instance
_gemini_service = None

def get_llm_service() -> GeminiService:
    """
    Get global LLM service instance
    
    Usage:
        from src.llm_service import get_llm_service
        
        llm = get_llm_service()
        response = llm.analyze_medical_vitals(hr=95, hrv=38, spo2=94)
        print(response.metadata['diagnosis'])
    """
    global _gemini_service
    if _gemini_service is None:
        _gemini_service = GeminiService()
    return _gemini_service


# Convenience functions for quick access
def analyze_vitals(heart_rate: int, hrv: float, spo2: int, **kwargs) -> LLMResponse:
    """Quick access to vital analysis"""
    return get_llm_service().analyze_medical_vitals(heart_rate, hrv, spo2, **kwargs)

def analyze_trend(vitals_history: List[Dict], **kwargs) -> LLMResponse:
    """Quick access to trend analysis"""
    return get_llm_service().analyze_trend(vitals_history, **kwargs)

def predict_risk(current_vitals: Dict, recent_history: List[Dict], **kwargs) -> LLMResponse:
    """Quick access to risk prediction"""
    return get_llm_service().predict_risk(current_vitals, recent_history, **kwargs)

def chat_medical(message: str, **kwargs) -> LLMResponse:
    """Quick access to medical chat"""
    return get_llm_service().chat(message, **kwargs)


if __name__ == "__main__":
    # Test the service
    logger.info("🧪 Testing Gemini LLM Service...")
    
    llm = get_llm_service()
    
    # Test 1: Analyze vitals
    logger.info("\n📊 Test 1: Analyzing vital signs...")
    response = llm.analyze_medical_vitals(
        heart_rate=95,
        hrv=38,
        spo2=94
    )
    
    if response.success:
        logger.info(f"✅ Success!")
        logger.info(f"Diagnosis: {response.metadata.get('diagnosis')}")
        logger.info(f"Confidence: {response.confidence * 100:.1f}%")
        logger.info(f"Risk: {response.metadata.get('risk_level')}")
    else:
        logger.error(f"❌ Failed: {response.error}")
    
    # Test 2: Trend analysis
    logger.info("\n📈 Test 2: Trend analysis...")
    history = [
        {"hr": 72, "hrv": 65, "timestamp": "10:00"},
        {"hr": 85, "hrv": 52, "timestamp": "10:05"},
        {"hr": 95, "hrv": 38, "timestamp": "10:10"}
    ]
    
    response = llm.analyze_trend(history)
    if response.success and response.metadata:
        logger.info(f"✅ Trend: {response.metadata.get('trend')}")
        logger.info(f"Risk trajectory: {response.metadata.get('risk_trajectory')}")
    
    # Test 3: Chat
    logger.info("\n💬 Test 3: Medical chat...")
    response = llm.chat("What does low HRV mean?")
    if response.success:
        logger.info(f"✅ Response: {response.text[:200]}...")
    
    logger.info("\n✅ All tests complete!")
