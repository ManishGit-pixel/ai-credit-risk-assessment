import React from 'react';
import { Brain, Eye, Zap, Database, BarChart3, Lock } from 'lucide-react';

const services = [
  {
    icon: Brain,
    title: 'AI Risk Analysis',
    desc: 'Our XGBoost ensemble model processes 4 core financial dimensions to compute a calibrated probability of default, clamped to realistic bounds and validated against historical lending data.',
    tags: ['XGBoost', 'ML Pipeline', 'Probability Calibration'],
  },
  {
    icon: Eye,
    title: 'Explainable AI (XAI)',
    desc: 'Every decision is backed by SHAP (SHapley Additive exPlanations) feature attributions, converting raw model outputs into human-readable impact assessments for full regulatory transparency.',
    tags: ['SHAP', 'Feature Attribution', 'Regulatory Compliant'],
  },
  {
    icon: Zap,
    title: 'Instant Underwriting',
    desc: 'The system follows a comprehensive analysis pipeline, orchestrating multiple ML tools in parallel to deliver authoritative loan decisions in under 500 milliseconds.',
    tags: ['ML Pipeline', 'FastAPI', 'Sub-500ms'],
  },
  {
    icon: Database,
    title: 'Decision Memory',
    desc: 'MongoDB-backed decision logs with asynchronous writes allow the system to retrieve similar historical applications as contextual signals, continuously improving accuracy over time.',
    tags: ['MongoDB', 'Motor Async', 'Historical Context'],
  },
  {
    icon: BarChart3,
    title: 'Confidence Scoring',
    desc: 'Beyond binary risk scores, the system outputs a calibrated confidence metric derived from the distance to the uncertainty boundary, helping analysts triage borderline cases.',
    tags: ['Calibration', 'Uncertainty Quantification'],
  },
  {
    icon: Lock,
    title: 'Rule-Based Safety Layer',
    desc: 'A deterministic heuristic engine validates ML outputs against hard business rules — credit score thresholds, DTI limits, and employment tenure — forming a safety net before decisions are issued.',
    tags: ['Heuristics', 'Business Rules', 'Risk Controls'],
  },
];

export default function Services() {
  return (
    <div className="pb-24 px-4">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="text-center py-20 max-w-3xl mx-auto">
          <h1 className="text-5xl md:text-7xl font-black text-white mb-6 tracking-tight">
            Our <span className="bg-gradient-to-r from-amber-300 to-amber-600 bg-clip-text text-transparent">Services</span>
          </h1>
          <p className="text-slate-400 text-xl font-light leading-relaxed">
            A modular, production-ready credit intelligence platform built for scale — from community banks to global lenders.
          </p>
        </div>

        {/* Service Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {services.map(({ icon: Icon, title, desc, tags }) => (
            <div key={title} className="backdrop-blur-xl bg-white/5 border border-white/10 rounded-2xl p-8 hover:border-amber-500/30 hover:bg-white/8 transition-all duration-300 group flex flex-col gap-5">
              <div className="bg-gradient-to-br from-amber-400/15 to-amber-600/5 border border-amber-500/20 w-14 h-14 rounded-2xl flex items-center justify-center group-hover:scale-110 transition-transform duration-300">
                <Icon className="w-7 h-7 text-amber-400" />
              </div>
              <div>
                <h3 className="text-xl font-bold text-white mb-3">{title}</h3>
                <p className="text-slate-400 leading-relaxed text-sm">{desc}</p>
              </div>
              <div className="flex flex-wrap gap-2 mt-auto pt-2 border-t border-white/5">
                {tags.map(t => (
                  <span key={t} className="text-xs font-semibold px-3 py-1 rounded-full bg-amber-500/10 border border-amber-500/20 text-amber-400">
                    {t}
                  </span>
                ))}
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
