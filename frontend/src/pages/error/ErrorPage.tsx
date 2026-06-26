import React from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Box, Container, Typography, Button, Paper } from '@mui/material';
import { Home, Refresh } from '@mui/icons-material';

const errorMessages: Record<string, { title: string; message: string }> = {
  '404': {
    title: 'Page Not Found',
    message: 'The page you are looking for does not exist or has been moved.',
  },
  '500': {
    title: 'Server Error',
    message: 'Something went wrong on our end. Please try again later.',
  },
  '403': {
    title: 'Access Denied',
    message: 'You do not have permission to access this page.',
  },
  default: {
    title: 'An Error Occurred',
    message: 'Something unexpected happened. Please try again.',
  },
};

export const ErrorPage: React.FC = () => {
  const { code } = useParams<{ code: string }>();
  const navigate = useNavigate();
  const errorInfo = errorMessages[code || ''] || errorMessages.default;

  const handleGoHome = () => {
    navigate('/dashboard');
  };

  const handleRefresh = () => {
    window.location.reload();
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
      <Container maxWidth="md">
        <Paper
          sx={{
            p: 6,
            textAlign: 'center',
            bgcolor: '#1A1D23',
            borderRadius: 3,
          }}
        >
          <Typography variant="h1" sx={{ fontSize: '6rem', fontWeight: 700, color: '#3F51B5', mb: 2 }}>
            {code || 'Error'}
          </Typography>
          <Typography variant="h4" sx={{ color: '#FFFFFF', mb: 2 }}>
            {errorInfo?.title || 'Error'}
          </Typography>
          <Typography variant="body1" sx={{ color: '#B0B3B8', mb: 4 }}>
            {errorInfo?.message || 'An unexpected error occurred'}
          </Typography>
          <Box sx={{ display: 'flex', gap: 2, justifyContent: 'center' }}>
            <Button
              variant="contained"
              startIcon={<Home />}
              onClick={handleGoHome}
              sx={{ px: 4, py: 1.5 }}
            >
              Go to Dashboard
            </Button>
            <Button
              variant="outlined"
              startIcon={<Refresh />}
              onClick={handleRefresh}
              sx={{ px: 4, py: 1.5 }}
            >
              Refresh Page
            </Button>
          </Box>
        </Paper>
      </Container>
    </Box>
  );
};
