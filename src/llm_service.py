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
6. prevention_tips: Lifestyle modifications and preventive measures

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
    
    def chat(self, message: str, conversation_history: Optional[List[Dict]] = None), language: str = 'english' -> LLMResponse:
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
        
        # Get language-specific instruction
        language_instruction = LANGUAGE_PROMPTS.get(language.lower(), LANGUAGE_PROMPTS['english'])
        
        prompt = f"""You are a helpful medical AI assistant for cardiac health.
        
{language_instruction}

{context}

User: {message}

Provide a helpful, accurate response with:
1. Clear medical explanation in simple terms
2. **Prevention tips and lifestyle recommendations**
3. When to seek emergency care (if applicable)
4. Empathetic and supportive tone

If medical emergency, advise to call emergency services (911/108)."""

        return self.analyze(prompt, temperature=0.8)

    def analyze_report(self, report_text: str, report_type: str = "general") -> LLMResponse:
        """
        Analyze medical reports with structured output
        
        Args:
            report_text: Text content of the medical report
            report_type: Type of report (e.g., 'blood_test', 'ecg', 'xray', 'general')
            
        Returns:
            LLMResponse with structured report analysis
        """
        prompt = f"""You are a medical AI assistant analyzing a {report_type} report.
        
**Report Content:**
{report_text}

**Task:**
Provide a BRIEF, structured analysis in JSON format with:

1. summary: Brief 2-3 sentence overview
2. key_findings: List of important findings
3. abnormalities: List of values outside normal range
4. risk_assessment: LOW/MEDIUM/HIGH with reasoning
5. recommendations: Immediate actions needed
6. prevention_tips: Lifestyle changes to improve health
7. follow_up: When to consult doctor

Be concise, clear, and patient-friendly. Focus on actionable insights.

Respond ONLY with valid JSON."""
        
        return self.analyze(prompt, temperature=0.3)
