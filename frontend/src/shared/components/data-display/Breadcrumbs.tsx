import React from 'react';
import { Box, Breadcrumbs as MuiBreadcrumbs, Typography, Link, Chip, useTheme, useMediaQuery } from '@mui/material';
import { NavigateNext } from '@mui/icons-material';
import { useLocation, Link as RouterLink } from 'react-router-dom';

interface BreadcrumbItem {
  label: string;
  path?: string;
  icon?: React.ReactNode;
}

interface BreadcrumbsProps {
  items?: BreadcrumbItem[];
  showCurrent?: boolean;
}

const breadcrumbMap: Record<string, string> = {
  '/': 'Dashboard',
  '/projects': 'Projects',
  '/queries': 'Queries',
  '/execution-plans': 'Execution Plans',
  '/diagnostics': 'Diagnostics',
  '/suggestions': 'Suggestions',
  '/groups': 'Query Groups',
  '/history': 'Analysis History',
  '/settings': 'Settings',
};

export const Breadcrumbs: React.FC<BreadcrumbsProps> = ({
  items: customItems,
  showCurrent = true,
}) => {
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('sm'));
  const location = useLocation();

  // Generate breadcrumbs from current path if not provided
  const generateBreadcrumbs = (): BreadcrumbItem[] => {
    if (customItems) return customItems;

    const pathSegments = location.pathname.split('/').filter(Boolean);
    const breadcrumbs: BreadcrumbItem[] = [];

    let currentPath = '';
    pathSegments.forEach((segment, index) => {
      currentPath += `/${segment}`;
      const isLast = index === pathSegments.length - 1;

      // Check if this is a dynamic route (e.g., /projects/123)
      const isDynamic = !isNaN(parseInt(segment));

      breadcrumbs.push({
        label: isDynamic ? segment : breadcrumbMap[currentPath] || segment,
        path: isLast && !showCurrent ? undefined : currentPath,
      });
    });

    return breadcrumbs;
  };

  const breadcrumbs = generateBreadcrumbs();

  // On mobile, show only last item with a back indicator
  if (isMobile && breadcrumbs.length > 1) {
    const lastItem = breadcrumbs[breadcrumbs.length - 1];
    if (!lastItem) return null;
    
    return (
      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 2 }}>
        <Chip
          label="Back"
          size="small"
          onClick={() => window.history.back()}
          sx={{
            bgcolor: '#242830',
            color: '#B0B3B8',
            border: '1px solid #3D4450',
            '&:hover': {
              bgcolor: '#3D4450',
              color: '#FFFFFF',
            },
          }}
        />
        <Typography variant="h6" sx={{ color: '#FFFFFF', fontWeight: 600 }}>
          {lastItem.label}
        </Typography>
      </Box>
    );
  }

  return (
    <MuiBreadcrumbs
      separator={<NavigateNext fontSize="small" sx={{ color: '#6B7280' }} />}
      sx={{ mb: 3 }}
    >
      <Link
        component={RouterLink}
        to="/"
        underline="hover"
        sx={{
          color: '#B0B3B8',
          fontSize: '0.875rem',
          '&:hover': {
            color: '#3F51B5',
          },
        }}
      >
        Home
      </Link>
      {breadcrumbs.map((item, index) => {
        const isLast = index === breadcrumbs.length - 1;

        if (isLast && !showCurrent) {
          return null;
        }

        if (isLast) {
          return (
            <Typography
              key={item.path || index}
              sx={{
                color: '#FFFFFF',
                fontSize: '0.875rem',
                fontWeight: 600,
              }}
            >
              {item.label}
            </Typography>
          );
        }

        return (
          <Link
            key={item.path || index}
            component={RouterLink}
            to={item.path || '#'}
            underline="hover"
            sx={{
              color: '#B0B3B8',
              fontSize: '0.875rem',
              '&:hover': {
                color: '#3F51B5',
              },
            }}
          >
            {item.label}
          </Link>
        );
      })}
    </MuiBreadcrumbs>
  );
};
