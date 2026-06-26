import React from 'react';
import { Box } from '@mui/material';
import { useParams, useNavigate } from 'react-router-dom';
import { PageHeader } from '@/shared/components/ui';
import { EmptyState } from '@/shared/components/loading';

export const ExecutionPlanViewerPage: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();

  return (
    <Box sx={{ p: 3, bgcolor: '#0F1115', minHeight: '100vh' }}>
      <PageHeader
        title={`Execution Plan ${id}`}
        subtitle="Execution plan visualization and analysis"
      />
      <EmptyState
        variant="no-data"
        title="Execution Plan Details Require Project Context"
        message="Execution plan details are organized by project. Please access this plan through a project page."
      />
    </Box>
  );
};
