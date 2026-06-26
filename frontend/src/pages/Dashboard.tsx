import React from 'react';
import { Box, Grid, useTheme, useMediaQuery, Card, CardContent, Typography, Button } from '@mui/material';
import { PageHeader, StatCard, HealthScoreCard } from '@/shared/components/ui';
import { LoadingSkeleton, ErrorState, EmptyState } from '@/shared/components/loading';
import { useDashboardMetrics } from '@/lib/react-query';
import { useProjects } from '@/lib/react-query';
import { useNavigate } from 'react-router-dom';
import { ROUTES } from '@/lib/routes/constants';
import { useProjectContext } from '@/contexts/ProjectContext';

export const Dashboard: React.FC = () => {
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('sm'));
  const navigate = useNavigate();
  const { selectedProject } = useProjectContext();

  const { data: dashboardData, isLoading, error, refetch } = useDashboardMetrics(selectedProject?.id ? String(selectedProject.id) : undefined);
  const { data: projects } = useProjects(1, 1);

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
          title="Failed to load dashboard"
          message="Unable to fetch dashboard data. Please try again."
          onRetry={() => refetch()}
        />
      </Box>
    );
  }

  const latestProject = selectedProject || projects?.items?.[0];

  if (!dashboardData || !latestProject) {
    return (
      <Box sx={{ p: isMobile ? 2 : 3, bgcolor: '#0F1115', minHeight: '100vh' }}>
        <PageHeader
          title="Dashboard"
          subtitle="High-level overview of your codebase analysis"
          onRefresh={() => refetch()}
        />
        <EmptyState
          variant="no-data"
          title="No analysis data available"
          message="Select a project and run a scan to populate the dashboard with analysis results."
        />
      </Box>
    );
  }

  return (
    <Box sx={{ p: isMobile ? 2 : 3, bgcolor: '#0F1115', minHeight: '100vh' }}>
      {/* Page Header */}
      <PageHeader
        title="Dashboard"
        subtitle={`Overview for ${latestProject.name}`}
        onRefresh={() => refetch()}
      />

      {/* Project Overview Card */}
      <Card sx={{ bgcolor: '#1A1D23', border: '1px solid #242830', borderRadius: 2, mb: 3 }}>
        <CardContent sx={{ p: 3 }}>
          <Typography variant="h6" sx={{ color: '#FFFFFF', fontWeight: 600, mb: 2 }}>
            Project: {latestProject.name}
          </Typography>
          <Grid container spacing={2}>
            <Grid item xs={12} sm={6} md={3}>
              <Typography variant="body2" sx={{ color: '#B0B3B8' }}>Last Scan</Typography>
              <Typography variant="body1" sx={{ color: '#E5E7EB' }}>
                {latestProject.updatedAt ? new Date(latestProject.updatedAt).toLocaleString() : 'Never'}
              </Typography>
            </Grid>
            <Grid item xs={12} sm={6} md={3}>
              <Typography variant="body2" sx={{ color: '#B0B3B8' }}>Repository Path</Typography>
              <Typography variant="body1" sx={{ color: '#E5E7EB' }}>
                {latestProject.config?.codebase?.source || 'N/A'}
              </Typography>
            </Grid>
            <Grid item xs={12} sm={6} md={3}>
              <Typography variant="body2" sx={{ color: '#B0B3B8' }}>Status</Typography>
              <Typography variant="body1" sx={{ color: '#E5E7EB' }}>
                {latestProject.status || 'Active'}
              </Typography>
            </Grid>
            <Grid item xs={12} sm={6} md={3}>
              <Button 
                variant="outlined" 
                size="small"
                onClick={() => navigate(ROUTES.PROJECTS)}
                sx={{ mt: 1 }}
              >
                View All Projects
              </Button>
            </Grid>
          </Grid>
        </CardContent>
      </Card>

      {/* Summary Metrics */}
      <Grid container spacing={2} sx={{ mb: 3 }}>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Files Scanned"
            value={dashboardData?.filesScanned || 0}
            subtitle="Total files analyzed"
            icon={<Typography variant="h4">📁</Typography>}
            color="primary"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Queries Discovered"
            value={dashboardData?.totalQueries || 0}
            subtitle="SQL queries extracted"
            icon={<Typography variant="h4">🔍</Typography>}
            color="primary"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Diagnostics Generated"
            value={dashboardData?.diagnosticsCount || 0}
            subtitle="Performance risks detected"
            icon={<Typography variant="h4">⚠️</Typography>}
            color="warning"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Pattern Groups"
            value={dashboardData?.patternGroups || 0}
            subtitle="Similar query patterns"
            icon={<Typography variant="h4">🔄</Typography>}
            color="info"
          />
        </Grid>
      </Grid>

      {/* Health Score */}
      <Grid container spacing={2}>
        <Grid item xs={12} md={6}>
          <HealthScoreCard
            score={dashboardData?.healthScore || 75}
            label="Overall Health Score"
            description="Based on query performance, cost, and optimization status"
          />
        </Grid>
        <Grid item xs={12} md={6}>
          <Card sx={{ bgcolor: '#1A1D23', border: '1px solid #242830', borderRadius: 2 }}>
            <CardContent sx={{ p: 3 }}>
              <Typography variant="h6" sx={{ color: '#FFFFFF', fontWeight: 600, mb: 2 }}>
                Quick Actions
              </Typography>
              <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
                <Button 
                  variant="contained" 
                  onClick={() => navigate(ROUTES.QUERIES)}
                  sx={{ bgcolor: '#3F51B5' }}
                >
                  View All Queries
                </Button>
                <Button 
                  variant="outlined" 
                  onClick={() => navigate(ROUTES.DIAGNOSTICS_GLOBAL)}
                  sx={{ borderColor: '#242830', color: '#E5E7EB' }}
                >
                  Review Diagnostics
                </Button>
                <Button 
                  variant="outlined" 
                  onClick={() => navigate(ROUTES.SUGGESTIONS)}
                  sx={{ borderColor: '#242830', color: '#E5E7EB' }}
                >
                  View Suggestions
                </Button>
              </Box>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Box>
  );
};
