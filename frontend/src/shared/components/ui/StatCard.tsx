import React from 'react';
import { Box, Card, CardContent, Typography, useTheme, useMediaQuery, alpha } from '@mui/material';
import { TrendingUp, TrendingDown, TrendingFlat } from '@mui/icons-material';

interface StatCardProps {
  title: string;
  value: string | number;
  subtitle?: string;
  icon?: React.ReactNode;
  trend?: 'up' | 'down' | 'neutral';
  trendValue?: string;
  color?: 'primary' | 'secondary' | 'success' | 'warning' | 'error' | 'info';
  onClick?: () => void;
  loading?: boolean;
}

export const StatCard: React.FC<StatCardProps> = ({
  title,
  value,
  subtitle,
  icon,
  trend,
  trendValue,
  color = 'primary',
  onClick,
  loading = false,
}) => {
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('sm'));

  const colorMap = {
    primary: '#3F51B5',
    secondary: '#2196F3',
    success: '#10B981',
    warning: '#F59E0B',
    error: '#EF4444',
    info: '#3B82F6',
  };

  const bgColor = alpha(colorMap[color], 0.1);
  const iconColor = colorMap[color];

  const getTrendIcon = () => {
    switch (trend) {
      case 'up':
        return <TrendingUp fontSize="small" sx={{ color: '#10B981' }} />;
      case 'down':
        return <TrendingDown fontSize="small" sx={{ color: '#EF4444' }} />;
      case 'neutral':
        return <TrendingFlat fontSize="small" sx={{ color: '#6B7280' }} />;
      default:
        return null;
    }
  };

  const getTrendColor = () => {
    switch (trend) {
      case 'up':
        return '#10B981';
      case 'down':
        return '#EF4444';
      case 'neutral':
        return '#6B7280';
      default:
        return '#6B7280';
    }
  };

  if (loading) {
    return (
      <Card
        sx={{
          bgcolor: '#1A1D23',
          border: '1px solid #242830',
          borderRadius: 2,
          height: isMobile ? 120 : 140,
        }}
      >
        <CardContent sx={{ height: '100%', display: 'flex', alignItems: 'center' }}>
          <Box
            sx={{
              width: '100%',
              height: 20,
              bgcolor: '#242830',
              borderRadius: 1,
              animation: 'pulse 1.5s ease-in-out infinite',
              '@keyframes pulse': {
                '0%, 100%': { opacity: 0.4 },
                '50%': { opacity: 0.8 },
              },
            }}
          />
        </CardContent>
      </Card>
    );
  }

  return (
    <Card
      onClick={onClick}
      sx={{
        bgcolor: '#1A1D23',
        border: '1px solid #242830',
        borderRadius: 2,
        height: isMobile ? 120 : 140,
        cursor: onClick ? 'pointer' : 'default',
        transition: 'all 0.2s ease',
        '&:hover': onClick
          ? {
              borderColor: iconColor,
              transform: 'translateY(-2px)',
              boxShadow: `0 4px 20px ${alpha(iconColor, 0.2)}`,
            }
          : {
              borderColor: '#3D4450',
            },
      }}
    >
      <CardContent sx={{ height: '100%', display: 'flex', flexDirection: 'column', justifyContent: 'space-between', p: 2 }}>
        {/* Header */}
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: 1 }}>
          <Box sx={{ flex: 1 }}>
            <Typography
              variant="caption"
              sx={{
                color: '#B0B3B8',
                fontSize: '0.75rem',
                fontWeight: 500,
                textTransform: 'uppercase',
                letterSpacing: '0.05em',
              }}
            >
              {title}
            </Typography>
          </Box>
          {icon && (
            <Box
              sx={{
                bgcolor: bgColor,
                color: iconColor,
                p: 1,
                borderRadius: 1,
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
              }}
            >
              {icon}
            </Box>
          )}
        </Box>

        {/* Value */}
        <Box sx={{ mb: 1 }}>
          <Typography
            variant={isMobile ? 'h5' : 'h4'}
            sx={{
              color: '#FFFFFF',
              fontWeight: 700,
              fontSize: { xs: '1.75rem', sm: '2rem', md: '2.25rem' },
              lineHeight: 1,
            }}
          >
            {value}
          </Typography>
        </Box>

        {/* Footer */}
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          {trend && trendValue && (
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
              {getTrendIcon()}
              <Typography
                variant="caption"
                sx={{
                  color: getTrendColor(),
                  fontWeight: 600,
                  fontSize: '0.75rem',
                }}
              >
                {trendValue}
              </Typography>
            </Box>
          )}
          {subtitle && (
            <Typography
              variant="caption"
              sx={{
                color: '#6B7280',
                fontSize: '0.75rem',
              }}
            >
              {subtitle}
            </Typography>
          )}
        </Box>
      </CardContent>
    </Card>
  );
};
