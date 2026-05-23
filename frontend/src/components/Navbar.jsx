import React, { useState } from 'react';
import { Link, useLocation } from 'react-router-dom';
import { ShieldCheck, LogOut, Menu, X } from 'lucide-react';
import { useAuth } from '../contexts/AuthContext';

const navLinks = [
  { label: 'Home', to: '/' },
  { label: 'Services', to: '/services' },
  { label: 'How It Works', to: '/how-it-works' },
  { label: 'Benefits', to: '/benefits' },
  { label: 'Pricing', to: '/pricing' },
];

export default function Navbar() {
  const { user, logout } = useAuth();
  const location = useLocation();
  const [mobileOpen, setMobileOpen] = useState(false);

  return (
    <header className="fixed top-0 left-0 right-0 z-50 border-b border-white/10 bg-slate-950/80 backdrop-blur-xl">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-18 flex items-center justify-between py-4">

        {/* Logo */}
        <Link to="/" className="flex items-center gap-3 group">
          <div className="bg-gradient-to-br from-amber-400 to-amber-600 p-2 rounded-xl shadow-lg shadow-amber-500/20 group-hover:scale-105 transition-transform duration-300">
            <ShieldCheck className="w-5 h-5 text-slate-950" />
          </div>
          <span className="text-lg font-bold text-white tracking-tight">
            LoanRisk<span className="text-amber-400">AI</span>
          </span>
        </Link>

        {/* Desktop Nav */}
        <nav className="hidden md:flex items-center gap-1">
          {navLinks.map(link => (
            <Link
              key={link.to}
              to={link.to}
              className={`px-4 py-2 rounded-lg text-sm font-medium transition-all duration-200 ${
                location.pathname === link.to
                  ? 'text-amber-400 bg-amber-400/10'
                  : 'text-slate-400 hover:text-white hover:bg-white/5'
              }`}
            >
              {link.label}
            </Link>
          ))}
        </nav>

        {/* Auth Buttons */}
        <div className="hidden md:flex items-center gap-3">
          {user ? (
            <>
              <Link
                to="/dashboard"
                className="text-sm font-semibold text-slate-300 hover:text-white px-4 py-2 rounded-lg hover:bg-white/5 transition-all"
              >
                Dashboard
              </Link>
              <button
                onClick={logout}
                className="flex items-center gap-2 text-sm font-semibold text-slate-400 hover:text-red-400 px-4 py-2 rounded-lg hover:bg-red-500/10 transition-all"
              >
                <LogOut className="w-4 h-4" /> Logout
              </button>
            </>
          ) : (
            <>
              <Link
                to="/login"
                className="text-sm font-semibold text-slate-300 hover:text-white px-4 py-2 rounded-lg border border-white/10 hover:border-white/20 transition-all"
              >
                Login
              </Link>
              <Link
                to="/signup"
                className="text-sm font-bold bg-gradient-to-r from-amber-400 to-amber-600 text-slate-950 px-5 py-2 rounded-lg hover:from-amber-300 hover:to-amber-500 shadow-md shadow-amber-500/20 hover:scale-105 transition-all"
              >
                Get Started
              </Link>
            </>
          )}
        </div>

        {/* Mobile toggle */}
        <button className="md:hidden text-slate-400 hover:text-white" onClick={() => setMobileOpen(!mobileOpen)}>
          {mobileOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
        </button>
      </div>

      {/* Mobile menu */}
      {mobileOpen && (
        <div className="md:hidden bg-slate-900 border-t border-white/10 px-4 py-4 flex flex-col gap-2">
          {navLinks.map(link => (
            <Link key={link.to} to={link.to} onClick={() => setMobileOpen(false)}
              className="text-slate-300 hover:text-white px-3 py-2 rounded-lg hover:bg-white/5 font-medium text-sm transition-all">
              {link.label}
            </Link>
          ))}
          <hr className="border-white/10 my-2" />
          {user ? (
            <>
              <Link to="/dashboard" onClick={() => setMobileOpen(false)} className="text-amber-400 px-3 py-2 text-sm font-semibold">Dashboard</Link>
              <button onClick={() => { logout(); setMobileOpen(false); }} className="text-left text-red-400 px-3 py-2 text-sm font-semibold">Logout</button>
            </>
          ) : (
            <>
              <Link to="/login" onClick={() => setMobileOpen(false)} className="text-slate-300 px-3 py-2 text-sm font-semibold">Login</Link>
              <Link to="/signup" onClick={() => setMobileOpen(false)} className="text-amber-400 px-3 py-2 text-sm font-semibold">Get Started</Link>
            </>
          )}
        </div>
      )}
    </header>
  );
}
