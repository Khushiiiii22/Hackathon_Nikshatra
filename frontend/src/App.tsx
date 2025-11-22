import React from 'react';
import { useAppStore } from './stores/appStore';
import { Navigation } from './components/Navigation';
import { ChatBot } from './components/ChatBot';
import { HomeScreen } from './screens/HomeScreen';
import { DashboardScreen } from './screens/DashboardScreen';
import { UploadScreen } from './screens/UploadScreen';
import { AboutScreen } from './screens/AboutScreen';

function App() {
  const { currentScreen } = useAppStore();

  return (
    <div className="min-h-screen bg-background text-foreground">
      {/* Background Effects */}
      <div className="fixed inset-0 z-0 pointer-events-none">
        <div className="absolute top-0 left-1/4 w-96 h-96 bg-purple-600/20 rounded-full blur-3xl animate-float" />
        <div
          className="absolute bottom-0 right-1/4 w-96 h-96 bg-pink-600/20 rounded-full blur-3xl animate-float"
          style={{ animationDelay: '1s' }}
        />
        <div
          className="absolute top-1/2 left-1/2 w-96 h-96 bg-blue-600/15 rounded-full blur-3xl animate-float"
          style={{ animationDelay: '2s' }}
        />
      </div>

      {/* Navigation */}
      <Navigation />

      {/* Main Content */}
      <div className="relative z-10">
        {currentScreen === 'home' && <HomeScreen />}
        {currentScreen === 'dashboard' && <DashboardScreen />}
        {currentScreen === 'upload' && <UploadScreen />}
        {currentScreen === 'about' && <AboutScreen />}
      </div>

      {/* Floating Chatbot */}
      <ChatBot />
    </div>
  );
}

export default App;
