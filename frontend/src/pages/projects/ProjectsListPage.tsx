import React from 'react';
import { Box, Typography, Button } from '@mui/material';
import { ProjectList } from '@/features/projects/components/ProjectList';
import { PageHeader } from '@/shared/components/ui';

export const ProjectsListPage: React.FC = () => {
  return (
    <Box sx={{ p: 3, bgcolor: '#0F1115', minHeight: '100vh' }}>
      <PageHeader
        title="Projects"
        subtitle="Manage your codebase analysis projects"
      />
      <ProjectList />
    </Box>
  );
};
