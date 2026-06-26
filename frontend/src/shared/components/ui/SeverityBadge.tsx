import React from 'react';
import { Chip } from '@mui/material';
import { Warning, Error, Info, CheckCircle } from '@mui/icons-material';

interface SeverityBadgeProps {
  severity: 'critical' | 'high' | 'medium' | 'low' | 'info';
  label?: string;
  size?: 'small' | 'medium';
  showIcon?: boolean;
}

export const SeverityBadge: React.FC<SeverityBadgeProps> = ({
  severity,
  label,
  size = 'small',
  showIcon = true,
}) => {
  const severityConfig = {
    critical: {
      color: '#EF4444',
      bgColor: 'rgba(239, 68, 68, 0.1)',
      borderColor: 'rgba(239, 68, 68, 0.3)',
      icon: <Error fontSize="small" />,
      label: label || 'Critical',
    },
    high: {
      color: '#F97316',
      bgColor: 'rgba(249, 115, 22, 0.1)',
      borderColor: 'rgba(249, 115, 22, 0.3)',
      icon: <Warning fontSize="small" />,
      label: label || 'High',
    },
    medium: {
      color: '#F59E0B',
      bgColor: 'rgba(245, 158, 11, 0.1)',
      borderColor: 'rgba(245, 158, 11, 0.3)',
      icon: <Warning fontSize="small" />,
      label: label || 'Medium',
    },
    low: {
      color: '#10B981',
      bgColor: 'rgba(16, 185, 129, 0.1)',
      borderColor: 'rgba(16, 185, 129, 0.3)',
      icon: <CheckCircle fontSize="small" />,
      label: label || 'Low',
    },
    info: {
      color: '#3B82F6',
      bgColor: 'rgba(59, 130, 246, 0.1)',
      borderColor: 'rgba(59, 130, 246, 0.3)',
      icon: <Info fontSize="small" />,
      label: label || 'Info',
    },
  };

  const config = severityConfig[severity];

  return (
    <Chip
      label={config.label}
      size={size}
      icon={showIcon ? config.icon : undefined}
      sx={{
        bgcolor: config.bgColor,
        color: config.color,
        border: `1px solid ${config.borderColor}`,
        fontWeight: 600,
        fontSize: size === 'small' ? '0.7rem' : '0.75rem',
        height: size === 'small' ? 20 : 24,
        '& .MuiChip-icon': {
          color: config.color,
          fontSize: size === 'small' ? 14 : 16,
        },
        '&:hover': {
          bgcolor: config.bgColor,
          opacity: 0.8,
        },
      }}
    />
  );
};
