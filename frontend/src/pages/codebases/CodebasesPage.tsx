import React from 'react';
import { Box, Typography, Grid, Card, CardContent, Chip } from '@mui/material';
import { LoadingSkeleton, ErrorState, EmptyState } from '@/shared/components/loading';
import { PageHeader } from '@/shared/components/ui';

export const CodebasesPage: React.FC = () => {

  // This would connect to a codebases API when implemented
  const codebases: any[] = [];
  const isLoading = false;
  const error = null;

  if (isLoading) {
    return (
      <Box sx={{ p: 3 }}>
        <LoadingSkeleton variant="table" />
      </Box>
    );
  }

  if (error) {
    return (
      <Box sx={{ p: 3 }}>
        <ErrorState
          title="Failed to load codebases"
          message="Unable to fetch codebase data. Please try again."
          onRetry={() => {}}
        />
      </Box>
    );
  }

  if (codebases.length === 0) {
    return (
      <Box sx={{ p: 3 }}>
        <PageHeader
          title="Codebases"
          subtitle="Manage your codebases for SQL analysis"
          onRefresh={() => {}}
        />
        <EmptyState
          variant="no-data"
          title="No codebases found"
          message="Add a codebase to start analyzing SQL queries."
        />
      </Box>
    );
  }

  return (
    <Box sx={{ p: 3 }}>
      <PageHeader
        title="Codebases"
        subtitle="Manage your codebases for SQL analysis"
        onRefresh={() => {}}
      />
      <Grid container spacing={2}>
        {codebases.map((codebase: any) => (
          <Grid item xs={12} sm={6} md={4} key={codebase.id}>
            <Card sx={{ bgcolor: '#1A1D23', border: '1px solid #242830' }}>
              <CardContent>
                <Typography variant="h6" sx={{ color: '#FFFFFF', mb: 1 }}>
                  {codebase.name}
                </Typography>
                <Typography variant="body2" sx={{ color: '#9CA3AF', mb: 2 }}>
                  {codebase.scan_path}
                </Typography>
                <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
                  <Chip
                    label={codebase.status}
                    size="small"
                    sx={{
                      bgcolor: codebase.status === 'completed' ? '#059669' : '#D97706',
                      color: '#FFFFFF',
                    }}
                  />
                  <Chip
                    label={`${codebase.file_count} files`}
                    size="small"
                    sx={{ bgcolor: '#374151', color: '#FFFFFF' }}
                  />
                </Box>
              </CardContent>
            </Card>
          </Grid>
        ))}
      </Grid>
    </Box>
  );
};
