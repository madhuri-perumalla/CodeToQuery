import React from 'react';
import { Box, Card, CardContent, Typography, Chip, List, ListItem, ListItemText, Grid } from '@mui/material';
import { GroupWork, Code } from '@mui/icons-material';
import { useGroups } from '@/lib/react-query';
import { LoadingSkeleton, ErrorState, EmptyState } from '@/shared/components/loading';
import { PageHeader } from '@/shared/components/ui';
import { useProjectContext } from '@/contexts/ProjectContext';

export const PatternsPage: React.FC = () => {
  const { selectedProject, selectedCodebaseId } = useProjectContext();
  const codebaseId = selectedCodebaseId;
  const { data, isLoading, error, refetch } = useGroups({ page: 1, page_size: 50, codebase_id: codebaseId || undefined });

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
          title="Failed to load query groups"
          message="Unable to fetch query group data. Please try again."
          onRetry={() => refetch()}
        />
      </Box>
    );
  }

  const groups = data?.items || [];

  if (!groups || groups.length === 0) {
    return (
      <Box sx={{ p: 3, bgcolor: '#0F1115', minHeight: '100vh' }}>
        <PageHeader
          title="Query Groups"
          subtitle={selectedProject ? `Query Groups for ${selectedProject.name}` : "AST-based query pattern grouping"}
          onRefresh={() => refetch()}
        />
        <EmptyState
          variant="no-data"
          title="No query groups found"
          message={selectedProject 
            ? "No query patterns have been grouped yet for this project. Run analysis to populate query groups."
            : "Select a project to view query groups."
          }
        />
      </Box>
    );
  }

  return (
    <Box sx={{ p: 3, bgcolor: '#0F1115', minHeight: '100vh' }}>
      <PageHeader
        title="Query Groups"
        subtitle={`Found ${data?.total || 0} AST-based query patterns`}
        onRefresh={() => refetch()}
      />

      <Box sx={{ mt: 2 }}>
        {groups.map((group: any) => (
          <Card key={group.id} sx={{ bgcolor: '#1A1D23', border: '1px solid #242830', borderRadius: 2, mb: 2 }}>
            <CardContent sx={{ p: 2 }}>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 2 }}>
                <GroupWork sx={{ color: '#8B5CF6', fontSize: 28 }} />
                <Box sx={{ flex: 1 }}>
                  <Typography variant="h6" sx={{ color: '#FFFFFF', fontWeight: 600 }}>
                    Pattern: {group.patternType || group.patternSignature || 'Unknown Pattern'}
                  </Typography>
                  <Box sx={{ display: 'flex', gap: 1, mt: 1 }}>
                    <Chip
                      label={`${group.queryCount || 0} occurrences`}
                      size="small"
                      sx={{ bgcolor: '#242830', color: '#B0B3B8' }}
                    />
                    {group.riskScore && (
                      <Chip
                        label={group.riskScore}
                        size="small"
                        sx={{
                          bgcolor: group.riskScore === 'high' ? '#DC2626' :
                                 group.riskScore === 'medium' ? '#D97706' : '#059669',
                          color: '#FFFFFF',
                        }}
                      />
                    )}
                  </Box>
                </Box>
              </Box>

              <Grid container spacing={2} sx={{ mb: 2 }}>
                <Grid item xs={12} sm={4}>
                  <Box sx={{ p: 2, bgcolor: '#14171C', borderRadius: 1 }}>
                    <Typography variant="caption" sx={{ color: '#6B7280', display: 'block', mb: 0.5 }}>
                      Average Cost
                    </Typography>
                    <Typography variant="body2" sx={{ color: '#E5E7EB', fontWeight: 600 }}>
                      {group.avgCost ? `$${group.avgCost.toFixed(2)}` : group.maxCost ? `$${group.maxCost.toFixed(2)}` : 'N/A'}
                    </Typography>
                  </Box>
                </Grid>
                <Grid item xs={12} sm={4}>
                  <Box sx={{ p: 2, bgcolor: '#14171C', borderRadius: 1 }}>
                    <Typography variant="caption" sx={{ color: '#6B7280', display: 'block', mb: 0.5 }}>
                      Max Cost
                    </Typography>
                    <Typography variant="body2" sx={{ color: '#E5E7EB', fontWeight: 600 }}>
                      {group.maxCost ? `$${group.maxCost.toFixed(2)}` : 'N/A'}
                    </Typography>
                  </Box>
                </Grid>
                <Grid item xs={12} sm={4}>
                  <Box sx={{ p: 2, bgcolor: '#14171C', borderRadius: 1 }}>
                    <Typography variant="caption" sx={{ color: '#6B7280', display: 'block', mb: 0.5 }}>
                      Total Queries
                    </Typography>
                    <Typography variant="body2" sx={{ color: '#E5E7EB', fontWeight: 600 }}>
                      {group.queryCount || 0}
                    </Typography>
                  </Box>
                </Grid>
              </Grid>

              {group.representativeQuery && (
                <Box sx={{ mb: 2 }}>
                  <Typography variant="caption" sx={{ color: '#6B7280', display: 'block', mb: 0.5 }}>
                    Representative Query
                  </Typography>
                  <Typography variant="body2" sx={{ color: '#E5E7EB', fontFamily: 'monospace', fontSize: '0.875rem', p: 1, bgcolor: '#14171C', borderRadius: 1 }}>
                    {group.representativeQuery}
                  </Typography>
                </Box>
              )}

              {group.files && group.files.length > 0 && (
                <Box sx={{ mt: 2, pt: 2, borderTop: '1px solid #242830' }}>
                  <Typography variant="caption" sx={{ color: '#6B7280', display: 'block', mb: 1 }}>
                    Files Affected
                  </Typography>
                  <List sx={{ bgcolor: '#14171C', borderRadius: 1 }}>
                    {group.files.map((file: string, idx: number) => (
                      <ListItem key={idx} sx={{ py: 0.5 }}>
                        <Code sx={{ color: '#3F51B5', mr: 1, fontSize: 18 }} />
                        <ListItemText
                          primary={file}
                          primaryTypographyProps={{ sx: { color: '#E5E7EB', fontFamily: 'monospace', fontSize: '0.875rem' } }}
                        />
                      </ListItem>
                    ))}
                  </List>
                </Box>
              )}

              {group.createdAt && (
                <Typography variant="caption" sx={{ color: '#6B7280', display: 'block', mt: 2 }}>
                  Detected: {new Date(group.createdAt).toLocaleString()}
                </Typography>
              )}
            </CardContent>
          </Card>
        ))}
      </Box>
    </Box>
  );
};
