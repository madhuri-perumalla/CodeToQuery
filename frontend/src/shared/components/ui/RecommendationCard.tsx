import React from 'react';
import { Box, Card, CardContent, Typography, Chip, Button, useTheme, useMediaQuery, alpha, IconButton, Tooltip } from '@mui/material';
import { Lightbulb, TrendingUp, CheckCircle, ArrowForward, Close } from '@mui/icons-material';

interface RecommendationCardProps {
  title: string;
  description: string;
  impact: string;
  type: 'index' | 'rewrite' | 'filter' | 'optimization';
  severity: 'critical' | 'high' | 'medium' | 'low';
  estimatedImprovement?: string;
  onApply?: () => void;
  onDismiss?: () => void;
  applied?: boolean;
}

export const RecommendationCard: React.FC<RecommendationCardProps> = ({
  title,
  description,
  impact,
  type,
  severity,
  estimatedImprovement,
  onApply,
  onDismiss,
  applied = false,
}) => {
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('sm'));

  const severityColorMap = {
    critical: '#EF4444',
    high: '#F97316',
    medium: '#F59E0B',
    low: '#10B981',
  };

  const typeIconMap = {
    index: <TrendingUp />,
    rewrite: <Lightbulb />,
    filter: <CheckCircle />,
    optimization: <Lightbulb />,
  };

  const severityColor = severityColorMap[severity];
  const typeIcon = typeIconMap[type];

  return (
    <Card
      sx={{
        bgcolor: applied ? 'rgba(16, 185, 129, 0.1)' : '#1A1D23',
        border: applied ? '1px solid #10B981' : '1px solid #242830',
        borderRadius: 2,
        transition: 'all 0.2s ease',
        opacity: applied ? 0.7 : 1,
        '&:hover': {
          borderColor: applied ? '#10B981' : severityColor,
          transform: 'translateY(-2px)',
          boxShadow: applied ? `0 4px 20px ${alpha('#10B981', 0.2)}` : `0 4px 20px ${alpha(severityColor, 0.2)}`,
        },
      }}
    >
      <CardContent sx={{ p: 2 }}>
        {/* Header */}
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: 2 }}>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.5, flex: 1 }}>
            <Box
              sx={{
                bgcolor: alpha(severityColor, 0.1),
                color: severityColor,
                p: 1,
                borderRadius: 1,
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
              }}
            >
              {typeIcon}
            </Box>
            <Box sx={{ flex: 1 }}>
              <Typography
                variant="subtitle2"
                sx={{
                  color: '#FFFFFF',
                  fontWeight: 600,
                  fontSize: '0.875rem',
                  mb: 0.5,
                }}
              >
                {title}
              </Typography>
              <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
                <Chip
                  label={type}
                  size="small"
                  sx={{
                    bgcolor: alpha('#3F51B5', 0.1),
                    color: '#3F51B5',
                    fontSize: '0.7rem',
                    height: 20,
                  }}
                />
                <Chip
                  label={severity}
                  size="small"
                  sx={{
                    bgcolor: alpha(severityColor, 0.1),
                    color: severityColor,
                    fontSize: '0.7rem',
                    height: 20,
                  }}
                />
              </Box>
            </Box>
          </Box>
          {onDismiss && !applied && (
            <Tooltip title="Dismiss">
              <IconButton
                size="small"
                onClick={onDismiss}
                sx={{ color: '#B0B3B8', '&:hover': { color: '#FFFFFF' } }}
              >
                <Close fontSize="small" />
              </IconButton>
            </Tooltip>
          )}
        </Box>

        {/* Description */}
        <Typography
          variant="body2"
          sx={{
            color: '#B0B3B8',
            fontSize: '0.875rem',
            mb: 2,
            lineHeight: 1.5,
          }}
        >
          {description}
        </Typography>

        {/* Impact */}
        <Box
          sx={{
            bgcolor: alpha(severityColor, 0.05),
            border: `1px solid ${alpha(severityColor, 0.2)}`,
            borderRadius: 1,
            p: 1.5,
            mb: 2,
          }}
        >
          <Typography
            variant="caption"
            sx={{
              color: '#6B7280',
              fontSize: '0.7rem',
              textTransform: 'uppercase',
              letterSpacing: '0.05em',
              mb: 0.5,
              display: 'block',
            }}
          >
            Expected Impact
          </Typography>
          <Typography
            variant="body2"
            sx={{
              color: '#FFFFFF',
              fontSize: '0.875rem',
              fontWeight: 500,
            }}
          >
            {impact}
          </Typography>
          {estimatedImprovement && (
            <Typography
              variant="caption"
              sx={{
                color: severityColor,
                fontSize: '0.75rem',
                mt: 0.5,
                display: 'block',
                fontWeight: 600,
              }}
            >
              {estimatedImprovement}
            </Typography>
          )}
        </Box>

        {/* Actions */}
        {onApply && (
          <Button
            variant={applied ? 'outlined' : 'contained'}
            onClick={onApply}
            disabled={applied}
            fullWidth={isMobile}
            startIcon={applied ? <CheckCircle /> : <ArrowForward />}
            sx={{
              bgcolor: applied ? 'transparent' : '#3F51B5',
              color: applied ? '#10B981' : '#FFFFFF',
              borderColor: applied ? '#10B981' : undefined,
              '&:hover': {
                bgcolor: applied ? 'rgba(16, 185, 129, 0.1)' : '#3949AB',
              },
              '&:disabled': {
                bgcolor: 'transparent',
                color: '#10B981',
                borderColor: '#10B981',
              },
            }}
          >
            {applied ? 'Applied' : 'Apply Recommendation'}
          </Button>
        )}
      </CardContent>
    </Card>
  );
};
