import React from 'react';
import { useAppStore } from '../stores/appStore';
import { Activity, Heart, Brain, Zap, MessageCircle, FileText, TrendingUp, ChevronRight } from 'lucide-react';

export const DashboardScreen: React.FC = () => {
  const { user, messages, toggleChat, setCurrentScreen } = useAppStore();

  const healthMetrics = [
    {
      label: 'Heart Rate',
      value: '86',
      unit: 'BPM',
      icon: '❤️',
      gradient: 'from-red-500 to-pink-500',
      status: 'Normal',
      statusColor: 'bg-green-500/20 text-green-400',
    },
    {
      label: 'Blood Pressure',
      value: '120/80',
      unit: 'mmHg',
      icon: '🩺',
      gradient: 'from-blue-500 to-cyan-500',
      status: 'Optimal',
      statusColor: 'bg-blue-500/20 text-blue-400',
    },
    {
      label: 'Oxygen Level',
      value: '98',
      unit: '%',
      icon: '🫁',
      gradient: 'from-green-500 to-emerald-500',
      status: 'Good',
      statusColor: 'bg-green-500/20 text-green-400',
    },
    {
      label: 'Heart Score',
      value: '94',
      unit: '%',
      icon: '💪',
      gradient: 'from-purple-500 to-pink-500',
      status: 'Healthy',
      statusColor: 'bg-purple-500/20 text-purple-400',
    },
  ];

  const aiAgents = [
    { name: 'Safety Agent', status: 'Active', icon: '🚨', color: 'text-red-400' },
    { name: 'Cardiology', status: 'Active', icon: '❤️', color: 'text-pink-400' },
    { name: 'Pulmonary', status: 'Active', icon: '🫁', color: 'text-blue-400' },
    { name: 'Gastro', status: 'Active', icon: '🔬', color: 'text-green-400' },
    { name: 'MSK', status: 'Active', icon: '🦴', color: 'text-orange-400' },
    { name: 'Triage', status: 'Ready', icon: '🎯', color: 'text-purple-400' },
  ];

  return (
    <div className="min-h-screen pt-24 pb-12 px-4">
      <div className="container mx-auto max-w-7xl">
        {/* Welcome Header */}
        <div className="mb-8">
          <h1 className="text-4xl font-bold text-white mb-2">
            Welcome back, {user?.name || 'User'}! 👋
          </h1>
          <p className="text-gray-400">Here's your real-time health dashboard</p>
        </div>

        {/* Health Metrics Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          {healthMetrics.map((metric, i) => (
            <div
              key={i}
              className="bg-gray-900/30 backdrop-blur-sm border border-white/5 rounded-2xl p-6 hover:border-purple-500/30 transition-all group"
            >
              <div className="flex items-center justify-between mb-4">
                <div className={`w-12 h-12 rounded-xl bg-gradient-to-br ${metric.gradient} flex items-center justify-center text-2xl group-hover:scale-110 transition-transform`}>
                  {metric.icon}
                </div>
                <span className={`text-xs px-3 py-1 rounded-full ${metric.statusColor} font-medium`}>
                  {metric.status}
                </span>
              </div>
              <div className="mb-2">
                <span className="text-3xl font-bold text-white">{metric.value}</span>
                <span className="text-gray-400 text-sm ml-1">{metric.unit}</span>
              </div>
              <div className="text-gray-400 text-sm">{metric.label}</div>
            </div>
          ))}
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8 mb-8">
          {/* AI Agents Status */}
          <div className="lg:col-span-2 bg-gray-900/30 backdrop-blur-sm border border-white/5 rounded-2xl p-6">
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-2xl font-bold text-white flex items-center space-x-2">
                <Brain className="w-6 h-6 text-purple-400" />
                <span>AI Specialist Agents</span>
              </h2>
              <button
                onClick={toggleChat}
                className="px-4 py-2 bg-gradient-to-r from-purple-600 to-blue-600 rounded-lg text-white text-sm font-semibold hover:shadow-lg hover:shadow-purple-500/50 transition-all"
              >
                Start Analysis
              </button>
            </div>
            <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
              {aiAgents.map((agent, i) => (
                <div
                  key={i}
                  className="bg-white/5 rounded-xl p-4 border border-white/5 hover:border-purple-500/30 transition-all"
                >
                  <div className="flex items-center space-x-3 mb-2">
                    <span className="text-2xl">{agent.icon}</span>
                    <div className="w-2 h-2 rounded-full bg-green-400 animate-pulse"></div>
                  </div>
                  <div className="text-white font-semibold text-sm mb-1">{agent.name}</div>
                  <div className="text-gray-400 text-xs">{agent.status}</div>
                </div>
              ))}
            </div>
          </div>

          {/* Quick Actions */}
          <div className="bg-gray-900/30 backdrop-blur-sm border border-white/5 rounded-2xl p-6">
            <h2 className="text-2xl font-bold text-white mb-6">Quick Actions</h2>
            <div className="space-y-3">
              <button
                onClick={toggleChat}
                className="w-full bg-gradient-to-r from-purple-600 to-blue-600 rounded-xl p-4 text-left hover:shadow-lg hover:shadow-purple-500/50 transition-all group"
              >
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-3">
                    <div className="w-10 h-10 rounded-lg bg-white/10 flex items-center justify-center">
                      <MessageCircle className="w-5 h-5 text-white" />
                    </div>
                    <div>
                      <div className="text-white font-semibold">Chat with AI</div>
                      <div className="text-white/70 text-xs">Get instant help</div>
                    </div>
                  </div>
                  <ChevronRight className="w-5 h-5 text-white/50 group-hover:translate-x-1 transition-transform" />
                </div>
              </button>

              <button
                onClick={() => setCurrentScreen('upload')}
                className="w-full bg-white/5 rounded-xl p-4 text-left hover:bg-white/10 transition-all group border border-white/5"
              >
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-3">
                    <div className="w-10 h-10 rounded-lg bg-blue-500/20 flex items-center justify-center">
                      <FileText className="w-5 h-5 text-blue-400" />
                    </div>
                    <div>
                      <div className="text-white font-semibold">Upload Reports</div>
                      <div className="text-gray-400 text-xs">Medical records</div>
                    </div>
                  </div>
                  <ChevronRight className="w-5 h-5 text-gray-400 group-hover:translate-x-1 transition-transform" />
                </div>
              </button>

              <button className="w-full bg-red-500/10 rounded-xl p-4 text-left hover:bg-red-500/20 transition-all group border border-red-500/20 pulse-emergency">
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-3">
                    <div className="w-10 h-10 rounded-lg bg-red-500/20 flex items-center justify-center">
                      <Zap className="w-5 h-5 text-red-400" />
                    </div>
                    <div>
                      <div className="text-white font-semibold">Emergency</div>
                      <div className="text-red-300 text-xs">Immediate help</div>
                    </div>
                  </div>
                  <ChevronRight className="w-5 h-5 text-red-400 group-hover:translate-x-1 transition-transform" />
                </div>
              </button>
            </div>
          </div>
        </div>

        {/* Recent Activity */}
        <div className="bg-gray-900/30 backdrop-blur-sm border border-white/5 rounded-2xl p-6">
          <h2 className="text-2xl font-bold text-white mb-6">Recent Activity</h2>
          <div className="space-y-4">
            {[
              { icon: MessageCircle, text: 'Started AI health assessment', time: '5 minutes ago', color: 'bg-blue-500/20 text-blue-400' },
              { icon: Heart, text: 'Heart rate monitoring completed', time: '2 hours ago', color: 'bg-red-500/20 text-red-400' },
              { icon: FileText, text: 'Medical report uploaded successfully', time: '1 day ago', color: 'bg-green-500/20 text-green-400' },
              { icon: Brain, text: 'AI analysis generated insights', time: '2 days ago', color: 'bg-purple-500/20 text-purple-400' },
            ].map((activity, i) => {
              const Icon = activity.icon;
              return (
                <div key={i} className="flex items-center space-x-4 p-4 bg-white/5 rounded-xl border border-white/5 hover:border-purple-500/30 transition-all">
                  <div className={`w-10 h-10 rounded-lg ${activity.color} flex items-center justify-center`}>
                    <Icon className="w-5 h-5" />
                  </div>
                  <div className="flex-1">
                    <p className="text-white font-medium">{activity.text}</p>
                    <p className="text-gray-400 text-sm">{activity.time}</p>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      </div>
    </div>
  );
};
