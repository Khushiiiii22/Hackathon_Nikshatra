/**
 * Analysis Screen - Real-Time Agent Processing
 * Shows live updates from all 6 AI agents via WebSocket
 */

import React, { useState, useEffect } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { Check, Loader2, AlertCircle, Brain, Heart, Wind, Utensils, Bone, Activity } from 'lucide-react';
import wsService from '../services/websocket';
import type { AgentUpdate } from '../services/websocket';
import { startAnalysis } from '../services/api';
import EmergencyButton from '../components/EmergencyButton';

interface AgentState {
  id: string;
  name: string;
  icon: React.ReactNode;
  status: 'waiting' | 'analyzing' | 'processing' | 'complete' | 'error';
  progress: number;
  confidence?: number;
  error?: string;
}

export const AnalysisScreen: React.FC = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const patientId = location.state?.patientId || `patient_${Date.now()}`;

  const [agents, setAgents] = useState<AgentState[]>([
    { id: 'safety', name: 'Emergency Triage AI', icon: <AlertCircle className="w-8 h-8" />, status: 'waiting', progress: 0 },
    { id: 'cardiology', name: 'Heart Specialist AI', icon: <Heart className="w-8 h-8" />, status: 'waiting', progress: 0 },
    { id: 'pulmonary', name: 'Lung Specialist AI', icon: <Wind className="w-8 h-8" />, status: 'waiting', progress: 0 },
    { id: 'gastro', name: 'Stomach Specialist AI', icon: <Utensils className="w-8 h-8" />, status: 'waiting', progress: 0 },
    { id: 'musculoskeletal', name: 'Bone & Muscle AI', icon: <Bone className="w-8 h-8" />, status: 'waiting', progress: 0 },
    { id: 'triage', name: 'Priority Assessment AI', icon: <Activity className="w-8 h-8" />, status: 'waiting', progress: 0 },
  ]);

  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [, setAnalysisId] = useState<string | null>(null);

  useEffect(() => {
    // Connect to WebSocket
    const connectWebSocket = async () => {
      try {
        await wsService.connect();
        wsService.subscribe(patientId);

        // Listen for agent updates
        wsService.on('agent_update', (data: AgentUpdate) => {
          console.log('Agent update received:', data);
          updateAgentStatus(data);
        });

        // Listen for analysis completion
        wsService.on('analysis_complete', (data: any) => {
          console.log('Analysis complete:', data);
          setIsAnalyzing(false);
          // Navigate to results after 2 seconds
          setTimeout(() => {
            navigate('/results', { state: { patientId, analysisId: data.analysis_id } });
          }, 2000);
        });

        // Start analysis automatically
        beginAnalysis();

      } catch (err: any) {
        console.error('WebSocket connection failed:', err);
        setError('Failed to connect to server. Please check your connection.');
      }
    };

    connectWebSocket();

    return () => {
      wsService.disconnect();
    };
  }, [patientId]);

  const beginAnalysis = async () => {
    setIsAnalyzing(true);
    setError(null);

    try {
      const response = await startAnalysis({
        patient_id: patientId,
        symptoms: ['chest pain', 'shortness of breath'], // TODO: Get from chat history
        vitals: {
          heart_rate: 85,
          blood_pressure: '120/80',
        },
      });

      setAnalysisId(response.analysis_id);
      console.log('Analysis started:', response);

    } catch (err: any) {
      setError(err.message || 'Failed to start analysis');
      setIsAnalyzing(false);
    }
  };

  const updateAgentStatus = (update: AgentUpdate) => {
    setAgents((prevAgents) =>
      prevAgents.map((agent) =>
        agent.id === update.agent_id
          ? {
              ...agent,
              status: update.status,
              progress: update.progress,
              confidence: update.confidence,
              error: update.error,
            }
          : agent
      )
    );
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'complete':
        return 'bg-green-100 border-green-600 text-green-900';
      case 'analyzing':
      case 'processing':
        return 'bg-blue-100 border-blue-600 text-blue-900';
      case 'error':
        return 'bg-red-100 border-red-600 text-red-900';
      default:
        return 'bg-gray-100 border-gray-400 text-gray-700';
    }
  };

  const getStatusIcon = (agent: AgentState) => {
    if (agent.status === 'complete') {
      return <Check className="w-8 h-8 text-green-600" />;
    } else if (agent.status === 'analyzing' || agent.status === 'processing') {
      return <Loader2 className="w-8 h-8 text-blue-600 animate-spin" />;
    } else if (agent.status === 'error') {
      return <AlertCircle className="w-8 h-8 text-red-600" />;
    } else {
      return <div className="w-8 h-8 rounded-full border-4 border-gray-400" />;
    }
  };

  const completedCount = agents.filter((a) => a.status === 'complete').length;
  const overallProgress = (completedCount / agents.length) * 100;

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-50 via-white to-blue-50 p-4">
      <div className="max-w-4xl mx-auto">
        {/* Header */}
        <div className="text-center mb-8">
          <Brain className="w-16 h-16 text-purple-600 mx-auto mb-4" />
          <h1 className="text-3xl md:text-4xl font-bold text-gray-900 mb-2">
            Analyzing Your Symptoms
          </h1>
          <p className="text-lg text-gray-600">
            AI Specialists Are Reviewing Your Case
          </p>
        </div>

        {/* Overall Progress */}
        <div className="bg-white rounded-2xl shadow-lg p-6 mb-6">
          <div className="flex items-center justify-between mb-3">
            <span className="text-lg font-semibold text-gray-900">Overall Progress</span>
            <span className="text-2xl font-bold text-purple-600">{Math.round(overallProgress)}%</span>
          </div>
          <div className="w-full h-4 bg-gray-200 rounded-full overflow-hidden">
            <div
              className="h-full bg-gradient-to-r from-purple-600 to-blue-600 transition-all duration-500 ease-out"
              style={{ width: `${overallProgress}%` }}
            />
          </div>
          <p className="text-sm text-gray-600 mt-3 text-center">
            {completedCount} of {agents.length} specialists complete
          </p>
        </div>

        {/* Agent Cards */}
        <div className="space-y-4 mb-8">
          {agents.map((agent) => (
            <div
              key={agent.id}
              className={`border-2 rounded-2xl p-6 transition-all duration-300 ${getStatusColor(agent.status)}`}
            >
              <div className="flex items-center gap-4">
                {/* Icon */}
                <div className="flex-shrink-0">{getStatusIcon(agent)}</div>

                {/* Agent Info */}
                <div className="flex-1">
                  <h3 className="text-xl font-bold mb-1">{agent.name}</h3>
                  
                  {/* Progress Bar */}
                  {(agent.status === 'analyzing' || agent.status === 'processing') && (
                    <div className="w-full h-2 bg-white bg-opacity-50 rounded-full overflow-hidden mt-2">
                      <div
                        className="h-full bg-blue-600 transition-all duration-300"
                        style={{ width: `${agent.progress}%` }}
                      />
                    </div>
                  )}

                  {/* Confidence Score */}
                  {agent.status === 'complete' && agent.confidence && (
                    <p className="text-sm font-semibold mt-2">
                      Confidence: {agent.confidence}%
                    </p>
                  )}

                  {/* Error Message */}
                  {agent.status === 'error' && agent.error && (
                    <p className="text-sm mt-2">{agent.error}</p>
                  )}
                </div>

                {/* Agent Specific Icon */}
                <div className="flex-shrink-0 text-gray-600">{agent.icon}</div>
              </div>
            </div>
          ))}
        </div>

        {/* Status Message */}
        <div className="bg-white rounded-2xl shadow-lg p-6 text-center">
          {isAnalyzing && completedCount < agents.length ? (
            <>
              <Loader2 className="w-12 h-12 text-blue-600 animate-spin mx-auto mb-3" />
              <p className="text-lg text-gray-900 font-semibold">
                Analysis in progress...
              </p>
              <p className="text-gray-600 mt-2">
                This usually takes 30-45 seconds. Please wait.
              </p>
              <p className="text-sm text-gray-500 mt-4">
                You're doing great. Just breathe slowly and stay calm.
              </p>
            </>
          ) : completedCount === agents.length ? (
            <>
              <Check className="w-16 h-16 text-green-600 mx-auto mb-3" />
              <p className="text-2xl text-gray-900 font-bold">
                Analysis Complete!
              </p>
              <p className="text-gray-600 mt-2">
                Preparing your results...
              </p>
            </>
          ) : null}
        </div>

        {/* Error Display */}
        {error && (
          <div className="mt-6 bg-red-100 border-2 border-red-600 text-red-900 px-6 py-4 rounded-xl flex items-center gap-3">
            <AlertCircle className="w-6 h-6" />
            <div>
              <p className="font-semibold">Error</p>
              <p>{error}</p>
            </div>
          </div>
        )}
      </div>

      {/* Emergency Button */}
      <EmergencyButton />
    </div>
  );
};

export default AnalysisScreen;
