import React from 'react';
import { Box } from '@mui/material';
import { PageHeader } from '@/shared/components/ui';
import { EmptyState } from '@/shared/components/loading';

export const SummaryPage: React.FC = () => {
  return (
    <Box sx={{ p: 3, bgcolor: '#0F1115', minHeight: '100vh' }}>
      <PageHeader
        title="Summary"
        subtitle="Project summary and overview"
      />
      <EmptyState
        variant="no-data"
        title="No summary available"
        message="Select a project from the Projects page to view its summary."
      />
    </Box>
  );
};
