import React, { useState } from 'react';
import { Zap, RefreshCcw, Upload, AlertTriangle, ShieldCheck, ShieldAlert, CheckCircle2 } from 'lucide-react';
import { verifyKYC } from '../services/api';

export default function LoanForm({ onSubmit, isLoading }) {
  const [formData, setFormData] = useState({
    cifNumber: '',
    income: '',
    credit_score: '',
    employment_length: '',
    existing_loans: '',
    total_debt: '',
    credit_card_usage: '',
    loan_amount_requested: '',
    loan_tenure: '',
    currency: 'USD'
  });

  const [kycData, setKycData] = useState({
    aadhaar_number: '',
    pan_number: ''
  });

  const [isKYCVerified, setIsKYCVerified] = useState(false);
  const [kycLoading, setKycLoading] = useState(false);
  const [kycError, setKycError] = useState(null);
  const [kycSuccess, setKycSuccess] = useState(null);

  const [payslipFile, setPayslipFile] = useState(null);
  const [fraudAlert, setFraudAlert] = useState(null);
  const [verifying, setVerifying] = useState(false);
  const [payslipVerificationData, setPayslipVerificationData] = useState(null);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleKycChange = (e) => {
    const { name, value } = e.target;
    setKycData(prev => ({
      ...prev,
      [name]: value.toUpperCase()
    }));
    // Reset success/error when user types
    setKycError(null);
    setKycSuccess(null);
  };

  // Sync KYC if cifNumber is entered after verification
  React.useEffect(() => {
    if (isKYCVerified && formData.cifNumber && !kycLoading) {
      const syncKYC = async () => {
        try {
          await verifyKYC({
            user_id: formData.cifNumber,
            aadhaar_number: kycData.aadhaar_number || null,
            pan_number: kycData.pan_number || null
          });
          console.log("KYC synced with CIF Number");
        } catch (err) {
          console.error("Late KYC sync failed", err);
        }
      };
      syncKYC();
    }
  }, [formData.cifNumber, isKYCVerified]);

  const handleVerifyKYC = async () => {
    if (!kycData.aadhaar_number && !kycData.pan_number) {
      setKycError("Please enter Aadhaar or PAN.");
      return;
    }

    setKycLoading(true);
    setKycError(null);
    try {
      const result = await verifyKYC({
        user_id: formData.cifNumber || null,
        aadhaar_number: kycData.aadhaar_number || null,
        pan_number: kycData.pan_number || null
      });

      if (result.kyc_status === "Verified") {
        setIsKYCVerified(true);
        setKycSuccess(result.message);
      } else {
        setIsKYCVerified(false);
        setKycError(result.message);
      }
    } catch (err) {
      setKycError("KYC service unavailable. Please check backend.");
    } finally {
      setKycLoading(false);
    }
  };

  const handleFileChange = (e) => {
    const file = e.target.files[0];
    if (file && file.type === 'application/pdf') {
      setPayslipFile(file);
      setFraudAlert(null);
    } else if (file) {
      alert('Please upload a PDF file');
      e.target.value = '';
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setFraudAlert(null);

    if (!isKYCVerified) {
      setKycError("You must verify your KYC before proceeding.");
      return;
    }

    // Step 1: Check if payslip is uploaded (mandatory)
    if (!payslipFile) {
      setFraudAlert('Payslip PDF is required. Please upload your payslip document.');
      return;
    }

    // Step 2: Verify income with payslip
    setVerifying(true);
    try {
      const formDataPayslip = new FormData();
      formDataPayslip.append('claimed_income', formData.income);
      formDataPayslip.append('document', payslipFile);

      const verifyResponse = await fetch('http://localhost:8000/verify-income', {
        method: 'POST',
        body: formDataPayslip
      });

      const verifyResult = await verifyResponse.json();

      if (verifyResult.fraud_flag) {
        setFraudAlert(verifyResult.message);
        setVerifying(false);
        return; // Stop submission
      }

      // Store verification data for later use in report
      setPayslipVerificationData(verifyResult.verification_data);

    } catch (error) {
      console.error('Income verification failed:', error);
      setFraudAlert('Failed to verify income document. Please try again.');
      setVerifying(false);
      return;
    }
    setVerifying(false);

    // Step 3: Proceed with normal loan analysis
    const submissionData = {
      user_id: formData.cifNumber,
      income: Number(formData.income),
      credit_score: parseInt(formData.credit_score, 10),
      employment_length: parseInt(formData.employment_length, 10),
      existing_loans: Number(formData.existing_loans),
      total_debt: Number(formData.total_debt),
      credit_card_usage: Number(formData.credit_card_usage),
      loan_amount_requested: Number(formData.loan_amount_requested),
      loan_tenure: formData.loan_tenure ? parseInt(formData.loan_tenure, 10) : null,
      currency: formData.currency,
      payslip_verification: payslipVerificationData
    };

    onSubmit(submissionData);
  };

  const handleReset = () => {
    setFormData({
      cifNumber: '',
      income: '',
      credit_score: '',
      employment_length: '',
      existing_loans: '',
      total_debt: '',
      credit_card_usage: '',
      loan_amount_requested: '',
      loan_tenure: '',
      currency: 'USD'
    });
    setKycData({
      aadhaar_number: '',
      pan_number: ''
    });
    setIsKYCVerified(false);
    setPayslipFile(null);
    setFraudAlert(null);
    setKycError(null);
    setKycSuccess(null);
    setPayslipVerificationData(null);
  };

  return (
    <div className="flex flex-col gap-6">
      {/* KYC Section */}
      <div className="backdrop-blur-xl bg-slate-900/40 border border-amber-500/20 rounded-3xl p-8 flex flex-col gap-5 shadow-xl">
        <div className="flex items-center gap-3 border-b border-white/5 pb-4">
          <ShieldCheck className="w-6 h-6 text-amber-500" />
          <h2 className="text-xl font-bold text-white tracking-wide">Identity Verification (KYC)</h2>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
          <div>
            <label className="block text-xs font-semibold tracking-wider text-slate-400 mb-2 uppercase">Aadhaar Number (12 Digits)</label>
            <input 
              name="aadhaar_number"
              type="text" 
              maxLength="12"
              disabled={isKYCVerified}
              value={kycData.aadhaar_number}
              onChange={handleKycChange}
              className="w-full bg-slate-950/60 border border-white/10 rounded-xl p-4 text-white placeholder-slate-700 focus:ring-1 focus:ring-amber-500/50 outline-none transition-all disabled:opacity-50"
              placeholder="0000 0000 0000" 
            />
          </div>
          <div>
            <label className="block text-xs font-semibold tracking-wider text-slate-400 mb-2 uppercase">PAN Card (10 Chars)</label>
            <input 
              name="pan_number"
              type="text" 
              maxLength="10"
              disabled={isKYCVerified}
              value={kycData.pan_number}
              onChange={handleKycChange}
              className="w-full bg-slate-950/60 border border-white/10 rounded-xl p-4 text-white placeholder-slate-700 focus:ring-1 focus:ring-amber-500/50 outline-none transition-all disabled:opacity-50"
              placeholder="ABCDE1234F" 
            />
          </div>
        </div>

        {kycError && (
          <div className="bg-red-500/10 border border-red-500/30 rounded-xl p-3 flex items-center gap-3 text-red-400 text-sm">
            <ShieldAlert className="w-4 h-4" />
            {kycError}
          </div>
        )}

        {kycSuccess && (
          <div className="bg-emerald-500/10 border border-emerald-500/30 rounded-xl p-3 flex items-center gap-3 text-emerald-400 text-sm">
            <CheckCircle2 className="w-4 h-4" />
            {kycSuccess}
          </div>
        )}

        {!isKYCVerified ? (
          <button 
            type="button"
            onClick={handleVerifyKYC}
            disabled={kycLoading}
            className="bg-amber-500/10 border border-amber-500/50 hover:bg-amber-500/20 text-amber-500 font-bold py-3 rounded-xl transition-all flex justify-center items-center gap-2 disabled:opacity-50"
          >
            {kycLoading ? "Processing Identity..." : "Verify Identity"}
          </button>
        ) : (
          <div className="flex items-center justify-center gap-2 py-3 bg-emerald-500/10 border border-emerald-500/30 rounded-xl text-emerald-400 font-bold border-dashed">
            <ShieldCheck className="w-5 h-5" />
            IDENTITY VERIFIED
          </div>
        )}
      </div>

      {/* Main Form */}
      <form onSubmit={handleSubmit} className={`backdrop-blur-xl bg-white/5 border border-white/10 rounded-3xl shadow-2xl p-8 flex flex-col gap-6 transition-all duration-500 ${!isKYCVerified ? 'opacity-40 grayscale pointer-events-none' : 'hover:border-white/20'}`}>
        
        <div className="flex justify-between items-center border-b border-white/10 pb-5">
          <h2 className="text-xl font-bold text-white tracking-wide">Applicant Matrix</h2>
          <button 
            type="button" 
            onClick={handleReset} 
            className="text-xs font-semibold uppercase tracking-wider bg-white/5 border border-white/10 text-slate-300 hover:text-white px-4 py-2 rounded-lg transition-all hover:bg-white/10 flex items-center gap-2"
          >
            <RefreshCcw className="w-3.5 h-3.5" />
            Reset
          </button>
        </div>
        
        <div className="space-y-5">
          {fraudAlert && (
            <div className="bg-red-500/10 border-2 border-red-500 rounded-xl p-4 flex items-start gap-3 animate-pulse">
              <AlertTriangle className="w-6 h-6 text-red-500 flex-shrink-0 mt-0.5" />
              <div>
                <h3 className="text-red-500 font-bold text-sm uppercase tracking-wider mb-1">Fraud Alert</h3>
                <p className="text-red-300 text-sm">{fraudAlert}</p>
              </div>
            </div>
          )}

          <div>
            <label className="block text-xs font-semibold tracking-wider text-slate-400 mb-2 uppercase">CIF NUMBER (CUSTOMER ID)</label>
            <input 
              required 
              name="cifNumber"
              type="text" 
              value={formData.cifNumber}
              onChange={handleChange}
              className="w-full bg-slate-900/60 border border-white/10 rounded-xl p-4 text-white placeholder-slate-600 focus:bg-slate-900 focus:ring-2 focus:ring-amber-500/50 focus:border-amber-500 outline-none transition-all duration-300 shadow-inner"
              placeholder="e.g. 85930291044" 
            />
          </div>

          <div className="grid grid-cols-2 gap-5">
            <div>
              <label className="block text-xs font-semibold tracking-wider text-slate-400 mb-2 uppercase">Currency</label>
              <select 
                required 
                name="currency"
                value={formData.currency}
                onChange={handleChange}
                className="w-full bg-slate-900/60 border border-white/10 rounded-xl p-4 text-white focus:bg-slate-900 focus:ring-2 focus:ring-amber-500/50 focus:border-amber-500 outline-none transition-all duration-300 shadow-inner"
              >
                <option value="USD">USD ($)</option>
                <option value="INR">INR (₹)</option>
              </select>
            </div>

            <div>
              <label className="block text-xs font-semibold tracking-wider text-slate-400 mb-2 uppercase">
                Annual Income ({formData.currency === 'USD' ? '$' : '₹'})
              </label>
              <input 
                required 
                name="income"
                type="number" 
                min="1000"
                value={formData.income}
                onChange={handleChange}
                className="w-full bg-slate-900/60 border border-white/10 rounded-xl p-4 text-white placeholder-slate-600 focus:bg-slate-900 focus:ring-2 focus:ring-amber-500/50 focus:border-amber-500 outline-none transition-all duration-300 shadow-inner"
                placeholder={formData.currency === 'USD' ? '120000' : '10000000'} 
              />
            </div>
            
            <div>
              <label className="block text-xs font-semibold tracking-wider text-slate-400 mb-2 uppercase">Credit Velocity (Score)</label>
              <input 
                required 
                name="credit_score"
                type="number" 
                min="300" max="900"
                value={formData.credit_score}
                onChange={handleChange}
                className="w-full bg-slate-900/60 border border-white/10 rounded-xl p-4 text-white placeholder-slate-600 focus:bg-slate-900 focus:ring-2 focus:ring-amber-500/50 focus:border-amber-500 outline-none transition-all duration-300 shadow-inner"
                placeholder="760" 
              />
            </div>
            
            <div>
              <label className="block text-xs font-semibold tracking-wider text-slate-400 mb-2 uppercase">Employment Length (Yrs)</label>
              <input 
                required 
                name="employment_length"
                type="number" 
                min="0"
                max="50"
                value={formData.employment_length}
                onChange={handleChange}
                className="w-full bg-slate-900/60 border border-white/10 rounded-xl p-4 text-white placeholder-slate-600 focus:bg-slate-900 focus:ring-2 focus:ring-amber-500/50 focus:border-amber-500 outline-none transition-all duration-300 shadow-inner"
                placeholder="5" 
              />
            </div>

            <div>
              <label className="block text-xs font-semibold tracking-wider text-slate-400 mb-2 uppercase">Requested Amount</label>
              <input 
                required 
                name="loan_amount_requested"
                type="number" 
                min="1"
                value={formData.loan_amount_requested}
                onChange={handleChange}
                className="w-full bg-slate-900/60 border border-white/10 rounded-xl p-4 text-white placeholder-slate-600 focus:bg-slate-900 focus:ring-2 focus:ring-amber-500/50 focus:border-amber-500 outline-none transition-all duration-300 shadow-inner"
                placeholder="25000" 
              />
            </div>

            <div>
              <label className="block text-xs font-semibold tracking-wider text-slate-400 mb-2 uppercase">Total Debt (Liabilities)</label>
              <input 
                required 
                name="total_debt"
                type="number" 
                min="0"
                value={formData.total_debt}
                onChange={handleChange}
                className="w-full bg-slate-900/60 border border-white/10 rounded-xl p-4 text-white placeholder-slate-600 focus:bg-slate-900 focus:ring-2 focus:ring-amber-500/50 focus:border-amber-500 outline-none transition-all duration-300 shadow-inner"
                placeholder="15000" 
              />
            </div>

            <div>
              <label className="block text-xs font-semibold tracking-wider text-slate-400 mb-2 uppercase">Monthly CC Usage</label>
              <input 
                required 
                name="credit_card_usage"
                type="number" 
                min="0"
                value={formData.credit_card_usage}
                onChange={handleChange}
                className="w-full bg-slate-900/60 border border-white/10 rounded-xl p-4 text-white placeholder-slate-600 focus:bg-slate-900 focus:ring-2 focus:ring-amber-500/50 focus:border-amber-500 outline-none transition-all duration-300 shadow-inner"
                placeholder="1200" 
              />
            </div>

            <div>
              <label className="block text-xs font-semibold tracking-wider text-slate-400 mb-2 uppercase">Existing Loans (Total)</label>
              <input 
                required 
                name="existing_loans"
                type="number" 
                min="0"
                value={formData.existing_loans}
                onChange={handleChange}
                className="w-full bg-slate-900/60 border border-white/10 rounded-xl p-4 text-white placeholder-slate-600 focus:bg-slate-900 focus:ring-2 focus:ring-amber-500/50 focus:border-amber-500 outline-none transition-all duration-300 shadow-inner"
                placeholder="5000" 
              />
            </div>
          </div>

          <div>
            <label className="block text-xs font-semibold tracking-wider text-slate-400 mb-2 uppercase">
              Income Verification (Payslip PDF) <span className="text-red-500">*</span>
            </label>
            <div className="relative">
              <input 
                type="file"
                accept=".pdf"
                onChange={handleFileChange}
                className="hidden"
                id="payslip-upload"
                required
              />
              <label 
                htmlFor="payslip-upload"
                className="w-full bg-slate-900/60 border border-white/10 rounded-xl p-4 text-slate-400 hover:text-white hover:border-amber-500/50 cursor-pointer flex items-center gap-3 transition-all duration-300 shadow-inner hover:bg-slate-900"
              >
                <Upload className="w-5 h-5" />
                <span className="flex-1">
                  {payslipFile ? payslipFile.name : 'Upload Payslip Document'}
                </span>
                {payslipFile && (
                  <CheckCircle2 className="w-5 h-5 text-emerald-500" />
                )}
              </label>
            </div>
          </div>
        </div>
        
        <button 
          type="submit" 
          disabled={isLoading || verifying || !isKYCVerified}
          className="mt-6 bg-gradient-to-r from-amber-400 to-amber-600 hover:from-amber-300 hover:to-amber-500 text-slate-950 font-bold text-lg py-4 rounded-xl flex justify-center items-center shadow-lg shadow-amber-500/25 transition-all duration-300 disabled:opacity-50 disabled:grayscale hover:scale-[1.02] disabled:hover:scale-100 uppercase tracking-widest disabled:cursor-not-allowed"
        >
          {verifying ? (
            <span className="flex items-center gap-3">
              <svg className="animate-spin h-5 w-5 text-slate-950" fill="none" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8H4z"></path>
              </svg>
              Verifying Income...
            </span>
          ) : isLoading ? (
            <span className="flex items-center gap-3">
              <svg className="animate-spin h-5 w-5 text-slate-950" fill="none" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8H4z"></path>
              </svg>
              Analyzing Risk Profile...
            </span>
          ) : (
            <span className="flex items-center gap-2">
              <Zap className="w-5 h-5" />
              Analyze Loan
            </span>
          )}
        </button>
      </form>
    </div>
  );
}
