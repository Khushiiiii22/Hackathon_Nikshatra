/**
 * Assessment Screen - Voice + Chat Interface
 * Integrated with backend AI agents
 */

import React, { useState, useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { Mic, MicOff, Send, Loader2, AlertCircle } from 'lucide-react';
import voiceService from '../services/voice';
import { sendChatMessage } from '../services/api';
import EmergencyButton from '../components/EmergencyButton';

interface Message {
  role: 'user' | 'assistant';
  content: string;
  timestamp: string;
}

export const AssessmentScreen: React.FC = () => {
  const navigate = useNavigate();
  const [isListening, setIsListening] = useState(false);
  const [transcript, setTranscript] = useState('');
  const [inputText, setInputText] = useState('');
  const [messages, setMessages] = useState<Message[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [voiceSupported, setVoiceSupported] = useState(true);
  const [patientId] = useState(() => `patient_${Date.now()}`);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    // Check voice support
    setVoiceSupported(voiceService.isSupported());

    // Initialize with welcome message
    setMessages([{
      role: 'assistant',
      content: "Hi! I'm MIMIQ, your medical AI assistant. I'm here to help you. Can you tell me what symptoms you're experiencing? You can speak or type - whatever's easier for you.",
      timestamp: new Date().toISOString(),
    }]);

    // Setup voice callbacks
    voiceService.onResult((result) => {
      setTranscript(result.transcript);
      if (result.isFinal) {
        handleVoiceInput(result.transcript);
      }
    });

    voiceService.onError((error) => {
      console.error('Voice error:', error);
      setError(error.message);
      setIsListening(false);
    });

    voiceService.onStart(() => {
      setIsListening(true);
      setError(null);
    });

    voiceService.onEnd(() => {
      setIsListening(false);
      setTranscript('');
    });

    return () => {
      voiceService.stop();
    };
  }, []);

  useEffect(() => {
    // Scroll to bottom when messages change
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handleVoiceInput = async (text: string) => {
    if (!text.trim()) return;

    // Add user message
    const userMessage: Message = {
      role: 'user',
      content: text,
      timestamp: new Date().toISOString(),
    };
    setMessages((prev) => [...prev, userMessage]);
    setTranscript('');

    // Send to backend
    await sendMessageToBackend(text);
  };

  const handleTextInput = async () => {
    if (!inputText.trim()) return;

    const text = inputText;
    setInputText('');

    // Add user message
    const userMessage: Message = {
      role: 'user',
      content: text,
      timestamp: new Date().toISOString(),
    };
    setMessages((prev) => [...prev, userMessage]);

    // Send to backend
    await sendMessageToBackend(text);
  };

  const sendMessageToBackend = async (text: string) => {
    setIsLoading(true);
    setError(null);

    try {
      const response = await sendChatMessage({
        patient_id: patientId,
        message: text,
        timestamp: new Date().toISOString(),
      });

      // Add assistant response
      const assistantMessage: Message = {
        role: 'assistant',
        content: response.response,
        timestamp: response.timestamp,
      };
      setMessages((prev) => [...prev, assistantMessage]);

      // Check urgency
      if (response.urgency_level === 'critical' || response.urgency_level === 'high') {
        // Show urgent warning
        setTimeout(() => {
          const warningMessage: Message = {
            role: 'assistant',
            content: `⚠️ Based on your symptoms, this could be urgent. If your symptoms worsen, please use the emergency button to call 911 (US) or 108 (India) immediately.`,
            timestamp: new Date().toISOString(),
          };
          setMessages((prev) => [...prev, warningMessage]);
        }, 1000);
      }

      // Check if enough data for analysis
      if (response.extracted_symptoms.length >= 3) {
        setTimeout(() => {
          const analysisMessage: Message = {
            role: 'assistant',
            content: "I have enough information to analyze your symptoms. Would you like me to start the AI analysis now? Just say 'yes' or 'analyze'.",
            timestamp: new Date().toISOString(),
          };
          setMessages((prev) => [...prev, analysisMessage]);
        }, 1500);
      }

    } catch (err: any) {
      setError(err.message || 'Failed to send message. Please try again.');
      console.error('Chat error:', err);
    } finally {
      setIsLoading(false);
    }
  };

  const toggleVoice = async () => {
    if (isListening) {
      voiceService.stop();
    } else {
      // Request permission first
      const permitted = await voiceService.requestPermission();
      if (permitted) {
        voiceService.start();
      }
    }
  };

  const startAnalysis = () => {
    // Navigate to analysis screen
    navigate('/analysis', { state: { patientId } });
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50 flex flex-col">
      {/* Header */}
      <div className="bg-white shadow-sm border-b border-gray-200 p-4">
        <div className="max-w-4xl mx-auto">
          <h1 className="text-2xl md:text-3xl font-bold text-gray-900">
            Tell Me About Your Symptoms
          </h1>
          <p className="text-gray-600 mt-1">
            You can speak or type - I'm here to listen
          </p>
        </div>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-4 pb-32">
        <div className="max-w-4xl mx-auto space-y-4">
          {messages.map((message, index) => (
            <div
              key={index}
              className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
            >
              <div
                className={`max-w-[80%] rounded-2xl px-6 py-4 ${
                  message.role === 'user'
                    ? 'bg-blue-600 text-white'
                    : 'bg-white text-gray-900 shadow-md border border-gray-200'
                }`}
              >
                <p className="text-lg leading-relaxed">{message.content}</p>
                <p
                  className={`text-xs mt-2 ${
                    message.role === 'user' ? 'text-blue-100' : 'text-gray-500'
                  }`}
                >
                  {new Date(message.timestamp).toLocaleTimeString()}
                </p>
              </div>
            </div>
          ))}

          {isLoading && (
            <div className="flex justify-start">
              <div className="bg-white rounded-2xl px-6 py-4 shadow-md border border-gray-200">
                <Loader2 className="w-6 h-6 text-blue-600 animate-spin" />
              </div>
            </div>
          )}

          <div ref={messagesEndRef} />
        </div>
      </div>

      {/* Error Display */}
      {error && (
        <div className="fixed top-20 left-1/2 transform -translate-x-1/2 bg-red-100 border-2 border-red-600 text-red-900 px-6 py-3 rounded-xl shadow-lg flex items-center gap-3 z-40">
          <AlertCircle className="w-5 h-5" />
          <p>{error}</p>
        </div>
      )}

      {/* Input Area - Fixed at bottom */}
      <div className="fixed bottom-0 left-0 right-0 bg-white border-t-2 border-gray-200 p-4 shadow-lg">
        <div className="max-w-4xl mx-auto">
          {/* Voice Indicator */}
          {isListening && (
            <div className="mb-4 bg-green-100 border-2 border-green-600 rounded-xl p-4">
              <div className="flex items-center gap-3">
                <div className="w-3 h-3 bg-green-600 rounded-full animate-pulse" />
                <p className="text-green-900 font-semibold">I'm listening...</p>
              </div>
              {transcript && (
                <p className="text-gray-700 mt-2 text-lg">{transcript}</p>
              )}
            </div>
          )}

          <div className="flex gap-3">
            {/* Voice Button */}
            {voiceSupported && (
              <button
                onClick={toggleVoice}
                disabled={isLoading}
                className={`w-20 h-20 rounded-full shadow-lg flex items-center justify-center transition-all duration-200 ${
                  isListening
                    ? 'bg-red-600 hover:bg-red-700 animate-pulse'
                    : 'bg-green-600 hover:bg-green-700 hover:scale-110'
                } disabled:opacity-50 disabled:cursor-not-allowed`}
              >
                {isListening ? (
                  <MicOff className="w-10 h-10 text-white" />
                ) : (
                  <Mic className="w-10 h-10 text-white" />
                )}
              </button>
            )}

            {/* Text Input */}
            <div className="flex-1 flex gap-3">
              <input
                type="text"
                value={inputText}
                onChange={(e) => setInputText(e.target.value)}
                onKeyPress={(e) => e.key === 'Enter' && handleTextInput()}
                placeholder="Or type your symptoms here..."
                disabled={isLoading}
                className="flex-1 h-20 px-6 text-lg border-2 border-gray-300 rounded-2xl focus:outline-none focus:border-blue-600 disabled:opacity-50"
              />
              <button
                onClick={handleTextInput}
                disabled={isLoading || !inputText.trim()}
                className="w-20 h-20 bg-blue-600 hover:bg-blue-700 rounded-2xl shadow-lg flex items-center justify-center disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200 hover:scale-105"
              >
                <Send className="w-8 h-8 text-white" />
              </button>
            </div>
          </div>

          {/* Start Analysis Button */}
          {messages.length > 4 && (
            <button
              onClick={startAnalysis}
              className="w-full mt-4 h-16 bg-gradient-to-r from-purple-600 to-blue-600 hover:from-purple-700 hover:to-blue-700 text-white text-xl font-bold rounded-2xl shadow-lg transition-all duration-200 hover:scale-105"
            >
              Start AI Analysis
            </button>
          )}
        </div>
      </div>

      {/* Emergency Button */}
      <EmergencyButton />
    </div>
  );
};

export default AssessmentScreen;
