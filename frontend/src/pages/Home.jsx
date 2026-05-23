import React from 'react';
import { Link } from 'react-router-dom';
import { Brain, Zap, ShieldCheck, TrendingUp, ArrowRight, CheckCircle } from 'lucide-react';

const features = [
  { icon: Brain, title: 'AI-Powered Analysis', desc: 'XGBoost models trained on millions of data points evaluate each application instantly.' },
  { icon: ShieldCheck, title: 'Explainable Decisions', desc: 'SHAP-driven transparency shows exactly why every loan was approved or rejected.' },
  { icon: Zap, title: 'Instant Underwriting', desc: 'Sub-second decisions replace days of manual review and paperwork.' },
  { icon: TrendingUp, title: 'Better Risk Management', desc: 'Calibrated confidence scores and rule-based heuristics minimize portfolio risk.' },
];

const stats = [
  { value: '99.8%', label: 'Uptime SLA' },
  { value: '<500ms', label: 'Avg Decision Time' },
  { value: '40%', label: 'Risk Reduction' },
  { value: '10x', label: 'Faster Processing' },
];

export default function Home() {
  return (
    <div className="pb-24">
      {/* Hero */}
      <section className="relative pt-20 pb-28 px-4 text-center max-w-5xl mx-auto">
        <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-amber-500/10 border border-amber-500/20 text-amber-400 text-sm font-semibold mb-8 tracking-wide">
          <div className="w-2 h-2 rounded-full bg-amber-400 animate-pulse" />
          XGBoost + SHAP Explainability
        </div>
        <h1 className="text-6xl md:text-8xl font-black tracking-tight mb-6 leading-none">
          <span className="text-white">Smarter Capital.</span>
          <br />
          <span className="bg-gradient-to-r from-amber-200 via-amber-400 to-amber-600 bg-clip-text text-transparent">
            Instant Decisions.
          </span>
        </h1>
        <p className="text-slate-400 text-xl md:text-2xl leading-relaxed max-w-3xl mx-auto font-light mb-12">
          Advanced AI underwriting system that transforms raw financial data into precise, explainable loan decisions — in milliseconds.
        </p>
        <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
          <Link
            to="/signup"
            className="inline-flex items-center gap-2 bg-gradient-to-r from-amber-400 to-amber-600 text-slate-950 px-8 py-4 rounded-xl font-bold text-lg shadow-xl shadow-amber-500/25 hover:from-amber-300 hover:to-amber-500 hover:scale-105 transition-all duration-300"
          >
            Get Started Free <ArrowRight className="w-5 h-5" />
          </Link>
          <Link
            to="/how-it-works"
            className="inline-flex items-center gap-2 text-slate-300 border border-white/10 px-8 py-4 rounded-xl font-semibold text-lg hover:border-white/20 hover:bg-white/5 transition-all duration-300"
          >
            See How It Works
          </Link>
        </div>
      </section>

      {/* Stats band */}
      <section className="border-y border-white/10 bg-white/2 backdrop-blur-sm py-12 px-4 mb-24">
        <div className="max-w-5xl mx-auto grid grid-cols-2 md:grid-cols-4 gap-8 text-center">
          {stats.map(s => (
            <div key={s.label}>
              <div className="text-4xl font-black text-amber-400 mb-1">{s.value}</div>
              <div className="text-slate-400 text-sm font-medium">{s.label}</div>
            </div>
          ))}
        </div>
      </section>

      {/* Features */}
      <section className="max-w-7xl mx-auto px-4 mb-24">
        <div className="text-center mb-16">
          <h2 className="text-4xl font-black text-white mb-4">Everything You Need to Lend Smarter</h2>
          <p className="text-slate-400 text-lg max-w-2xl mx-auto font-light">Built for modern financial institutions demanding speed, compliance, and total transparency.</p>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {features.map(({ icon: Icon, title, desc }) => (
            <div key={title} className="backdrop-blur-xl bg-white/5 border border-white/10 rounded-2xl p-8 hover:border-amber-500/30 hover:bg-white/8 transition-all duration-300 group">
              <div className="bg-gradient-to-br from-amber-400/20 to-amber-600/10 border border-amber-500/20 w-12 h-12 rounded-xl flex items-center justify-center mb-5 group-hover:scale-110 transition-transform duration-300">
                <Icon className="w-6 h-6 text-amber-400" />
              </div>
              <h3 className="text-xl font-bold text-white mb-2">{title}</h3>
              <p className="text-slate-400 leading-relaxed">{desc}</p>
            </div>
          ))}
        </div>
      </section>

      {/* CTA banner */}
      <section className="max-w-5xl mx-auto px-4">
        <div className="backdrop-blur-xl bg-gradient-to-r from-amber-500/10 to-amber-700/5 border border-amber-500/20 rounded-3xl p-12 text-center relative overflow-hidden">
          <div className="absolute top-0 left-0 w-full h-1 bg-gradient-to-r from-transparent via-amber-400 to-transparent opacity-50" />
          <h2 className="text-4xl font-black text-white mb-4">Ready to Transform Your Lending Pipeline?</h2>
          <p className="text-slate-400 text-lg mb-8 font-light">Join financial institutions already processing thousands of applications daily.</p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Link to="/signup" className="inline-flex items-center gap-2 bg-gradient-to-r from-amber-400 to-amber-600 text-slate-950 px-8 py-4 rounded-xl font-bold text-lg hover:scale-105 transition-all shadow-lg shadow-amber-500/25">
              Start Free Trial <ArrowRight className="w-5 h-5" />
            </Link>
            <Link to="/pricing" className="inline-flex items-center gap-2 text-slate-300 border border-white/10 px-8 py-4 rounded-xl font-semibold text-lg hover:bg-white/5 transition-all">
              View Pricing
            </Link>
          </div>
        </div>
      </section>
    </div>
  );
}
