import React, { createContext, useContext, useState } from 'react';

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  // Mock auth state — replace with real backend auth later
  const [user, setUser] = useState(() => {
    const saved = localStorage.getItem('loanAgentUser');
    return saved ? JSON.parse(saved) : null;
  });

  const login = (email, name = '') => {
    const userData = { email, name: name || email.split('@')[0] };
    localStorage.setItem('loanAgentUser', JSON.stringify(userData));
    setUser(userData);
  };

  const logout = () => {
    localStorage.removeItem('loanAgentUser');
    setUser(null);
  };

  return (
    <AuthContext.Provider value={{ user, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

export const useAuth = () => useContext(AuthContext);
