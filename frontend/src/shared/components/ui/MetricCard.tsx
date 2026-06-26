import React from 'react';
import { Box, Card, CardContent, Typography, LinearProgress, useTheme, useMediaQuery, alpha } from '@mui/material';
import { TrendingUp, TrendingDown, TrendingFlat } from '@mui/icons-material';

interface MetricCardProps {
  title: string;
  value: string | number;
  unit?: string;
  previousValue?: string | number;
  trend?: 'up' | 'down' | 'neutral';
  trendValue?: string;
  icon?: React.ReactNode;
  color?: 'primary' | 'secondary' | 'success' | 'warning' | 'error' | 'info';
  progress?: number;
  onClick?: () => void;
}

export const MetricCard: React.FC<MetricCardProps> = ({
  title,
  value,
  unit,
  previousValue,
  trend,
  trendValue,
  icon,
  color = 'primary',
  progress,
  onClick,
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

  return (
    <Card
      onClick={onClick}
      sx={{
        bgcolor: '#1A1D23',
        border: '1px solid #242830',
        borderRadius: 2,
        height: isMobile ? 100 : 120,
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
                fontSize: '0.7rem',
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
                p: 0.75,
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
          <Box sx={{ display: 'flex', alignItems: 'baseline', gap: 0.5 }}>
            <Typography
              variant={isMobile ? 'h5' : 'h4'}
              sx={{
                color: '#FFFFFF',
                fontWeight: 700,
                fontSize: isMobile ? '1.5rem' : '1.75rem',
                lineHeight: 1,
              }}
            >
              {value}
            </Typography>
            {unit && (
              <Typography
                variant="caption"
                sx={{
                  color: '#B0B3B8',
                  fontSize: '0.75rem',
                }}
              >
                {unit}
              </Typography>
            )}
          </Box>
          {previousValue && (
            <Typography
              variant="caption"
              sx={{
                color: '#6B7280',
                fontSize: '0.7rem',
              }}
            >
              Previous: {previousValue}
            </Typography>
          )}
        </Box>

        {/* Footer */}
        <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
          {trend && trendValue && (
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
              {getTrendIcon()}
              <Typography
                variant="caption"
                sx={{
                  color: getTrendColor(),
                  fontWeight: 600,
                  fontSize: '0.7rem',
                }}
              >
                {trendValue}
              </Typography>
            </Box>
          )}
          {progress !== undefined && (
            <Box sx={{ flex: 1, ml: 2 }}>
              <LinearProgress
                variant="determinate"
                value={progress}
                sx={{
                  height: 4,
                  borderRadius: 2,
                  bgcolor: '#242830',
                  '& .MuiLinearProgress-bar': {
                    bgcolor: iconColor,
                    borderRadius: 2,
                  },
                }}
              />
            </Box>
          )}
        </Box>
      </CardContent>
    </Card>
  );
};
