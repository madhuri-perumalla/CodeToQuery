import React, { useState } from 'react';
import { Box, useTheme, useMediaQuery, Tab, Tabs, Paper, Grid, Typography, Chip } from '@mui/material';
import { PageHeader, StatCard, HealthScoreCard, RecommendationCard, SeverityBadge } from '@/shared/components/ui';
import { LoadingSkeleton, ErrorState, EmptyState } from '@/shared/components/loading';
import { useQueryById, useDiagnostics } from '@/lib/react-query';
import { useParams } from 'react-router-dom';
import { Code, Speed, Lightbulb, History, LocationOn, AttachMoney } from '@mui/icons-material';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { vscDarkPlus } from 'react-syntax-highlighter/dist/esm/styles/prism';
import { PerformanceChart } from '@/shared/components/charts';

interface TabPanelProps {
  children?: React.ReactNode;
  index: number;
  value: number;
}

const TabPanel: React.FC<TabPanelProps> = ({ children, value, index }) => {
  return (
    <div role="tabpanel" hidden={value !== index}>
      {value === index && <Box sx={{ py: 3 }}>{children}</Box>}
    </div>
  );
};

export const QueryDetail: React.FC = () => {
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('sm'));
  const { id } = useParams<{ id: string }>();
  const [tabValue, setTabValue] = useState(0);

  const { data: query, isLoading, error, refetch } = useQueryById(id || '');
  const { data: diagnostics } = useDiagnostics(id || '');

  const handleTabChange = (_event: React.SyntheticEvent, newValue: number) => {
    setTabValue(newValue);
  };

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
          title="Failed to load query details"
          message="Unable to fetch query data. Please try again."
          onRetry={() => refetch()}
        />
      </Box>
    );
  }

  const queryData = query;
  const diagnosticList = diagnostics?.diagnostics || [];

  if (!queryData) {
    return (
      <Box sx={{ p: isMobile ? 2 : 3, bgcolor: '#0F1115', minHeight: '100vh' }}>
        <PageHeader
          title="Query Details"
          subtitle="View detailed information about this query"
          onRefresh={() => refetch()}
        />
        <EmptyState
          variant="no-results"
          title="Query not found"
          message="The requested query could not be found or may have been deleted."
          actionLabel="Go to Query Inventory"
          onAction={() => window.location.href = '/queries'}
        />
      </Box>
    );
  }

  return (
    <Box sx={{ p: isMobile ? 2 : 3, bgcolor: '#0F1115', minHeight: '100vh' }}>
      {/* Page Header */}
      <PageHeader
        title={queryData?.name || 'Query Details'}
        subtitle="View detailed information about this query"
        action={
          <Chip
            label={queryData?.status || 'analyzing'}
            size="small"
            sx={{ bgcolor: 'rgba(63, 81, 181, 0.1)', color: '#3F51B5' }}
          />
        }
        breadcrumbs={[
          { label: 'Dashboard', path: '/' },
          { label: 'Query Inventory', path: '/queries' },
          { label: queryData?.name || 'Query', path: `/queries/${id}` },
        ]}
      />

      {/* Tabs */}
      <Paper
        sx={{
          bgcolor: '#1A1D23',
          border: '1px solid #242830',
          borderRadius: 2,
          mb: 3,
        }}
      >
        <Tabs
          value={tabValue}
          onChange={handleTabChange}
          sx={{
            borderBottom: '1px solid #242830',
            '& .MuiTab-root': {
              color: '#B0B3B8',
              textTransform: 'none',
              fontWeight: 500,
              minWidth: isMobile ? 80 : 120,
            },
            '& .Mui-selected': {
              color: '#3F51B5',
            },
            '& .MuiTabs-indicator': {
              backgroundColor: '#3F51B5',
            },
          }}
        >
          <Tab label="Overview" icon={<Code fontSize="small" />} iconPosition="start" />
          <Tab label="SQL Viewer" icon={<Code fontSize="small" />} iconPosition="start" />
          <Tab label="Performance" icon={<Speed fontSize="small" />} iconPosition="start" />
          <Tab label="Recommendations" icon={<Lightbulb fontSize="small" />} iconPosition="start" />
        </Tabs>
      </Paper>

      {/* Overview Tab */}
      <TabPanel value={tabValue} index={0}>
        <Grid container spacing={2}>
          {/* Query Info */}
          <Grid item xs={12} lg={8}>
            <Paper
              sx={{
                bgcolor: '#1A1D23',
                border: '1px solid #242830',
                borderRadius: 2,
                p: 2,
                mb: 2,
              }}
            >
              <Typography variant="h6" sx={{ color: '#FFFFFF', fontWeight: 600, mb: 2 }}>
                Query Information
              </Typography>
              <Grid container spacing={2}>
                <Grid item xs={12} sm={6}>
                  <Box sx={{ mb: 2 }}>
                    <Typography variant="caption" sx={{ color: '#6B7280', fontSize: '0.75rem' }}>
                      Query Hash
                    </Typography>
                    <Typography variant="body2" sx={{ color: '#B0B3B8', fontFamily: 'monospace', wordBreak: 'break-all' }}>
                      {queryData?.queryHash || '-'}
                    </Typography>
                  </Box>
                </Grid>
                <Grid item xs={12} sm={6}>
                  <Box sx={{ mb: 2 }}>
                    <Typography variant="caption" sx={{ color: '#6B7280', fontSize: '0.75rem' }}>
                      Dialect
                    </Typography>
                    <Typography variant="body2" sx={{ color: '#B0B3B8' }}>
                      {queryData?.dialect || '-'}
                    </Typography>
                  </Box>
                </Grid>
                <Grid item xs={12} sm={6}>
                  <Box sx={{ mb: 2 }}>
                    <Typography variant="caption" sx={{ color: '#6B7280', fontSize: '0.75rem' }}>
                      Type
                    </Typography>
                    <Chip label={queryData?.type || 'SELECT'} size="small" sx={{ bgcolor: 'rgba(63, 81, 181, 0.1)', color: '#3F51B5' }} />
                  </Box>
                </Grid>
                <Grid item xs={12} sm={6}>
                  <Box sx={{ mb: 2 }}>
                    <Typography variant="caption" sx={{ color: '#6B7280', fontSize: '0.75rem' }}>
                      Tables
                    </Typography>
                    <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5 }}>
                      {queryData?.tables?.map((table: string, index: number) => (
                        <Chip key={index} label={table} size="small" sx={{ bgcolor: '#242830', color: '#B0B3B8' }} />
                      ))}
                    </Box>
                  </Box>
                </Grid>
                <Grid item xs={12} sm={6}>
                  <Box sx={{ mb: 2 }}>
                    <Typography variant="caption" sx={{ color: '#6B7280', fontSize: '0.75rem' }}>
                      Created At
                    </Typography>
                    <Typography variant="body2" sx={{ color: '#B0B3B8' }}>
                      {queryData?.createdAt ? new Date(queryData.createdAt).toLocaleString() : '-'}
                    </Typography>
                  </Box>
                </Grid>
                <Grid item xs={12} sm={6}>
                  <Box sx={{ mb: 2 }}>
                    <Typography variant="caption" sx={{ color: '#6B7280', fontSize: '0.75rem' }}>
                      Last Updated
                    </Typography>
                    <Typography variant="body2" sx={{ color: '#B0B3B8' }}>
                      {queryData?.updatedAt ? new Date(queryData.updatedAt).toLocaleString() : '-'}
                    </Typography>
                  </Box>
                </Grid>
              </Grid>
            </Paper>

            {/* Locations */}
            <Paper
              sx={{
                bgcolor: '#1A1D23',
                border: '1px solid #242830',
                borderRadius: 2,
                p: 2,
              }}
            >
              <Typography variant="h6" sx={{ color: '#FFFFFF', fontWeight: 600, mb: 2 }}>
                <LocationOn fontSize="small" sx={{ mr: 1, verticalAlign: 'middle' }} />
                Code Locations
              </Typography>
              {queryData?.locations?.map((location: unknown, index: number) => (
                <Box
                  key={index}
                  sx={{
                    bgcolor: '#242830',
                    borderRadius: 1,
                    p: 1.5,
                    mb: 1,
                    border: '1px solid #3D4450',
                  }}
                >
                  <Typography variant="body2" sx={{ color: '#FFFFFF', fontWeight: 500, mb: 0.5 }}>
                    {(location as any).filePath}
                  </Typography>
                  <Box sx={{ display: 'flex', gap: 2, alignItems: 'center' }}>
                    <Typography variant="caption" sx={{ color: '#B0B3B8' }}>
                      Line {(location as any).lineNumber}, Column {(location as any).column}
                    </Typography>
                    <Typography variant="caption" sx={{ color: '#6B7280' }}>
                      Function: {(location as any).function}
                    </Typography>
                  </Box>
                </Box>
              ))}
            </Paper>
          </Grid>

          {/* Metrics */}
          <Grid item xs={12} lg={4}>
            <Grid container spacing={2}>
              <Grid item xs={6} lg={12}>
                <StatCard
                  title="Cost"
                  value={queryData?.cost || 0}
                  icon={<AttachMoney />}
                  color="warning"
                />
              </Grid>
              <Grid item xs={6} lg={12}>
                <StatCard
                  title="Execution Time"
                  value={queryData?.executionTime || 0}
                  icon={<Speed />}
                  color="info"
                />
              </Grid>
              <Grid item xs={12}>
                <HealthScoreCard
                  score={queryData?.healthScore || 75}
                  label="Query Health"
                  description="Based on performance, cost, and optimization potential"
                />
              </Grid>
              <Grid item xs={12}>
                <Paper
                  sx={{
                    bgcolor: '#1A1D23',
                    border: '1px solid #242830',
                    borderRadius: 2,
                    p: 2,
                  }}
                >
                  <Typography variant="h6" sx={{ color: '#FFFFFF', fontWeight: 600, mb: 2 }}>
                    <History fontSize="small" sx={{ mr: 1, verticalAlign: 'middle' }} />
                    Diagnostics
                  </Typography>
                  {diagnosticList.length === 0 ? (
                    <Typography variant="body2" sx={{ color: '#6B7280' }}>
                      No diagnostics available
                    </Typography>
                  ) : (
                    diagnosticList.slice(0, 5).map((diag: unknown, index: number) => (
                      <Box key={index} sx={{ mb: 2 }}>
                        <SeverityBadge severity={(diag as any).severity} size="small" />
                        <Typography variant="body2" sx={{ color: '#B0B3B8', ml: 1, mt: 0.5 }}>
                          {(diag as any).message}
                        </Typography>
                      </Box>
                    ))
                  )}
                </Paper>
              </Grid>
            </Grid>
          </Grid>
        </Grid>
      </TabPanel>

      {/* SQL Viewer Tab */}
      <TabPanel value={tabValue} index={1}>
        <Paper
          sx={{
            bgcolor: '#1A1D23',
            border: '1px solid #242830',
            borderRadius: 2,
            overflow: 'hidden',
          }}
        >
          <Box sx={{ p: 2, borderBottom: '1px solid #242830' }}>
            <Typography variant="h6" sx={{ color: '#FFFFFF', fontWeight: 600 }}>
              SQL Query
            </Typography>
          </Box>
          <Box sx={{ p: 2, maxHeight: 600, overflow: 'auto' }}>
            <SyntaxHighlighter
              language="sql"
              style={vscDarkPlus}
              customStyle={{
                backgroundColor: '#0F1115',
                borderRadius: 1,
                fontSize: isMobile ? '0.75rem' : '0.875rem',
                lineHeight: 1.6,
              }}
              showLineNumbers
              wrapLines
            >
              {queryData?.normalizedSql || queryData?.rawSql || queryData?.normalized_sql || queryData?.raw_sql || '-- No SQL available'}
            </SyntaxHighlighter>
          </Box>
        </Paper>
      </TabPanel>

      {/* Performance Tab */}
      <TabPanel value={tabValue} index={2}>
        <Grid container spacing={2}>
          <Grid item xs={12}>
            <Paper
              sx={{
                bgcolor: '#1A1D23',
                border: '1px solid #242830',
                borderRadius: 2,
                p: 2,
              }}
            >
              <Typography variant="h6" sx={{ color: '#FFFFFF', fontWeight: 600, mb: 2 }}>
                Performance Metrics
              </Typography>
              <PerformanceChart data={[]} />
            </Paper>
          </Grid>
          <Grid item xs={12}>
            <Paper
              sx={{
                bgcolor: '#1A1D23',
                border: '1px solid #242830',
                borderRadius: 2,
                p: 2,
              }}
            >
              <Typography variant="h6" sx={{ color: '#FFFFFF', fontWeight: 600, mb: 2 }}>
                Execution Plan
              </Typography>
              <Box sx={{ bgcolor: '#0F1115', borderRadius: 1, p: 2, fontFamily: 'monospace', fontSize: '0.875rem', color: '#B0B3B8' }}>
                {queryData?.executionPlan ? (
                  <pre>{JSON.stringify(queryData.executionPlan.planJson, null, 2)}</pre>
                ) : (
                  <Typography variant="body2" sx={{ color: '#6B7280' }}>
                    No execution plan available
                  </Typography>
                )}
              </Box>
            </Paper>
          </Grid>
        </Grid>
      </TabPanel>

      {/* Recommendations Tab */}
      <TabPanel value={tabValue} index={3}>
        <Grid container spacing={2}>
          {diagnosticList.length === 0 ? (
            <Grid item xs={12}>
              <Paper
                sx={{
                  bgcolor: '#1A1D23',
                  border: '1px solid #242830',
                  borderRadius: 2,
                  p: 4,
                  textAlign: 'center',
                }}
              >
                <Lightbulb sx={{ fontSize: 48, color: '#3F51B5', mb: 2 }} />
                <Typography variant="h6" sx={{ color: '#FFFFFF', fontWeight: 600, mb: 1 }}>
                  No Recommendations
                </Typography>
                <Typography variant="body2" sx={{ color: '#B0B3B8' }}>
                  This query is performing well. No optimizations needed at this time.
                </Typography>
              </Paper>
            </Grid>
          ) : (
            diagnosticList.map((diag: unknown, index: number) => (
              <Grid item xs={12} md={6} key={index}>
                <RecommendationCard
                  title={(diag as any).message}
                  description={(diag as any).description}
                  impact={(diag as any).impact || 'Medium impact on performance'}
                  type={(diag as any).suggestions?.[0]?.type || 'optimization'}
                  severity={(diag as any).severity}
                  estimatedImprovement={(diag as any).suggestions?.[0]?.estimatedImprovement ? `~${(diag as any).suggestions[0].estimatedImprovement}% improvement` : undefined}
                  onApply={() => console.log('Apply recommendation:', (diag as any).id)}
                  onDismiss={() => console.log('Dismiss recommendation:', (diag as any).id)}
                />
              </Grid>
            ))
          )}
        </Grid>
      </TabPanel>
    </Box>
  );
};
