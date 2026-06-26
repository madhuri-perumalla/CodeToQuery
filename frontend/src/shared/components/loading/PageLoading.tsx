import React from 'react';
import { Box, CircularProgress, Typography } from '@mui/material';

export const PageLoading: React.FC = () => {
  return (
    <Box
      sx={{
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        minHeight: '100vh',
        bgcolor: '#0D0E10',
      }}
    >
      <CircularProgress size={60} sx={{ color: '#3F51B5', mb: 3 }} />
      <Typography variant="h6" sx={{ color: '#B0B3B8' }}>
        Loading...
      </Typography>
    </Box>
  );
};
