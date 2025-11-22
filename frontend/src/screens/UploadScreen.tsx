import React, { useCallback, useState } from 'react';
import { useAppStore, type UploadedFile } from '../stores/appStore';
import { Upload, FileText, X, CheckCircle, AlertCircle, Loader2 } from 'lucide-react';
import { cn } from '../lib/utils';

export const UploadScreen: React.FC = () => {
  const { uploadedFiles, addFile, updateFileProgress, updateFileStatus, removeFile, patientId } = useAppStore();
  const [isDragging, setIsDragging] = useState(false);

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
    files.forEach((file) => {
      const uploadFile: UploadedFile = {
        id: `file_${Date.now()}_${Math.random()}`,
        name: file.name,
        size: file.size,
        type: file.type,
        uploadedAt: new Date().toISOString(),
        status: 'uploading',
        progress: 0,
      };

      addFile(uploadFile);

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
              <button className="px-4 py-2 bg-gradient-to-r from-primary to-secondary rounded-lg text-white text-sm hover:shadow-neon transition-all">
                Analyze All Files
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
