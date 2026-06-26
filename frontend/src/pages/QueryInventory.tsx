import React, { useState } from 'react';
import { Box, Grid, useTheme, useMediaQuery, Card, Typography, Chip } from '@mui/material';
import { PageHeader, StatusChip, CostBadge } from '@/shared/components/ui';
import { LoadingSkeleton, ErrorState, EmptyState } from '@/shared/components/loading';
import { QueryTable, SearchBar, FilterPanel } from '@/shared/components/data-display';
import { useQueries } from '@/lib/react-query';
import { QueryListParams } from '@/types/api.types';
import { Visibility, Speed, HealthAndSafety } from '@mui/icons-material';
import { useParams } from 'react-router-dom';

export const QueryInventory: React.FC = () => {
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('sm'));
  const { projectId } = useParams<{ projectId: string }>();
  const codebaseId = projectId ? parseInt(projectId) : undefined;

  const [searchQuery, setSearchQuery] = useState('');
  const [filters, setFilters] = useState<Record<string, string | number | undefined>>({});
  const [page, setPage] = useState(0);
  const [pageSize, setPageSize] = useState(25);
  const [sortBy, setSortBy] = useState('createdAt');
  const [sortOrder, setSortOrder] = useState<'asc' | 'desc'>('desc');

  const queryParams: QueryListParams = {
    page: page + 1,
    page_size: pageSize,
    sort_by: sortBy,
    sort_order: sortOrder,
    search: searchQuery || undefined,
    codebase_id: codebaseId,
    severity: filters.severity as string | undefined,
  };

  const { data, isLoading, error, refetch } = useQueries(queryParams);

  const handleSearch = (query: string) => {
    setSearchQuery(query);
    setPage(0);
  };

  const handleFilterChange = (newFilters: Record<string, unknown>) => {
    setFilters(newFilters as Record<string, string | number | undefined>);
    setPage(0);
  };

  const handleSort = (column: string, direction: 'asc' | 'desc') => {
    setSortBy(column);
    setSortOrder(direction);
  };


  const handleRowClick = (row: unknown) => {
    console.log('Row clicked:', row);
    // Navigate to query details page
  };

  const filterFields = [
    {
      id: 'projectId',
      label: 'Project',
      type: 'select' as const,
      options: [
        { label: 'All Projects', value: '' },
        { label: 'Project A', value: 'project-a' },
        { label: 'Project B', value: 'project-b' },
      ],
    },
    {
      id: 'codebaseId',
      label: 'Codebase',
      type: 'select' as const,
      options: [
        { label: 'All Codebases', value: '' },
        { label: 'Main', value: 'main' },
        { label: 'Feature', value: 'feature' },
      ],
    },
    {
      id: 'severity',
      label: 'Severity',
      type: 'select' as const,
      options: [
        { label: 'All Severities', value: '' },
        { label: 'Critical', value: 'critical' },
        { label: 'High', value: 'high' },
        { label: 'Medium', value: 'medium' },
        { label: 'Low', value: 'low' },
      ],
    },
    {
      id: 'minCost',
      label: 'Min Cost ($)',
      type: 'number' as const,
      placeholder: '0',
    },
    {
      id: 'maxCost',
      label: 'Max Cost ($)',
      type: 'number' as const,
      placeholder: '1000',
    },
  ];

  const columns = [
    {
      id: 'name',
      label: 'Query Name',
      width: '25%',
      sortable: true,
      format: (value: unknown) => (
        <Typography variant="body2" sx={{ color: '#FFFFFF', fontWeight: 500 }}>
          {value as string || 'Unnamed Query'}
        </Typography>
      ),
    },
    {
      id: 'type',
      label: 'Type',
      width: '10%',
      sortable: true,
      format: (value: unknown) => (
        <Chip
          label={value as string || 'SELECT'}
          size="small"
          sx={{
            bgcolor: 'rgba(63, 81, 181, 0.1)',
            color: '#3F51B5',
            fontSize: '0.7rem',
            height: 20,
          }}
        />
      ),
    },
    {
      id: 'tables',
      label: 'Tables',
      width: '15%',
      sortable: false,
      format: (value: unknown) => (
        <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5 }}>
          {(value as string[] || []).slice(0, 2).map((table: string, index: number) => (
            <Chip
              key={index}
              label={table}
              size="small"
              sx={{
                bgcolor: '#242830',
                color: '#B0B3B8',
                fontSize: '0.7rem',
                height: 20,
              }}
            />
          ))}
          {(value as string[])?.length > 2 && (
            <Chip
              label={`+${(value as string[]).length - 2}`}
              size="small"
              sx={{
                bgcolor: '#242830',
                color: '#6B7280',
                fontSize: '0.7rem',
                height: 20,
              }}
            />
          )}
        </Box>
      ),
    },
    {
      id: 'cost',
      label: 'Cost',
      width: '12%',
      align: 'right' as const,
      sortable: true,
      format: (value: unknown) => <CostBadge cost={value as number || 0} size="small" />,
    },
    {
      id: 'executionTime',
      label: 'Execution Time',
      width: '12%',
      align: 'right' as const,
      sortable: true,
      format: (value: unknown) => (
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
          <Speed fontSize="small" sx={{ color: '#B0B3B8', fontSize: 14 }} />
          <Typography variant="body2" sx={{ color: '#FFFFFF' }}>
            {value ? `${value}ms` : '-'}
          </Typography>
        </Box>
      ),
    },
    {
      id: 'healthScore',
      label: 'Health Score',
      width: '12%',
      align: 'center' as const,
      sortable: true,
      format: (value: unknown) => (
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5, justifyContent: 'center' }}>
          <HealthAndSafety fontSize="small" sx={{ color: (value as number) >= 80 ? '#10B981' : (value as number) >= 60 ? '#F59E0B' : '#EF4444', fontSize: 14 }} />
          <Typography variant="body2" sx={{ color: '#FFFFFF', fontWeight: 600 }}>
            {(value !== undefined && value !== null) ? String(value) : '-'}
          </Typography>
        </Box>
      ),
    },
    {
      id: 'status',
      label: 'Status',
      width: '10%',
      sortable: true,
      format: (value: unknown) => <StatusChip status={(value as string) as any || 'analyzing'} size="small" />,
    },
  ];

  const tableActions = [
    {
      icon: <Visibility fontSize="small" />,
      label: 'View Details',
      onClick: (row: Record<string, unknown>) => handleRowClick(row),
    },
  ];

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

  const queries = data?.items || data?.queries || [];
  const total = data?.total || 0;

  return (
    <Box sx={{ p: isMobile ? 2 : 3, bgcolor: '#0F1115', minHeight: '100vh' }}>
      {/* Page Header */}
      <PageHeader
        title="Query Inventory"
        subtitle="Browse and analyze all detected queries across your codebases"
        onRefresh={() => refetch()}
      />

      {/* Search and Filter Bar */}
      <Box sx={{ mb: 3, display: 'flex', gap: 2, alignItems: 'center', flexWrap: 'wrap' }}>
        <SearchBar
          placeholder="Search queries by name, SQL, or table..."
          onSearch={handleSearch}
          fullWidth={isMobile}
        />
      </Box>

      {/* Filter Panel */}
      <FilterPanel
        fields={filterFields}
        onFilterChange={handleFilterChange}
        onClear={() => {
          setFilters({});
          setSearchQuery('');
          setPage(0);
        }}
        collapsible
        defaultExpanded={false}
      />

      {/* Summary Cards */}
      <Grid container spacing={2} sx={{ mb: 3 }}>
        <Grid item xs={6} sm={3}>
          <Card
            sx={{
              bgcolor: '#1A1D23',
              border: '1px solid #242830',
              borderRadius: 2,
              p: 2,
            }}
          >
            <Typography variant="caption" sx={{ color: '#B0B3B8', fontSize: '0.7rem', textTransform: 'uppercase' }}>
              Total Queries
            </Typography>
            <Typography variant="h5" sx={{ color: '#FFFFFF', fontWeight: 700, mt: 0.5 }}>
              {total}
            </Typography>
          </Card>
        </Grid>
        <Grid item xs={6} sm={3}>
          <Card
            sx={{
              bgcolor: '#1A1D23',
              border: '1px solid #242830',
              borderRadius: 2,
              p: 2,
            }}
          >
            <Typography variant="caption" sx={{ color: '#B0B3B8', fontSize: '0.7rem', textTransform: 'uppercase' }}>
              Page {page + 1}
            </Typography>
            <Typography variant="h5" sx={{ color: '#FFFFFF', fontWeight: 700, mt: 0.5 }}>
              {queries.length}
            </Typography>
          </Card>
        </Grid>
      </Grid>

      {/* Query Table */}
      {queries.length === 0 ? (
        <EmptyState
          variant="no-results"
          title="No queries found"
          message="Try adjusting your search or filter criteria"
          actionLabel="Clear Filters"
          onAction={() => {
            setFilters({});
            setSearchQuery('');
            setPage(0);
          }}
        />
      ) : (
        <QueryTable
          columns={columns}
          data={queries as unknown as Record<string, unknown>[]}
          loading={isLoading}
          onRowClick={handleRowClick}
          onSort={handleSort}
          onPageChange={setPage}
          onRowsPerPageChange={setPageSize}
          actions={tableActions}
          emptyMessage="No queries available"
          page={page}
          pageSize={pageSize}
          pageSizeOptions={[10, 25, 50, 100]}
          totalCount={total}
          serverSidePagination
        />
      )}
    </Box>
  );
};
