import React, { useState, useRef, useEffect } from 'react';
import { useAppStore } from '../stores/appStore';
import { X, Send, Mic, Loader2 } from 'lucide-react';
import { cn } from '../lib/utils';

const API_URL = 'http://localhost:5000/api';

export const ChatBot: React.FC = () => {
  const { isChatOpen, toggleChat, messages, addMessage, patientId } = useAppStore();
  const [inputText, setInputText] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [isListening, setIsListening] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

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

  const toggleVoice = () => {
    setIsListening(!isListening);
    // TODO: Implement Web Speech API
  };

  if (!isChatOpen) return null;

  return (
    <div className="fixed bottom-4 right-4 z-50 w-96 h-[600px] glass-morphism rounded-2xl shadow-neon-strong flex flex-col overflow-hidden">
      {/* Header */}
      <div className="bg-gradient-to-r from-primary to-secondary p-4 flex items-center justify-between">
        <div className="flex items-center space-x-3">
          <div className="w-10 h-10 rounded-full bg-white/20 flex items-center justify-center">
            <span className="text-2xl">🤖</span>
          </div>
          <div>
            <h3 className="text-white font-semibold">MIMIQ AI Assistant</h3>
            <p className="text-white/80 text-xs">Online • Always here to help</p>
          </div>
        </div>
        <button
          onClick={toggleChat}
          className="text-white/80 hover:text-white transition-colors"
        >
          <X className="w-5 h-5" />
        </button>
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
