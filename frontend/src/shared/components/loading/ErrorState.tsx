import React from 'react';
import { Box, Typography, Button, useTheme, useMediaQuery, Card, CardContent, Alert, AlertTitle } from '@mui/material';
import { ErrorOutline, Refresh, Home, Support } from '@mui/icons-material';

interface ErrorStateProps {
  title?: string;
  message?: string;
  onRetry?: () => void;
  onGoHome?: () => void;
  showSupport?: boolean;
  onSupport?: () => void;
  error?: Error | string;
}

export const ErrorState: React.FC<ErrorStateProps> = ({
  title = 'Something went wrong',
  message = 'An unexpected error occurred. Please try again later.',
  onRetry,
  onGoHome,
  showSupport = false,
  onSupport,
  error,
}) => {
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('sm'));

  const errorMessage = typeof error === 'string' ? error : error?.message;

  return (
    <Box
      sx={{
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        minHeight: 400,
        p: 3,
      }}
    >
      <Card
        sx={{
          bgcolor: '#1A1D23',
          border: '1px solid #EF4444',
          borderRadius: 2,
          maxWidth: 500,
          width: '100%',
        }}
      >
        <CardContent sx={{ p: 4, textAlign: 'center' }}>
          {/* Error Icon */}
          <Box
            sx={{
              width: 80,
              height: 80,
              bgcolor: 'rgba(239, 68, 68, 0.1)',
              borderRadius: '50%',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              mx: 'auto',
              mb: 3,
            }}
          >
            <ErrorOutline sx={{ color: '#EF4444', fontSize: 48 }} />
          </Box>

          {/* Title */}
          <Typography
            variant={isMobile ? 'h6' : 'h5'}
            sx={{
              color: '#FFFFFF',
              fontWeight: 700,
              mb: 2,
            }}
          >
            {title}
          </Typography>

          {/* Message */}
          <Typography
            variant="body2"
            sx={{
              color: '#B0B3B8',
              mb: errorMessage ? 2 : 3,
              fontSize: '0.875rem',
            }}
          >
            {message}
          </Typography>

          {/* Error Details */}
          {errorMessage && (
            <Alert
              severity="error"
              sx={{
                mb: 3,
                bgcolor: 'rgba(239, 68, 68, 0.1)',
                border: '1px solid rgba(239, 68, 68, 0.3)',
                '& .MuiAlert-icon': { color: '#EF4444' },
                '& .MuiAlert-message': { color: '#FFFFFF' },
              }}
            >
              <AlertTitle sx={{ color: '#EF4444', fontSize: '0.875rem' }}>Error Details</AlertTitle>
              <Typography variant="caption" sx={{ color: '#B0B3B8', fontSize: '0.75rem' }}>
                {errorMessage}
              </Typography>
            </Alert>
          )}

          {/* Actions */}
          <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1.5, alignItems: 'center' }}>
            {onRetry && (
              <Button
                variant="contained"
                onClick={onRetry}
                startIcon={<Refresh />}
                fullWidth={isMobile}
                sx={{
                  bgcolor: '#3F51B5',
                  color: '#FFFFFF',
                  '&:hover': { bgcolor: '#3949AB' },
                }}
              >
                Try Again
              </Button>
            )}
            
            {onGoHome && (
              <Button
                variant="outlined"
                onClick={onGoHome}
                startIcon={<Home />}
                fullWidth={isMobile}
                sx={{
                  borderColor: '#3D4450',
                  color: '#B0B3B8',
                  '&:hover': {
                    borderColor: '#4B5563',
                    bgcolor: 'rgba(255, 255, 255, 0.05)',
                  },
                }}
              >
                Go to Dashboard
              </Button>
            )}

            {showSupport && onSupport && (
              <Button
                variant="text"
                onClick={onSupport}
                startIcon={<Support />}
                fullWidth={isMobile}
                sx={{
                  color: '#3F51B5',
                  '&:hover': { bgcolor: 'rgba(63, 81, 181, 0.1)' },
                }}
              >
                Contact Support
              </Button>
            )}
          </Box>
        </CardContent>
      </Card>
    </Box>
  );
};
