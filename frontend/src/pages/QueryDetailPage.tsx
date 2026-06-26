import React from 'react';
import { Box } from '@mui/material';
import { useParams } from 'react-router-dom';
import { PageHeader } from '@/shared/components/ui';
import { EmptyState } from '@/shared/components/loading';

export const QueryDetailPage: React.FC = () => {
  const { id } = useParams<{ id: string }>();

  return (
    <Box sx={{ p: 3, bgcolor: '#0F1115', minHeight: '100vh' }}>
      <PageHeader
        title={`Query ${id}`}
        subtitle="Query details and analysis"
      />
      <EmptyState
        variant="no-data"
        title="Query Details Require Project Context"
        message="Query details are organized by project. Please access this query through a project page."
      />
    </Box>
  );
};
