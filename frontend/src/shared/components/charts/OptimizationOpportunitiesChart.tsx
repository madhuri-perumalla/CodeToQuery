import React from 'react';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend,
} from 'chart.js';
import { Bar } from 'react-chartjs-2';
import { Box, useTheme, useMediaQuery } from '@mui/material';

ChartJS.register(CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend);

interface OptimizationOpportunitiesChartProps {
  data: {
    labels: string[];
    datasets: Array<{
      label: string;
      data: number[];
      backgroundColor: string;
      borderColor: string;
      borderWidth: number;
      yAxisID?: string;
    }>;
  };
}

export const OptimizationOpportunitiesChart: React.FC<OptimizationOpportunitiesChartProps> = ({ data }) => {
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('sm'));

  const options = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: 'top' as const,
        labels: {
          color: '#B0B3B8',
          font: {
            size: isMobile ? 10 : 12,
          },
        },
      },
      tooltip: {
        backgroundColor: '#1A1D23',
        titleColor: '#FFFFFF',
        bodyColor: '#B0B3B8',
        borderColor: '#242830',
        borderWidth: 1,
        padding: 12,
      },
    },
    scales: {
      x: {
        grid: {
          color: '#242830',
          drawBorder: false,
        },
        ticks: {
          color: '#B0B3B8',
          font: {
            size: isMobile ? 10 : 11,
          },
        },
      },
      y: {
        grid: {
          color: '#242830',
          drawBorder: false,
        },
        ticks: {
          color: '#B0B3B8',
          font: {
            size: isMobile ? 10 : 11,
          },
        },
        beginAtZero: true,
        position: 'left' as const,
        title: {
          display: true,
          text: 'Savings ($)',
          color: '#6B7280',
          font: { size: 10 },
        },
      },
      y1: {
        grid: {
          drawOnChartArea: false,
        },
        ticks: {
          color: '#B0B3B8',
          font: {
            size: isMobile ? 10 : 11,
          },
        },
        beginAtZero: true,
        position: 'right' as const,
        title: {
          display: true,
          text: 'Effort (1-10)',
          color: '#6B7280',
          font: { size: 10 },
        },
      },
    },
  };

  return (
    <Box>
      <Bar data={data} options={options} />
    </Box>
  );
};
