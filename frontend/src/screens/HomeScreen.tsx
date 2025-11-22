import React from 'react';
import { useAppStore } from '../stores/appStore';
import { Brain, Shield, Zap, Users } from 'lucide-react';

export const HomeScreen: React.FC = () => {
  const { setCurrentScreen, toggleChat } = useAppStore();

  const features = [
    {
      icon: '🧠',
      gradient: 'from-pink-500 to-pink-600',
      title: 'AI-Powered Diagnosis',
      description: '6 specialist AI agents analyze your symptoms in real-time',
    },
    {
      icon: '🛡️',
      gradient: 'from-blue-500 to-blue-600',
      title: 'Emergency Detection',
      description: 'Instant triage and urgency assessment to save lives',
    },
    {
      icon: '⚡',
      gradient: 'from-orange-500 to-orange-600',
      title: 'Real-Time Monitoring',
      description: 'Predicts emergencies 30-60 minutes before they happen',
    },
    {
      icon: '👥',
      gradient: 'from-purple-500 to-purple-600',
      title: 'Patient-Friendly',
      description: 'Simple, empathetic language - no medical jargon',
    },
  ];

  return (
    <div className="min-h-screen pt-24 pb-12 px-4">
      <div className="container mx-auto max-w-7xl">
        {/* Hero Section with Heart Visualization */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-12 mb-16 items-center">
          {/* Left: Text Content */}
          <div>
            <h1 className="text-5xl lg:text-7xl font-black mb-6 leading-tight">
              Emergency
              <br />
              <span className="text-transparent bg-clip-text bg-gradient-to-r from-purple-500 to-blue-500">
                Medical AI
              </span>
              <br />
              Assessment
            </h1>
            <p className="text-lg text-gray-400 mb-8 leading-relaxed">
              Get instant medical assessment from AI specialists. Powered by Google Gemini and 6
              specialized agents.
            </p>
            <div className="flex flex-col sm:flex-row gap-4">
              <button
                onClick={toggleChat}
                className="px-8 py-4 bg-gradient-to-r from-purple-600 to-blue-600 rounded-xl text-white font-semibold text-lg hover:shadow-lg hover:shadow-purple-500/50 transition-all"
              >
                Start Assessment
              </button>
              <button
                onClick={() => setCurrentScreen('dashboard')}
                className="px-8 py-4 bg-white/5 backdrop-blur-sm border border-white/10 rounded-xl text-white font-semibold text-lg hover:bg-white/10 transition-all"
              >
                View Dashboard
              </button>
            </div>
          </div>

          {/* Right: Medical Visualization */}
          <div className="relative">
            {/* ECG/Heart Rate Visualization */}
            <div className="relative h-96 bg-gradient-to-br from-gray-900/50 to-gray-800/50 rounded-3xl p-8 border border-white/5 backdrop-blur-sm overflow-hidden">
              {/* Heart Icon */}
              <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 opacity-10">
                <svg className="w-64 h-64 text-blue-500" viewBox="0 0 24 24" fill="currentColor">
                  <path d="M12 21.35l-1.45-1.32C5.4 15.36 2 12.28 2 8.5 2 5.42 4.42 3 7.5 3c1.74 0 3.41.81 4.5 2.09C13.09 3.81 14.76 3 16.5 3 19.58 3 22 5.42 22 8.5c0 3.78-3.4 6.86-8.55 11.54L12 21.35z"/>
                </svg>
              </div>

              {/* ECG Lines */}
              <svg className="absolute inset-0 w-full h-full opacity-40" preserveAspectRatio="none">
                <path
                  d="M0,200 Q50,200 100,180 T200,160 T300,140 T400,120 T500,100 L500,200 L0,200 Z"
                  fill="url(#ecg-gradient)"
                  className="animate-pulse"
                />
                <defs>
                  <linearGradient id="ecg-gradient" x1="0%" y1="0%" x2="100%" y2="0%">
                    <stop offset="0%" stopColor="#3B82F6" stopOpacity="0.3" />
                    <stop offset="100%" stopColor="#8B5CF6" stopOpacity="0.1" />
                  </linearGradient>
                </defs>
              </svg>

              {/* Stats Overlay */}
              <div className="absolute top-6 right-6 space-y-4">
                <div className="bg-gray-900/70 backdrop-blur-md rounded-xl p-4 border border-white/10">
                  <div className="flex items-center space-x-3">
                    <div className="w-12 h-12 bg-blue-500/20 rounded-lg flex items-center justify-center">
                      <svg className="w-6 h-6 text-blue-400" fill="currentColor" viewBox="0 0 24 24">
                        <path d="M12 21.35l-1.45-1.32C5.4 15.36 2 12.28 2 8.5 2 5.42 4.42 3 7.5 3c1.74 0 3.41.81 4.5 2.09C13.09 3.81 14.76 3 16.5 3 19.58 3 22 5.42 22 8.5c0 3.78-3.4 6.86-8.55 11.54L12 21.35z"/>
                      </svg>
                    </div>
                    <div>
                      <div className="text-gray-400 text-xs">Heart Rate</div>
                      <div className="text-white text-xl font-bold">86 <span className="text-sm text-gray-400">BPM</span></div>
                    </div>
                  </div>
                </div>

                <div className="bg-gray-900/70 backdrop-blur-md rounded-xl p-4 border border-white/10">
                  <div className="flex items-center space-x-3">
                    <div className="w-12 h-12 bg-purple-500/20 rounded-lg flex items-center justify-center">
                      <svg className="w-6 h-6 text-purple-400" fill="currentColor" viewBox="0 0 24 24">
                        <path d="M12 21.35l-1.45-1.32C5.4 15.36 2 12.28 2 8.5 2 5.42 4.42 3 7.5 3c1.74 0 3.41.81 4.5 2.09C13.09 3.81 14.76 3 16.5 3 19.58 3 22 5.42 22 8.5c0 3.78-3.4 6.86-8.55 11.54L12 21.35z"/>
                      </svg>
                    </div>
                    <div>
                      <div className="text-gray-400 text-xs">Heart Score</div>
                      <div className="text-white text-xl font-bold">94% <span className="text-sm text-gray-400">Healthy</span></div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Stats Grid */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-16">
          <div className="bg-gray-900/30 backdrop-blur-sm border border-white/5 rounded-2xl p-6">
            <div className="flex items-center space-x-3 mb-2">
              <div className="text-3xl">🎯</div>
              <div className="text-4xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-purple-400 to-blue-400">
                99.2%
              </div>
            </div>
            <div className="text-gray-400 text-sm">Accuracy</div>
          </div>

          <div className="bg-gray-900/30 backdrop-blur-sm border border-white/5 rounded-2xl p-6">
            <div className="flex items-center space-x-3 mb-2">
              <div className="text-3xl">⚡</div>
              <div className="text-4xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-purple-400 to-blue-400">
                &lt;1s
              </div>
            </div>
            <div className="text-gray-400 text-sm">Response</div>
          </div>

          <div className="bg-gray-900/30 backdrop-blur-sm border border-white/5 rounded-2xl p-6">
            <div className="flex items-center space-x-3 mb-2">
              <div className="text-3xl">🌍</div>
              <div className="text-4xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-purple-400 to-blue-400">
                24/7
              </div>
            </div>
            <div className="text-gray-400 text-sm">Availability</div>
          </div>
        </div>

        {/* Features Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-16">
          {features.map((feature, i) => (
            <div
              key={i}
              className="bg-gray-900/30 backdrop-blur-sm border border-white/5 rounded-2xl p-8 hover:border-purple-500/30 transition-all group"
            >
              <div className={`w-14 h-14 bg-gradient-to-br ${feature.gradient} rounded-xl flex items-center justify-center mb-4 text-2xl group-hover:scale-110 transition-transform`}>
                {feature.icon}
              </div>
              <h3 className="text-xl font-bold text-white mb-2">{feature.title}</h3>
              <p className="text-gray-400 text-sm leading-relaxed">{feature.description}</p>
            </div>
          ))}
        </div>

        {/* Trust Indicators */}
        <div className="text-center">
          <p className="text-gray-500 text-sm mb-4">Trusted by healthcare providers worldwide</p>
          <div className="flex items-center justify-center space-x-6 text-3xl opacity-50">
            <span>🏥</span>
            <span>💊</span>
            <span>🔬</span>
            <span>�</span>
            <span>🩺</span>
          </div>
        </div>
      </div>
    </div>
  );
};
