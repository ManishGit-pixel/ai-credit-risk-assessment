import React, { useState, useCallback } from 'react';
import { usePlaidLink } from 'react-plaid-link';
import { Building2, CheckCircle, AlertCircle } from 'lucide-react';
import api from '../services/api';

export default function PlaidLinkButton({ userId, onSuccess, onError }) {
  const [linkToken, setLinkToken] = useState(null);
  const [loading, setLoading] = useState(false);
  const [status, setStatus] = useState('idle'); // idle, loading, success, error

  // Initialize Plaid Link
  const { open, ready } = usePlaidLink({
    token: linkToken,
    onSuccess: async (public_token, metadata) => {
      try {
        setLoading(true);
        setStatus('loading');
        
        // Exchange public token for access token
        const exchangeResponse = await api.post('/plaid/exchange-token', {
          public_token
        });
        
        const { access_token } = exchangeResponse.data;
        
        // Get account balances
        const balanceResponse = await api.post('/plaid/get-balances', {
          access_token
        });
        
        // Get income data
        const incomeResponse = await api.post('/plaid/get-income', {
          access_token
        });
        
        setStatus('success');
        
        if (onSuccess) {
          onSuccess({
            access_token,
            balances: balanceResponse.data,
            income: incomeResponse.data,
            metadata
          });
        }
      } catch (error) {
        console.error('Error processing Plaid data:', error);
        setStatus('error');
        if (onError) {
          onError(error);
        }
      } finally {
        setLoading(false);
      }
    },
    onExit: (err, metadata) => {
      if (err) {
        console.error('Plaid Link error:', err);
        setStatus('error');
        if (onError) {
          onError(err);
        }
      }
    },
  });

  // Create link token and open Plaid Link
  const handleClick = async () => {
    try {
      setLoading(true);
      setStatus('loading');
      
      const response = await api.post('/plaid/create-link-token', {
        user_id: userId,
        user_name: userId
      });
      
      setLinkToken(response.data.link_token);
      
      // Wait a moment for the link token to be set
      setTimeout(() => {
        if (response.data.link_token) {
          open();
        }
      }, 100);
    } catch (error) {
      console.error('Error creating link token:', error);
      setStatus('error');
      if (onError) {
        onError(error);
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-3">
      <button
        onClick={handleClick}
        disabled={loading || status === 'success'}
        className={`w-full flex items-center justify-center gap-3 px-6 py-4 rounded-xl font-bold text-sm uppercase tracking-wider transition-all duration-300 ${
          status === 'success'
            ? 'bg-emerald-500/20 border-2 border-emerald-500/50 text-emerald-400 cursor-not-allowed'
            : status === 'error'
            ? 'bg-red-500/20 border-2 border-red-500/50 text-red-400 hover:bg-red-500/30'
            : 'bg-gradient-to-r from-blue-500 to-blue-600 hover:from-blue-400 hover:to-blue-500 text-white shadow-lg shadow-blue-500/25 hover:scale-105'
        } disabled:opacity-50 disabled:cursor-not-allowed disabled:hover:scale-100`}
      >
        {status === 'success' ? (
          <>
            <CheckCircle className="w-5 h-5" />
            Bank Connected
          </>
        ) : status === 'error' ? (
          <>
            <AlertCircle className="w-5 h-5" />
            Try Again
          </>
        ) : loading ? (
          <>
            <svg className="animate-spin h-5 w-5" fill="none" viewBox="0 0 24 24">
              <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
              <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8H4z"></path>
            </svg>
            Connecting...
          </>
        ) : (
          <>
            <Building2 className="w-5 h-5" />
            Connect Bank Account
          </>
        )}
      </button>
      
      {status === 'success' && (
        <p className="text-xs text-emerald-400 text-center">
          ✓ Bank account verified successfully
        </p>
      )}
      
      {status === 'error' && (
        <p className="text-xs text-red-400 text-center">
          Failed to connect. Please try again.
        </p>
      )}
    </div>
  );
}
