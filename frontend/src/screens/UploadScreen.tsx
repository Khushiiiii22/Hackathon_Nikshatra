import React, { useCallback, useState } from 'react';
import { useAppStore, type UploadedFile } from '../stores/appStore';
import { Upload, FileText, X, CheckCircle, AlertCircle, Loader2 } from 'lucide-react';
import { cn } from '../lib/utils';

interface AnalysisResult {
  summary: {
    urgency: string;
    esi_level: number;
    primary_concern: string;
    recommendation: string;
    patient_brief: string;
    symptoms_identified: string[];
    medications_mentioned: string[];
    medication_recommendations: string[];
    prevention_strategies: string[];
    risk_factors: string[];
    key_findings: string[];
    next_steps: string[];
    follow_up_actions: string[];
    agents_consulted: number;
  };
  detailed_results: Record<string, any>;
}

export const UploadScreen: React.FC = () => {
  const { uploadedFiles, addFile, updateFileProgress, updateFileStatus, removeFile, patientId } = useAppStore();
  const [isDragging, setIsDragging] = useState(false);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [analysisResult, setAnalysisResult] = useState<AnalysisResult | null>(null);

  const handleDrag = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
  }, []);

  const handleDragIn = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.dataTransfer.items && e.dataTransfer.items.length > 0) {
      setIsDragging(true);
    }
  }, []);

  const handleDragOut = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);
  }, []);

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);

    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      handleFiles(Array.from(e.dataTransfer.files));
    }
  }, []);

  const handleFileInput = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      handleFiles(Array.from(e.target.files));
    }
  };

  const handleFiles = (files: File[]) => {
    files.forEach(async (file) => {
      const uploadFile: UploadedFile = {
        id: `file_${Date.now()}_${Math.random()}`,
        name: file.name,
        size: file.size,
        type: file.type,
        uploadedAt: new Date().toISOString(),
        status: 'uploading',
        progress: 0,
        file: file, // Store the actual file
      };

      addFile(uploadFile);

      // Read file content for text-based files
      if (file.type.includes('text') || file.name.endsWith('.txt')) {
        const reader = new FileReader();
        reader.onload = (e) => {
          const content = e.target?.result as string;
          // Update file with content
          const fileWithContent = { ...uploadFile, content };
          // You'd need to add an updateFile method to the store
          // For now, we'll use the file object directly
        };
        reader.readAsText(file);
      }

      // Simulate upload progress
      simulateUpload(uploadFile.id);
    });
  };

  const simulateUpload = (fileId: string) => {
    let progress = 0;
    const interval = setInterval(() => {
      progress += 10;
      updateFileProgress(fileId, progress);

      if (progress >= 100) {
        clearInterval(interval);
        updateFileStatus(fileId, 'success');
      }
    }, 200);
  };

  const formatFileSize = (bytes: number) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i];
  };

  const handleAnalyzeAll = async () => {
    if (uploadedFiles.length === 0) {
      alert('Please upload at least one file to analyze');
      return;
    }

    setIsAnalyzing(true);
    setAnalysisResult(null);

    try {
      // Get the first file that has actual file content
      const fileToAnalyze = uploadedFiles.find(f => f.file);
      
      if (!fileToAnalyze || !fileToAnalyze.file) {
        // Fallback to JSON request if no file object
        const response = await fetch('http://localhost:5000/api/analyze', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            patient_id: patientId,
            symptoms: `Analyzing ${uploadedFiles.length} file(s):\n${uploadedFiles.map(f => `- ${f.name}`).join('\n')}\n\nPlease provide comprehensive analysis including symptoms, medications, and prevention strategies.`,
          }),
        });

        if (!response.ok) {
          throw new Error('Analysis failed');
        }

        const result = await response.json();
        setAnalysisResult(result);
      } else {
        // Send actual file
        const formData = new FormData();
        formData.append('file', fileToAnalyze.file);
        formData.append('patient_id', patientId);

        const response = await fetch('http://localhost:5000/api/analyze', {
          method: 'POST',
          body: formData,
        });

        if (!response.ok) {
          throw new Error('Analysis failed');
        }

        const result = await response.json();
        setAnalysisResult(result);
      }
      
      // Mark all files as analyzed
      uploadedFiles.forEach(file => {
        updateFileStatus(file.id, 'success');
      });

    } catch (error) {
      console.error('Analysis error:', error);
      alert('Failed to analyze files. Please try again.');
    } finally {
      setIsAnalyzing(false);
    }
  };

  return (
    <div className="min-h-screen pt-24 pb-12 px-4">
      <div className="container mx-auto max-w-5xl">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-4xl font-bold text-white mb-2">Upload Medical Reports</h1>
          <p className="text-gray-400">
            Upload your medical reports, lab results, or imaging files for AI analysis
          </p>
        </div>

        {/* Upload Zone */}
        <div
          className={cn(
            "glass-morphism rounded-2xl p-12 border-2 border-dashed transition-all mb-8",
            isDragging
              ? "border-primary shadow-neon-strong bg-primary/10"
              : "border-white/20 hover:border-primary/50"
          )}
          onDrag={handleDrag}
          onDragEnter={handleDragIn}
          onDragLeave={handleDragOut}
          onDragOver={handleDrag}
          onDrop={handleDrop}
        >
          <div className="text-center">
            <div className="w-20 h-20 mx-auto mb-6 rounded-full bg-gradient-to-br from-primary to-secondary flex items-center justify-center">
              <Upload className="w-10 h-10 text-white" />
            </div>
            <h3 className="text-2xl font-bold text-white mb-2">Drop files here</h3>
            <p className="text-gray-400 mb-6">
              or click to browse from your computer
            </p>
            <label className="inline-block">
              <input
                type="file"
                multiple
                accept=".pdf,.jpg,.jpeg,.png,.dcm,.txt,.csv"
                onChange={handleFileInput}
                className="hidden"
              />
              <span className="px-6 py-3 bg-gradient-to-r from-primary to-secondary rounded-lg text-white font-semibold cursor-pointer hover:shadow-neon transition-all inline-block">
                Select Files
              </span>
            </label>
            <p className="text-gray-500 text-sm mt-4">
              Supported: PDF, JPEG, PNG, DICOM, TXT, CSV (Max 10MB each)
            </p>
          </div>
        </div>

        {/* Uploaded Files List */}
        {uploadedFiles.length > 0 && (
          <div className="glass-morphism rounded-2xl p-6">
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-2xl font-bold text-white">
                Uploaded Files ({uploadedFiles.length})
              </h2>
              <button 
                onClick={handleAnalyzeAll}
                disabled={isAnalyzing}
                className="px-4 py-2 bg-gradient-to-r from-primary to-secondary rounded-lg text-white text-sm hover:shadow-neon transition-all disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
              >
                {isAnalyzing && <Loader2 className="w-4 h-4 animate-spin" />}
                {isAnalyzing ? 'Analyzing...' : 'Analyze All Files'}
              </button>
            </div>

            <div className="space-y-4">
              {uploadedFiles.map((file) => (
                <div
                  key={file.id}
                  className="bg-white/5 rounded-lg p-4 flex items-center space-x-4"
                >
                  <div className="w-12 h-12 rounded-lg bg-gradient-to-br from-blue-500 to-cyan-500 flex items-center justify-center flex-shrink-0">
                    <FileText className="w-6 h-6 text-white" />
                  </div>

                  <div className="flex-1 min-w-0">
                    <div className="flex items-center justify-between mb-2">
                      <h3 className="text-white font-medium truncate">{file.name}</h3>
                      <button
                        onClick={() => removeFile(file.id)}
                        className="text-gray-400 hover:text-red-400 transition-colors ml-2"
                      >
                        <X className="w-5 h-5" />
                      </button>
                    </div>

                    <div className="flex items-center space-x-4 text-sm text-gray-400">
                      <span>{formatFileSize(file.size)}</span>
                      <span>•</span>
                      <span>{new Date(file.uploadedAt).toLocaleString()}</span>
                    </div>

                    {/* Progress Bar */}
                    {file.status === 'uploading' && (
                      <div className="mt-2">
                        <div className="flex items-center justify-between text-xs mb-1">
                          <span className="text-gray-400">Uploading...</span>
                          <span className="text-primary">{file.progress}%</span>
                        </div>
                        <div className="w-full h-1.5 bg-white/10 rounded-full overflow-hidden">
                          <div
                            className="h-full bg-gradient-to-r from-primary to-secondary transition-all duration-300"
                            style={{ width: `${file.progress}%` }}
                          />
                        </div>
                      </div>
                    )}

                    {/* Status Indicators */}
                    {file.status === 'success' && (
                      <div className="mt-2 flex items-center space-x-2 text-green-500 text-sm">
                        <CheckCircle className="w-4 h-4" />
                        <span>Upload complete</span>
                      </div>
                    )}

                    {file.status === 'error' && (
                      <div className="mt-2 flex items-center space-x-2 text-red-500 text-sm">
                        <AlertCircle className="w-4 h-4" />
                        <span>Upload failed</span>
                      </div>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Analysis Results */}
        {analysisResult && (
          <div className="glass-morphism rounded-2xl p-6 mt-8">
            <h2 className="text-2xl font-bold text-white mb-6">Analysis Results</h2>
            
            {/* Patient Brief */}
            <div className="bg-white/5 rounded-lg p-4 mb-6">
              <h3 className="text-lg font-semibold text-white mb-2">Patient Brief</h3>
              <p className="text-gray-300">{analysisResult.summary.patient_brief}</p>
            </div>

            {/* Urgency Level */}
            <div className={cn(
              "rounded-lg p-4 mb-6",
              analysisResult.summary.urgency === 'high' ? 'bg-red-500/20 border border-red-500' :
              analysisResult.summary.urgency === 'moderate-high' ? 'bg-orange-500/20 border border-orange-500' :
              'bg-green-500/20 border border-green-500'
            )}>
              <h3 className="text-lg font-semibold text-white mb-2">
                Urgency Level: {analysisResult.summary.urgency.toUpperCase()}
              </h3>
              <p className="text-gray-300">{analysisResult.summary.recommendation}</p>
              <p className="text-gray-400 text-sm mt-2">
                ESI Triage Level: {analysisResult.summary.esi_level} | 
                Primary Concern: {analysisResult.summary.primary_concern}
              </p>
            </div>

            {/* Grid Layout for Details */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
              {/* Symptoms */}
              <div className="bg-white/5 rounded-lg p-4">
                <h3 className="text-lg font-semibold text-white mb-3 flex items-center gap-2">
                  🩺 Symptoms Identified
                </h3>
                <ul className="space-y-2">
                  {analysisResult.summary.symptoms_identified.map((symptom, idx) => (
                    <li key={idx} className="text-gray-300 flex items-start gap-2">
                      <span className="text-primary">•</span>
                      {symptom}
                    </li>
                  ))}
                </ul>
              </div>

              {/* Medications */}
              <div className="bg-white/5 rounded-lg p-4">
                <h3 className="text-lg font-semibold text-white mb-3 flex items-center gap-2">
                  💊 Medication Recommendations
                </h3>
                <ul className="space-y-2">
                  {analysisResult.summary.medication_recommendations.map((med, idx) => (
                    <li key={idx} className="text-gray-300 flex items-start gap-2">
                      <span className="text-secondary">•</span>
                      {med}
                    </li>
                  ))}
                </ul>
              </div>
            </div>

            {/* Prevention Strategies */}
            <div className="bg-gradient-to-br from-primary/10 to-secondary/10 rounded-lg p-6 mb-6 border border-primary/30">
              <h3 className="text-xl font-semibold text-white mb-4 flex items-center gap-2">
                🛡️ Prevention Strategies
              </h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                {analysisResult.summary.prevention_strategies.map((strategy, idx) => (
                  <div key={idx} className="bg-white/5 rounded-lg p-3 text-gray-300">
                    {strategy}
                  </div>
                ))}
              </div>
            </div>

            {/* Risk Factors */}
            {analysisResult.summary.risk_factors.length > 0 && (
              <div className="bg-white/5 rounded-lg p-4 mb-6">
                <h3 className="text-lg font-semibold text-white mb-3 flex items-center gap-2">
                  ⚠️ Risk Factors
                </h3>
                <ul className="space-y-2">
                  {analysisResult.summary.risk_factors.map((risk, idx) => (
                    <li key={idx} className="text-gray-300 flex items-start gap-2">
                      <span className="text-orange-400">•</span>
                      {risk}
                    </li>
                  ))}
                </ul>
              </div>
            )}

            {/* Next Steps */}
            {analysisResult.summary.next_steps && analysisResult.summary.next_steps.length > 0 && (
              <div className="bg-white/5 rounded-lg p-4 mb-6">
                <h3 className="text-lg font-semibold text-white mb-3 flex items-center gap-2">
                  📋 Next Steps
                </h3>
                <ul className="space-y-2">
                  {analysisResult.summary.next_steps.map((step, idx) => (
                    <li key={idx} className="text-gray-300 flex items-start gap-2">
                      <span className="text-green-400">•</span>
                      {step}
                    </li>
                  ))}
                </ul>
              </div>
            )}

            {/* Key Findings */}
            <div className="bg-white/5 rounded-lg p-4">
              <h3 className="text-lg font-semibold text-white mb-3">📊 Key Findings</h3>
              <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
                {analysisResult.summary.key_findings.map((finding, idx) => (
                  <div key={idx} className="text-center p-3 bg-white/5 rounded-lg">
                    <p className="text-gray-300 text-sm">{finding}</p>
                  </div>
                ))}
              </div>
              <p className="text-gray-400 text-sm mt-4 text-center">
                Analyzed by {analysisResult.summary.agents_consulted} specialist AI agents
              </p>
            </div>
          </div>
        )}

        {/* Info Cards */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mt-8">
          <div className="glass-morphism rounded-2xl p-6">
            <div className="text-4xl mb-3">🔒</div>
            <h3 className="text-lg font-bold text-white mb-2">Secure & Private</h3>
            <p className="text-gray-400 text-sm">
              Your files are encrypted and never shared without consent
            </p>
          </div>

          <div className="glass-morphism rounded-2xl p-6">
            <div className="text-4xl mb-3">🤖</div>
            <h3 className="text-lg font-bold text-white mb-2">AI Analysis</h3>
            <p className="text-gray-400 text-sm">
              6 specialist agents analyze your reports automatically
            </p>
          </div>

          <div className="glass-morphism rounded-2xl p-6">
            <div className="text-4xl mb-3">⚡</div>
            <h3 className="text-lg font-bold text-white mb-2">Instant Results</h3>
            <p className="text-gray-400 text-sm">
              Get comprehensive analysis in under 30 seconds
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};
