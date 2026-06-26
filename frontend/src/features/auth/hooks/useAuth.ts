import { useState, useEffect } from 'react';
import { authService } from '../services/authService';

interface AuthState {
  isAuthenticated: boolean;
  isLoading: boolean;
  token: string | null;
  user: any | null;
}

export const useAuth = () => {
  const [authState, setAuthState] = useState<AuthState>({
    isAuthenticated: false,
    isLoading: true,
    token: null,
    user: null,
  });

  useEffect(() => {
    const token = localStorage.getItem('auth_token');
    if (token) {
      setAuthState({
        isAuthenticated: true,
        isLoading: false,
        token,
        user: null,
      });
    } else {
      setAuthState({
        isAuthenticated: false,
        isLoading: false,
        token: null,
        user: null,
      });
    }
  }, []);

  const login = async (email: string, password: string) => {
    try {
      const response = await authService.login(email, password);
      const token = response.access_token || response.token;
      localStorage.setItem('auth_token', token);
      setAuthState({
        isAuthenticated: true,
        isLoading: false,
        token,
        user: response.user || { email },
      });
    } catch (error: any) {
      console.error('Login failed:', error);
      const errorMessage = error.response?.data?.detail || error.message || 'Login failed';
      throw new Error(errorMessage);
    }
  };

  const logout = async () => {
    try {
      await authService.logout();
    } catch (error) {
      console.error('Logout failed:', error);
    } finally {
      localStorage.removeItem('auth_token');
      setAuthState({
        isAuthenticated: false,
        isLoading: false,
        token: null,
        user: null,
      });
    }
  };

  return {
    ...authState,
    login,
    logout,
  };
};
