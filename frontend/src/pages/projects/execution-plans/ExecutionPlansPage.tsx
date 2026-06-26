import React from 'react';
import { Box, Card, CardContent, Typography, Chip, Accordion, AccordionSummary, AccordionDetails, Grid } from '@mui/material';
import { ExpandMore } from '@mui/icons-material';
import { useExecutionPlans } from '@/lib/react-query';
import { LoadingSkeleton, ErrorState, EmptyState } from '@/shared/components/loading';
import { useParams } from 'react-router-dom';

export const ExecutionPlansPage: React.FC = () => {
  const { projectId } = useParams<{ projectId: string }>();
  const codebaseId = projectId ? parseInt(projectId) : undefined;
  const { data, isLoading, error, refetch } = useExecutionPlans({ page: 1, page_size: 50, codebase_id: codebaseId });

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
          title="Failed to load execution plans"
          message="Unable to fetch execution plan data. Please try again."
          onRetry={() => refetch()}
        />
      </Box>
    );
  }

  const plans = data?.items || [];

  if (!plans || plans.length === 0) {
    return (
      <Box sx={{ p: 3 }}>
        <EmptyState
          variant="no-data"
          title="No execution plans found"
          message="No execution plans have been generated yet for this project. Run analysis to populate execution plans."
          actionLabel="Run Analysis"
          onAction={() => window.location.href = `/projects/${projectId}/overview`}
        />
      </Box>
    );
  }

  return (
    <Box sx={{ mt: 2 }}>
      {plans.map((plan: any) => (
        <Card key={plan.id} sx={{ bgcolor: '#1A1D23', border: '1px solid #242830', borderRadius: 2, mb: 2 }}>
          <CardContent sx={{ p: 2 }}>
            <Typography variant="h6" sx={{ color: '#FFFFFF', mb: 2 }}>
              Plan #{plan.id}
            </Typography>

            <Grid container spacing={2} sx={{ mb: 2 }}>
              <Grid item xs={12} sm={6} md={3}>
                <Box sx={{ p: 2, bgcolor: '#14171C', borderRadius: 1 }}>
                  <Typography variant="caption" sx={{ color: '#6B7280', display: 'block', mb: 0.5 }}>
                    Startup Cost
                  </Typography>
                  <Typography variant="body2" sx={{ color: '#E5E7EB', fontWeight: 600 }}>
                    {plan.startupCost ? plan.startupCost.toFixed(2) : 'N/A'}
                  </Typography>
                </Box>
              </Grid>
              <Grid item xs={12} sm={6} md={3}>
                <Box sx={{ p: 2, bgcolor: '#14171C', borderRadius: 1 }}>
                  <Typography variant="caption" sx={{ color: '#6B7280', display: 'block', mb: 0.5 }}>
                    Total Cost
                  </Typography>
                  <Typography variant="body2" sx={{ color: '#E5E7EB', fontWeight: 600 }}>
                    {plan.totalCost ? plan.totalCost.toFixed(2) : 'N/A'}
                  </Typography>
                </Box>
              </Grid>
              <Grid item xs={12} sm={6} md={3}>
                <Box sx={{ p: 2, bgcolor: '#14171C', borderRadius: 1 }}>
                  <Typography variant="caption" sx={{ color: '#6B7280', display: 'block', mb: 0.5 }}>
                    Estimated Rows
                  </Typography>
                  <Typography variant="body2" sx={{ color: '#E5E7EB', fontWeight: 600 }}>
                    {plan.totalRows || 'N/A'}
                  </Typography>
                </Box>
              </Grid>
              <Grid item xs={12} sm={6} md={3}>
                <Box sx={{ p: 2, bgcolor: '#14171C', borderRadius: 1 }}>
                  <Typography variant="caption" sx={{ color: '#6B7280', display: 'block', mb: 0.5 }}>
                    Plan Width
                  </Typography>
                  <Typography variant="body2" sx={{ color: '#E5E7EB', fontWeight: 600 }}>
                    {plan.planWidth || 'N/A'}
                  </Typography>
                </Box>
              </Grid>
            </Grid>

            <Accordion sx={{ bgcolor: '#14171C', border: '1px solid #242830', borderRadius: 1 }}>
              <AccordionSummary expandIcon={<ExpandMore sx={{ color: '#B0B3B8' }} />} sx={{ minHeight: 48 }}>
                <Typography variant="body2" sx={{ color: '#B0B3B8' }}>
                  View Plan Details
                </Typography>
              </AccordionSummary>
              <AccordionDetails sx={{ bgcolor: '#14171C' }}>
                <Box sx={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: 2 }}>
                  <Box>
                    <Typography variant="caption" sx={{ color: '#6B7280', display: 'block', mb: 0.5 }}>
                      Scan Type
                    </Typography>
                    <Chip
                      label={plan.scanType || 'UNKNOWN'}
                      size="small"
                      sx={{ bgcolor: '#242830', color: '#B0B3B8' }}
                    />
                  </Box>
                  <Box>
                    <Typography variant="caption" sx={{ color: '#6B7280', display: 'block', mb: 0.5 }}>
                      Join Strategy
                    </Typography>
                    <Chip
                      label={plan.joinStrategy || 'NONE'}
                      size="small"
                      sx={{ bgcolor: '#242830', color: '#B0B3B8' }}
                    />
                  </Box>
                  <Box>
                    <Typography variant="caption" sx={{ color: '#6B7280', display: 'block', mb: 0.5 }}>
                      Query ID
                    </Typography>
                    <Typography variant="body2" sx={{ color: '#E5E7EB' }}>
                      {plan.queryId || 'N/A'}
                    </Typography>
                  </Box>
                  <Box>
                    <Typography variant="caption" sx={{ color: '#6B7280', display: 'block', mb: 0.5 }}>
                      Execution Time
                    </Typography>
                    <Typography variant="body2" sx={{ color: '#E5E7EB' }}>
                      {plan.executionTimeMs ? `${plan.executionTimeMs.toFixed(2)} ms` : 'N/A'}
                    </Typography>
                  </Box>
                  {plan.analyzedAt && (
                    <Box>
                      <Typography variant="caption" sx={{ color: '#6B7280', display: 'block', mb: 0.5 }}>
                        Analyzed At
                      </Typography>
                      <Typography variant="body2" sx={{ color: '#E5E7EB' }}>
                        {new Date(plan.analyzedAt).toLocaleString()}
                      </Typography>
                    </Box>
                  )}
                </Box>

                {plan.planJson && (
                  <Box sx={{ mt: 2 }}>
                    <Typography variant="caption" sx={{ color: '#6B7280', display: 'block', mb: 0.5 }}>
                      Execution Plan JSON
                    </Typography>
                    <Typography variant="body2" sx={{ color: '#E5E7EB', fontFamily: 'monospace', fontSize: '0.75rem', wordBreak: 'break-all' }}>
                      {JSON.stringify(plan.planJson, null, 2)}
                    </Typography>
                  </Box>
                )}
              </AccordionDetails>
            </Accordion>
          </CardContent>
        </Card>
      ))}
    </Box>
  );
};
