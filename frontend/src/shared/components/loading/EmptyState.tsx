import React from 'react';
import { Box, Typography, Button, useTheme, useMediaQuery, Card, CardContent } from '@mui/material';
import { Inbox, Add, Search, FolderOff } from '@mui/icons-material';

interface EmptyStateProps {
  icon?: React.ReactNode;
  title?: string;
  message?: string;
  actionLabel?: string;
  onAction?: () => void;
  variant?: 'default' | 'no-results' | 'no-data' | 'create-first';
}

export const EmptyState: React.FC<EmptyStateProps> = ({
  icon,
  title,
  message,
  actionLabel,
  onAction,
  variant = 'default',
}) => {
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('sm'));

  const getVariantConfig = () => {
    switch (variant) {
      case 'no-results':
        return {
          icon: <Search />,
          title: title || 'No results found',
          message: message || 'Try adjusting your search or filter criteria',
          actionLabel: actionLabel || 'Clear Filters',
        };
      case 'no-data':
        return {
          icon: <FolderOff />,
          title: title || 'No data available',
          message: message || 'There is no data to display at this time',
          actionLabel: actionLabel,
        };
      case 'create-first':
        return {
          icon: <Add />,
          title: title || 'Get started',
          message: message || 'Create your first item to begin',
          actionLabel: actionLabel || 'Create Item',
        };
      default:
        return {
          icon: icon || <Inbox />,
          title: title || 'Nothing here',
          message: message || 'No items to display',
          actionLabel: actionLabel,
        };
    }
  };

  const config = getVariantConfig();

  return (
    <Box
      sx={{
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        minHeight: 300,
        p: 3,
      }}
    >
      <Card
        sx={{
          bgcolor: '#1A1D23',
          border: '1px solid #242830',
          borderRadius: 2,
          maxWidth: 450,
          width: '100%',
        }}
      >
        <CardContent sx={{ p: 4, textAlign: 'center' }}>
          {/* Icon */}
          <Box
            sx={{
              width: 80,
              height: 80,
              bgcolor: 'rgba(176, 179, 184, 0.1)',
              borderRadius: '50%',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              mx: 'auto',
              mb: 3,
            }}
          >
            <Box sx={{ color: '#B0B3B8', fontSize: 48 }}>{config.icon}</Box>
          </Box>

          {/* Title */}
          <Typography
            variant={isMobile ? 'h6' : 'h5'}
            sx={{
              color: '#FFFFFF',
              fontWeight: 600,
              mb: 2,
            }}
          >
            {config.title}
          </Typography>

          {/* Message */}
          <Typography
            variant="body2"
            sx={{
              color: '#B0B3B8',
              mb: config.actionLabel ? 3 : 0,
              fontSize: '0.875rem',
              maxWidth: 350,
              mx: 'auto',
            }}
          >
            {config.message}
          </Typography>

          {/* Action Button */}
          {config.actionLabel && onAction && (
            <Button
              variant="contained"
              onClick={onAction}
              startIcon={variant === 'create-first' ? <Add /> : undefined}
              fullWidth={isMobile}
              sx={{
                bgcolor: '#3F51B5',
                color: '#FFFFFF',
                '&:hover': { bgcolor: '#3949AB' },
              }}
            >
              {config.actionLabel}
            </Button>
          )}
        </CardContent>
      </Card>
    </Box>
  );
};
