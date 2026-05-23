import React, { useState } from 'react';
import { Check, Zap } from 'lucide-react';
import { Link } from 'react-router-dom';

const plans = [
  {
    name: 'Free',
    price: '$0',
    period: 'forever',
    desc: 'Perfect for evaluating the platform or small-scale testing.',
    highlight: false,
    features: [
      '100 applications/month',
      'Basic risk scoring',
      'Standard explainability',
      'REST API access',
      'Community support',
      '7-day decision history',
    ],
    cta: 'Start Free',
    to: '/signup',
  },
  {
    name: 'Pro',
    price: '$299',
    period: 'per month',
    desc: 'For growing lending operations needing full AI capabilities.',
    highlight: true,
    badge: 'Most Popular',
    features: [
      'Unlimited applications',
      'Advanced XGBoost model',
      'Full SHAP explainability',
      'Confidence scoring',
      'Rule-based safety layer',
      'Priority API access',
      'Unlimited decision history',
      'Email + Slack support',
    ],
    cta: 'Start Pro Trial',
    to: '/signup',
  },
  {
    name: 'Enterprise',
    price: 'Custom',
    period: 'contact us',
    desc: 'For financial institutions demanding dedicated infrastructure and compliance.',
    highlight: false,
    features: [
      'Everything in Pro',
      'Dedicated model training',
      'Custom risk thresholds',
      'SSO & role-based access',
      'On-premise deployment',
      'SLA guarantee (99.9%)',
      'Regulatory audit reports',
      'Dedicated account manager',
    ],
    cta: 'Contact Sales',
    to: '/signup',
  },
];

export default function Pricing() {
  const [annual, setAnnual] = useState(false);

  return (
    <div className="pb-24 px-4">
      <div className="max-w-6xl mx-auto">
        <div className="text-center py-20 max-w-3xl mx-auto">
          <h1 className="text-5xl md:text-7xl font-black text-white mb-6 tracking-tight">
            Simple <span className="bg-gradient-to-r from-amber-300 to-amber-600 bg-clip-text text-transparent">Pricing</span>
          </h1>
          <p className="text-slate-400 text-xl font-light leading-relaxed mb-8">
            Transparent plans that scale with your lending volume. No hidden fees, no surprises.
          </p>

          {/* Annual toggle */}
          <div className="inline-flex items-center gap-3 bg-white/5 border border-white/10 rounded-xl px-4 py-2">
            <span className={`text-sm font-semibold transition-colors ${!annual ? 'text-white' : 'text-slate-500'}`}>Monthly</span>
            <button
              onClick={() => setAnnual(!annual)}
              className={`relative w-12 h-6 rounded-full transition-all duration-300 ${annual ? 'bg-amber-500' : 'bg-white/10'}`}
            >
              <span className={`absolute top-1 w-4 h-4 rounded-full bg-white shadow transition-all duration-300 ${annual ? 'left-7' : 'left-1'}`} />
            </button>
            <span className={`text-sm font-semibold transition-colors ${annual ? 'text-white' : 'text-slate-500'}`}>
              Annual <span className="text-amber-400">-20%</span>
            </span>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {plans.map(plan => (
            <div
              key={plan.name}
              className={`relative backdrop-blur-xl rounded-2xl p-8 flex flex-col gap-6 transition-all duration-300 hover:scale-[1.02] ${
                plan.highlight
                  ? 'bg-gradient-to-b from-amber-500/15 to-white/5 border-2 border-amber-500/40 shadow-2xl shadow-amber-500/15'
                  : 'bg-white/5 border border-white/10 hover:border-white/20'
              }`}
            >
              {plan.badge && (
                <div className="absolute -top-4 left-1/2 -translate-x-1/2 bg-gradient-to-r from-amber-400 to-amber-600 text-slate-950 text-xs font-black px-4 py-1.5 rounded-full uppercase tracking-widest shadow-lg shadow-amber-500/25 flex items-center gap-1">
                  <Zap className="w-3 h-3" /> {plan.badge}
                </div>
              )}

              <div>
                <h3 className="text-lg font-bold text-slate-300 uppercase tracking-widest mb-1">{plan.name}</h3>
                <div className="flex items-end gap-2 mb-2">
                  <span className="text-5xl font-black text-white">{annual && plan.price !== 'Custom' ? `$${Math.floor(parseInt(plan.price.replace('$','')) * 0.8)}` : plan.price}</span>
                  <span className="text-slate-500 text-sm pb-1">/{plan.period}</span>
                </div>
                <p className="text-slate-400 text-sm leading-relaxed">{plan.desc}</p>
              </div>

              <ul className="flex flex-col gap-3 flex-1">
                {plan.features.map(f => (
                  <li key={f} className="flex items-start gap-3 text-sm text-slate-300">
                    <Check className={`w-4 h-4 shrink-0 mt-0.5 ${plan.highlight ? 'text-amber-400' : 'text-emerald-400'}`} />
                    {f}
                  </li>
                ))}
              </ul>

              <Link
                to={plan.to}
                className={`text-center py-4 rounded-xl font-bold uppercase tracking-widest transition-all duration-300 ${
                  plan.highlight
                    ? 'bg-gradient-to-r from-amber-400 to-amber-600 text-slate-950 hover:from-amber-300 hover:to-amber-500 shadow-lg shadow-amber-500/25'
                    : 'bg-white/10 text-white border border-white/10 hover:bg-white/15'
                }`}
              >
                {plan.cta}
              </Link>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
