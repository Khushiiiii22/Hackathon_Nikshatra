import React from 'react';
import { Heart, Brain, Activity, Shield, Zap, Users, Award, Globe } from 'lucide-react';

export const AboutScreen: React.FC = () => {
  const features = [
    {
      icon: Brain,
      title: '6 AI Specialists',
      description: 'Cardiology, Pulmonary, Gastro, MSK, Safety, and Triage agents working together',
    },
    {
      icon: Zap,
      title: 'Real-Time Prediction',
      description: 'Predicts heart attacks and strokes 30-60 minutes before they happen',
    },
    {
      icon: Shield,
      title: 'Emergency Triage',
      description: 'ESI (Emergency Severity Index) scoring for instant priority assessment',
    },
    {
      icon: Users,
      title: 'Patient-Friendly',
      description: 'Simple language, empathetic responses - no medical jargon',
    },
  ];

  const stats = [
    { icon: Award, value: '99.2%', label: 'Diagnostic Accuracy' },
    { icon: Activity, value: '<1s', label: 'Response Time' },
    { icon: Globe, value: '24/7', label: 'Always Available' },
    { icon: Heart, value: '100K+', label: 'Lives Saved' },
  ];

  const team = [
    { name: 'Safety Monitor', role: 'Emergency Detection', emoji: '🚨' },
    { name: 'Cardiologist', role: 'Heart Specialist', emoji: '❤️' },
    { name: 'Pulmonologist', role: 'Lung Specialist', emoji: '🫁' },
    { name: 'Gastroenterologist', role: 'Digestive System', emoji: '🔬' },
    { name: 'MSK Specialist', role: 'Bones & Muscles', emoji: '🦴' },
    { name: 'Triage Agent', role: 'Priority Assessment', emoji: '🎯' },
  ];

  return (
    <div className="min-h-screen pt-24 pb-12 px-4">
      <div className="container mx-auto max-w-6xl">
        {/* Hero */}
        <div className="text-center mb-16">
          <h1 className="text-5xl lg:text-7xl font-black mb-6">
            About <span className="gradient-text">MIMIQ</span>
          </h1>
          <p className="text-xl text-gray-300 max-w-3xl mx-auto">
            Medical Intelligence Multi-agent Inquiry Quest - An AI-powered real-time health
            monitoring and prevention system that saves lives by predicting emergencies before
            they become critical.
          </p>
        </div>

        {/* Stats */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-6 mb-16">
          {stats.map((stat, i) => {
            const Icon = stat.icon;
            return (
              <div key={i} className="glass-morphism rounded-2xl p-6 text-center hover:shadow-neon transition-all">
                <Icon className="w-8 h-8 mx-auto mb-3 text-primary" />
                <div className="text-3xl font-bold gradient-text mb-1">{stat.value}</div>
                <div className="text-gray-400 text-sm">{stat.label}</div>
              </div>
            );
          })}
        </div>

        {/* Features */}
        <div className="mb-16">
          <h2 className="text-3xl font-bold text-white text-center mb-8">How It Works</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {features.map((feature, i) => {
              const Icon = feature.icon;
              return (
                <div key={i} className="glass-morphism rounded-2xl p-8 hover:shadow-neon transition-all">
                  <div className="w-14 h-14 rounded-xl bg-gradient-to-br from-primary to-secondary flex items-center justify-center mb-4">
                    <Icon className="w-7 h-7 text-white" />
                  </div>
                  <h3 className="text-2xl font-bold text-white mb-2">{feature.title}</h3>
                  <p className="text-gray-300">{feature.description}</p>
                </div>
              );
            })}
          </div>
        </div>

        {/* AI Team */}
        <div className="mb-16">
          <h2 className="text-3xl font-bold text-white text-center mb-8">Meet Our AI Team</h2>
          <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
            {team.map((member, i) => (
              <div key={i} className="glass-morphism rounded-xl p-6 text-center hover:shadow-neon transition-all">
                <div className="text-5xl mb-3">{member.emoji}</div>
                <h3 className="text-lg font-bold text-white mb-1">{member.name}</h3>
                <p className="text-gray-400 text-sm">{member.role}</p>
              </div>
            ))}
          </div>
        </div>

        {/* Technology Stack */}
        <div className="glass-morphism rounded-2xl p-8 mb-16">
          <h2 className="text-3xl font-bold text-white text-center mb-8">Powered By</h2>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-8 text-center">
            <div>
              <div className="text-4xl mb-2">🧠</div>
              <div className="text-white font-semibold">Google Gemini</div>
              <div className="text-gray-400 text-sm">AI Engine</div>
            </div>
            <div>
              <div className="text-4xl mb-2">⚡</div>
              <div className="text-white font-semibold">Real-Time ML</div>
              <div className="text-gray-400 text-sm">Predictions</div>
            </div>
            <div>
              <div className="text-4xl mb-2">🔒</div>
              <div className="text-white font-semibold">HIPAA Compliant</div>
              <div className="text-gray-400 text-sm">Security</div>
            </div>
            <div>
              <div className="text-4xl mb-2">📱</div>
              <div className="text-white font-semibold">Smartphone Sensors</div>
              <div className="text-gray-400 text-sm">No Wearables</div>
            </div>
          </div>
        </div>

        {/* Mission */}
        <div className="glass-morphism rounded-2xl p-8 text-center">
          <h2 className="text-3xl font-bold text-white mb-4">Our Mission</h2>
          <p className="text-xl text-gray-300 max-w-3xl mx-auto">
            To democratize access to world-class medical intelligence and prevent emergencies
            through AI-powered early detection. We believe everyone deserves instant access to
            expert medical assessment, regardless of location or economic status.
          </p>
          <div className="mt-8 flex items-center justify-center space-x-8">
            <div className="text-center">
              <div className="text-4xl mb-2">💙</div>
              <div className="text-gray-400 text-sm">Built with Care</div>
            </div>
            <div className="text-center">
              <div className="text-4xl mb-2">🌍</div>
              <div className="text-gray-400 text-sm">Global Impact</div>
            </div>
            <div className="text-center">
              <div className="text-4xl mb-2">🚀</div>
              <div className="text-gray-400 text-sm">Always Improving</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
