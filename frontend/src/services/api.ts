/**
 * API Service for MIMIQ Medical AI Platform
 * Handles all HTTP requests to Flask backend
 */

import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:5000';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 30000, // 30 seconds
});

// Request interceptor
api.interceptors.request.use(
  (config) => {
    // Add timestamp to all requests
    config.headers['X-Request-Time'] = new Date().toISOString();
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor
api.interceptors.response.use(
  (response) => response,
  (error) => {
    console.error('API Error:', error);
    
    // Handle different error types
    if (error.response) {
      // Server responded with error
      const message = error.response.data?.error || error.response.data?.message || 'Server error';
      throw new Error(message);
    } else if (error.request) {
      // Request made but no response
      throw new Error('Cannot connect to server. Please check your connection.');
    } else {
      // Something else happened
      throw new Error(error.message || 'An unexpected error occurred');
    }
  }
);

export interface ChatMessage {
  patient_id: string;
  message: string;
  timestamp?: string;
}

export interface ChatResponse {
  response: string;
  extracted_symptoms: string[];
  urgency_level: string;
  next_question: string;
  patient_id: string;
  timestamp: string;
}

export interface AnalysisRequest {
  patient_id: string;
  symptoms: string[];
  vitals?: {
    heart_rate?: number;
    blood_pressure?: string;
    oxygen_saturation?: number;
    temperature?: number;
  };
}

export interface AnalysisResponse {
  status: string;
  analysis_id: string;
  estimated_time: string;
  patient_id: string;
  message: string;
}

export interface PatientSummary {
  urgency: string;
  esi_level: number;
  primary_concern: string;
  recommendation: string;
  next_steps: string[];
  agents_consulted: number;
}

export interface AgentResult {
  diagnosis: string;
  confidence: number;
  raw_result: string;
  timestamp: string;
}

export interface ResultsResponse {
  patient_id: string;
  analysis_id: string;
  timestamp: string;
  summary: PatientSummary;
  detailed_results: Record<string, AgentResult>;
  symptoms: string[];
  vitals: any;
}

export interface AgentStatus {
  id: string;
  name: string;
  status: string;
}

/**
 * Health check
 */
export const healthCheck = async () => {
  const response = await api.get('/health');
  return response.data;
};

/**
 * Send chat message (voice or text)
 */
export const sendChatMessage = async (data: ChatMessage): Promise<ChatResponse> => {
  const response = await api.post<ChatResponse>('/api/chat', data);
  return response.data;
};

/**
 * Start AI agent analysis
 */
export const startAnalysis = async (data: AnalysisRequest): Promise<AnalysisResponse> => {
  const response = await api.post<AnalysisResponse>('/api/analyze', data);
  return response.data;
};

/**
 * Get analysis results for patient
 */
export const getResults = async (patientId: string): Promise<ResultsResponse> => {
  const response = await api.get<ResultsResponse>(`/api/results/${patientId}`);
  return response.data;
};

/**
 * Get agent status
 */
export const getAgentStatus = async () => {
  const response = await api.get('/api/agents/status');
  return response.data;
};

/**
 * Submit vital signs
 */
export const submitVitals = async (patientId: string, vitals: any) => {
  const response = await api.post('/api/vitals', {
    patient_id: patientId,
    vitals,
  });
  return response.data;
};

export default api;
