import React from 'react';
import { Chip } from '@mui/material';
import { CheckCircle, Pending, Error as ErrorIcon, Schedule, PlayCircle, PauseCircle } from '@mui/icons-material';

interface StatusChipProps {
  status: 'success' | 'error' | 'pending' | 'running' | 'paused' | 'scheduled' | 'completed' | 'failed';
  label?: string;
  size?: 'small' | 'medium';
  showIcon?: boolean;
}

export const StatusChip: React.FC<StatusChipProps> = ({
  status,
  label,
  size = 'small',
  showIcon = true,
}) => {
  const statusConfig = {
    success: {
      color: '#10B981',
      bgColor: 'rgba(16, 185, 129, 0.1)',
      borderColor: 'rgba(16, 185, 129, 0.3)',
      icon: <CheckCircle fontSize="small" />,
      label: label || 'Success',
    },
    completed: {
      color: '#10B981',
      bgColor: 'rgba(16, 185, 129, 0.1)',
      borderColor: 'rgba(16, 185, 129, 0.3)',
      icon: <CheckCircle fontSize="small" />,
      label: label || 'Completed',
    },
    error: {
      color: '#EF4444',
      bgColor: 'rgba(239, 68, 68, 0.1)',
      borderColor: 'rgba(239, 68, 68, 0.3)',
      icon: <ErrorIcon fontSize="small" />,
      label: label || 'Error',
    },
    failed: {
      color: '#EF4444',
      bgColor: 'rgba(239, 68, 68, 0.1)',
      borderColor: 'rgba(239, 68, 68, 0.3)',
      icon: <ErrorIcon fontSize="small" />,
      label: label || 'Failed',
    },
    pending: {
      color: '#F59E0B',
      bgColor: 'rgba(245, 158, 11, 0.1)',
      borderColor: 'rgba(245, 158, 11, 0.3)',
      icon: <Pending fontSize="small" />,
      label: label || 'Pending',
    },
    running: {
      color: '#3B82F6',
      bgColor: 'rgba(59, 130, 246, 0.1)',
      borderColor: 'rgba(59, 130, 246, 0.3)',
      icon: <PlayCircle fontSize="small" />,
      label: label || 'Running',
    },
    paused: {
      color: '#8B5CF6',
      bgColor: 'rgba(139, 92, 246, 0.1)',
      borderColor: 'rgba(139, 92, 246, 0.3)',
      icon: <PauseCircle fontSize="small" />,
      label: label || 'Paused',
    },
    scheduled: {
      color: '#6B7280',
      bgColor: 'rgba(107, 114, 128, 0.1)',
      borderColor: 'rgba(107, 114, 128, 0.3)',
      icon: <Schedule fontSize="small" />,
      label: label || 'Scheduled',
    },
  };

  const config = statusConfig[status];

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
