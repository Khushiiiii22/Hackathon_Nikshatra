/**
 * Emergency Call Button - Always Visible
 * Supports 911 (US) and 108 (India) emergency numbers
 */

import React, { useState } from 'react';
import { Phone, X } from 'lucide-react';

interface EmergencyButtonProps {
  className?: string;
}

export const EmergencyButton: React.FC<EmergencyButtonProps> = ({ className = '' }) => {
  const [showOptions, setShowOptions] = useState(false);

  const handleEmergencyCall = (number: string) => {
    // Confirm before calling
    const confirmed = window.confirm(
      `You are about to call emergency services (${number}).\n\nAre you sure you want to proceed?`
    );

    if (confirmed) {
      window.location.href = `tel:${number}`;
    }
  };

  return (
    <>
      {/* Main Emergency Button - Fixed Position */}
      <div className={`fixed bottom-6 right-6 z-50 ${className}`}>
        {!showOptions ? (
          <button
            onClick={() => setShowOptions(true)}
            className="group relative w-20 h-20 bg-red-600 hover:bg-red-700 rounded-full shadow-2xl flex items-center justify-center transition-all duration-300 hover:scale-110 animate-pulse"
            aria-label="Emergency Call"
          >
            <Phone className="w-10 h-10 text-white" />
            <span className="absolute -top-12 right-0 bg-red-600 text-white text-xs font-bold px-3 py-1 rounded-full opacity-0 group-hover:opacity-100 transition-opacity whitespace-nowrap">
              Emergency
            </span>
          </button>
        ) : (
          <div className="flex flex-col gap-3">
            {/* Close button */}
            <button
              onClick={() => setShowOptions(false)}
              className="self-end w-10 h-10 bg-gray-700 hover:bg-gray-800 rounded-full flex items-center justify-center shadow-lg"
              aria-label="Close emergency options"
            >
              <X className="w-5 h-5 text-white" />
            </button>

            {/* Emergency number options */}
            <div className="flex flex-col gap-3 bg-white rounded-2xl shadow-2xl p-4 border-4 border-red-600">
              <p className="text-sm font-bold text-gray-900 text-center">
                Choose Emergency Number
              </p>

              {/* 911 (US) */}
              <button
                onClick={() => handleEmergencyCall('911')}
                className="w-full min-w-[200px] h-16 bg-red-600 hover:bg-red-700 rounded-xl shadow-lg flex items-center justify-center gap-3 transition-all duration-200 hover:scale-105"
              >
                <Phone className="w-6 h-6 text-white" />
                <div className="text-left">
                  <div className="text-white font-bold text-xl">911</div>
                  <div className="text-red-100 text-xs">United States</div>
                </div>
              </button>

              {/* 108 (India) */}
              <button
                onClick={() => handleEmergencyCall('108')}
                className="w-full min-w-[200px] h-16 bg-red-600 hover:bg-red-700 rounded-xl shadow-lg flex items-center justify-center gap-3 transition-all duration-200 hover:scale-105"
              >
                <Phone className="w-6 h-6 text-white" />
                <div className="text-left">
                  <div className="text-white font-bold text-xl">108</div>
                  <div className="text-red-100 text-xs">India</div>
                </div>
              </button>

              {/* 112 (International) */}
              <button
                onClick={() => handleEmergencyCall('112')}
                className="w-full min-w-[200px] h-14 bg-orange-600 hover:bg-orange-700 rounded-xl shadow-lg flex items-center justify-center gap-3 transition-all duration-200 hover:scale-105"
              >
                <Phone className="w-5 h-5 text-white" />
                <div className="text-left">
                  <div className="text-white font-bold text-lg">112</div>
                  <div className="text-orange-100 text-xs">International</div>
                </div>
              </button>
            </div>
          </div>
        )}
      </div>

      {/* Mobile bottom banner for emergencies */}
      {showOptions && (
        <div
          className="fixed inset-0 bg-black bg-opacity-50 z-40 md:hidden"
          onClick={() => setShowOptions(false)}
        />
      )}
    </>
  );
};

export default EmergencyButton;
