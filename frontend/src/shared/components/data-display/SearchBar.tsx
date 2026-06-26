import React, { useState } from 'react';
import {
  InputBase,
  IconButton,
  Paper,
  useTheme,
  useMediaQuery,
  alpha,
} from '@mui/material';
import { Search as SearchIcon, Clear } from '@mui/icons-material';

interface SearchBarProps {
  placeholder?: string;
  onSearch?: (query: string) => void;
  fullWidth?: boolean;
  size?: 'small' | 'medium';
}

export const SearchBar: React.FC<SearchBarProps> = ({
  placeholder = 'Search queries, projects, diagnostics...',
  onSearch,
  fullWidth = false,
  size = 'medium',
}) => {
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('sm'));
  const [query, setQuery] = useState('');
  const [isFocused, setIsFocused] = useState(false);

  const handleSearch = () => {
    if (onSearch && query.trim()) {
      onSearch(query.trim());
    }
  };

  const handleClear = () => {
    setQuery('');
    if (onSearch) {
      onSearch('');
    }
  };

  const handleKeyPress = (event: React.KeyboardEvent) => {
    if (event.key === 'Enter') {
      handleSearch();
    }
  };

  const height = size === 'small' ? 36 : 44;
  const fontSize = size === 'small' ? '0.875rem' : '0.95rem';

  return (
    <Paper
      elevation={0}
      sx={{
        display: 'flex',
        alignItems: 'center',
        width: fullWidth ? '100%' : isMobile ? '100%' : 400,
        height,
        bgcolor: isFocused ? alpha('#3F51B5', 0.1) : '#242830',
        border: `1px solid ${isFocused ? '#3F51B5' : '#3D4450'}`,
        borderRadius: 2,
        transition: 'all 0.2s ease',
        '&:hover': {
          borderColor: '#4B5563',
          bgcolor: '#2D323C',
        },
      }}
    >
      <IconButton
        size="small"
        sx={{ color: '#B0B3B8', ml: 1 }}
        onClick={handleSearch}
      >
        <SearchIcon fontSize={size === 'small' ? 'small' : 'medium'} />
      </IconButton>
      <InputBase
        placeholder={placeholder}
        value={query}
        onChange={(e) => setQuery(e.target.value)}
        onKeyPress={handleKeyPress}
        onFocus={() => setIsFocused(true)}
        onBlur={() => setIsFocused(false)}
        sx={{
          flex: 1,
          mx: 1,
          color: '#FFFFFF',
          fontSize,
          '& .MuiInputBase-input::placeholder': {
            color: '#6B7280',
            opacity: 1,
          },
        }}
      />
      {query && (
        <IconButton
          size="small"
          sx={{ color: '#B0B3B8', mr: 1 }}
          onClick={handleClear}
        >
          <Clear fontSize={size === 'small' ? 'small' : 'medium'} />
        </IconButton>
      )}
    </Paper>
  );
};
