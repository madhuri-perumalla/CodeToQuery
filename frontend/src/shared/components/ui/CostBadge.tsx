import React from 'react';
import { Chip } from '@mui/material';
import { AttachMoney } from '@mui/icons-material';

interface CostBadgeProps {
  cost: number;
  currency?: string;
  size?: 'small' | 'medium';
  showIcon?: boolean;
  format?: 'short' | 'full';
}

export const CostBadge: React.FC<CostBadgeProps> = ({
  cost,
  currency = '$',
  size = 'small',
  showIcon = true,
  format = 'short',
}) => {
  const formatCost = (value: number): string => {
    if (format === 'short') {
      if (value >= 1000000) {
        return `${currency}${(value / 1000000).toFixed(1)}M`;
      }
      if (value >= 1000) {
        return `${currency}${(value / 1000).toFixed(1)}K`;
      }
      return `${currency}${value.toFixed(2)}`;
    }
    return `${currency}${value.toFixed(2)}`;
  };

  const getCostColor = (value: number): string => {
    if (value >= 1000) return '#EF4444';
    if (value >= 100) return '#F97316';
    if (value >= 10) return '#F59E0B';
    return '#10B981';
  };

  const costColor = getCostColor(cost);
  const bgColor = cost >= 1000 ? 'rgba(239, 68, 68, 0.1)' : 
                   cost >= 100 ? 'rgba(249, 115, 22, 0.1)' :
                   cost >= 10 ? 'rgba(245, 158, 11, 0.1)' : 'rgba(16, 185, 129, 0.1)';
  const borderColor = cost >= 1000 ? 'rgba(239, 68, 68, 0.3)' :
                      cost >= 100 ? 'rgba(249, 115, 22, 0.3)' :
                      cost >= 10 ? 'rgba(245, 158, 11, 0.3)' : 'rgba(16, 185, 129, 0.3)';

  return (
    <Chip
      label={formatCost(cost)}
      size={size}
      icon={showIcon ? <AttachMoney fontSize="small" /> : undefined}
      sx={{
        bgcolor: bgColor,
        color: costColor,
        border: `1px solid ${borderColor}`,
        fontWeight: 600,
        fontSize: size === 'small' ? '0.7rem' : '0.75rem',
        height: size === 'small' ? 20 : 24,
        '& .MuiChip-icon': {
          color: costColor,
          fontSize: size === 'small' ? 14 : 16,
        },
        '&:hover': {
          bgcolor: bgColor,
          opacity: 0.8,
        },
      }}
    />
  );
};
