import React from 'react';
import { Zap, Eye, Users, TrendingUp, ShieldCheck, Clock } from 'lucide-react';
import { Link } from 'react-router-dom';

const benefits = [
  {
    icon: Zap,
    title: 'Faster Decisions',
    headline: '10x Faster',
    desc: 'Replace multi-day manual underwriting cycles with sub-second AI verdicts. Process thousands of applications simultaneously without adding headcount.',
    color: 'from-amber-400/20 to-amber-600/10 border-amber-500/20',
    iconColor: 'text-amber-400',
  },
  {
    icon: Eye,
    title: 'Full Transparency',
    headline: '100% Explainable',
    desc: 'Every decision comes with a narrative explanation and SHAP feature attributions. Satisfy regulators, comply with fair lending laws, and build borrower trust simultaneously.',
    color: 'from-blue-400/20 to-blue-600/10 border-blue-500/20',
    iconColor: 'text-blue-400',
  },
  {
    icon: Users,
    title: 'Reduced Manual Effort',
    headline: '80% Less Review',
    desc: 'Automate routine approvals and rejections. Your team\'s expertise focuses only on edge cases flagged for \'Review\', dramatically improving operational efficiency.',
    color: 'from-emerald-400/20 to-emerald-600/10 border-emerald-500/20',
    iconColor: 'text-emerald-400',
  },
  {
    icon: TrendingUp,
    title: 'Better Risk Management',
    headline: '40% Risk Reduction',
    desc: 'Calibrated ML probabilities combined with hard business rule safeguards catch risk patterns that human reviewers consistently miss across large application volumes.',
    color: 'from-purple-400/20 to-purple-600/10 border-purple-500/20',
    iconColor: 'text-purple-400',
  },
  {
    icon: ShieldCheck,
    title: 'Regulatory Compliance',
    headline: 'Audit Ready',
    desc: 'Persistent decision logs in MongoDB provide a complete audit trail with timestamps, risk scores, confidence levels, and full explanations for every decision ever made.',
    color: 'from-red-400/20 to-red-600/10 border-red-500/20',
    iconColor: 'text-red-400',
  },
  {
    icon: Clock,
    title: 'Always Available',
    headline: '99.8% Uptime',
    desc: 'Cloud-native FastAPI backend with async MongoDB operations ensures your lending pipeline never sleeps — processing applications 24/7 with consistent reliability.',
    color: 'from-cyan-400/20 to-cyan-600/10 border-cyan-500/20',
    iconColor: 'text-cyan-400',
  },
];

export default function Benefits() {
  return (
    <div className="pb-24 px-4">
      <div className="max-w-7xl mx-auto">
        <div className="text-center py-20 max-w-3xl mx-auto">
          <h1 className="text-5xl md:text-7xl font-black text-white mb-6 tracking-tight">
            Why Choose <span className="bg-gradient-to-r from-amber-300 to-amber-600 bg-clip-text text-transparent">Us</span>
          </h1>
          <p className="text-slate-400 text-xl font-light leading-relaxed">
            Built specifically for financial institutions that can't afford slow decisions, opaque models, or manual bottlenecks.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-16">
          {benefits.map(({ icon: Icon, title, headline, desc, color, iconColor }) => (
            <div key={title} className="backdrop-blur-xl bg-white/5 border border-white/10 rounded-2xl p-8 hover:border-white/20 hover:bg-white/8 transition-all duration-300 group flex flex-col gap-4">
              <div className={`bg-gradient-to-br ${color} border w-14 h-14 rounded-2xl flex items-center justify-center group-hover:scale-110 transition-transform duration-300`}>
                <Icon className={`w-7 h-7 ${iconColor}`} />
              </div>
              <div>
                <div className={`text-3xl font-black mb-1 ${iconColor}`}>{headline}</div>
                <h3 className="text-xl font-bold text-white mb-2">{title}</h3>
                <p className="text-slate-400 leading-relaxed text-sm">{desc}</p>
              </div>
            </div>
          ))}
        </div>

        {/* CTA */}
        <div className="text-center">
          <Link to="/signup" className="inline-flex items-center gap-2 bg-gradient-to-r from-amber-400 to-amber-600 text-slate-950 px-10 py-5 rounded-xl font-bold text-lg hover:scale-105 transition-all shadow-xl shadow-amber-500/25">
            Start Your Free Trial
          </Link>
        </div>
      </div>
    </div>
  );
}
