import React from 'react';
import {
  Chart as ChartJS,
  ArcElement,
  Tooltip,
  Legend,
} from 'chart.js';
import { Doughnut } from 'react-chartjs-2';
import { Box, useTheme, useMediaQuery } from '@mui/material';

ChartJS.register(ArcElement, Tooltip, Legend);

interface CostDistributionChartProps {
  data: Array<{ category: string; cost: number; percentage: number }>;
}

export const CostDistributionChart: React.FC<CostDistributionChartProps> = ({ data }) => {
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('sm'));

  const colors = [
    '#3F51B5',
    '#2196F3',
    '#10B981',
    '#F59E0B',
    '#EF4444',
    '#8B5CF6',
    '#EC4899',
  ];

  const chartData = {
    labels: data.map((d) => d.category),
    datasets: [
      {
        data: data.map((d) => d.cost),
        backgroundColor: colors,
        borderColor: '#1A1D23',
        borderWidth: 2,
        hoverOffset: 10,
      },
    ],
  };

  const options = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: 'bottom' as const,
        labels: {
          color: '#B0B3B8',
          font: {
            size: isMobile ? 10 : 12,
          },
          padding: isMobile ? 10 : 20,
          usePointStyle: true,
          pointStyle: 'circle',
        },
      },
      tooltip: {
        backgroundColor: '#1A1D23',
        titleColor: '#FFFFFF',
        bodyColor: '#B0B3B8',
        borderColor: '#242830',
        borderWidth: 1,
        padding: 12,
        callbacks: {
          label: (context: unknown) => {
            const index = (context as { dataIndex?: number }).dataIndex;
            if (index === undefined || index < 0 || index >= data.length) return '';
            const item = data[index];
            if (!item) return '';
            return `${item.category}: $${item.cost.toFixed(2)} (${item.percentage}%)`;
          },
        },
      },
    },
    cutout: isMobile ? '60%' : '70%',
  };

  return (
    <Box sx={{ height: isMobile ? 250 : 350, display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
      <Doughnut data={chartData} options={options} />
    </Box>
  );
};
