import React, { useState } from 'react';
import { Box, Container, Typography, Link, Alert } from '@mui/material';
import { useNavigate } from 'react-router-dom';
import { LoginForm } from '@/features/auth/components/LoginForm';
import { useAuth } from '@/features/auth/hooks/useAuth';
import { authService } from '@/features/auth/services/authService';

export const LoginPage: React.FC = () => {
  const navigate = useNavigate();
  const { login } = useAuth();
  const [showRegister, setShowRegister] = useState(false);
  const [registerError, setRegisterError] = useState<string | null>(null);

  const handleLogin = async (email: string, password: string) => {
    try {
      await login(email, password);
      navigate('/dashboard');
    } catch (error: any) {
      const errorMessage = error.response?.data?.detail || error.message || 'Login failed. Please try again.';
      throw new Error(errorMessage);
    }
  };

  const handleRegister = async (email: string, password: string, username: string) => {
    try {
      setRegisterError(null);
      await authService.register(email, password, username);
      await login(username, password);
      navigate('/dashboard');
    } catch (error: any) {
      const errorMessage = error.response?.data?.detail || error.message || 'Registration failed. Please try again.';
      setRegisterError(errorMessage);
      throw new Error(errorMessage);
    }
  };

  return (
    <Box
      sx={{
        minHeight: '100vh',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        bgcolor: '#0D0E10',
      }}
    >
      <Container maxWidth="sm">
        <Typography variant="h4" align="center" gutterBottom sx={{ color: '#FFFFFF', mb: 3 }}>
          {showRegister ? 'Create Account' : 'Welcome Back'}
        </Typography>
        
        {registerError && (
          <Alert severity="error" sx={{ mb: 2 }}>
            {registerError}
          </Alert>
        )}
        
        <LoginForm 
          onLogin={handleLogin} 
          onRegister={showRegister ? handleRegister : undefined}
          isRegisterMode={showRegister}
        />
        
        <Box sx={{ mt: 2, textAlign: 'center' }}>
          <Link 
            component="button" 
            variant="body2" 
            onClick={() => { setShowRegister(!showRegister); setRegisterError(null); }}
            sx={{ color: '#3B82F6' }}
          >
            {showRegister ? 'Already have an account? Login' : "Don't have an account? Register"}
          </Link>
        </Box>
      </Container>
    </Box>
  );
};
