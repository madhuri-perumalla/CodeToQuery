import React from 'react';
import { Box, Typography, Chip, Card, CardContent, Accordion, AccordionSummary, AccordionDetails } from '@mui/material';
import { ExpandMore } from '@mui/icons-material';
import { useQueries } from '@/lib/react-query';
import { LoadingSkeleton, ErrorState, EmptyState } from '@/shared/components/loading';
import { PageHeader } from '@/shared/components/ui';
import { useProjectContext } from '@/contexts/ProjectContext';

export const QueriesPage: React.FC = () => {
  const { selectedProjectId, selectedProject, selectedCodebaseId } = useProjectContext();
  const codebaseId = selectedCodebaseId;
  const { data, isLoading, error, refetch } = useQueries({ page: 1, page_size: 50, codebase_id: codebaseId || undefined });

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

  const queries = data?.items || [];

  if (!queries || queries.length === 0) {
    return (
      <Box sx={{ p: 3, bgcolor: '#0F1115', minHeight: '100vh' }}>
        <PageHeader
          title="Queries"
          subtitle={selectedProject ? `Queries for ${selectedProject.name}` : "Extracted SQL queries from source code"}
          onRefresh={() => refetch()}
        />
        <EmptyState
          variant="no-data"
          title="No queries found"
          message={selectedProject 
            ? "No SQL queries have been extracted yet for this project. Run analysis to populate queries."
            : "Select a project to view queries."
          }
        />
      </Box>
    );
  }

  return (
    <Box sx={{ p: 3, bgcolor: '#0F1115', minHeight: '100vh' }}>
      <PageHeader
        title="Queries"
        subtitle={`Found ${data?.total || 0} SQL queries extracted from source code`}
        onRefresh={() => refetch()}
      />

      <Box sx={{ mt: 2 }}>
        {queries.map((query: any) => (
          <Card key={query.id} sx={{ bgcolor: '#1A1D23', border: '1px solid #242830', borderRadius: 2, mb: 2 }}>
            <CardContent sx={{ p: 2 }}>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: 2 }}>
                <Box sx={{ flex: 1, mr: 2 }}>
                  <Typography variant="body2" sx={{ fontFamily: 'monospace', color: '#E5E7EB', fontSize: '0.875rem', mb: 1 }}>
                    {query.rawSql || query.normalized_sql || 'N/A'}
                  </Typography>
                </Box>
                <Chip
                  label={query.queryType?.toUpperCase() || 'UNKNOWN'}
                  size="small"
                  sx={{
                    bgcolor: query.queryType === 'select' ? '#059669' : 
                           query.queryType === 'insert' ? '#2563EB' :
                           query.queryType === 'update' ? '#D97706' :
                           query.queryType === 'delete' ? '#DC2626' : '#6B7280',
                    color: '#FFFFFF',
                  }}
                />
              </Box>

              <Accordion sx={{ bgcolor: '#14171C', border: '1px solid #242830', borderRadius: 1 }}>
                <AccordionSummary expandIcon={<ExpandMore sx={{ color: '#B0B3B8' }} />} sx={{ minHeight: 48 }}>
                  <Typography variant="body2" sx={{ color: '#B0B3B8' }}>
                    View Details
                  </Typography>
                </AccordionSummary>
                <AccordionDetails sx={{ bgcolor: '#14171C' }}>
                  <Box sx={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: 2 }}>
                    <Box>
                      <Typography variant="caption" sx={{ color: '#6B7280', display: 'block', mb: 0.5 }}>
                        File Path
                      </Typography>
                      <Typography variant="body2" sx={{ color: '#E5E7EB', fontFamily: 'monospace' }}>
                        {query.file || 'N/A'}
                      </Typography>
                    </Box>
                    <Box>
                      <Typography variant="caption" sx={{ color: '#6B7280', display: 'block', mb: 0.5 }}>
                        Line Number
                      </Typography>
                      <Typography variant="body2" sx={{ color: '#E5E7EB' }}>
                        {query.line || 'N/A'}
                      </Typography>
                    </Box>
                    <Box>
                      <Typography variant="caption" sx={{ color: '#6B7280', display: 'block', mb: 0.5 }}>
                        Function Name
                      </Typography>
                      <Typography variant="body2" sx={{ color: '#E5E7EB' }}>
                        {query.function_name || 'N/A'}
                      </Typography>
                    </Box>
                    <Box>
                      <Typography variant="caption" sx={{ color: '#6B7280', display: 'block', mb: 0.5 }}>
                        Source File Type
                      </Typography>
                      <Chip
                        label={query.file_type || query.file?.split('.').pop() || 'UNKNOWN'}
                        size="small"
                        sx={{ bgcolor: '#242830', color: '#B0B3B8' }}
                      />
                    </Box>
                    <Box>
                      <Typography variant="caption" sx={{ color: '#6B7280', display: 'block', mb: 0.5 }}>
                        Query Category
                      </Typography>
                      <Chip
                        label={query.category || 'GENERAL'}
                        size="small"
                        sx={{ bgcolor: '#242830', color: '#B0B3B8' }}
                      />
                    </Box>
                    {query.cost && (
                      <Box>
                        <Typography variant="caption" sx={{ color: '#6B7280', display: 'block', mb: 0.5 }}>
                          Estimated Cost
                        </Typography>
                        <Typography variant="body2" sx={{ color: '#E5E7EB' }}>
                          ${query.cost.toFixed(2)}
                        </Typography>
                      </Box>
                    )}
                  </Box>
                </AccordionDetails>
              </Accordion>
            </CardContent>
          </Card>
        ))}
      </Box>
    </Box>
  );
};
