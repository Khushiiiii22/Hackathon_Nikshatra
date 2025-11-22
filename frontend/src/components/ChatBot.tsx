import React, { useState, useRef, useEffect } from 'react';
import { useAppStore } from '../stores/appStore';
import { X, Send, Mic, Loader2, Phone, AlertCircle, Languages } from 'lucide-react';
import { cn } from '../lib/utils';

const API_URL = 'http://localhost:5000/api';

// Language options
const LANGUAGES = [
  { code: 'en-US', name: 'English', flag: '🇺🇸' },
  { code: 'hi-IN', name: 'हिन्दी (Hindi)', flag: '🇮🇳' },
  { code: 'kn-IN', name: 'ಕನ್ನಡ (Kannada)', flag: '🇮🇳' },
];

export const ChatBot: React.FC = () => {
  const { isChatOpen, toggleChat, messages, addMessage, patientId } = useAppStore();
  const [inputText, setInputText] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [isListening, setIsListening] = useState(false);
  const [selectedLanguage, setSelectedLanguage] = useState('en-US');
  const [showLanguageMenu, setShowLanguageMenu] = useState(false);
  const [showEmergency, setShowEmergency] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const recognitionRef = useRef<any>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSendMessage = async () => {
    if (!inputText.trim() || isLoading) return;

    const userMessage = inputText.trim();
    setInputText('');

    // Add user message
    addMessage({
      role: 'user',
      content: userMessage,
    });

    setIsLoading(true);

    try {
      // Call backend API
      const response = await fetch(`${API_URL}/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          patient_id: patientId,
          message: userMessage,
        }),
      });

      const data = await response.json();

      // Add AI response
      addMessage({
        role: 'assistant',
        content: data.response || 'I apologize, I encountered an error. Please try again.',
      });
    } catch (error) {
      console.error('Chat error:', error);
      addMessage({
        role: 'assistant',
        content: '❌ Sorry, I\'m having trouble connecting. Please make sure the backend server is running on port 5000.',
      });
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  const handleEmergencyCall = () => {
    // Show emergency options
    setShowEmergency(true);
  };

  const callAmbulance = () => {
    // Direct call to ambulance service
    window.location.href = 'tel:108'; // India ambulance
  };

  const callEmergency = (number: string) => {
    window.location.href = `tel:${number}`;
  };

  const toggleVoice = () => {
    if (!isListening) {
      // Start listening
      if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
        const SpeechRecognition = (window as any).webkitSpeechRecognition || (window as any).SpeechRecognition;
        const recognition = new SpeechRecognition();
        
        recognition.continuous = false;
        recognition.interimResults = false;
        recognition.lang = selectedLanguage; // Use selected language
        
        recognition.onstart = () => {
          setIsListening(true);
        };
        
        recognition.onresult = (event: any) => {
          const transcript = event.results[0][0].transcript;
          setInputText(transcript);
          setIsListening(false);
        };
        
        recognition.onerror = (event: any) => {
          console.error('Speech recognition error:', event.error);
          setIsListening(false);
          if (event.error === 'language-not-supported') {
            alert(`Language not supported. Switching to English.`);
            setSelectedLanguage('en-US');
          }
        };
        
        recognition.onend = () => {
          setIsListening(false);
        };

        recognitionRef.current = recognition;
        recognition.start();
      } else {
        alert('Speech recognition is not supported in your browser. Please use Chrome or Edge.');
      }
    } else {
      // Stop listening
      if (recognitionRef.current) {
        recognitionRef.current.stop();
      }
      setIsListening(false);
    }
  };

  if (!isChatOpen) return null;

  return (
    <div className="fixed bottom-4 right-4 z-50 w-96 h-[600px] glass-morphism rounded-2xl shadow-neon-strong flex flex-col overflow-hidden">
      {/* Emergency Modal */}
      {showEmergency && (
        <div className="absolute inset-0 bg-black/80 z-50 flex items-center justify-center p-4">
          <div className="bg-gradient-to-br from-red-600 to-red-800 rounded-2xl p-6 w-full max-w-sm">
            <h3 className="text-white text-xl font-bold mb-4 flex items-center">
              <AlertCircle className="w-6 h-6 mr-2" />
              Emergency Services
            </h3>
            
            <div className="space-y-3">
              <button
                onClick={callAmbulance}
                className="w-full bg-white text-red-600 rounded-lg p-4 font-semibold flex items-center justify-between hover:bg-red-50 transition-colors"
              >
                <div className="flex items-center">
                  <Phone className="w-5 h-5 mr-3" />
                  <div className="text-left">
                    <div className="font-bold">Ambulance (108)</div>
                    <div className="text-xs opacity-80">India Emergency Service</div>
                  </div>
                </div>
                <span className="text-2xl">🚑</span>
              </button>

              <button
                onClick={() => callEmergency('102')}
                className="w-full bg-white text-red-600 rounded-lg p-4 font-semibold flex items-center justify-between hover:bg-red-50 transition-colors"
              >
                <div className="flex items-center">
                  <Phone className="w-5 h-5 mr-3" />
                  <div className="text-left">
                    <div className="font-bold">Medical Helpline (102)</div>
                    <div className="text-xs opacity-80">Free medical assistance</div>
                  </div>
                </div>
                <span className="text-2xl">🏥</span>
              </button>

              <button
                onClick={() => callEmergency('112')}
                className="w-full bg-white text-red-600 rounded-lg p-4 font-semibold flex items-center justify-between hover:bg-red-50 transition-colors"
              >
                <div className="flex items-center">
                  <Phone className="w-5 h-5 mr-3" />
                  <div className="text-left">
                    <div className="font-bold">Emergency (112)</div>
                    <div className="text-xs opacity-80">Universal emergency number</div>
                  </div>
                </div>
                <span className="text-2xl">🚨</span>
              </button>

              <button
                onClick={() => setShowEmergency(false)}
                className="w-full bg-white/20 text-white rounded-lg p-3 font-semibold hover:bg-white/30 transition-colors"
              >
                Cancel
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Header */}
      <div className="bg-gradient-to-r from-primary to-secondary p-4 flex items-center justify-between">
        <div className="flex items-center space-x-3">
          <div className="w-10 h-10 rounded-full bg-white/20 flex items-center justify-center">
            <span className="text-2xl">🤖</span>
          </div>
          <div>
            <h3 className="text-white font-semibold">MIMIQ AI Assistant</h3>
            <p className="text-white/80 text-xs">Online • {LANGUAGES.find(l => l.code === selectedLanguage)?.name}</p>
          </div>
        </div>
        <div className="flex items-center space-x-2">
          {/* Emergency Button */}
          <button
            onClick={handleEmergencyCall}
            className="text-white bg-red-500 hover:bg-red-600 rounded-full p-2 transition-all shadow-lg hover:shadow-neon-red"
            title="Emergency - Call Ambulance"
          >
            <Phone className="w-4 h-4" />
          </button>
          
          {/* Language Selector */}
          <div className="relative">
            <button
              onClick={() => setShowLanguageMenu(!showLanguageMenu)}
              className="text-white/80 hover:text-white transition-colors p-2"
              title="Change Language"
            >
              <Languages className="w-5 h-5" />
            </button>
            
            {showLanguageMenu && (
              <div className="absolute top-full right-0 mt-2 bg-gray-900 rounded-lg shadow-xl overflow-hidden min-w-[200px] z-50">
                {LANGUAGES.map((lang) => (
                  <button
                    key={lang.code}
                    onClick={() => {
                      setSelectedLanguage(lang.code);
                      setShowLanguageMenu(false);
                    }}
                    className={cn(
                      "w-full px-4 py-3 text-left hover:bg-gray-800 transition-colors flex items-center space-x-2",
                      selectedLanguage === lang.code ? "bg-primary/20 text-primary" : "text-white"
                    )}
                  >
                    <span className="text-xl">{lang.flag}</span>
                    <span className="text-sm">{lang.name}</span>
                  </button>
                ))}
              </div>
            )}
          </div>

          <button
            onClick={toggleChat}
            className="text-white/80 hover:text-white transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.map((message) => (
          <div
            key={message.id}
            className={cn(
              "flex",
              message.role === 'user' ? "justify-end" : "justify-start"
            )}
          >
            <div
              className={cn(
                "max-w-[80%] rounded-2xl px-4 py-2",
                message.role === 'user'
                  ? "bg-gradient-to-r from-primary to-secondary text-white"
                  : "glass-morphism text-gray-100"
              )}
            >
              <p className="text-sm whitespace-pre-wrap">{message.content}</p>
              <p className="text-xs opacity-60 mt-1">
                {new Date(message.timestamp).toLocaleTimeString([], {
                  hour: '2-digit',
                  minute: '2-digit',
                })}
              </p>
            </div>
          </div>
        ))}
        {isLoading && (
          <div className="flex justify-start">
            <div className="glass-morphism rounded-2xl px-4 py-3 flex items-center space-x-2">
              <Loader2 className="w-4 h-4 animate-spin text-primary" />
              <span className="text-sm text-gray-300">MIMIQ is typing...</span>
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Input */}
      <div className="p-4 border-t border-white/10">
        <div className="flex items-center space-x-2">
          <button
            onClick={toggleVoice}
            className={cn(
              "p-2 rounded-lg transition-all",
              isListening
                ? "bg-red-500 text-white shadow-neon-red"
                : "glass-morphism text-gray-300 hover:text-white"
            )}
          >
            <Mic className="w-5 h-5" />
          </button>

          <input
            type="text"
            value={inputText}
            onChange={(e) => setInputText(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="Type your message..."
            className="flex-1 bg-white/5 border border-white/10 rounded-lg px-4 py-2 text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-primary"
            disabled={isLoading}
          />

          <button
            onClick={handleSendMessage}
            disabled={!inputText.trim() || isLoading}
            className={cn(
              "p-2 rounded-lg transition-all",
              inputText.trim() && !isLoading
                ? "bg-gradient-to-r from-primary to-secondary text-white hover:shadow-neon"
                : "glass-morphism text-gray-500 cursor-not-allowed"
            )}
          >
            <Send className="w-5 h-5" />
          </button>
        </div>

        {isListening && (
          <div className="mt-2 flex items-center justify-center space-x-1">
            {[...Array(5)].map((_, i) => (
              <div
                key={i}
                className="w-1 h-8 bg-red-500 rounded-full animate-wave"
                style={{ animationDelay: `${i * 0.1}s` }}
              />
            ))}
          </div>
        )}
      </div>
    </div>
  );
};
