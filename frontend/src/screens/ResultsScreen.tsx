/**
 * Results Screen - Patient-Friendly Diagnosis Display
 * Shows simplified results with clear next steps
 */

import React, { useState, useEffect } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import { AlertCircle, CheckCircle, AlertTriangle, Info, Phone, Download, Share2, ArrowLeft } from 'lucide-react';
import { getResults } from '../services/api';
import type { ResultsResponse } from '../services/api';
import EmergencyButton from '../components/EmergencyButton';

export const ResultsScreen: React.FC = () => {
  const location = useLocation();
  const navigate = useNavigate();
  const patientId = location.state?.patientId;

  const [results, setResults] = useState<ResultsResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!patientId) {
      navigate('/');
      return;
    }

    fetchResults();
  }, [patientId]);

  const fetchResults = async () => {
    try {
      const data = await getResults(patientId);
      setResults(data);
    } catch (err: any) {
      setError(err.message || 'Failed to load results');
    } finally {
      setLoading(false);
    }
  };

  const getUrgencyConfig = (esiLevel: number) => {
    switch (esiLevel) {
      case 1:
        return {
          icon: <AlertCircle className="w-16 h-16" />,
          color: 'text-red-600',
          bgColor: 'bg-red-100',
          borderColor: 'border-red-600',
          label: 'CRITICAL - EMERGENCY',
        };
      case 2:
        return {
          icon: <AlertTriangle className="w-16 h-16" />,
          color: 'text-orange-600',
          bgColor: 'bg-orange-100',
          borderColor: 'border-orange-600',
          label: 'HIGH PRIORITY - URGENT',
        };
      case 3:
        return {
          icon: <Info className="w-16 h-16" />,
          color: 'text-yellow-600',
          bgColor: 'bg-yellow-100',
          borderColor: 'border-yellow-600',
          label: 'MODERATE - SEE DOCTOR SOON',
        };
      default:
        return {
          icon: <CheckCircle className="w-16 h-16" />,
          color: 'text-green-600',
          bgColor: 'bg-green-100',
          borderColor: 'border-green-600',
          label: 'LOW PRIORITY - ROUTINE CARE',
        };
    }
  };

  const handleDownload = () => {
    if (!results) return;

    const report = `
MIMIQ Medical AI Analysis Report
Generated: ${new Date(results.timestamp).toLocaleString()}
Patient ID: ${results.patient_id}

URGENCY LEVEL: ${results.summary?.esi_level || 'N/A'}
${results.summary?.recommendation || ''}

PRIMARY CONCERN:
${results.summary?.primary_concern || 'N/A'}

NEXT STEPS:
${results.summary?.next_steps?.map((step, i) => `${i + 1}. ${step}`).join('\n') || 'N/A'}

SYMPTOMS REPORTED:
${results.symptoms?.join(', ') || 'N/A'}

Note: This is an AI-generated analysis and should not replace professional medical advice.
    `.trim();

    const blob = new Blob([report], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `MIMIQ_Report_${results.patient_id}.txt`;
    a.click();
    URL.revokeObjectURL(url);
  };

  const handleShare = async () => {
    if (!results) return;

    const shareText = `MIMIQ Medical Analysis - ESI Level ${results.summary?.esi_level}\n${results.summary?.recommendation}`;

    if (navigator.share) {
      try {
        await navigator.share({
          title: 'MIMIQ Medical Analysis',
          text: shareText,
        });
      } catch (err) {
        console.log('Share cancelled');
      }
    } else {
      // Fallback: copy to clipboard
      navigator.clipboard.writeText(shareText);
      alert('Report copied to clipboard!');
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50 flex items-center justify-center">
        <div className="text-center">
          <div className="w-16 h-16 border-4 border-blue-600 border-t-transparent rounded-full animate-spin mx-auto mb-4" />
          <p className="text-xl text-gray-700">Loading your results...</p>
        </div>
      </div>
    );
  }

  if (error || !results) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50 flex items-center justify-center p-4">
        <div className="bg-red-100 border-2 border-red-600 rounded-2xl p-8 max-w-md">
          <AlertCircle className="w-16 h-16 text-red-600 mx-auto mb-4" />
          <h2 className="text-2xl font-bold text-red-900 mb-2">Error Loading Results</h2>
          <p className="text-red-800">{error || 'No results found'}</p>
          <button
            onClick={() => navigate('/')}
            className="mt-6 w-full h-14 bg-red-600 hover:bg-red-700 text-white font-bold rounded-xl"
          >
            Start New Assessment
          </button>
        </div>
      </div>
    );
  }

  const urgencyConfig = getUrgencyConfig(results.summary?.esi_level || 3);

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50 p-4 pb-24">
      <div className="max-w-4xl mx-auto">
        {/* Back Button */}
        <button
          onClick={() => navigate('/')}
          className="mb-6 flex items-center gap-2 text-gray-700 hover:text-gray-900"
        >
          <ArrowLeft className="w-5 h-5" />
          <span className="font-semibold">New Assessment</span>
        </button>

        {/* Urgency Banner */}
        <div className={`${urgencyConfig.bgColor} border-4 ${urgencyConfig.borderColor} rounded-2xl p-8 mb-6 shadow-lg`}>
          <div className="flex items-center justify-center gap-4 mb-4">
            <div className={urgencyConfig.color}>{urgencyConfig.icon}</div>
          </div>
          <div className="text-center">
            <div className={`text-3xl font-bold mb-2 ${urgencyConfig.color}`}>
              ESI Level {results.summary?.esi_level}
            </div>
            <div className={`text-xl font-bold ${urgencyConfig.color}`}>
              {urgencyConfig.label}
            </div>
          </div>
        </div>

        {/* Recommendation */}
        <div className="bg-white rounded-2xl shadow-lg p-8 mb-6">
          <h2 className="text-2xl font-bold text-gray-900 mb-4">What This Means</h2>
          <p className="text-xl text-gray-800 leading-relaxed">
            {results.summary?.recommendation}
          </p>
        </div>

        {/* Primary Concern */}
        <div className="bg-white rounded-2xl shadow-lg p-8 mb-6">
          <h2 className="text-2xl font-bold text-gray-900 mb-4">Primary Concern</h2>
          <p className="text-lg text-gray-800 leading-relaxed">
            {results.summary?.primary_concern}
          </p>
        </div>

        {/* Next Steps */}
        <div className="bg-white rounded-2xl shadow-lg p-8 mb-6">
          <h2 className="text-2xl font-bold text-gray-900 mb-6">
            What To Do RIGHT NOW
          </h2>
          <div className="space-y-4">
            {results.summary?.next_steps?.map((step, index) => (
              <div key={index} className="flex gap-4">
                <div className="flex-shrink-0 w-10 h-10 bg-blue-600 text-white rounded-full flex items-center justify-center font-bold text-lg">
                  {index + 1}
                </div>
                <p className="text-lg text-gray-800 pt-1">{step}</p>
              </div>
            ))}
          </div>
        </div>

        {/* Emergency Calls */}
        {results.summary?.esi_level <= 2 && (
          <div className="bg-red-50 border-4 border-red-600 rounded-2xl p-8 mb-6">
            <h2 className="text-2xl font-bold text-red-900 mb-4 flex items-center gap-3">
              <Phone className="w-8 h-8" />
              Emergency Contact
            </h2>
            <div className="grid md:grid-cols-2 gap-4">
              <a
                href="tel:911"
                className="h-20 bg-red-600 hover:bg-red-700 text-white rounded-xl shadow-lg flex items-center justify-center gap-3 transition-all duration-200 hover:scale-105"
              >
                <Phone className="w-6 h-6" />
                <div>
                  <div className="font-bold text-2xl">911</div>
                  <div className="text-xs">United States</div>
                </div>
              </a>
              <a
                href="tel:108"
                className="h-20 bg-red-600 hover:bg-red-700 text-white rounded-xl shadow-lg flex items-center justify-center gap-3 transition-all duration-200 hover:scale-105"
              >
                <Phone className="w-6 h-6" />
                <div>
                  <div className="font-bold text-2xl">108</div>
                  <div className="text-xs">India</div>
                </div>
              </a>
            </div>
          </div>
        )}

        {/* Symptoms Reported */}
        <div className="bg-white rounded-2xl shadow-lg p-8 mb-6">
          <h2 className="text-2xl font-bold text-gray-900 mb-4">Symptoms You Reported</h2>
          <div className="flex flex-wrap gap-3">
            {results.symptoms?.map((symptom, index) => (
              <span
                key={index}
                className="px-4 py-2 bg-blue-100 text-blue-900 rounded-full font-semibold"
              >
                {symptom}
              </span>
            ))}
          </div>
        </div>

        {/* AI Specialists Consulted */}
        <div className="bg-white rounded-2xl shadow-lg p-8 mb-6">
          <h2 className="text-2xl font-bold text-gray-900 mb-4">
            AI Specialists Consulted: {results.summary?.agents_consulted || 6}
          </h2>
          <div className="grid md:grid-cols-2 gap-4">
            {Object.entries(results.detailed_results || {}).map(([agentId, result]: [string, any]) => (
              <div key={agentId} className="border-2 border-gray-200 rounded-xl p-4">
                <div className="flex items-center justify-between mb-2">
                  <span className="font-bold text-gray-900 capitalize">{agentId}</span>
                  {result.confidence && (
                    <span className="text-sm font-semibold text-blue-600">
                      {result.confidence}% confident
                    </span>
                  )}
                </div>
                <p className="text-sm text-gray-700">{result.diagnosis}</p>
              </div>
            ))}
          </div>
        </div>

        {/* Action Buttons */}
        <div className="grid md:grid-cols-2 gap-4">
          <button
            onClick={handleDownload}
            className="h-16 bg-blue-600 hover:bg-blue-700 text-white font-bold rounded-xl shadow-lg flex items-center justify-center gap-3 transition-all duration-200 hover:scale-105"
          >
            <Download className="w-6 h-6" />
            Download Report
          </button>
          <button
            onClick={handleShare}
            className="h-16 bg-purple-600 hover:bg-purple-700 text-white font-bold rounded-xl shadow-lg flex items-center justify-center gap-3 transition-all duration-200 hover:scale-105"
          >
            <Share2 className="w-6 h-6" />
            Share with Doctor
          </button>
        </div>

        {/* Disclaimer */}
        <div className="mt-8 bg-yellow-50 border-2 border-yellow-600 rounded-xl p-6">
          <p className="text-sm text-yellow-900">
            <strong>Important:</strong> This is an AI-generated analysis and should not replace professional medical advice. 
            If you have serious symptoms or your condition worsens, seek immediate medical attention.
          </p>
        </div>
      </div>

      {/* Emergency Button */}
      <EmergencyButton />
    </div>
  );
};

export default ResultsScreen;
