import React from 'react';
import { FileText, Cpu, BarChart2, CheckSquare } from 'lucide-react';

const steps = [
  {
    number: '01',
    icon: FileText,
    title: 'Submit Loan Request',
    desc: 'The analyst inputs the applicant\'s financial profile — income, credit score, debt-to-income ratio, and employment history — into the secure API endpoint.',
    details: ['Strict Pydantic validation', 'Input range enforcement', 'Sanitized before processing'],
  },
  {
    number: '02',
    icon: Cpu,
    title: 'Data Processing',
    desc: 'The system orchestrates a comprehensive analysis pipeline, dynamically calling ML tools, fetching historical context from MongoDB, and building the decision context.',
    details: ['XGBoost inference', 'SHAP value computation', 'Historical memory retrieval'],
  },
  {
    number: '03',
    icon: BarChart2,
    title: 'Risk Evaluation',
    desc: 'A calibrated probability of default is computed, clamped to [0.05, 0.95], and then checked against a deterministic heuristic engine enforcing hard business rules.',
    details: ['Probability calibration', 'Confidence scoring', 'Rule-based safety checks'],
  },
  {
    number: '04',
    icon: CheckSquare,
    title: 'Decision Output',
    desc: 'A final Approve / Review / Reject verdict is issued with a full narrative explanation combining SHAP feature impacts and heuristic reasoning, persisted to MongoDB.',
    details: ['Decision in <500ms', 'Human-readable reasoning', 'Async MongoDB logging'],
  },
];

export default function HowItWorks() {
  return (
    <div className="pb-24 px-4">
      <div className="max-w-5xl mx-auto">
        <div className="text-center py-20">
          <h1 className="text-5xl md:text-7xl font-black text-white mb-6 tracking-tight">
            How It <span className="bg-gradient-to-r from-amber-300 to-amber-600 bg-clip-text text-transparent">Works</span>
          </h1>
          <p className="text-slate-400 text-xl font-light leading-relaxed max-w-2xl mx-auto">
            A transparent, four-step pipeline from raw financial data to explainable credit decision.
          </p>
        </div>

        {/* Timeline */}
        <div className="relative">
          {/* Vertical line */}
          <div className="absolute left-8 md:left-1/2 top-0 bottom-0 w-px bg-gradient-to-b from-amber-500/50 via-amber-500/20 to-transparent hidden sm:block" />

          <div className="flex flex-col gap-12">
            {steps.map((step, i) => {
              const Icon = step.icon;
              const isLeft = i % 2 === 0;
              return (
                <div key={step.number} className={`flex flex-col md:flex-row items-center gap-8 ${!isLeft ? 'md:flex-row-reverse' : ''}`}>
                  {/* Card */}
                  <div className="flex-1 backdrop-blur-xl bg-white/5 border border-white/10 rounded-2xl p-8 hover:border-amber-500/30 transition-all duration-300 group">
                    <div className="flex items-center gap-4 mb-4">
                      <div className="bg-gradient-to-br from-amber-400/20 to-amber-600/10 border border-amber-500/20 w-12 h-12 rounded-xl flex items-center justify-center group-hover:scale-110 transition-transform duration-300">
                        <Icon className="w-6 h-6 text-amber-400" />
                      </div>
                      <span className="text-5xl font-black text-white/10 leading-none select-none">{step.number}</span>
                    </div>
                    <h3 className="text-2xl font-bold text-white mb-3">{step.title}</h3>
                    <p className="text-slate-400 leading-relaxed mb-5">{step.desc}</p>
                    <ul className="flex flex-col gap-2">
                      {step.details.map(d => (
                        <li key={d} className="flex items-center gap-2 text-sm text-slate-400">
                          <div className="w-1.5 h-1.5 rounded-full bg-amber-400 shrink-0" />
                          {d}
                        </li>
                      ))}
                    </ul>
                  </div>

                  {/* Center dot */}
                  <div className="hidden md:flex items-center justify-center w-10 h-10 rounded-full bg-slate-950 border-2 border-amber-500 shadow-lg shadow-amber-500/25 shrink-0 z-10">
                    <div className="w-3 h-3 rounded-full bg-amber-400 animate-pulse" />
                  </div>

                  <div className="flex-1 hidden md:block" />
                </div>
              );
            })}
          </div>
        </div>
      </div>
    </div>
  );
}
