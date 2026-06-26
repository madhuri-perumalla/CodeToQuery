import React, { useState } from 'react';
import { useParams } from 'react-router-dom';
import {
  Box,
  useTheme,
  useMediaQuery,
  Grid,
  Typography,
  Paper,
  IconButton,
  Collapse,
  Alert,
  AlertTitle,
  Divider,
  Select,
  MenuItem,
  FormControl,
} from '@mui/material';
import { PageHeader, SeverityBadge, StatCard } from '@/shared/components/ui';
import { LoadingSkeleton, ErrorState, EmptyState } from '@/shared/components/loading';
import { useDiagnostics } from '@/lib/react-query';
import {
  Warning,
  ErrorOutline,
  ExpandMore,
  ExpandLess,
  FilterList,
  TrendingUp,
  Storage,
  MergeType,
  Sort,
  CheckCircle,
  Info,
} from '@mui/icons-material';

type Severity = 'critical' | 'high' | 'medium' | 'low' | 'info';

interface DiagnosticItem {
  id: string;
  planId: string;
  ruleId: string;
  severity: Severity;
  message: string;
  description: string;
  location?: any;
  createdAt: string;
  suggestions?: any[];
}

interface DiagnosticCategory {
  type: string;
  title: string;
  icon: React.ReactNode;
  color: string;
  items: DiagnosticItem[];
}

export const Diagnostics: React.FC = () => {
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('sm'));
  const { projectId } = useParams<{ projectId: string }>();
  const codebaseId = projectId ? parseInt(projectId) : undefined;
  
  const [severityFilter, setSeverityFilter] = useState<Severity | 'all'>('all');
  const [expandedCategories, setExpandedCategories] = useState<Set<string>>(new Set(['all']));

  const { data, isLoading, error, refetch } = useDiagnostics(
    codebaseId ? String(codebaseId) : undefined,
    severityFilter === 'all' ? undefined : severityFilter
  );

  const diagnostics = data?.diagnostics || [];

  // Categorize diagnostics by rule_id
  const categories: DiagnosticCategory[] = [
    {
      type: 'index',
      title: 'Index Issues',
      icon: <TrendingUp />,
      color: '#EF4444',
      items: diagnostics.filter((d: any) => d.ruleId?.toLowerCase().includes('index')).map((d: any) => ({
        ...d,
        id: d.id_str || String(d.id),
      })) as DiagnosticItem[],
    },
    {
      type: 'scan',
      title: 'Scan Issues',
      icon: <Storage />,
      color: '#F59E0B',
      items: diagnostics.filter((d: any) => d.ruleId?.toLowerCase().includes('scan')).map((d: any) => ({
        ...d,
        id: d.id_str || String(d.id),
      })) as DiagnosticItem[],
    },
    {
      type: 'join',
      title: 'Join Issues',
      icon: <MergeType />,
      color: '#3F51B5',
      items: diagnostics.filter((d: any) => d.ruleId?.toLowerCase().includes('join')).map((d: any) => ({
        ...d,
        id: d.id_str || String(d.id),
      })) as DiagnosticItem[],
    },
    {
      type: 'sort',
      title: 'Sort Issues',
      icon: <Sort />,
      color: '#EC4899',
      items: diagnostics.filter((d: any) => d.ruleId?.toLowerCase().includes('sort')).map((d: any) => ({
        ...d,
        id: d.id_str || String(d.id),
      })) as DiagnosticItem[],
    },
  ];

  const filteredCategories = categories.map(category => ({
    ...category,
    items: category.items.filter(item => 
      severityFilter === 'all' || item.severity === severityFilter
    ),
  })).filter(category => category.items.length > 0);

  const toggleCategory = (type: string) => {
    setExpandedCategories(prev => {
      const newSet = new Set(prev);
      if (newSet.has(type)) {
        newSet.delete(type);
      } else {
        newSet.add(type);
      }
      return newSet;
    });
  };

  const getSeverityCount = (severity: Severity) => {
    return diagnostics.filter((d: any) => d.severity === severity).length;
  };

  const getSeverityColor = (severity: Severity) => {
    switch (severity) {
      case 'critical': return '#EF4444';
      case 'high': return '#F59E0B';
      case 'medium': return '#3F51B5';
      case 'low': return '#10B981';
      default: return '#6B7280';
    }
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
          title="Failed to load diagnostics"
          message="Unable to fetch diagnostic data. Please try again."
          onRetry={() => refetch()}
        />
      </Box>
    );
  }

  return (
    <Box sx={{ p: isMobile ? 2 : 3, bgcolor: '#0F1115', minHeight: '100vh' }}>
      {/* Page Header */}
      <PageHeader
        title="Diagnostics"
        subtitle="Identify and resolve performance issues in your queries"
        onRefresh={() => refetch()}
      />

      {/* Summary Cards */}
      <Grid container spacing={2} sx={{ mb: 3 }}>
        <Grid item xs={6} sm={3}>
          <StatCard
            title="Critical Issues"
            value={getSeverityCount('critical')}
            icon={<ErrorOutline />}
            color="error"
          />
        </Grid>
        <Grid item xs={6} sm={3}>
          <StatCard
            title="High Severity"
            value={getSeverityCount('high')}
            icon={<Warning />}
            color="warning"
          />
        </Grid>
        <Grid item xs={6} sm={3}>
          <StatCard
            title="Medium Severity"
            value={getSeverityCount('medium')}
            icon={<Info />}
            color="info"
          />
        </Grid>
        <Grid item xs={6} sm={3}>
          <StatCard
            title="Total Issues"
            value={diagnostics.length}
            icon={<FilterList />}
            color="info"
          />
        </Grid>
      </Grid>

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
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
          <FilterList sx={{ color: '#B0B3B8' }} />
          <Typography variant="body2" sx={{ color: '#B0B3B8' }}>
            Filter by severity:
          </Typography>
        </Box>
        <FormControl size="small" sx={{ minWidth: 150 }}>
          <Select
            value={severityFilter}
            onChange={(e) => setSeverityFilter(e.target.value as Severity | 'all')}
            sx={{
              color: '#FFFFFF',
              bgcolor: '#242830',
              '& .MuiSelect-icon': { color: '#B0B3B8' },
            }}
          >
            <MenuItem value="all">All Severities</MenuItem>
            <MenuItem value="critical">Critical</MenuItem>
            <MenuItem value="high">High</MenuItem>
            <MenuItem value="medium">Medium</MenuItem>
            <MenuItem value="low">Low</MenuItem>
          </Select>
        </FormControl>
      </Paper>

      {/* Diagnostic Categories */}
      {filteredCategories.length === 0 ? (
        <EmptyState
          variant="no-results"
          title="No diagnostics found"
          message="Try adjusting your severity filter"
          actionLabel="Clear Filter"
          onAction={() => setSeverityFilter('all')}
        />
      ) : (
        <Grid container spacing={2}>
          {filteredCategories.map((category) => (
            <Grid item xs={12} key={category.type}>
              <Paper
                sx={{
                  bgcolor: '#1A1D23',
                  border: '1px solid #242830',
                  borderRadius: 2,
                  overflow: 'hidden',
                }}
              >
                {/* Category Header */}
                <Box
                  sx={{
                    p: 2,
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'space-between',
                    cursor: 'pointer',
                    bgcolor: 'rgba(63, 81, 181, 0.05)',
                    borderBottom: expandedCategories.has(category.type) ? '1px solid #242830' : 'none',
                    '&:hover': {
                      bgcolor: 'rgba(63, 81, 181, 0.1)',
                    },
                  }}
                  onClick={() => toggleCategory(category.type)}
                >
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                    <Box
                      sx={{
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                        width: 36,
                        height: 36,
                        borderRadius: 1,
                        bgcolor: `${category.color}20`,
                        color: category.color,
                      }}
                    >
                      {category.icon}
                    </Box>
                    <Box>
                      <Typography variant="h6" sx={{ color: '#FFFFFF', fontWeight: 600 }}>
                        {category.title}
                      </Typography>
                      <Typography variant="caption" sx={{ color: '#B0B3B8' }}>
                        {category.items.length} issue{category.items.length !== 1 ? 's' : ''} found
                      </Typography>
                    </Box>
                  </Box>
                  <IconButton size="small" sx={{ color: '#B0B3B8' }}>
                    {expandedCategories.has(category.type) ? <ExpandLess /> : <ExpandMore />}
                  </IconButton>
                </Box>

                {/* Category Items */}
                <Collapse in={expandedCategories.has(category.type)}>
                  <Box sx={{ p: 2 }}>
                    {category.items.map((item, index) => (
                      <Alert
                        key={item.id}
                        severity={item.severity === 'critical' ? 'error' : item.severity === 'high' ? 'warning' : 'info'}
                        sx={{
                          mb: index < category.items.length - 1 ? 2 : 0,
                          bgcolor: item.severity === 'critical' ? 'rgba(239, 68, 68, 0.1)' : 
                                 item.severity === 'high' ? 'rgba(245, 158, 11, 0.1)' :
                                 item.severity === 'medium' ? 'rgba(63, 81, 181, 0.1)' : 'rgba(16, 185, 129, 0.1)',
                          border: `1px solid ${getSeverityColor(item.severity)}`,
                          borderRadius: 1,
                          '& .MuiAlert-icon': {
                            color: getSeverityColor(item.severity),
                          },
                        }}
                      >
                        <AlertTitle sx={{ color: '#FFFFFF', fontWeight: 600 }}>
                          <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', gap: 2 }}>
                            <span>{item.ruleId}</span>
                            <SeverityBadge severity={item.severity} size="small" />
                          </Box>
                        </AlertTitle>
                        <Typography variant="body2" sx={{ color: '#B0B3B8', mb: 1 }}>
                          {item.message}
                        </Typography>
                        
                        <Divider sx={{ my: 1, borderColor: 'rgba(255, 255, 255, 0.1)' }} />
                        
                        <Grid container spacing={2} sx={{ mb: 1 }}>
                          <Grid item xs={12} sm={6}>
                            <Typography variant="caption" sx={{ color: '#6B7280', fontSize: '0.7rem', display: 'block' }}>
                              Plan ID
                            </Typography>
                            <Typography variant="body2" sx={{ color: '#FFFFFF', fontWeight: 500 }}>
                              {item.planId}
                            </Typography>
                          </Grid>
                          <Grid item xs={12} sm={6}>
                            <Typography variant="caption" sx={{ color: '#6B7280', fontSize: '0.7rem', display: 'block' }}>
                              Detected At
                            </Typography>
                            <Typography variant="body2" sx={{ color: '#FFFFFF', fontWeight: 500 }}>
                              {item.createdAt ? new Date(item.createdAt).toLocaleString() : '-'}
                            </Typography>
                          </Grid>
                        </Grid>

                        {item.suggestions && item.suggestions.length > 0 && (
                          <>
                            <Divider sx={{ my: 1, borderColor: 'rgba(255, 255, 255, 0.1)' }} />
                            <Box sx={{ display: 'flex', gap: 2, alignItems: 'flex-start' }}>
                              <Box sx={{ flex: 1 }}>
                                <Typography variant="caption" sx={{ color: '#6B7280', fontSize: '0.7rem', display: 'block', mb: 0.5 }}>
                                  Suggestion
                                </Typography>
                                <Typography variant="body2" sx={{ color: '#10B981', fontWeight: 500 }}>
                                  {item.suggestions[0]?.description || 'No suggestion available'}
                                </Typography>
                              </Box>
                            </Box>
                          </>
                        )}
                      </Alert>
                    ))}
                  </Box>
                </Collapse>
              </Paper>
            </Grid>
          ))}
        </Grid>
      )}

      {/* No Issues State */}
      {diagnostics.length === 0 && !isLoading && (
        <Paper
          sx={{
            p: 4,
            bgcolor: '#1A1D23',
            border: '1px solid #242830',
            borderRadius: 2,
            textAlign: 'center',
          }}
        >
          <CheckCircle sx={{ fontSize: 64, color: '#10B981', mb: 2 }} />
          <Typography variant="h6" sx={{ color: '#FFFFFF', fontWeight: 600, mb: 1 }}>
            All Clear!
          </Typography>
          <Typography variant="body2" sx={{ color: '#B0B3B8' }}>
            No diagnostic issues found. Your queries are performing well.
          </Typography>
        </Paper>
      )}
    </Box>
  );
};
