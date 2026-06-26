import React from 'react';
import { Box, Card, CardContent, Typography, LinearProgress, useTheme, useMediaQuery } from '@mui/material';
import { CheckCircle, Warning, Error } from '@mui/icons-material';

interface HealthScoreCardProps {
  score: number;
  label: string;
  description?: string;
  showDetails?: boolean;
  onClick?: () => void;
}

export const HealthScoreCard: React.FC<HealthScoreCardProps> = ({
  score,
  label,
  description,
  showDetails = false,
  onClick,
}) => {
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('sm'));

  const getHealthStatus = () => {
    if (score >= 90) return { status: 'excellent', color: '#10B981', icon: <CheckCircle /> };
    if (score >= 75) return { status: 'good', color: '#34D399', icon: <CheckCircle /> };
    if (score >= 60) return { status: 'fair', color: '#F59E0B', icon: <Warning /> };
    if (score >= 40) return { status: 'poor', color: '#F97316', icon: <Warning /> };
    return { status: 'critical', color: '#EF4444', icon: <Error /> };
  };

  const health = getHealthStatus();

  return (
    <Card
      onClick={onClick}
      sx={{
        bgcolor: '#1A1D23',
        border: '1px solid #242830',
        borderRadius: 2,
        cursor: onClick ? 'pointer' : 'default',
        transition: 'all 0.2s ease',
        '&:hover': onClick
          ? {
              borderColor: health.color,
              transform: 'translateY(-2px)',
              boxShadow: `0 4px 20px ${health.color}33`,
            }
          : {
              borderColor: '#3D4450',
            },
      }}
    >
      <CardContent sx={{ p: 2 }}>
        {/* Header */}
        <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 2 }}>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.5 }}>
            <Box
              sx={{
                color: health.color,
                fontSize: isMobile ? 24 : 32,
              }}
            >
              {health.icon}
            </Box>
            <Box>
              <Typography
                variant="h6"
                sx={{
                  color: '#FFFFFF',
                  fontWeight: 700,
                  fontSize: isMobile ? '1rem' : '1.125rem',
                }}
              >
                {label}
              </Typography>
              {description && (
                <Typography
                  variant="caption"
                  sx={{
                    color: '#B0B3B8',
                    fontSize: '0.75rem',
                  }}
                >
                  {description}
                </Typography>
              )}
            </Box>
          </Box>
        </Box>

        {/* Score Display */}
        <Box sx={{ mb: 2 }}>
          <Box sx={{ display: 'flex', alignItems: 'baseline', gap: 1, mb: 1 }}>
            <Typography
              variant={isMobile ? 'h3' : 'h2'}
              sx={{
                color: health.color,
                fontWeight: 800,
                fontSize: isMobile ? '2rem' : '2.5rem',
                lineHeight: 1,
              }}
            >
              {score}
            </Typography>
            <Typography
              variant="body2"
              sx={{
                color: '#B0B3B8',
                fontSize: '0.875rem',
              }}
            >
              / 100
            </Typography>
          </Box>
          <Typography
            variant="subtitle2"
            sx={{
              color: health.color,
              fontWeight: 600,
              textTransform: 'capitalize',
              fontSize: '0.875rem',
            }}
          >
            {health.status}
          </Typography>
        </Box>

        {/* Progress Bar */}
        <Box sx={{ mb: showDetails ? 2 : 0 }}>
          <LinearProgress
            variant="determinate"
            value={score}
            sx={{
              height: 8,
              borderRadius: 4,
              bgcolor: '#242830',
              '& .MuiLinearProgress-bar': {
                bgcolor: health.color,
                borderRadius: 4,
              },
            }}
          />
        </Box>

        {/* Details */}
        {showDetails && (
          <Box
            sx={{
              pt: 2,
              borderTop: '1px solid #242830',
              display: 'grid',
              gridTemplateColumns: 'repeat(2, 1fr)',
              gap: 1.5,
            }}
          >
            <Box>
              <Typography variant="caption" sx={{ color: '#6B7280', fontSize: '0.7rem', mb: 0.5 }}>
                Critical Issues
              </Typography>
              <Typography variant="body2" sx={{ color: '#EF4444', fontWeight: 600, fontSize: '0.875rem' }}>
                {Math.round((100 - score) / 10)}
              </Typography>
            </Box>
            <Box>
              <Typography variant="caption" sx={{ color: '#6B7280', fontSize: '0.7rem', mb: 0.5 }}>
                Optimization
              </Typography>
              <Typography variant="body2" sx={{ color: '#10B981', fontWeight: 600, fontSize: '0.875rem' }}>
                {Math.round(score / 10)}%
              </Typography>
            </Box>
          </Box>
        )}
      </CardContent>
    </Card>
  );
};
