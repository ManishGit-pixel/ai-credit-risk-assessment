import axios from 'axios';

const api = axios.create({
  baseURL: 'http://localhost:8000',
  headers: {
    'Content-Type': 'application/json',
  },
});

// Loan Analysis API - Enhanced Integration
export const analyzeLoan = async (loanData) => {
  try {
    const response = await api.post('/analyze-loan', loanData);
    return response.data;
  } catch (error) {
    console.error('Loan analysis failed:', error);
    throw error;
  }
};

// KYC Verification
export const verifyKYC = async (kycData) => {
  try {
    const response = await api.post('/verify-kyc', kycData);
    return response.data;
  } catch (error) {
    console.error('KYC verification failed:', error);
    throw error;
  }
};

// Credit Bureau Check
export const checkCreditBureau = async (userId, fullName = '') => {
  try {
    const response = await api.post('/credit-bureau/check', { 
      user_id: userId, 
      full_name: fullName 
    });
    return response.data;
  } catch (error) {
    console.error('Credit bureau check failed:', error);
    throw error;
  }
};

// Plaid Integration
export const createPlaidLinkToken = async (userId, userName = null) => {
  try {
    const response = await api.post('/plaid/create-link-token', { 
      user_id: userId, 
      user_name: userName 
    });
    return response.data;
  } catch (error) {
    console.error('Plaid link token creation failed:', error);
    throw error;
  }
};

export const exchangePlaidToken = async (publicToken) => {
  try {
    const response = await api.post('/plaid/exchange-token', { 
      public_token: publicToken 
    });
    return response.data;
  } catch (error) {
    console.error('Plaid token exchange failed:', error);
    throw error;
  }
};

export const getPlaidBalances = async (accessToken) => {
  try {
    const response = await api.post('/plaid/get-balances', { 
      access_token: accessToken 
    });
    return response.data;
  } catch (error) {
    console.error('Failed to get Plaid balances:', error);
    throw error;
  }
};

export const getPlaidIncome = async (accessToken) => {
  try {
    const response = await api.post('/plaid/get-income', { 
      access_token: accessToken 
    });
    return response.data;
  } catch (error) {
    console.error('Failed to get Plaid income:', error);
    throw error;
  }
};

// KYC Document Upload
export const uploadKYCDocument = async (userId, file, expectedName = null, expectedDob = null) => {
  try {
    const formData = new FormData();
    formData.append('user_id', userId);
    formData.append('file', file);
    if (expectedName) formData.append('expected_name', expectedName);
    if (expectedDob) formData.append('expected_dob', expectedDob);
    
    const response = await api.post('/kyc/upload-document', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  } catch (error) {
    console.error('KYC document upload failed:', error);
    throw error;
  }
};

// User Profile
export const getUserProfile = async (userId) => {
  try {
    const response = await api.get(`/user/${userId}`);
    return response.data;
  } catch (error) {
    console.error('Failed to get user profile:', error);
    throw error;
  }
};

// Health Check
export const healthCheck = async () => {
  try {
    const response = await api.get('/health');
    return response.data;
  } catch (error) {
    console.error('Health check failed:', error);
    throw error;
  }
};

export default api;
