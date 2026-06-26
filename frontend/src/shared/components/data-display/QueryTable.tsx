import React, { useState } from 'react';
import {
  Box,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  TablePagination,
  Paper,
  Checkbox,
  IconButton,
  Tooltip,
  useTheme,
  useMediaQuery,
  Typography,
} from '@mui/material';
import {
  ArrowUpward,
  ArrowDownward,
} from '@mui/icons-material';

interface Column {
  id: string;
  label: string;
  width?: number | string;
  align?: 'left' | 'center' | 'right';
  sortable?: boolean;
  format?: (value: unknown) => React.ReactNode;
}

interface QueryTableProps {
  columns: Column[];
  data: Record<string, unknown>[];
  loading?: boolean;
  selectable?: boolean;
  onRowClick?: (row: Record<string, unknown>) => void;
  onSort?: (column: string, direction: 'asc' | 'desc') => void;
  onSelectionChange?: (selected: Record<string, unknown>[]) => void;
  onPageChange?: (page: number) => void;
  onRowsPerPageChange?: (pageSize: number) => void;
  actions?: Array<{
    icon: React.ReactNode;
    label: string;
    onClick: (row: Record<string, unknown>) => void;
    show?: (row: Record<string, unknown>) => boolean;
  }>;
  emptyMessage?: string;
  page?: number;
  pageSize?: number;
  pageSizeOptions?: number[];
  totalCount?: number;
  serverSidePagination?: boolean;
}

export const QueryTable: React.FC<QueryTableProps> = ({
  columns,
  data,
  loading = false,
  selectable = false,
  onRowClick,
  onSort,
  onSelectionChange,
  onPageChange,
  onRowsPerPageChange,
  actions,
  emptyMessage = 'No data available',
  page: externalPage = 0,
  pageSize: externalPageSize = 10,
  pageSizeOptions = [10, 25, 50, 100],
  totalCount,
  serverSidePagination = false,
}) => {
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('sm'));

  const [internalPage, setInternalPage] = useState(0);
  const [internalRowsPerPage, setInternalRowsPerPage] = useState(externalPageSize);
  const [selected, setSelected] = useState<Set<number>>(new Set());
  const [sortColumn, setSortColumn] = useState<string | null>(null);
  const [sortDirection, setSortDirection] = useState<'asc' | 'desc'>('asc');

  const page = serverSidePagination ? externalPage : internalPage;
  const rowsPerPage = serverSidePagination ? externalPageSize : internalRowsPerPage;

  const handleChangePage = (_event: unknown, newPage: number) => {
    if (serverSidePagination) {
      onPageChange?.(newPage);
    } else {
      setInternalPage(newPage);
    }
  };

  const handleChangeRowsPerPage = (event: React.ChangeEvent<HTMLInputElement>) => {
    const newPageSize = parseInt(event.target.value, 10);
    if (serverSidePagination) {
      onRowsPerPageChange?.(newPageSize);
    } else {
      setInternalRowsPerPage(newPageSize);
      setInternalPage(0);
    }
  };

  const handleSort = (columnId: string) => {
    const newDirection = sortColumn === columnId && sortDirection === 'asc' ? 'desc' : 'asc';
    setSortColumn(columnId);
    setSortDirection(newDirection);
    onSort?.(columnId, newDirection);
  };

  const handleSelectAllClick = (event: React.ChangeEvent<HTMLInputElement>) => {
    if (event.target.checked) {
      const newSelected = new Set(data.map((_, index) => index));
      setSelected(newSelected);
      onSelectionChange?.(data);
    } else {
      setSelected(new Set());
      onSelectionChange?.([]);
    }
  };

  const handleRowSelect = (index: number) => {
    const newSelected = new Set(selected);
    if (newSelected.has(index)) {
      newSelected.delete(index);
    } else {
      newSelected.add(index);
    }
    setSelected(newSelected);
    onSelectionChange?.(Array.from(newSelected).map((i) => data[i]!));
  };

  const isSelected = (index: number) => selected.has(index);
  const isAllSelected = data.length > 0 && selected.size === data.length;
  const isIndeterminate = selected.size > 0 && selected.size < data.length;

  const paginatedData = data.slice(page * rowsPerPage, page * rowsPerPage + rowsPerPage);

  if (loading) {
    return (
      <Box sx={{ width: '100%' }}>
        {[...Array(5)].map((_, index) => (
          <Box
            key={index}
            sx={{
              height: 56,
              bgcolor: '#1A1D23',
              mb: 1,
              borderRadius: 1,
              animation: 'pulse 1.5s ease-in-out infinite',
              '@keyframes pulse': {
                '0%, 100%': { opacity: 0.4 },
                '50%': { opacity: 0.8 },
              },
            }}
          />
        ))}
      </Box>
    );
  }

  if (data.length === 0) {
    return (
      <Box
        sx={{
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          justifyContent: 'center',
          py: 8,
          bgcolor: '#1A1D23',
          borderRadius: 2,
          border: '1px solid #242830',
        }}
      >
        <Typography variant="body1" sx={{ color: '#B0B3B8' }}>
          {emptyMessage}
        </Typography>
      </Box>
    );
  }

  return (
    <Paper
      sx={{
        width: '100%',
        bgcolor: '#1A1D23',
        border: '1px solid #242830',
        borderRadius: 2,
        overflow: 'hidden',
      }}
    >
      <TableContainer sx={{ maxHeight: isMobile ? 400 : 600 }}>
        <Table stickyHeader aria-label="sticky table">
          <TableHead>
            <TableRow>
              {selectable && (
                <TableCell padding="checkbox" sx={{ bgcolor: '#242830' }}>
                  <Checkbox
                    indeterminate={isIndeterminate}
                    checked={isAllSelected}
                    onChange={handleSelectAllClick}
                    sx={{
                      color: '#B0B3B8',
                      '&.Mui-checked': { color: '#3F51B5' },
                    }}
                  />
                </TableCell>
              )}
              {columns.map((column) => (
                <TableCell
                  key={column.id}
                  align={column.align || 'left'}
                  style={{ width: column.width, minWidth: column.width }}
                  sx={{
                    bgcolor: '#242830',
                    color: '#FFFFFF',
                    fontWeight: 600,
                    fontSize: '0.75rem',
                    textTransform: 'uppercase',
                    letterSpacing: '0.05em',
                    borderBottom: '2px solid #3D4450',
                    cursor: column.sortable ? 'pointer' : 'default',
                    '&:hover': column.sortable ? { bgcolor: '#2D323C' } : {},
                  }}
                  onClick={() => column.sortable && handleSort(column.id)}
                >
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
                    {column.label}
                    {column.sortable && sortColumn === column.id && (
                      sortDirection === 'asc' ? (
                        <ArrowUpward fontSize="small" />
                      ) : (
                        <ArrowDownward fontSize="small" />
                      )
                    )}
                  </Box>
                </TableCell>
              ))}
              {actions && (
                <TableCell sx={{ bgcolor: '#242830', borderBottom: '2px solid #3D4450' }} />
              )}
            </TableRow>
          </TableHead>
          <TableBody>
            {paginatedData.map((row, index) => {
              const actualIndex = page * rowsPerPage + index;
              const isRowSelected = isSelected(actualIndex);

              return (
                <TableRow
                  hover
                  onClick={() => onRowClick?.(row)}
                  selected={isRowSelected}
                  sx={{
                    cursor: onRowClick ? 'pointer' : 'default',
                    '&:hover': { bgcolor: 'rgba(63, 81, 181, 0.08)' },
                    '&.Mui-selected': { bgcolor: 'rgba(63, 81, 181, 0.15)' },
                  }}
                >
                  {selectable && (
                    <TableCell padding="checkbox">
                      <Checkbox
                        checked={isRowSelected}
                        onChange={() => handleRowSelect(actualIndex)}
                        sx={{
                          color: '#B0B3B8',
                          '&.Mui-checked': { color: '#3F51B5' },
                        }}
                      />
                    </TableCell>
                  )}
                  {columns.map((column) => (
                    <TableCell
                      key={column.id}
                      align={column.align || 'left'}
                      sx={{
                        color: '#FFFFFF',
                        borderBottom: '1px solid #242830',
                        fontSize: '0.875rem',
                      }}
                    >
                      {column.format ? column.format(row[column.id]) : String(row[column.id] ?? '')}
                    </TableCell>
                  ))}
                  {actions && (
                    <TableCell sx={{ borderBottom: '1px solid #242830' }}>
                      <Box sx={{ display: 'flex', gap: 0.5 }}>
                        {actions
                          .filter((action) => !action.show || action.show(row))
                          .map((action, actionIndex) => (
                            <Tooltip key={actionIndex} title={action.label}>
                              <IconButton
                                size="small"
                                onClick={(e) => {
                                  e.stopPropagation();
                                  action.onClick(row);
                                }}
                                sx={{ color: '#B0B3B8', '&:hover': { color: '#3F51B5' } }}
                              >
                                {action.icon}
                              </IconButton>
                            </Tooltip>
                          ))}
                      </Box>
                    </TableCell>
                  )}
                </TableRow>
              );
            })}
          </TableBody>
        </Table>
      </TableContainer>
      <TablePagination
        rowsPerPageOptions={pageSizeOptions}
        component="div"
        count={serverSidePagination ? (totalCount || 0) : data.length}
        rowsPerPage={rowsPerPage}
        page={page}
        onPageChange={handleChangePage}
        onRowsPerPageChange={handleChangeRowsPerPage}
        sx={{
          bgcolor: '#1A1D23',
          borderTop: '1px solid #242830',
          '& .MuiTablePagination-select': {
            color: '#FFFFFF',
          },
          '& .MuiTablePagination-selectIcon': {
            color: '#B0B3B8',
          },
          '& .MuiTablePagination-displayedRows': {
            color: '#B0B3B8',
          },
          '& .MuiTablePagination-actions': {
            color: '#B0B3B8',
          },
        }}
      />
    </Paper>
  );
};
