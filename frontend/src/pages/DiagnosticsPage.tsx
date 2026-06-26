import React from 'react';
import { Box, Typography, Alert, AlertTitle } from '@mui/material';
import { Warning, Error, Info } from '@mui/icons-material';
import { useDiagnostics } from '@/lib/react-query';
import { LoadingSkeleton, ErrorState, EmptyState } from '@/shared/components/loading';
import { PageHeader } from '@/shared/components/ui';
import { useProjectContext } from '@/contexts/ProjectContext';

export const DiagnosticsPage: React.FC = () => {
  const { selectedProject, selectedCodebaseId } = useProjectContext();
  const codebaseId = selectedCodebaseId ? String(selectedCodebaseId) : undefined;
  const { data, isLoading, error, refetch } = useDiagnostics(codebaseId);

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
          title="Failed to load diagnostics"
          message="Unable to fetch diagnostic data. Please try again."
          onRetry={() => refetch()}
        />
      </Box>
    );
  }

  const diagnostics = data?.items || [];

  if (!diagnostics || diagnostics.length === 0) {
    return (
      <Box sx={{ p: 3, bgcolor: '#0F1115', minHeight: '100vh' }}>
        <PageHeader
          title="Diagnostics"
          subtitle={selectedProject ? `Diagnostics for ${selectedProject.name}` : "Performance risk analysis"}
          onRefresh={() => refetch()}
        />
        <EmptyState
          variant="no-data"
          title="No diagnostics found"
          message={selectedProject 
            ? "No performance risks have been detected yet for this project. Run analysis to generate diagnostics."
            : "Select a project to view diagnostics."
          }
        />
      </Box>
    );
  }

  const getSeverityIcon = (severity: string) => {
    switch (severity) {
      case 'critical':
        return <Error sx={{ color: '#DC2626' }} />;
      case 'warning':
        return <Warning sx={{ color: '#D97706' }} />;
      case 'info':
        return <Info sx={{ color: '#2563EB' }} />;
      default:
        return <Info sx={{ color: '#6B7280' }} />;
    }
  };

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case 'critical':
        return '#DC2626';
      case 'warning':
        return '#D97706';
      case 'info':
        return '#2563EB';
      default:
        return '#6B7280';
    }
  };

  return (
    <Box sx={{ p: 3, bgcolor: '#0F1115', minHeight: '100vh' }}>
      <PageHeader
        title="Diagnostics"
        subtitle={`Found ${data?.total || 0} performance risks`}
        onRefresh={() => refetch()}
      />

      <Box sx={{ mt: 2 }}>
        {diagnostics.map((diagnostic: any) => (
          <Alert
            key={diagnostic.id}
            severity={diagnostic.severity === 'critical' ? 'error' : diagnostic.severity === 'warning' ? 'warning' : 'info'}
            sx={{
              bgcolor: '#1A1D23',
              border: `1px solid ${getSeverityColor(diagnostic.severity)}`,
              borderRadius: 2,
              mb: 2,
              '& .MuiAlert-icon': {
                color: getSeverityColor(diagnostic.severity),
              },
            }}
            icon={getSeverityIcon(diagnostic.severity)}
          >
            <AlertTitle sx={{ color: '#E5E7EB' }}>
              {diagnostic.ruleId || 'Unknown Risk'} - {diagnostic.severity?.toUpperCase()}
            </AlertTitle>
            <Box sx={{ mt: 2 }}>
              <Typography variant="body2" sx={{ color: '#E5E7EB', mb: 1 }}>
                <strong>Explanation:</strong> {diagnostic.message || 'No explanation provided'}
              </Typography>
              
              {diagnostic.evidence && (
                <Typography variant="body2" sx={{ color: '#B0B3B8', mb: 1, fontFamily: 'monospace', fontSize: '0.875rem' }}>
                  <strong>Evidence:</strong> {diagnostic.evidence}
                </Typography>
              )}

              <Box sx={{ mt: 2, pt: 2, borderTop: '1px solid #242830' }}>
                <Typography variant="caption" sx={{ color: '#6B7280', display: 'block', mb: 0.5 }}>
                  Related Query ID: {diagnostic.planId || 'N/A'}
                </Typography>
                {diagnostic.createdAt && (
                  <Typography variant="caption" sx={{ color: '#6B7280' }}>
                  Detected: {new Date(diagnostic.createdAt).toLocaleString()}
                </Typography>
                )}
              </Box>
            </Box>
          </Alert>
        ))}
      </Box>
    </Box>
  );
};
