import React, { useState } from 'react';
import { Box, Button, Card, CardContent, Typography, LinearProgress, Chip, Grid, Alert, List, ListItem, ListItemText, ListItemIcon } from '@mui/material';
import { PlayArrow, Refresh, CheckCircle, Error as ErrorIcon, Schedule, Folder, Code, Description } from '@mui/icons-material';
import { PageHeader } from '@/shared/components/ui';
import { useAnalysisRuns, useCreateAnalysis, useProjects, useCodebases } from '@/lib/react-query';
import { LoadingSkeleton, ErrorState, EmptyState } from '@/shared/components/loading';
import { useProjectContext } from '@/contexts/ProjectContext';

export const AnalysisPage: React.FC = () => {
  const { selectedProjectId, selectedCodebaseId } = useProjectContext();
  const { data: runs, isLoading, error, refetch } = useAnalysisRuns({ page: 1, page_size: 10, codebase_id: selectedCodebaseId || undefined });
  const { data: projects } = useProjects(1, 100);
  const { data: codebasesData } = useCodebases(selectedProjectId || undefined);
  const createAnalysis = useCreateAnalysis();
  const [selectedCodebaseIdLocal, setSelectedCodebaseIdLocal] = useState<number | null>(selectedCodebaseId || null);

  const codebases = codebasesData || [];
  const latestRun = runs?.items?.[0];
  const isRunning = latestRun?.status === 'running' || latestRun?.status === 'pending';

  const handleRunAnalysis = async (codebaseId: number) => {
    try {
      await createAnalysis.mutateAsync({ codebase_id: codebaseId });
      refetch();
    } catch (error) {
      console.error('Failed to run analysis:', error);
    }
  };

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

  if (isLoading) {
    return (
      <Box sx={{ p: 3 }}>
        <LoadingSkeleton variant="dashboard" />
      </Box>
    );
  }

  if (error) {
    return (
      <Box sx={{ p: 3 }}>
        <ErrorState
          title="Failed to load analysis data"
          message="Unable to fetch analysis data. Please try again."
          onRetry={() => refetch()}
        />
      </Box>
    );
  }

  return (
    <Box sx={{ p: 3, bgcolor: '#0F1115', minHeight: '100vh' }}>
      <PageHeader
        title="Analysis"
        subtitle="Run and monitor codebase scans"
        onRefresh={() => refetch()}
      />

      <Grid container spacing={3}>
        {/* Codebase Selection Card */}
        <Grid item xs={12} md={6}>
          <Card sx={{ bgcolor: '#1A1D23', border: '1px solid #242830', borderRadius: 2 }}>
            <CardContent>
              <Typography variant="h6" sx={{ color: '#FFFFFF', mb: 2, display: 'flex', alignItems: 'center', gap: 1 }}>
                <Folder />
                Select Codebase to Scan
              </Typography>
              
              {codebases && codebases.length > 0 ? (
                <List sx={{ bgcolor: '#14171C', borderRadius: 1 }}>
                  {codebases.map((codebase: any) => (
                    <ListItem
                      key={codebase.id}
                      button
                      onClick={() => setSelectedCodebaseIdLocal(codebase.id)}
                      selected={selectedCodebaseIdLocal === codebase.id}
                      sx={{
                        '&.Mui-selected': { bgcolor: 'rgba(63, 81, 181, 0.2)' },
                        '&:hover': { bgcolor: '#242830' },
                      }}
                    >
                      <ListItemIcon>
                        <Code sx={{ color: '#3F51B5' }} />
                      </ListItemIcon>
                      <ListItemText
                        primary={codebase.scan_path || `Codebase #${codebase.id}`}
                        secondary={`Status: ${codebase.status}`}
                        primaryTypographyProps={{ sx: { color: '#E5E7EB' } }}
                        secondaryTypographyProps={{ sx: { color: '#B0B3B8' } }}
                      />
                    </ListItem>
                  ))}
                </List>
              ) : (
                <EmptyState
                  variant="no-data"
                  title="No codebases found"
                  message="Select a project with codebases to run analysis"
                />
              )}
            </CardContent>
          </Card>
        </Grid>

        {/* Scan Progress Card */}
        <Grid item xs={12} md={6}>
          <Card sx={{ bgcolor: '#1A1D23', border: '1px solid #242830', borderRadius: 2 }}>
            <CardContent>
              <Typography variant="h6" sx={{ color: '#FFFFFF', mb: 2, display: 'flex', alignItems: 'center', gap: 1 }}>
                {latestRun ? getStatusIcon(latestRun.status) : <Schedule sx={{ color: '#6B7280' }} />}
                Scan Progress
              </Typography>
              
              {latestRun ? (
                <Box>
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 2 }}>
                    <Chip
                      label={latestRun.status.toUpperCase()}
                      sx={{
                        bgcolor: getStatusColor(latestRun.status),
                        color: '#FFFFFF',
                        fontWeight: 600,
                      }}
                    />
                    <Typography variant="body2" sx={{ color: '#B0B3B8' }}>
                      Run #{latestRun.id}
                    </Typography>
                  </Box>
                  
                  {isRunning && (
                    <Box sx={{ mt: 2 }}>
                      <LinearProgress sx={{ bgcolor: '#242830', '& .MuiLinearProgress-bar': { bgcolor: '#3F51B5' } }} />
                      <Typography variant="caption" sx={{ color: '#B0B3B8', display: 'block', mt: 1 }}>
                        Analysis in progress...
                      </Typography>
                    </Box>
                  )}
                  
                  {latestRun.error_message && (
                    <Alert severity="error" sx={{ mt: 2, bgcolor: 'rgba(220, 38, 38, 0.1)' }}>
                      {latestRun.error_message}
                    </Alert>
                  )}
                </Box>
              ) : (
                <Typography variant="body2" sx={{ color: '#6B7280' }}>
                  Select a project and start a scan to see progress
                </Typography>
              )}
            </CardContent>
          </Card>
        </Grid>

        {/* Scan Actions Card */}
        <Grid item xs={12}>
          <Card sx={{ bgcolor: '#1A1D23', border: '1px solid #242830', borderRadius: 2 }}>
            <CardContent>
              <Typography variant="h6" sx={{ color: '#FFFFFF', mb: 2 }}>
                Scan Actions
              </Typography>
              
              <Box sx={{ display: 'flex', gap: 2, alignItems: 'center', flexWrap: 'wrap' }}>
                <Button
                  variant="contained"
                  startIcon={<PlayArrow />}
                  onClick={() => selectedCodebaseIdLocal && handleRunAnalysis(selectedCodebaseIdLocal)}
                  disabled={!selectedCodebaseIdLocal || isRunning || createAnalysis.isPending}
                  sx={{
                    bgcolor: '#3F51B5',
                    '&:hover': { bgcolor: '#3949AB' },
                    '&:disabled': { bgcolor: '#242830' },
                  }}
                >
                  {createAnalysis.isPending ? 'Starting Scan...' : 'Start Scan'}
                </Button>
                
                <Button
                  variant="outlined"
                  startIcon={<Refresh />}
                  onClick={() => refetch()}
                  disabled={isLoading}
                  sx={{
                    borderColor: '#242830',
                    color: '#B0B3B8',
                    '&:hover': { borderColor: '#3F51B5', color: '#FFFFFF' },
                  }}
                >
                  Refresh Status
                </Button>
              </Box>

              {!selectedCodebaseIdLocal && (
                <Typography variant="body2" sx={{ color: '#6B7280', mt: 2 }}>
                  Select a codebase from the list above to start a scan
                </Typography>
              )}
            </CardContent>
          </Card>
        </Grid>

        {/* Scan Summary Card */}
        {latestRun && latestRun.status === 'completed' && (
          <Grid item xs={12}>
            <Card sx={{ bgcolor: '#1A1D23', border: '1px solid #242830', borderRadius: 2 }}>
              <CardContent>
                <Typography variant="h6" sx={{ color: '#FFFFFF', mb: 2, display: 'flex', alignItems: 'center', gap: 1 }}>
                  <Description />
                  Scan Summary
                </Typography>
                
                <Grid container spacing={2}>
                  <Grid item xs={12} sm={6} md={3}>
                    <Box sx={{ p: 2, bgcolor: '#14171C', borderRadius: 1 }}>
                      <Typography variant="caption" sx={{ color: '#B0B3B8' }}>Started</Typography>
                      <Typography variant="body2" sx={{ color: '#E5E7EB' }}>
                        {latestRun.createdAt ? new Date(latestRun.createdAt).toLocaleString() : 'N/A'}
                      </Typography>
                    </Box>
                  </Grid>
                  <Grid item xs={12} sm={6} md={3}>
                    <Box sx={{ p: 2, bgcolor: '#14171C', borderRadius: 1 }}>
                      <Typography variant="caption" sx={{ color: '#B0B3B8' }}>Completed</Typography>
                      <Typography variant="body2" sx={{ color: '#E5E7EB' }}>
                        {latestRun.completedAt ? new Date(latestRun.completedAt).toLocaleString() : 'N/A'}
                      </Typography>
                    </Box>
                  </Grid>
                  <Grid item xs={12} sm={6} md={3}>
                    <Box sx={{ p: 2, bgcolor: '#14171C', borderRadius: 1 }}>
                      <Typography variant="caption" sx={{ color: '#B0B3B8' }}>Codebase ID</Typography>
                      <Typography variant="body2" sx={{ color: '#E5E7EB' }}>
                        {latestRun.codebaseId || 'N/A'}
                      </Typography>
                    </Box>
                  </Grid>
                  <Grid item xs={12} sm={6} md={3}>
                    <Box sx={{ p: 2, bgcolor: '#14171C', borderRadius: 1 }}>
                      <Typography variant="caption" sx={{ color: '#B0B3B8' }}>Status</Typography>
                      <Typography variant="body2" sx={{ color: '#059669' }}>
                        {latestRun.status}
                      </Typography>
                    </Box>
                  </Grid>
                </Grid>
              </CardContent>
            </Card>
          </Grid>
        )}

        {/* Recent Scans */}
        <Grid item xs={12}>
          <Card sx={{ bgcolor: '#1A1D23', border: '1px solid #242830', borderRadius: 2 }}>
            <CardContent>
              <Typography variant="h6" sx={{ color: '#FFFFFF', mb: 2 }}>
                Recent Scans
              </Typography>
              
              {runs && runs.items && runs.items.length > 0 ? (
                <List>
                  {runs.items.map((run: any) => (
                    <ListItem
                      key={run.id}
                      sx={{
                        bgcolor: '#14171C',
                        borderRadius: 1,
                        mb: 1,
                      }}
                    >
                      <ListItemIcon>
                        {getStatusIcon(run.status)}
                      </ListItemIcon>
                      <ListItemText
                        primary={`Run #${run.id}`}
                        secondary={`Codebase ID: ${run.codebaseId} | ${run.createdAt ? new Date(run.createdAt).toLocaleString() : 'N/A'}`}
                        primaryTypographyProps={{ sx: { color: '#E5E7EB' } }}
                        secondaryTypographyProps={{ sx: { color: '#B0B3B8' } }}
                      />
                      <Chip
                        label={run.status}
                        size="small"
                        sx={{
                          bgcolor: getStatusColor(run.status),
                          color: '#FFFFFF',
                        }}
                      />
                    </ListItem>
                  ))}
                </List>
              ) : (
                <EmptyState
                  variant="no-data"
                  title="No scan history"
                  message="Run your first scan to see history here"
                />
              )}
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Box>
  );
};
