import React from 'react';
import { useParams } from 'react-router-dom';
import {
  Box,
  useTheme,
  useMediaQuery,
  Grid,
  Typography,
  Paper,
} from '@mui/material';
import { PageHeader, StatCard } from '@/shared/components/ui';
import { LoadingSkeleton, ErrorState, EmptyState } from '@/shared/components/loading';
import { Pie } from 'react-chartjs-2';
import { Chart as ChartJS, ArcElement, Tooltip, Legend } from 'chart.js';

ChartJS.register(ArcElement, Tooltip, Legend);
import {
  Search,
  Warning,
  TrendingUp,
  AttachMoney,
  Assessment,
  CheckCircle,
} from '@mui/icons-material';
import { useSummary } from '@/lib/react-query';

export const ProjectSummary: React.FC = () => {
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('sm'));
  const { projectId } = useParams<{ projectId: string }>();

  const { data: summaryData, isLoading, error, refetch } = useSummary(projectId);
  
  if (isLoading) {
    return (
      <Box sx={{ p: 3 }}>
        <LoadingSkeleton variant="card" count={4} />
      </Box>
    );
  }

  if (error) {
    return (
      <Box sx={{ p: 3 }}>
        <ErrorState
          title="Failed to load project summary"
          message="Unable to fetch summary data. Please try again."
          onRetry={() => refetch()}
        />
      </Box>
    );
  }

  if (!summaryData) {
    return (
      <Box sx={{ p: 3 }}>
        <EmptyState
          variant="no-results"
          title="No summary data available"
          message="Project summary data is not available at this time."
        />
      </Box>
    );
  }

  const summaryMetrics = {
    totalQueries: summaryData.totalQueries || 0,
    criticalIssues: summaryData.criticalIssues || 0,
    highIssues: summaryData.highIssues || 0,
    mediumIssues: summaryData.mediumIssues || 0,
    avgQueryCost: summaryData.avgQueryCost || 0,
  };

  // Generate chart data from actual summary data - only use real data
  const issueDistributionData = {
    labels: ['Critical', 'High', 'Medium'],
    datasets: [
      {
        data: [
          summaryData.criticalIssues || 0,
          summaryData.highIssues || 0,
          summaryData.mediumIssues || 0,
        ],
        backgroundColor: [
          'rgba(239, 68, 68, 0.8)',
          'rgba(245, 158, 11, 0.8)',
          'rgba(63, 81, 181, 0.8)',
        ],
        borderColor: [
          '#EF4444',
          '#F59E0B',
          '#3F51B5',
        ],
        borderWidth: 2,
      },
    ],
  };

  const recentAnalyses = (summaryData.recentAnalyses || []).slice(0, 4).map((analysis: unknown) => ({
    title: `Analysis completed - ${(analysis as any).queryCount} queries analyzed`,
    date: (analysis as any).completedAt ? new Date((analysis as any).completedAt).toLocaleString() : 'Recently',
    icon: <Assessment />,
  }));

  return (
    <Box sx={{ p: isMobile ? 2 : 3, bgcolor: '#0F1115', minHeight: '100vh' }}>
      {/* Page Header */}
      <PageHeader
        title="Project Summary"
        subtitle="Overview of query optimization progress and impact"
      />

      {/* Summary Metrics */}
      <Grid container spacing={2} sx={{ mb: 3 }}>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Total Queries"
            value={summaryMetrics.totalQueries}
            subtitle="SQL queries extracted"
            icon={<Search />}
            color="primary"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Critical Issues"
            value={summaryMetrics.criticalIssues}
            subtitle="High severity risks"
            icon={<Warning />}
            color="error"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="High Issues"
            value={summaryMetrics.highIssues}
            subtitle="Performance warnings"
            icon={<TrendingUp />}
            color="warning"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Avg Query Cost"
            value={summaryMetrics.avgQueryCost.toFixed(2)}
            subtitle="Average execution cost"
            icon={<AttachMoney />}
            color="info"
          />
        </Grid>
      </Grid>

      {/* Issue Distribution Chart */}
      <Grid container spacing={2} sx={{ mb: 3 }}>
        <Grid item xs={12} md={6}>
          <Paper
            sx={{
              bgcolor: '#1A1D23',
              border: '1px solid #242830',
              borderRadius: 2,
              p: 2,
            }}
          >
            <Typography variant="h6" sx={{ color: '#FFFFFF', fontWeight: 600, mb: 2 }}>
              Issue Distribution
            </Typography>
            <Box sx={{ height: 300 }}>
              <Pie data={issueDistributionData} options={{ responsive: true, maintainAspectRatio: false, plugins: { legend: { position: 'bottom', labels: { color: '#E5E7EB' } } } }} />
            </Box>
          </Paper>
        </Grid>

        {/* Recent Analyses */}
        <Grid item xs={12} md={6}>
          <Paper
            sx={{
              bgcolor: '#1A1D23',
              border: '1px solid #242830',
              borderRadius: 2,
              p: 2,
            }}
          >
            <Typography variant="h6" sx={{ color: '#FFFFFF', fontWeight: 600, mb: 2 }}>
              Recent Analyses
            </Typography>
            {recentAnalyses.length > 0 ? (
              recentAnalyses.map((achievement, index) => (
                <Box
                  key={index}
                  sx={{
                    display: 'flex',
                    alignItems: 'center',
                    gap: 2,
                    p: 1.5,
                    bgcolor: '#242830',
                    borderRadius: 1,
                    mb: index < recentAnalyses.length - 1 ? 1.5 : 0,
                    border: '1px solid #3D4450',
                  }}
                >
                  <Box
                    sx={{
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      width: 40,
                      height: 40,
                      borderRadius: 1,
                      bgcolor: 'rgba(16, 185, 129, 0.1)',
                      color: '#10B981',
                    }}
                  >
                    {achievement.icon}
                  </Box>
                  <Box sx={{ flex: 1 }}>
                    <Typography variant="body2" sx={{ color: '#FFFFFF', fontWeight: 600 }}>
                      {achievement.title}
                    </Typography>
                    <Typography variant="caption" sx={{ color: '#B0B3B8' }}>
                      {achievement.date}
                    </Typography>
                  </Box>
                  <CheckCircle sx={{ color: '#10B981', fontSize: 20 }} />
                </Box>
              ))
            ) : (
              <Typography variant="body2" sx={{ color: '#6B7280' }}>
                No recent analyses available
              </Typography>
            )}
          </Paper>
        </Grid>
      </Grid>


    </Box>
  );
};
