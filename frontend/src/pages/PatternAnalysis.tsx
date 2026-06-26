import React from 'react';
import { useParams } from 'react-router-dom';
import {
  Box,
  useTheme,
  useMediaQuery,
  Grid,
  Typography,
  Paper,
  Card,
  CardContent,
  Chip,
  Select,
  MenuItem,
  FormControl,
  SelectChangeEvent,
} from '@mui/material';
import { PageHeader, StatCard } from '@/shared/components/ui';
import { LoadingSkeleton, ErrorState, EmptyState } from '@/shared/components/loading';
import { PatternFrequencyChart, QueryClustersChart, RiskDistributionChart, OptimizationOpportunitiesChart } from '@/shared/components/charts';
import { TrendingUp, Category, Warning, Lightbulb, Assessment } from '@mui/icons-material';
import { usePatterns } from '@/lib/react-query';

export const PatternAnalysis: React.FC = () => {
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('sm'));
  const { projectId } = useParams<{ projectId: string }>();
  const codebaseId = projectId ? parseInt(projectId) : undefined;
  
  const [timeRange, setTimeRange] = React.useState('7d');

  const { data, isLoading, error, refetch } = usePatterns(codebaseId ? String(codebaseId) : undefined);
  
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
          title="Failed to load pattern analysis"
          message="Unable to fetch pattern data. Please try again."
          onRetry={() => refetch()}
        />
      </Box>
    );
  }

  const patterns = data?.patterns || [];
  const totalPatterns = data?.total || 0;

  if (patterns.length === 0) {
    return (
      <Box sx={{ p: 3 }}>
        <EmptyState
          title="No patterns found"
          message="No query patterns have been grouped yet for this project. Run analysis to populate query groups."
          actionLabel="Run Analysis"
          onAction={() => window.location.href = `/projects/${projectId}/overview`}
        />
      </Box>
    );
  }

  // Calculate summary metrics from API data
  const summaryMetrics = {
    totalPatterns: totalPatterns,
    uniquePatterns: patterns.length,
    highRiskQueries: patterns.filter((p: any) => p.riskLevel === 'high').length,
    optimizationPotential: patterns.reduce((sum: number, p: any) => sum + (p.optimizationPotential || 0), 0),
  };

  // Generate chart data from API data
  const patternFrequencyData = {
    labels: patterns.slice(0, 8).map((p: any) => p.name || 'Unknown'),
    datasets: [{
      label: 'Query Count',
      data: patterns.slice(0, 8).map((p: any) => p.queryCount || 0),
      backgroundColor: patterns.slice(0, 8).map(() => 'rgba(63, 81, 181, 0.6)'),
      borderColor: patterns.slice(0, 8).map(() => 'rgba(63, 81, 181, 1)'),
      borderWidth: 1,
    }],
  };

  const queryClustersData = {
    labels: patterns.map((p: any) => p.name || 'Unknown'),
    datasets: [{
      label: 'Query Count',
      data: patterns.map((p: any) => p.queryCount || 0),
      backgroundColor: 'rgba(63, 81, 181, 0.6)',
      borderColor: 'rgba(63, 81, 181, 1)',
      borderWidth: 1,
    }],
  };

  const riskDistributionData = {
    labels: ['Low', 'Medium', 'High', 'Critical'],
    datasets: [{
      label: 'Count',
      data: [
        patterns.filter((p: any) => p.riskLevel === 'low').length,
        patterns.filter((p: any) => p.riskLevel === 'medium').length,
        patterns.filter((p: any) => p.riskLevel === 'high').length,
        patterns.filter((p: any) => p.riskLevel === 'critical').length,
      ],
      backgroundColor: ['rgba(16, 185, 129, 0.6)', 'rgba(245, 158, 11, 0.6)', 'rgba(239, 68, 68, 0.6)', 'rgba(127, 29, 29, 0.6)'],
      borderColor: ['rgba(16, 185, 129, 1)', 'rgba(245, 158, 11, 1)', 'rgba(239, 68, 68, 1)', 'rgba(127, 29, 29, 1)'],
      borderWidth: 1,
    }],
  };

  const optimizationOpportunitiesData = {
    labels: patterns
      .filter((p: any) => p.optimizationPotential > 0)
      .slice(0, 5)
      .map((p: any) => p.name || 'Unknown'),
    datasets: [{
      label: 'Potential Savings',
      data: patterns
        .filter((p: any) => p.optimizationPotential > 0)
        .slice(0, 5)
        .map((p: any) => p.optimizationPotential || 0),
      backgroundColor: 'rgba(16, 185, 129, 0.6)',
      borderColor: 'rgba(16, 185, 129, 1)',
      borderWidth: 1,
    }],
  };

  return (
    <Box sx={{ p: isMobile ? 2 : 3, bgcolor: '#0F1115', minHeight: '100vh' }}>
      {/* Page Header */}
      <PageHeader
        title="Pattern Analysis"
        subtitle="Analyze query patterns and identify optimization opportunities"
      />

      {/* Filter Bar */}
      <Paper
        sx={{
          mb: 3,
          p: 2,
          bgcolor: '#1A1D23',
          border: '1px solid #242830',
          borderRadius: 2,
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          flexWrap: 'wrap',
          gap: 2,
        }}
      >
        <Typography variant="body2" sx={{ color: '#B0B3B8' }}>
          Time Range:
        </Typography>
        <FormControl size="small" sx={{ minWidth: 150 }}>
          <Select
            value={timeRange}
            onChange={(e: SelectChangeEvent<string>) => setTimeRange(e.target.value as string)}
            sx={{
              color: '#FFFFFF',
              bgcolor: '#242830',
              '& .MuiSelect-icon': { color: '#B0B3B8' },
            }}
          >
            <MenuItem value="1d">Last 24 Hours</MenuItem>
            <MenuItem value="7d">Last 7 Days</MenuItem>
            <MenuItem value="30d">Last 30 Days</MenuItem>
            <MenuItem value="90d">Last 90 Days</MenuItem>
          </Select>
        </FormControl>
      </Paper>

      {/* Summary Metrics */}
      <Grid container spacing={2} sx={{ mb: 3 }}>
        <Grid item xs={6} sm={3}>
          <StatCard
            title="Total Patterns"
            value={summaryMetrics.totalPatterns}
            icon={<Category />}
            color="info"
          />
        </Grid>
        <Grid item xs={6} sm={3}>
          <StatCard
            title="Unique Patterns"
            value={summaryMetrics.uniquePatterns}
            icon={<Assessment />}
            color="primary"
          />
        </Grid>
        <Grid item xs={6} sm={3}>
          <StatCard
            title="High Risk Queries"
            value={summaryMetrics.highRiskQueries}
            icon={<Warning />}
            color="error"
          />
        </Grid>
        <Grid item xs={6} sm={3}>
          <StatCard
            title="Optimization Potential"
            value={summaryMetrics.optimizationPotential}
            icon={<Lightbulb />}
            color="success"
          />
        </Grid>
      </Grid>

      {/* Charts Grid */}
      <Grid container spacing={2}>
        {/* Pattern Frequency Chart */}
        <Grid item xs={12} lg={6}>
          <Paper
            sx={{
              bgcolor: '#1A1D23',
              border: '1px solid #242830',
              borderRadius: 2,
              p: 2,
              height: '100%',
            }}
          >
            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
              <Typography variant="h6" sx={{ color: '#FFFFFF', fontWeight: 600 }}>
                <TrendingUp sx={{ mr: 1, verticalAlign: 'middle', fontSize: 20 }} />
                Pattern Frequency
              </Typography>
              <Chip label="Top 8" size="small" sx={{ bgcolor: 'rgba(63, 81, 181, 0.1)', color: '#3F51B5' }} />
            </Box>
            <Box sx={{ height: isMobile ? 250 : 300 }}>
              <PatternFrequencyChart data={patternFrequencyData} />
            </Box>
          </Paper>
        </Grid>

        {/* Query Clusters Chart */}
        <Grid item xs={12} lg={6}>
          <Paper
            sx={{
              bgcolor: '#1A1D23',
              border: '1px solid #242830',
              borderRadius: 2,
              p: 2,
              height: '100%',
            }}
          >
            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
              <Typography variant="h6" sx={{ color: '#FFFFFF', fontWeight: 600 }}>
                <Category sx={{ mr: 1, verticalAlign: 'middle', fontSize: 20 }} />
                Query Clusters
              </Typography>
              <Chip label={patterns.length} size="small" sx={{ bgcolor: 'rgba(139, 92, 246, 0.1)', color: '#8B5CF6' }} />
            </Box>
            <Box sx={{ height: isMobile ? 250 : 300 }}>
              <QueryClustersChart data={queryClustersData} />
            </Box>
          </Paper>
        </Grid>

        {/* Risk Distribution Chart */}
        <Grid item xs={12} lg={6}>
          <Paper
            sx={{
              bgcolor: '#1A1D23',
              border: '1px solid #242830',
              borderRadius: 2,
              p: 2,
              height: '100%',
            }}
          >
            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
              <Typography variant="h6" sx={{ color: '#FFFFFF', fontWeight: 600 }}>
                <Warning sx={{ mr: 1, verticalAlign: 'middle', fontSize: 20 }} />
                Risk Distribution
              </Typography>
              <Chip label="235 Total" size="small" sx={{ bgcolor: 'rgba(245, 158, 11, 0.1)', color: '#F59E0B' }} />
            </Box>
            <Box sx={{ height: isMobile ? 250 : 300 }}>
              <RiskDistributionChart data={riskDistributionData} />
            </Box>
          </Paper>
        </Grid>

        {/* Optimization Opportunities Chart */}
        <Grid item xs={12} lg={6}>
          <Paper
            sx={{
              bgcolor: '#1A1D23',
              border: '1px solid #242830',
              borderRadius: 2,
              p: 2,
              height: '100%',
            }}
          >
            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
              <Typography variant="h6" sx={{ color: '#FFFFFF', fontWeight: 600 }}>
                <Lightbulb sx={{ mr: 1, verticalAlign: 'middle', fontSize: 20 }} />
                Optimization Opportunities
              </Typography>
              <Chip label={`$${summaryMetrics.optimizationPotential.toFixed(0)}`} size="small" sx={{ bgcolor: 'rgba(16, 185, 129, 0.1)', color: '#10B981' }} />
            </Box>
            <Box sx={{ height: isMobile ? 250 : 300 }}>
              <OptimizationOpportunitiesChart data={optimizationOpportunitiesData} />
            </Box>
          </Paper>
        </Grid>
      </Grid>

      {/* Insights Panel */}
      <Paper
        sx={{
          mt: 3,
          bgcolor: '#1A1D23',
          border: '1px solid #242830',
          borderRadius: 2,
          p: 2,
        }}
      >
        <Typography variant="h6" sx={{ color: '#FFFFFF', fontWeight: 600, mb: 2 }}>
          Key Insights
        </Typography>
        <Grid container spacing={2}>
          <Grid item xs={12} sm={6} md={3}>
            <Card sx={{ bgcolor: '#242830', border: '1px solid #3D4450', borderRadius: 1 }}>
              <CardContent sx={{ p: 1.5 }}>
                <Typography variant="caption" sx={{ color: '#6B7280', fontSize: '0.7rem', display: 'block', mb: 0.5 }}>
                  Most Common Pattern
                </Typography>
                <Typography variant="body2" sx={{ color: '#FFFFFF', fontWeight: 600 }}>
                  SELECT queries (38%)
                </Typography>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <Card sx={{ bgcolor: '#242830', border: '1px solid #3D4450', borderRadius: 1 }}>
              <CardContent sx={{ p: 1.5 }}>
                <Typography variant="caption" sx={{ color: '#6B7280', fontSize: '0.7rem', display: 'block', mb: 0.5 }}>
                  Largest Cluster
                </Typography>
                <Typography variant="body2" sx={{ color: '#FFFFFF', fontWeight: 600 }}>
                  {patterns[0]?.name || 'N/A'} ({patterns[0]?.queryCount || 0})
                </Typography>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <Card sx={{ bgcolor: '#242830', border: '1px solid #3D4450', borderRadius: 1 }}>
              <CardContent sx={{ p: 1.5 }}>
                <Typography variant="caption" sx={{ color: '#6B7280', fontSize: '0.7rem', display: 'block', mb: 0.5 }}>
                  Highest Risk Area
                </Typography>
                <Typography variant="body2" sx={{ color: '#EF4444', fontWeight: 600 }}>
                  Critical ({summaryMetrics.highRiskQueries})
                </Typography>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <Card sx={{ bgcolor: '#242830', border: '1px solid #3D4450', borderRadius: 1 }}>
              <CardContent sx={{ p: 1.5 }}>
                <Typography variant="caption" sx={{ color: '#6B7280', fontSize: '0.7rem', display: 'block', mb: 0.5 }}>
                  Best Opportunity
                </Typography>
                <Typography variant="body2" sx={{ color: '#10B981', fontWeight: 600 }}>
                  Index Creation ($2,500)
                </Typography>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      </Paper>
    </Box>
  );
};
