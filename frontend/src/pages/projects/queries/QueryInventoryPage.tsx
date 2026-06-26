import React from 'react';
import { useParams } from 'react-router-dom';
import { Box, Typography, Grid, Card, CardContent } from '@mui/material';
import { useQueries } from '@/lib/react-query/queryHooks';
import { LoadingSkeleton, ErrorState, EmptyState } from '@/shared/components/loading';
import { PageHeader } from '@/shared/components/ui';

export const QueryInventoryPage: React.FC = () => {
  const { projectId } = useParams<{ projectId: string }>();
  const { data, isLoading, error, refetch } = useQueries({ codebase_id: projectId });

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
          title="Failed to load queries"
          message="Unable to fetch query data. Please try again."
          onRetry={() => refetch()}
        />
      </Box>
    );
  }

  const queries = data?.queries || [];

  if (queries.length === 0) {
    return (
      <Box sx={{ p: 3 }}>
        <PageHeader
          title="Query Inventory"
          subtitle="View all extracted SQL queries"
          onRefresh={() => refetch()}
        />
        <EmptyState
          variant="no-data"
          title="No queries found"
          message="Scan a codebase to extract SQL queries."
          actionLabel="Refresh"
          onAction={() => refetch()}
        />
      </Box>
    );
  }

  return (
    <Box sx={{ p: 3 }}>
      <PageHeader
        title="Query Inventory"
        subtitle="View all extracted SQL queries"
        onRefresh={() => refetch()}
      />

      <Grid container spacing={2}>
        {queries.map((query: any) => (
          <Grid item xs={12} key={query.id}>
            <Card sx={{ bgcolor: '#1A1D23', border: '1px solid #242830' }}>
              <CardContent>
                <Typography variant="h6" sx={{ color: '#FFFFFF', mb: 1 }}>
                  Query #{query.id}
                </Typography>
                <Typography variant="body2" sx={{ color: '#9CA3AF', mb: 2 }}>
                  {query.normalized_sql?.substring(0, 100)}...
                </Typography>
                <Box sx={{ display: 'flex', gap: 2, flexWrap: 'wrap' }}>
                  <Typography variant="caption" sx={{ color: '#6B7280' }}>
                    Type: {query.query_type}
                  </Typography>
                  <Typography variant="caption" sx={{ color: '#6B7280' }}>
                    Cost: {query.cost}
                  </Typography>
                  <Typography variant="caption" sx={{ color: '#6B7280' }}>
                    Status: {query.status}
                  </Typography>
                </Box>
              </CardContent>
            </Card>
          </Grid>
        ))}
      </Grid>
    </Box>
  );
};
