import React, { useState } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  TextField,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  Chip,
  IconButton,
  Collapse,
  Grid,
  Button,
} from '@mui/material';
import { FilterList, ExpandMore, ExpandLess, Clear } from '@mui/icons-material';

interface FilterOption {
  label: string;
  value: string;
}

interface FilterField {
  id: string;
  label: string;
  type: 'text' | 'select' | 'multiselect' | 'number' | 'date';
  options?: FilterOption[];
  placeholder?: string;
}

interface FilterPanelProps {
  fields: FilterField[];
  onFilterChange: (filters: Record<string, unknown>) => void;
  onClear?: () => void;
  collapsible?: boolean;
  defaultExpanded?: boolean;
}

export const FilterPanel: React.FC<FilterPanelProps> = ({
  fields,
  onFilterChange,
  onClear,
  collapsible = true,
}) => {
  const [expanded, setExpanded] = useState(true);
  const [filters, setFilters] = useState<Record<string, unknown>>({});

  const handleFilterChange = (fieldId: string, value: unknown) => {
    const newFilters = { ...filters, [fieldId]: value };
    setFilters(newFilters);
    onFilterChange(newFilters);
  };

  const handleClear = () => {
    setFilters({});
    onClear?.();
  };

  const handleClearField = (fieldId: string) => {
    const newFilters = { ...filters };
    delete newFilters[fieldId];
    setFilters(newFilters);
    onFilterChange(newFilters);
  };

  const hasActiveFilters = Object.keys(filters).length > 0;

  const renderField = (field: FilterField) => {
    const value = filters[field.id];

    switch (field.type) {
      case 'text':
        return (
          <TextField
            fullWidth
            label={field.label}
            placeholder={field.placeholder}
            value={value || ''}
            onChange={(e) => handleFilterChange(field.id, e.target.value)}
            size="small"
            sx={{
              '& .MuiOutlinedInput-root': {
                color: '#FFFFFF',
                '& fieldset': { borderColor: '#3D4450' },
                '&:hover fieldset': { borderColor: '#4B5563' },
                '&.Mui-focused fieldset': { borderColor: '#3F51B5' },
              },
              '& .MuiInputLabel-root': { color: '#B0B3B8' },
              '& .MuiInputLabel-shrink': { color: '#3F51B5' },
            }}
          />
        );

      case 'select':
        return (
          <FormControl fullWidth size="small">
            <InputLabel sx={{ color: '#B0B3B8' }}>{field.label}</InputLabel>
            <Select
              value={value || ''}
              label={field.label}
              onChange={(e) => handleFilterChange(field.id, e.target.value)}
              sx={{
                color: '#FFFFFF',
                '& .MuiOutlinedInput-notchedOutline': { borderColor: '#3D4450' },
                '&:hover .MuiOutlinedInput-notchedOutline': { borderColor: '#4B5563' },
                '&.Mui-focused .MuiOutlinedInput-notchedOutline': { borderColor: '#3F51B5' },
                '& .MuiSelect-icon': { color: '#B0B3B8' },
              }}
            >
              <MenuItem value="">All</MenuItem>
              {field.options?.map((option) => (
                <MenuItem key={option.value} value={option.value}>
                  {option.label}
                </MenuItem>
              ))}
            </Select>
          </FormControl>
        );

      case 'multiselect':
        return (
          <Box>
            <FormControl fullWidth size="small">
              <InputLabel sx={{ color: '#B0B3B8' }}>{field.label}</InputLabel>
              <Select
                multiple
                value={value || []}
                label={field.label}
                onChange={(e) => handleFilterChange(field.id, e.target.value)}
                renderValue={(selected) => (
                  <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5 }}>
                    {(selected as string[]).map((value) => (
                      <Chip
                        key={value}
                        label={field.options?.find((o) => o.value === value)?.label || value}
                        size="small"
                        onDelete={() => {
                          const newValue = (value as unknown as string[]).filter((v) => v !== (value as unknown));
                          handleFilterChange(field.id, newValue);
                        }}
                        sx={{
                          bgcolor: '#3F51B5',
                          color: '#FFFFFF',
                          '& .MuiChip-deleteIcon': { color: '#FFFFFF' },
                        }}
                      />
                    ))}
                  </Box>
                )}
                sx={{
                  color: '#FFFFFF',
                  '& .MuiOutlinedInput-notchedOutline': { borderColor: '#3D4450' },
                  '&:hover .MuiOutlinedInput-notchedOutline': { borderColor: '#4B5563' },
                  '&.Mui-focused .MuiOutlinedInput-notchedOutline': { borderColor: '#3F51B5' },
                  '& .MuiSelect-icon': { color: '#B0B3B8' },
                }}
              >
                {field.options?.map((option) => (
                  <MenuItem key={option.value} value={option.value}>
                    {option.label}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
          </Box>
        );

      case 'number':
        return (
          <TextField
            fullWidth
            label={field.label}
            type="number"
            placeholder={field.placeholder}
            value={value || ''}
            onChange={(e) => handleFilterChange(field.id, e.target.value)}
            size="small"
            sx={{
              '& .MuiOutlinedInput-root': {
                color: '#FFFFFF',
                '& fieldset': { borderColor: '#3D4450' },
                '&:hover fieldset': { borderColor: '#4B5563' },
                '&.Mui-focused fieldset': { borderColor: '#3F51B5' },
              },
              '& .MuiInputLabel-root': { color: '#B0B3B8' },
              '& .MuiInputLabel-shrink': { color: '#3F51B5' },
            }}
          />
        );

      default:
        return null;
    }
  };

  return (
    <Card
      sx={{
        bgcolor: '#1A1D23',
        border: '1px solid #242830',
        borderRadius: 2,
        mb: 3,
      }}
    >
      <CardContent sx={{ p: 2 }}>
        {/* Header */}
        <Box
          sx={{
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            mb: 2,
          }}
        >
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <FilterList sx={{ color: '#3F51B5', fontSize: 20 }} />
            <Typography variant="h6" sx={{ color: '#FFFFFF', fontWeight: 600, fontSize: '1rem' }}>
              Filters
            </Typography>
            {hasActiveFilters && (
              <Chip
                label={`${Object.keys(filters).length} active`}
                size="small"
                sx={{
                  bgcolor: '#3F51B5',
                  color: '#FFFFFF',
                  fontSize: '0.75rem',
                }}
              />
            )}
          </Box>
          <Box sx={{ display: 'flex', gap: 0.5 }}>
            {hasActiveFilters && (
              <Button
                size="small"
                onClick={handleClear}
                startIcon={<Clear />}
                sx={{
                  color: '#B0B3B8',
                  '&:hover': { bgcolor: 'rgba(255, 255, 255, 0.05)' },
                }}
              >
                Clear
              </Button>
            )}
            {collapsible && (
              <IconButton
                size="small"
                onClick={() => setExpanded(!expanded)}
                sx={{ color: '#B0B3B8' }}
              >
                {expanded ? <ExpandLess /> : <ExpandMore />}
              </IconButton>
            )}
          </Box>
        </Box>

        {/* Active Filters */}
        {hasActiveFilters && (
          <Box sx={{ mb: 2, display: 'flex', flexWrap: 'wrap', gap: 1 }}>
            {Object.entries(filters).map(([key, value]) => {
              const field = fields.find((f) => f.id === key);
              if (!value || (Array.isArray(value) && value.length === 0)) return null;

              const displayValue = Array.isArray(value)
                ? value.length === 1
                  ? field?.options?.find((o) => o.value === value[0])?.label || value[0]
                  : `${value.length} selected`
                : field?.options?.find((o) => o.value === value)?.label || value;

              return (
                <Chip
                  key={key}
                  label={`${field?.label}: ${displayValue}`}
                  onDelete={() => handleClearField(key)}
                  size="small"
                  sx={{
                    bgcolor: '#242830',
                    color: '#FFFFFF',
                    border: '1px solid #3D4450',
                    '& .MuiChip-deleteIcon': { color: '#B0B3B8' },
                  }}
                />
              );
            })}
          </Box>
        )}

        {/* Filter Fields */}
        <Collapse in={expanded}>
          <Grid container spacing={2}>
            {fields.map((field) => (
              <Grid item xs={12} sm={6} md={4} lg={3} key={field.id}>
                {renderField(field)}
              </Grid>
            ))}
          </Grid>
        </Collapse>
      </CardContent>
    </Card>
  );
};
