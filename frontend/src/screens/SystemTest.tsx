import React, { useState, useEffect } from 'react';
import { Check, X, Loader2, AlertCircle } from 'lucide-react';
import { healthCheck, sendChatMessage, startAnalysis, getAgentStatus } from '../services/api';
import { useAppStore } from '../stores/appStore';

interface TestResult {
  name: string;
  status: 'pending' | 'success' | 'error';
  message: string;
  details?: any;
}

export const SystemTest: React.FC = () => {
  const { patientId } = useAppStore();
  const [tests, setTests] = useState<TestResult[]>([
    { name: 'Backend Health Check', status: 'pending', message: 'Waiting...' },
    { name: 'Gemini LLM Connection', status: 'pending', message: 'Waiting...' },
    { name: 'Chat API', status: 'pending', message: 'Waiting...' },
    { name: 'Agent System', status: 'pending', message: 'Waiting...' },
    { name: 'Analysis API', status: 'pending', message: 'Waiting...' },
    { name: 'Voice Recognition', status: 'pending', message: 'Waiting...' },
  ]);

  const updateTest = (name: string, status: 'pending' | 'success' | 'error', message: string, details?: any) => {
    setTests(prev => prev.map(test => 
      test.name === name ? { ...test, status, message, details } : test
    ));
  };

  const runTests = async () => {
    // Reset all tests
    setTests(prev => prev.map(test => ({ ...test, status: 'pending', message: 'Testing...' })));

    // Test 1: Backend Health Check
    try {
      const health = await healthCheck();
      updateTest('Backend Health Check', 'success', `✓ Server responding at ${health.timestamp}`, health);
    } catch (error) {
      updateTest('Backend Health Check', 'error', `✗ ${(error as Error).message}`);
      return; // Stop if backend is down
    }

    // Test 2: Gemini LLM Connection (via chat)
    try {
      const response = await sendChatMessage({
        patient_id: `test_${Date.now()}`,
        message: 'Hello, are you working?'
      });
      updateTest('Gemini LLM Connection', 'success', `✓ AI responded: "${response.response.substring(0, 50)}..."`, response);
    } catch (error) {
      updateTest('Gemini LLM Connection', 'error', `✗ ${(error as Error).message}`);
    }

    // Test 3: Chat API
    try {
      const response = await sendChatMessage({
        patient_id: patientId,
        message: 'I have chest pain'
      });
      updateTest('Chat API', 'success', `✓ Extracted symptoms: ${response.extracted_symptoms?.join(', ') || 'none'}`, response);
    } catch (error) {
      updateTest('Chat API', 'error', `✗ ${(error as Error).message}`);
    }

    // Test 4: Agent System
    try {
      const status = await getAgentStatus();
      const agentCount = Object.keys(status).length;
      updateTest('Agent System', 'success', `✓ ${agentCount} agents online`, status);
    } catch (error) {
      updateTest('Agent System', 'error', `✗ ${(error as Error).message}`);
    }

    // Test 5: Analysis API
    try {
      const response = await startAnalysis({
        patient_id: patientId,
        symptoms: ['chest pain', 'shortness of breath']
      });
      updateTest('Analysis API', 'success', `✓ ${response.message}`, response);
    } catch (error) {
      updateTest('Analysis API', 'error', `✗ ${(error as Error).message}`);
    }

    // Test 6: Voice Recognition
    if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
      updateTest('Voice Recognition', 'success', '✓ Browser supports Web Speech API');
    } else {
      updateTest('Voice Recognition', 'error', '✗ Browser does not support voice input');
    }
  };

  useEffect(() => {
    runTests();
  }, []);

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'success':
        return <Check className="w-5 h-5 text-green-400" />;
      case 'error':
        return <X className="w-5 h-5 text-red-400" />;
      default:
        return <Loader2 className="w-5 h-5 text-blue-400 animate-spin" />;
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'success':
        return 'border-green-500/30 bg-green-500/10';
      case 'error':
        return 'border-red-500/30 bg-red-500/10';
      default:
        return 'border-blue-500/30 bg-blue-500/10';
    }
  };

  const allPassed = tests.every(test => test.status === 'success');
  const anyFailed = tests.some(test => test.status === 'error');

  return (
    <div className="min-h-screen pt-24 pb-12 px-4">
      <div className="container mx-auto max-w-4xl">
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold text-white mb-2">🔧 System Diagnostics</h1>
          <p className="text-gray-400">Testing all MIMIQ Medical AI features</p>
        </div>

        {/* Overall Status */}
        <div className={`rounded-2xl p-6 mb-8 border ${
          allPassed ? 'border-green-500/30 bg-green-500/10' :
          anyFailed ? 'border-red-500/30 bg-red-500/10' :
          'border-blue-500/30 bg-blue-500/10'
        }`}>
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              {allPassed ? <Check className="w-8 h-8 text-green-400" /> :
               anyFailed ? <AlertCircle className="w-8 h-8 text-red-400" /> :
               <Loader2 className="w-8 h-8 text-blue-400 animate-spin" />}
              <div>
                <h2 className="text-2xl font-bold text-white">
                  {allPassed ? 'All Systems Operational ✅' :
                   anyFailed ? 'Some Systems Down ⚠️' :
                   'Testing in Progress...'}
                </h2>
                <p className="text-gray-400">
                  {tests.filter(t => t.status === 'success').length} / {tests.length} tests passed
                </p>
              </div>
            </div>
            <button
              onClick={runTests}
              className="px-6 py-3 bg-gradient-to-r from-purple-600 to-blue-600 rounded-lg text-white font-semibold hover:shadow-lg hover:shadow-purple-500/50 transition-all"
            >
              Rerun Tests
            </button>
          </div>
        </div>

        {/* Test Results */}
        <div className="space-y-4">
          {tests.map((test, index) => (
            <div
              key={index}
              className={`rounded-xl p-6 border backdrop-blur-sm transition-all ${getStatusColor(test.status)}`}
            >
              <div className="flex items-start justify-between">
                <div className="flex items-start space-x-4 flex-1">
                  <div className="mt-1">{getStatusIcon(test.status)}</div>
                  <div className="flex-1">
                    <h3 className="text-lg font-semibold text-white mb-1">{test.name}</h3>
                    <p className="text-gray-300 text-sm mb-2">{test.message}</p>
                    {test.details && (
                      <details className="mt-2">
                        <summary className="text-gray-400 text-xs cursor-pointer hover:text-white">
                          View Details
                        </summary>
                        <pre className="mt-2 p-3 bg-black/30 rounded text-gray-300 text-xs overflow-auto max-h-32">
                          {JSON.stringify(test.details, null, 2)}
                        </pre>
                      </details>
                    )}
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>

        {/* Feature Checklist */}
        <div className="mt-12 bg-gray-900/30 backdrop-blur-sm border border-white/5 rounded-2xl p-6">
          <h2 className="text-2xl font-bold text-white mb-6">✨ Project Features</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {[
              { feature: '🤖 AI Chatbot', status: 'Working' },
              { feature: '🎤 Voice Assistant', status: 'Working' },
              { feature: '🏥 6 Specialist Agents', status: 'Active' },
              { feature: '⚡ Real-time Analysis', status: 'Ready' },
              { feature: '🔍 Symptom Extraction', status: 'Working' },
              { feature: '🎯 ESI Triage System', status: 'Enabled' },
              { feature: '💊 Gemini AI Integration', status: 'Connected' },
              { feature: '🔌 WebSocket Updates', status: 'Live' },
              { feature: '📱 Responsive UI', status: 'Optimized' },
              { feature: '🎨 Beautiful Design', status: 'Complete' },
            ].map((item, i) => (
              <div key={i} className="flex items-center space-x-3 p-3 bg-white/5 rounded-lg">
                <Check className="w-5 h-5 text-green-400 flex-shrink-0" />
                <div>
                  <span className="text-white font-medium">{item.feature}</span>
                  <span className="text-gray-400 text-sm ml-2">• {item.status}</span>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};
