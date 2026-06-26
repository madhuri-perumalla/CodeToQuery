import React from 'react';
import { Box, Typography, Breadcrumbs as MuiBreadcrumbs, Link, useTheme, useMediaQuery, IconButton, Tooltip } from '@mui/material';
import { NavigateNext, Refresh, HelpOutline } from '@mui/icons-material';
import { Link as RouterLink } from 'react-router-dom';

interface PageHeaderProps {
  title: string;
  subtitle?: string;
  breadcrumbs?: Array<{ label: string; path?: string }>;
  action?: React.ReactNode;
  onRefresh?: () => void;
  showRefresh?: boolean;
  showHelp?: boolean;
  onHelp?: () => void;
}

export const PageHeader: React.FC<PageHeaderProps> = ({
  title,
  subtitle,
  breadcrumbs,
  action,
  onRefresh,
  showRefresh = false,
  showHelp = false,
  onHelp,
}) => {
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('sm'));

  return (
    <Box sx={{ mb: 4 }}>
      {/* Breadcrumbs */}
      {breadcrumbs && breadcrumbs.length > 0 && (
        <MuiBreadcrumbs
          separator={<NavigateNext fontSize="small" sx={{ color: '#6B7280' }} />}
          sx={{ mb: 2 }}
        >
          <Link
            component={RouterLink}
            to="/"
            underline="hover"
            sx={{
              color: '#B0B3B8',
              fontSize: '0.875rem',
              '&:hover': { color: '#3F51B5' },
            }}
          >
            Home
          </Link>
          {breadcrumbs.map((crumb, index) => {
            const isLast = index === breadcrumbs.length - 1;
            if (isLast) {
              return (
                <Typography
                  key={crumb.label}
                  sx={{ color: '#FFFFFF', fontSize: '0.875rem', fontWeight: 600 }}
                >
                  {crumb.label}
                </Typography>
              );
            }
            return (
              <Link
                key={crumb.label}
                component={RouterLink}
                to={crumb.path || '#'}
                underline="hover"
                sx={{
                  color: '#B0B3B8',
                  fontSize: '0.875rem',
                  '&:hover': { color: '#3F51B5' },
                }}
              >
                {crumb.label}
              </Link>
            );
          })}
        </MuiBreadcrumbs>
      )}

      {/* Header Content */}
      <Box
        sx={{
          display: 'flex',
          flexDirection: isMobile ? 'column' : 'row',
          justifyContent: 'space-between',
          alignItems: isMobile ? 'flex-start' : 'center',
          gap: 2,
        }}
      >
        {/* Title Section */}
        <Box sx={{ flex: 1 }}>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 0.5 }}>
            <Typography
              variant={isMobile ? 'h5' : 'h4'}
              sx={{
                color: '#FFFFFF',
                fontWeight: 700,
                fontSize: { xs: '1.5rem', sm: '1.75rem', md: '2rem' },
              }}
            >
              {title}
            </Typography>
            
            {/* Action Buttons */}
            <Box sx={{ display: 'flex', gap: 1 }}>
              {showRefresh && onRefresh && (
                <Tooltip title="Refresh">
                  <IconButton
                    onClick={onRefresh}
                    size="small"
                    sx={{
                      color: '#B0B3B8',
                      '&:hover': { bgcolor: 'rgba(255, 255, 255, 0.05)', color: '#FFFFFF' },
                    }}
                  >
                    <Refresh fontSize="small" />
                  </IconButton>
                </Tooltip>
              )}
              {showHelp && onHelp && (
                <Tooltip title="Help">
                  <IconButton
                    onClick={onHelp}
                    size="small"
                    sx={{
                      color: '#B0B3B8',
                      '&:hover': { bgcolor: 'rgba(255, 255, 255, 0.05)', color: '#FFFFFF' },
                    }}
                  >
                    <HelpOutline fontSize="small" />
                  </IconButton>
                </Tooltip>
              )}
            </Box>
          </Box>
          
          {subtitle && (
            <Typography
              variant="body2"
              sx={{
                color: '#B0B3B8',
                fontSize: '0.875rem',
                maxWidth: '800px',
              }}
            >
              {subtitle}
            </Typography>
          )}
        </Box>

        {/* Action Section */}
        {action && <Box sx={{ flexShrink: 0 }}>{action}</Box>}
      </Box>
    </Box>
  );
};
