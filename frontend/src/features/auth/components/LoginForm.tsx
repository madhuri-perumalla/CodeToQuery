import React, { useState } from 'react';
import { Box, TextField, Button, Typography, Alert } from '@mui/material';

interface LoginFormProps {
  onLogin: (email: string, password: string) => Promise<void>;
  onRegister?: (email: string, password: string, username: string) => Promise<void>;
  isRegisterMode?: boolean;
}

export const LoginForm: React.FC<LoginFormProps> = ({ onLogin, onRegister, isRegisterMode = false }) => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [username, setUsername] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    
    // Validation
    if (isRegisterMode) {
      if (username.length < 3) {
        setError('Username must be at least 3 characters');
        return;
      }
      if (password.length < 8) {
        setError('Password must be at least 8 characters');
        return;
      }
    }
    
    setLoading(true);

    try {
      if (isRegisterMode && onRegister) {
        await onRegister(email, password, username);
      } else {
        await onLogin(email, password);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Operation failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <Box component="form" onSubmit={handleSubmit} sx={{ maxWidth: 400, mx: 'auto', p: 3, bgcolor: '#1A1D23', borderRadius: 2, border: '1px solid #242830' }}>
      <Typography variant="h5" gutterBottom sx={{ color: '#FFFFFF' }}>
        {isRegisterMode ? 'Register' : 'Login'}
      </Typography>
      
      {error && (
        <Alert severity="error" sx={{ mb: 2 }}>
          {error}
        </Alert>
      )}

      {isRegisterMode && (
        <TextField
          fullWidth
          label="Username"
          value={username}
          onChange={(e) => setUsername(e.target.value)}
          margin="normal"
          required
          helperText="Minimum 3 characters"
          sx={{ 
            '& .MuiOutlinedInput-root': { color: '#FFFFFF' },
            '& .MuiInputLabel-root': { color: '#9CA3AF' },
            '& .MuiFormHelperText-root': { color: '#6B7280' },
          }}
        />
      )}

      <TextField
        fullWidth
        label="Email"
        type="email"
        value={email}
        onChange={(e) => setEmail(e.target.value)}
        margin="normal"
        required
        sx={{ 
          '& .MuiOutlinedInput-root': { color: '#FFFFFF' },
          '& .MuiInputLabel-root': { color: '#9CA3AF' },
        }}
      />

      <TextField
        fullWidth
        label="Password"
        type="password"
        value={password}
        onChange={(e) => setPassword(e.target.value)}
        margin="normal"
        required
        helperText="Minimum 8 characters"
        sx={{ 
          '& .MuiOutlinedInput-root': { color: '#FFFFFF' },
          '& .MuiInputLabel-root': { color: '#9CA3AF' },
          '& .MuiFormHelperText-root': { color: '#6B7280' },
        }}
      />

      <Button
        type="submit"
        fullWidth
        variant="contained"
        disabled={loading}
        sx={{ mt: 3, bgcolor: '#3B82F6', '&:hover': { bgcolor: '#2563EB' } }}
      >
        {loading ? (isRegisterMode ? 'Creating account...' : 'Logging in...') : (isRegisterMode ? 'Register' : 'Login')}
      </Button>
    </Box>
  );
};
