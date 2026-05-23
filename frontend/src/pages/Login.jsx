import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { ShieldCheck, Eye, EyeOff } from 'lucide-react';
import { useAuth } from '../contexts/AuthContext';

export default function Login() {
  const { login } = useAuth();
  const navigate = useNavigate();
  const [formData, setFormData] = useState({ email: '', password: '' });
  const [showPw, setShowPw] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = (e) => {
    e.preventDefault();
    // Mock auth — any email/password works
    if (formData.email && formData.password.length >= 6) {
      login(formData.email);
      navigate('/dashboard');
    } else {
      setError('Please enter a valid email and a password of at least 6 characters.');
    }
  };

  return (
    <div className="min-h-[calc(100vh-5rem)] flex items-center justify-center px-4 py-16">
      <div className="w-full max-w-md">
        {/* Logo */}
        <div className="flex flex-col items-center mb-8">
          <div className="bg-gradient-to-br from-amber-400 to-amber-600 p-3 rounded-2xl shadow-xl shadow-amber-500/25 mb-4">
            <ShieldCheck className="w-8 h-8 text-slate-950" />
          </div>
          <h1 className="text-3xl font-black text-white">Welcome back</h1>
          <p className="text-slate-400 mt-2 text-center">Sign in to access the AI underwriting dashboard</p>
        </div>

        <form onSubmit={handleSubmit} className="backdrop-blur-xl bg-white/5 border border-white/10 rounded-2xl p-8 flex flex-col gap-5 shadow-2xl">
          {error && (
            <div className="bg-red-950/50 border border-red-500/30 text-red-300 text-sm p-4 rounded-xl">
              {error}
            </div>
          )}

          <div>
            <label className="block text-xs font-bold uppercase tracking-widest text-slate-400 mb-2">Email Address</label>
            <input
              type="email" required
              value={formData.email}
              onChange={e => setFormData(p => ({ ...p, email: e.target.value }))}
              placeholder="analyst@bank.com"
              className="w-full bg-slate-900/60 border border-white/10 rounded-xl p-4 text-white placeholder-slate-600 focus:ring-2 focus:ring-amber-500/50 focus:border-amber-500 outline-none transition-all"
            />
          </div>

          <div>
            <label className="block text-xs font-bold uppercase tracking-widest text-slate-400 mb-2">Password</label>
            <div className="relative">
              <input
                type={showPw ? 'text' : 'password'} required
                value={formData.password}
                onChange={e => setFormData(p => ({ ...p, password: e.target.value }))}
                placeholder="••••••••••••"
                className="w-full bg-slate-900/60 border border-white/10 rounded-xl p-4 text-white placeholder-slate-600 focus:ring-2 focus:ring-amber-500/50 focus:border-amber-500 outline-none transition-all pr-12"
              />
              <button type="button" onClick={() => setShowPw(!showPw)} className="absolute right-4 top-1/2 -translate-y-1/2 text-slate-500 hover:text-slate-300 transition-colors">
                {showPw ? <EyeOff className="w-5 h-5" /> : <Eye className="w-5 h-5" />}
              </button>
            </div>
          </div>

          <button type="submit" className="mt-2 bg-gradient-to-r from-amber-400 to-amber-600 text-slate-950 font-bold py-4 rounded-xl hover:from-amber-300 hover:to-amber-500 hover:scale-[1.02] transition-all shadow-lg shadow-amber-500/25 uppercase tracking-widest">
            Sign In
          </button>

          <p className="text-center text-slate-500 text-sm">
            Don't have an account?{' '}
            <Link to="/signup" className="text-amber-400 hover:text-amber-300 font-semibold transition-colors">Create one free</Link>
          </p>
        </form>
      </div>
    </div>
  );
}
