import React from 'react';
import { Box, Card, CardContent, Typography, Chip, Grid } from '@mui/material';
import { History, CheckCircle, Error as ErrorIcon, Schedule } from '@mui/icons-material';
import { useAnalysisRuns } from '@/lib/react-query';
import { LoadingSkeleton, ErrorState, EmptyState } from '@/shared/components/loading';
import { PageHeader } from '@/shared/components/ui';
import { useParams } from 'react-router-dom';

export const HistoryPage: React.FC = () => {
  const { projectId } = useParams<{ projectId: string }>();
  const codebaseId = projectId ? parseInt(projectId) : undefined;
  const { data, isLoading, error, refetch } = useAnalysisRuns({ page: 1, page_size: 50, codebase_id: codebaseId });

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
          title="Failed to load analysis history"
          message="Unable to fetch analysis history. Please try again."
          onRetry={() => refetch()}
        />
      </Box>
    );
  }

  const runs = data?.items || [];

  if (!runs || runs.length === 0) {
    return (
      <Box sx={{ p: 3, bgcolor: '#0F1115', minHeight: '100vh' }}>
        <PageHeader
          title="History"
          subtitle="Historical scan results"
          onRefresh={() => refetch()}
        />
        <EmptyState
          variant="no-data"
          title="No analysis has been run for this project yet"
          message="Run analysis to populate scan history."
          actionLabel="Run Analysis"
          onAction={() => window.location.href = `/projects/${projectId}/overview`}
        />
      </Box>
    );
  }

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'completed':
        return <CheckCircle sx={{ color: '#059669' }} />;
      case 'failed':
        return <ErrorIcon sx={{ color: '#DC2626' }} />;
      case 'running':
      case 'pending':
        return <Schedule sx={{ color: '#D97706' }} />;
      default:
        return null;
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed':
        return '#059669';
      case 'failed':
        return '#DC2626';
      case 'running':
      case 'pending':
        return '#D97706';
      default:
        return '#6B7280';
    }
  };

  return (
    <Box sx={{ p: 3, bgcolor: '#0F1115', minHeight: '100vh' }}>
      <PageHeader
        title="History"
        subtitle={`Found ${data?.total || 0} historical scans`}
        onRefresh={() => refetch()}
      />

      <Box sx={{ mt: 2 }}>
        {runs.map((run: any) => (
          <Card key={run.id} sx={{ bgcolor: '#1A1D23', border: '1px solid #242830', borderRadius: 2, mb: 2 }}>
            <CardContent sx={{ p: 2 }}>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: 2 }}>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                  <History sx={{ color: '#8B5CF6', fontSize: 28 }} />
                  <Box>
                    <Typography variant="h6" sx={{ color: '#FFFFFF', fontWeight: 600 }}>
                      Scan #{run.id}
                    </Typography>
                    <Box sx={{ display: 'flex', gap: 1, mt: 1 }}>
                      <Chip
                        label={run.status}
                        size="small"
                        sx={{
                          bgcolor: getStatusColor(run.status),
                          color: '#FFFFFF',
                        }}
                      />
                      <Typography variant="caption" sx={{ color: '#B0B3B8' }}>
                        Codebase ID: {run.codebaseId || 'N/A'}
                      </Typography>
                    </Box>
                  </Box>
                </Box>
                {getStatusIcon(run.status)}
              </Box>

              <Grid container spacing={2} sx={{ mb: 2 }}>
                <Grid item xs={12} sm={6} md={2}>
                  <Box sx={{ p: 2, bgcolor: '#14171C', borderRadius: 1 }}>
                    <Typography variant="caption" sx={{ color: '#6B7280', display: 'block', mb: 0.5 }}>
                      Scan Date
                    </Typography>
                    <Typography variant="body2" sx={{ color: '#E5E7EB', fontWeight: 600 }}>
                      {run.createdAt ? new Date(run.createdAt).toLocaleDateString() : 'N/A'}
                    </Typography>
                  </Box>
                </Grid>
                <Grid item xs={12} sm={6} md={2}>
                  <Box sx={{ p: 2, bgcolor: '#14171C', borderRadius: 1 }}>
                    <Typography variant="caption" sx={{ color: '#6B7280', display: 'block', mb: 0.5 }}>
                      Files Scanned
                    </Typography>
                    <Typography variant="body2" sx={{ color: '#E5E7EB', fontWeight: 600 }}>
                      {run.filesScanned || 'N/A'}
                    </Typography>
                  </Box>
                </Grid>
                <Grid item xs={12} sm={6} md={2}>
                  <Box sx={{ p: 2, bgcolor: '#14171C', borderRadius: 1 }}>
                    <Typography variant="caption" sx={{ color: '#6B7280', display: 'block', mb: 0.5 }}>
                      Queries Found
                    </Typography>
                    <Typography variant="body2" sx={{ color: '#E5E7EB', fontWeight: 600 }}>
                      {run.queriesFound || 'N/A'}
                    </Typography>
                  </Box>
                </Grid>
                <Grid item xs={12} sm={6} md={2}>
                  <Box sx={{ p: 2, bgcolor: '#14171C', borderRadius: 1 }}>
                    <Typography variant="caption" sx={{ color: '#6B7280', display: 'block', mb: 0.5 }}>
                      Diagnostics Count
                    </Typography>
                    <Typography variant="body2" sx={{ color: '#E5E7EB', fontWeight: 600 }}>
                      {run.diagnosticsCount || 'N/A'}
                    </Typography>
                  </Box>
                </Grid>
                <Grid item xs={12} sm={6} md={2}>
                  <Box sx={{ p: 2, bgcolor: '#14171C', borderRadius: 1 }}>
                    <Typography variant="caption" sx={{ color: '#6B7280', display: 'block', mb: 0.5 }}>
                      Pattern Groups
                    </Typography>
                    <Typography variant="body2" sx={{ color: '#E5E7EB', fontWeight: 600 }}>
                      {run.patternGroups || 'N/A'}
                    </Typography>
                  </Box>
                </Grid>
                <Grid item xs={12} sm={6} md={2}>
                  <Box sx={{ p: 2, bgcolor: '#14171C', borderRadius: 1 }}>
                    <Typography variant="caption" sx={{ color: '#6B7280', display: 'block', mb: 0.5 }}>
                      Health Score
                    </Typography>
                    <Typography variant="body2" sx={{ color: '#E5E7EB', fontWeight: 600 }}>
                      {run.healthScore || 'N/A'}
                    </Typography>
                  </Box>
                </Grid>
              </Grid>

              <Box sx={{ mt: 2, pt: 2, borderTop: '1px solid #242830' }}>
                <Typography variant="caption" sx={{ color: '#6B7280', display: 'block', mb: 0.5 }}>
                  Started: {run.createdAt ? new Date(run.createdAt).toLocaleString() : 'N/A'}
                </Typography>
                <Typography variant="caption" sx={{ color: '#6B7280', display: 'block' }}>
                  Completed: {run.completedAt ? new Date(run.completedAt).toLocaleString() : 'In Progress'}
                </Typography>
                {run.errorMessage && (
                  <Typography variant="caption" sx={{ color: '#DC2626', display: 'block', mt: 1 }}>
                    Error: {run.errorMessage}
                  </Typography>
                )}
              </Box>
            </CardContent>
          </Card>
        ))}
      </Box>
    </Box>
  );
};
