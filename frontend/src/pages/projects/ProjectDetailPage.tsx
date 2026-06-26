import React from 'react';
import { Outlet } from 'react-router-dom';
import { Box } from '@mui/material';

export const ProjectDetailPage: React.FC = () => {
  return (
    <Box>
      <Outlet />
    </Box>
  );
};
