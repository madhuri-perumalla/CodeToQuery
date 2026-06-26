import React from 'react';
import { Box, Skeleton, useTheme, useMediaQuery, Grid } from '@mui/material';

interface LoadingSkeletonProps {
  variant?: 'card' | 'table' | 'list' | 'chart' | 'dashboard';
  count?: number;
}

export const LoadingSkeleton: React.FC<LoadingSkeletonProps> = ({
  variant = 'card',
  count = 1,
}) => {
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('sm'));

  const renderCardSkeleton = () => (
    <Box
      sx={{
        bgcolor: '#1A1D23',
        border: '1px solid #242830',
        borderRadius: 2,
        p: 2,
        height: isMobile ? 120 : 140,
      }}
    >
      <Skeleton
        variant="rectangular"
        width={40}
        height={40}
        sx={{ bgcolor: '#242830', mb: 2 }}
      />
      <Skeleton
        variant="text"
        width="60%"
        height={32}
        sx={{ bgcolor: '#242830', mb: 1 }}
      />
      <Skeleton
        variant="text"
        width="40%"
        height={20}
        sx={{ bgcolor: '#242830' }}
      />
    </Box>
  );

  const renderTableSkeleton = () => (
    <Box sx={{ width: '100%' }}>
      {[...Array(5)].map((_, index) => (
        <Box
          key={index}
          sx={{
            display: 'flex',
            alignItems: 'center',
            gap: 2,
            py: 2,
            px: 2,
            borderBottom: '1px solid #242830',
          }}
        >
          <Skeleton variant="rectangular" width={24} height={24} sx={{ bgcolor: '#242830' }} />
          {[...Array(4)].map((_, i) => (
            <Skeleton
              key={i}
              variant="text"
              width={`${20 + Math.random() * 30}%`}
              height={24}
              sx={{ bgcolor: '#242830', flex: 1 }}
            />
          ))}
        </Box>
      ))}
    </Box>
  );

  const renderListSkeleton = () => (
    <Box sx={{ width: '100%' }}>
      {[...Array(count)].map((_, index) => (
        <Box
          key={index}
          sx={{
            display: 'flex',
            alignItems: 'center',
            gap: 2,
            py: 2,
            px: 2,
            mb: 1,
            bgcolor: '#1A1D23',
            border: '1px solid #242830',
            borderRadius: 1,
          }}
        >
          <Skeleton
            variant="circular"
            width={48}
            height={48}
            sx={{ bgcolor: '#242830' }}
          />
          <Box sx={{ flex: 1 }}>
            <Skeleton
              variant="text"
              width="60%"
              height={24}
              sx={{ bgcolor: '#242830', mb: 1 }}
            />
            <Skeleton
              variant="text"
              width="40%"
              height={20}
              sx={{ bgcolor: '#242830' }}
            />
          </Box>
          <Skeleton
            variant="rectangular"
            width={100}
            height={32}
            sx={{ bgcolor: '#242830' }}
          />
        </Box>
      ))}
    </Box>
  );

  const renderChartSkeleton = () => (
    <Box
      sx={{
        bgcolor: '#1A1D23',
        border: '1px solid #242830',
        borderRadius: 2,
        p: 2,
        height: isMobile ? 250 : 350,
        display: 'flex',
        flexDirection: 'column',
      }}
    >
      <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 2 }}>
        <Skeleton
          variant="text"
          width="30%"
          height={28}
          sx={{ bgcolor: '#242830' }}
        />
        <Skeleton
          variant="rectangular"
          width={120}
          height={32}
          sx={{ bgcolor: '#242830' }}
        />
      </Box>
      <Box sx={{ flex: 1, display: 'flex', alignItems: 'flex-end', gap: 1 }}>
        {[...Array(12)].map((_, index) => (
          <Skeleton
            key={index}
            variant="rectangular"
            width="100%"
            height={`${30 + Math.random() * 70}%`}
            sx={{ bgcolor: '#242830', borderRadius: 1 }}
          />
        ))}
      </Box>
    </Box>
  );

  const renderDashboardSkeleton = () => (
    <Grid container spacing={2}>
      {[...Array(4)].map((_, index) => (
        <Grid item xs={12} sm={6} md={3} key={index}>
          {renderCardSkeleton()}
        </Grid>
      ))}
      <Grid item xs={12}>
        {renderChartSkeleton()}
      </Grid>
      <Grid item xs={12}>
        {renderTableSkeleton()}
      </Grid>
    </Grid>
  );

  switch (variant) {
    case 'card':
      return (
        <Grid container spacing={2}>
          {[...Array(count)].map((_, index) => (
            <Grid item xs={12} sm={6} md={4} lg={3} key={index}>
              {renderCardSkeleton()}
            </Grid>
          ))}
        </Grid>
      );
    case 'table':
      return renderTableSkeleton();
    case 'list':
      return renderListSkeleton();
    case 'chart':
      return renderChartSkeleton();
    case 'dashboard':
      return renderDashboardSkeleton();
    default:
      return renderCardSkeleton();
  }
};
