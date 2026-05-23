import React, { useState } from 'react';
import { Activity, LogOut } from 'lucide-react';
import { Link } from 'react-router-dom';
import LoanForm from '../components/LoanForm';
import ResultCard from '../components/ResultCard';
import api from '../services/api';
import { useAuth } from '../contexts/AuthContext';

export default function Dashboard() {
  const { user, logout } = useAuth();
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);
  const [applicationData, setApplicationData] = useState(null);

  const handleSubmit = async (formData) => {
    setLoading(true);
    setError(null);
    setResult(null);
    setApplicationData(formData); // Store application data
    try {
      // Add artificial delay to make the analysis look realistic
      await new Promise(resolve => setTimeout(resolve, 5000));
      
      const response = await api.post('/analyze-loan', formData);
      setResult(response.data);
    } catch (err) {
      setError(err.response?.data?.detail || "Failed to reach the AI Underwriting service. Please ensure the backend is running at http://localhost:8000.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="pb-24 px-4 pt-4">
      {/* Dashboard header */}
      <div className="max-w-7xl mx-auto mb-10 flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-white/10 pb-6">
        <div>
          <h1 className="text-2xl font-black text-white">AI Underwriting Dashboard</h1>
          <p className="text-slate-400 text-sm mt-1">
            Welcome back, <span className="text-amber-400 font-semibold">{user?.name}</span>
          </p>
        </div>
        <div className="flex items-center gap-3">
          <div className="flex items-center gap-2 px-4 py-1.5 rounded-full bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 text-sm font-semibold">
            <div className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse" />
            AI Engine Online
          </div>
          <button onClick={logout} className="flex items-center gap-2 text-sm font-semibold text-slate-400 hover:text-red-400 px-4 py-2 rounded-lg hover:bg-red-500/10 transition-all border border-white/10">
            <LogOut className="w-4 h-4" /> Exit
          </button>
        </div>
      </div>

      {/* Main Grid */}
      <div className="max-w-7xl mx-auto grid grid-cols-1 xl:grid-cols-12 gap-10 items-start">
        {/* Form */}
        <div className="xl:col-span-5">
          <LoanForm onSubmit={handleSubmit} isLoading={loading} />
          {error && (
            <div className="mt-6 backdrop-blur-md bg-red-950/40 border border-red-500/30 text-red-200 p-5 rounded-2xl flex gap-4 shadow-xl animate-in fade-in slide-in-from-bottom-4 duration-500">
              <div className="bg-red-500/20 p-2 rounded-lg shrink-0 h-fit">
                <Activity className="w-5 h-5 text-red-400" />
              </div>
              <div>
                <h4 className="font-bold text-red-400 mb-1">Execution Failed</h4>
                <p className="text-sm leading-relaxed text-red-200/80">{error}</p>
              </div>
            </div>
          )}
        </div>

        {/* Result */}
        <div className="xl:col-span-7">
          {result ? (
            <ResultCard result={result} applicationData={applicationData} />
          ) : (
            <div className="backdrop-blur-md bg-white/5 border border-white/10 rounded-3xl flex flex-col items-center justify-center p-16 text-center text-slate-500 min-h-[560px] shadow-2xl">
              <div className="relative mb-6">
                <div className="absolute inset-0 bg-amber-500/20 blur-xl rounded-full" />
                <div className="p-5 bg-slate-900 border border-white/10 rounded-2xl relative">
                  <Activity className="w-12 h-12 text-slate-400" />
                </div>
              </div>
              <h3 className="text-2xl font-bold text-white mb-3 tracking-tight">Awaiting Telemetry</h3>
              <p className="max-w-sm text-slate-400 leading-relaxed font-light">
                Input the applicant's financial coordinates to trigger the deep-learning analysis engine.
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
