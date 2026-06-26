import React from 'react';
import { Box, Card, CardContent, Typography, Chip, Button } from '@mui/material';
import { Lightbulb, CheckCircle } from '@mui/icons-material';
import { useSuggestions } from '@/lib/react-query';
import { LoadingSkeleton, ErrorState, EmptyState } from '@/shared/components/loading';
import { PageHeader } from '@/shared/components/ui';
import { useParams } from 'react-router-dom';

export const SuggestionsPage: React.FC = () => {
  const { projectId } = useParams<{ projectId: string }>();
  const codebaseId = projectId ? parseInt(projectId) : undefined;
  const { data, isLoading, error, refetch } = useSuggestions({ page: 1, page_size: 50, codebase_id: codebaseId });

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
          title="Failed to load suggestions"
          message="Unable to fetch suggestion data. Please try again."
          onRetry={() => refetch()}
        />
      </Box>
    );
  }

  const suggestions = data?.items || [];

  if (!suggestions || suggestions.length === 0) {
    return (
      <Box sx={{ p: 3, bgcolor: '#0F1115', minHeight: '100vh' }}>
        <PageHeader
          title="Suggestions"
          subtitle="Improvement recommendations"
          onRefresh={() => refetch()}
        />
        <EmptyState
          variant="no-data"
          title="No analysis has been run for this project yet"
          message="Run analysis to generate optimization suggestions."
          actionLabel="Run Analysis"
          onAction={() => window.location.href = `/projects/${projectId}/overview`}
        />
      </Box>
    );
  }

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'high':
        return '#DC2626';
      case 'medium':
        return '#D97706';
      case 'low':
        return '#059669';
      default:
        return '#6B7280';
    }
  };

  return (
    <Box sx={{ p: 3, bgcolor: '#0F1115', minHeight: '100vh' }}>
      <PageHeader
        title="Suggestions"
        subtitle={`Found ${data?.total || 0} improvement recommendations`}
        onRefresh={() => refetch()}
      />

      <Box sx={{ mt: 2 }}>
        {suggestions.map((suggestion: any) => (
          <Card key={suggestion.id} sx={{ bgcolor: '#1A1D23', border: '1px solid #242830', borderRadius: 2, mb: 2 }}>
            <CardContent sx={{ p: 2 }}>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: 2 }}>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, flex: 1 }}>
                  <Lightbulb sx={{ color: '#F59E0B', fontSize: 28 }} />
                  <Box>
                    <Typography variant="h6" sx={{ color: '#FFFFFF', fontWeight: 600 }}>
                      {suggestion.title || suggestion.suggestionType || 'Suggestion'}
                    </Typography>
                    <Box sx={{ display: 'flex', gap: 1, mt: 1 }}>
                      <Chip
                        label={suggestion.priority || 'medium'}
                        size="small"
                        sx={{
                          bgcolor: getPriorityColor(suggestion.priority),
                          color: '#FFFFFF',
                        }}
                      />
                      {suggestion.status && (
                        <Chip
                          label={suggestion.status}
                          size="small"
                          sx={{
                            bgcolor: suggestion.status === 'applied' ? '#059669' :
                                   suggestion.status === 'pending' ? '#D97706' : '#6B7280',
                            color: '#FFFFFF',
                          }}
                        />
                      )}
                    </Box>
                  </Box>
                </Box>
                {suggestion.status !== 'applied' && (
                  <Button
                    variant="outlined"
                    size="small"
                    startIcon={<CheckCircle />}
                    sx={{
                      borderColor: '#242830',
                      color: '#B0B3B8',
                      '&:hover': { borderColor: '#059669', color: '#FFFFFF' },
                    }}
                  >
                    Mark Applied
                  </Button>
                )}
              </Box>

              <Typography variant="body2" sx={{ color: '#E5E7EB', mb: 2 }}>
                <strong>Reason:</strong> {suggestion.description || suggestion.reason || 'No reason provided'}
              </Typography>

              {suggestion.evidence && (
                <Typography variant="body2" sx={{ color: '#B0B3B8', mb: 2, fontFamily: 'monospace', fontSize: '0.875rem' }}>
                  <strong>Evidence:</strong> {suggestion.evidence}
                </Typography>
              )}

              <Box sx={{ mt: 2, pt: 2, borderTop: '1px solid #242830' }}>
                <Typography variant="caption" sx={{ color: '#6B7280', display: 'block', mb: 0.5 }}>
                  Related Query ID: {suggestion.planId || 'N/A'}
                </Typography>
                {suggestion.impact && (
                  <Typography variant="caption" sx={{ color: '#6B7280', display: 'block', mb: 0.5 }}>
                    Expected Impact: {suggestion.impact}
                  </Typography>
                )}
                {suggestion.createdAt && (
                  <Typography variant="caption" sx={{ color: '#6B7280' }}>
                    Generated: {new Date(suggestion.createdAt).toLocaleString()}
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
