import React, { useState, useRef } from 'react';
import { Upload, FileText, CheckCircle, AlertCircle, X } from 'lucide-react';
import api from '../services/api';

export default function KYCUpload({ userId, expectedName, expectedDob, onVerified, onError }) {
  const [file, setFile] = useState(null);
  const [preview, setPreview] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [status, setStatus] = useState('idle'); // idle, uploading, success, error
  const [verificationResult, setVerificationResult] = useState(null);
  const fileInputRef = useRef(null);

  const handleFileSelect = (e) => {
    const selectedFile = e.target.files[0];
    
    if (!selectedFile) return;
    
    // Validate file type
    if (!selectedFile.type.startsWith('image/')) {
      alert('Please select an image file');
      return;
    }
    
    // Validate file size (5MB)
    if (selectedFile.size > 5 * 1024 * 1024) {
      alert('File size must be less than 5MB');
      return;
    }
    
    setFile(selectedFile);
    
    // Create preview
    const reader = new FileReader();
    reader.onloadend = () => {
      setPreview(reader.result);
    };
    reader.readAsDataURL(selectedFile);
    
    setStatus('idle');
    setVerificationResult(null);
  };

  const handleUpload = async () => {
    if (!file) return;
    
    try {
      setUploading(true);
      setStatus('uploading');
      
      const formData = new FormData();
      formData.append('file', file);
      formData.append('user_id', userId);
      if (expectedName) formData.append('expected_name', expectedName);
      if (expectedDob) formData.append('expected_dob', expectedDob);
      
      const response = await api.post('/kyc/upload-document', formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      });
      
      setStatus('success');
      setVerificationResult(response.data.verification);
      
      if (onVerified) {
        onVerified(response.data);
      }
    } catch (error) {
      console.error('Error uploading document:', error);
      setStatus('error');
      if (onError) {
        onError(error);
      }
    } finally {
      setUploading(false);
    }
  };

  const handleClear = () => {
    setFile(null);
    setPreview(null);
    setStatus('idle');
    setVerificationResult(null);
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  return (
    <div className="backdrop-blur-xl bg-white/5 border border-white/10 rounded-3xl p-6 space-y-4">
      <div className="flex items-center justify-between border-b border-white/10 pb-4">
        <h3 className="text-lg font-bold text-white">Identity Verification</h3>
        {status === 'success' && (
          <span className="flex items-center gap-2 text-emerald-400 text-sm font-semibold">
            <CheckCircle className="w-4 h-4" />
            Verified
          </span>
        )}
      </div>

      {!preview ? (
        <div
          onClick={() => fileInputRef.current?.click()}
          className="border-2 border-dashed border-white/20 rounded-2xl p-12 text-center cursor-pointer hover:border-amber-500/50 hover:bg-white/5 transition-all"
        >
          <Upload className="w-12 h-12 text-slate-400 mx-auto mb-4" />
          <p className="text-white font-semibold mb-2">Upload ID Document</p>
          <p className="text-slate-400 text-sm">
            Click to upload or drag and drop
          </p>
          <p className="text-slate-500 text-xs mt-2">
            PNG, JPG up to 5MB
          </p>
          <input
            ref={fileInputRef}
            type="file"
            accept="image/*"
            onChange={handleFileSelect}
            className="hidden"
          />
        </div>
      ) : (
        <div className="space-y-4">
          <div className="relative rounded-2xl overflow-hidden border border-white/10">
            <img
              src={preview}
              alt="ID Preview"
              className="w-full h-64 object-contain bg-slate-900"
            />
            <button
              onClick={handleClear}
              className="absolute top-2 right-2 p-2 bg-red-500/80 hover:bg-red-500 rounded-lg transition-colors"
            >
              <X className="w-4 h-4 text-white" />
            </button>
          </div>

          <div className="flex items-center gap-3 text-sm text-slate-300">
            <FileText className="w-4 h-4" />
            <span className="truncate">{file?.name}</span>
            <span className="text-slate-500">
              ({(file?.size / 1024).toFixed(1)} KB)
            </span>
          </div>

          {status === 'idle' && (
            <button
              onClick={handleUpload}
              disabled={uploading}
              className="w-full bg-gradient-to-r from-amber-500 to-amber-600 hover:from-amber-400 hover:to-amber-500 text-slate-950 font-bold py-3 rounded-xl transition-all duration-300 hover:scale-105 uppercase tracking-wider text-sm"
            >
              Verify Document
            </button>
          )}

          {status === 'uploading' && (
            <div className="flex items-center justify-center gap-3 py-3 text-blue-400">
              <svg className="animate-spin h-5 w-5" fill="none" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8H4z"></path>
              </svg>
              <span className="font-semibold">Verifying document...</span>
            </div>
          )}

          {status === 'success' && verificationResult && (
            <div className="bg-emerald-500/10 border border-emerald-500/30 rounded-xl p-4 space-y-2">
              <div className="flex items-center gap-2 text-emerald-400 font-bold">
                <CheckCircle className="w-5 h-5" />
                Document Verified
              </div>
              {verificationResult.extracted_name && (
                <p className="text-sm text-slate-300">
                  <span className="text-slate-500">Name:</span> {verificationResult.extracted_name}
                </p>
              )}
              {verificationResult.extracted_dob && (
                <p className="text-sm text-slate-300">
                  <span className="text-slate-500">DOB:</span> {verificationResult.extracted_dob}
                </p>
              )}
              <p className="text-xs text-emerald-400">
                Confidence: {(verificationResult.confidence * 100).toFixed(0)}%
              </p>
            </div>
          )}

          {status === 'error' && (
            <div className="bg-red-500/10 border border-red-500/30 rounded-xl p-4">
              <div className="flex items-center gap-2 text-red-400 font-bold mb-2">
                <AlertCircle className="w-5 h-5" />
                Verification Failed
              </div>
              <p className="text-sm text-red-300">
                Please try again with a clearer image
              </p>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
