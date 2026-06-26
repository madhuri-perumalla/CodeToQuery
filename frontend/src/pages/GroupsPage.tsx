import React from 'react';
import { Box } from '@mui/material';
import { PageHeader } from '@/shared/components/ui';
import { EmptyState } from '@/shared/components/loading';

export const GroupsPage: React.FC = () => {
  return (
    <Box sx={{ p: 3, bgcolor: '#0F1115', minHeight: '100vh' }}>
      <PageHeader
        title="Query Groups"
        subtitle="View and manage query groupings"
      />
      <EmptyState
        variant="no-data"
        title="Select a Project to View Query Groups"
        message="Query groups are organized by project. Please select a project to view its query groups."
      />
    </Box>
  );
};
