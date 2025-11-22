import React from 'react';
import { useAppStore } from '../stores/appStore';
import { Home, LayoutDashboard, Upload, Info, MessageCircle, LogIn, User, LogOut } from 'lucide-react';
import { cn } from '../lib/utils';

export const Navigation: React.FC = () => {
  const { currentScreen, setCurrentScreen, user, isLoggedIn, login, logout, toggleChat } = useAppStore();

  const handleLogin = () => {
    // Demo login
    login({
      id: 'user_1',
      name: 'John Doe',
      email: 'john@example.com',
      role: 'patient',
    });
  };

  const navItems = [
    { id: 'home', label: 'Home', icon: Home },
    { id: 'dashboard', label: 'Dashboard', icon: LayoutDashboard },
    { id: 'upload', label: 'Upload Reports', icon: Upload },
    { id: 'about', label: 'About', icon: Info },
  ] as const;

  return (
    <nav className="fixed top-0 left-0 right-0 z-50 glass-morphism border-b border-white/10">
      <div className="container mx-auto px-4">
        <div className="flex items-center justify-between h-16">
          {/* Logo */}
          <div className="flex items-center space-x-2">
            <div className="w-10 h-10 rounded-lg bg-gradient-to-br from-primary to-secondary flex items-center justify-center shadow-neon">
              <span className="text-white font-bold text-xl">M</span>
            </div>
            <span className="text-xl font-bold gradient-text">MIMIQ</span>
          </div>

          {/* Navigation Links */}
          <div className="hidden md:flex items-center space-x-1">
            {navItems.map((item) => {
              const Icon = item.icon;
              return (
                <button
                  key={item.id}
                  onClick={() => setCurrentScreen(item.id)}
                  className={cn(
                    "flex items-center space-x-2 px-4 py-2 rounded-lg transition-all",
                    currentScreen === item.id
                      ? "bg-primary/20 text-primary shadow-neon"
                      : "text-gray-300 hover:bg-white/5 hover:text-white"
                  )}
                >
                  <Icon className="w-4 h-4" />
                  <span>{item.label}</span>
                </button>
              );
            })}
          </div>

          {/* Right Side - Chat & User */}
          <div className="flex items-center space-x-3">
            {/* Chatbot Toggle */}
            <button
              onClick={toggleChat}
              className="flex items-center space-x-2 px-4 py-2 rounded-lg bg-gradient-to-r from-primary to-secondary text-white hover:shadow-neon transition-all"
            >
              <MessageCircle className="w-4 h-4" />
              <span className="hidden sm:inline">Chat with AI</span>
            </button>

            {/* User Account */}
            {isLoggedIn && user ? (
              <div className="relative group">
                <button className="flex items-center space-x-2 px-3 py-2 rounded-lg glass-morphism hover:shadow-neon transition-all">
                  <div className="w-8 h-8 rounded-full bg-gradient-to-br from-primary to-secondary flex items-center justify-center">
                    <span className="text-white text-sm font-semibold">
                      {user.name.charAt(0)}
                    </span>
                  </div>
                  <div className="hidden lg:block text-left">
                    <div className="text-sm font-semibold text-white">{user.name}</div>
                    <div className="text-xs text-gray-400 capitalize">{user.role}</div>
                  </div>
                </button>

                {/* Dropdown */}
                <div className="absolute right-0 top-full mt-2 w-48 glass-morphism rounded-lg shadow-neon opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all">
                  <div className="p-2">
                    <button className="w-full flex items-center space-x-2 px-3 py-2 rounded hover:bg-white/10 text-gray-300 hover:text-white transition-all">
                      <User className="w-4 h-4" />
                      <span>Profile</span>
                    </button>
                    <button
                      onClick={logout}
                      className="w-full flex items-center space-x-2 px-3 py-2 rounded hover:bg-white/10 text-gray-300 hover:text-white transition-all"
                    >
                      <LogOut className="w-4 h-4" />
                      <span>Logout</span>
                    </button>
                  </div>
                </div>
              </div>
            ) : (
              <button
                onClick={handleLogin}
                className="flex items-center space-x-2 px-4 py-2 rounded-lg glass-morphism hover:shadow-neon transition-all text-white"
              >
                <LogIn className="w-4 h-4" />
                <span className="hidden sm:inline">Login</span>
              </button>
            )}
          </div>
        </div>

        {/* Mobile Navigation */}
        <div className="md:hidden flex items-center justify-around pb-2">
          {navItems.map((item) => {
            const Icon = item.icon;
            return (
              <button
                key={item.id}
                onClick={() => setCurrentScreen(item.id)}
                className={cn(
                  "flex flex-col items-center space-y-1 px-3 py-2 rounded-lg transition-all",
                  currentScreen === item.id
                    ? "text-primary"
                    : "text-gray-400 hover:text-white"
                )}
              >
                <Icon className="w-5 h-5" />
                <span className="text-xs">{item.label}</span>
              </button>
            );
          })}
        </div>
      </div>
    </nav>
  );
};
