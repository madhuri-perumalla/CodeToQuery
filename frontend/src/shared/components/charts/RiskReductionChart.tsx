import React from 'react';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
} from 'chart.js';
import { Line } from 'react-chartjs-2';
import { Box, useTheme, useMediaQuery } from '@mui/material';

ChartJS.register(CategoryScale, LinearScale, PointElement, LineElement, Title, Tooltip, Legend);

interface RiskReductionChartProps {
  data: {
    labels: string[];
    datasets: Array<{
      label: string;
      data: number[];
      borderColor: string;
      backgroundColor: string;
      fill: boolean;
      tension: number;
      borderWidth: number;
    }>;
  };
}

export const RiskReductionChart: React.FC<RiskReductionChartProps> = ({ data }) => {
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
        title: {
          display: true,
          text: 'Issue Count',
          color: '#6B7280',
          font: { size: 10 },
        },
      },
    },
  };

  return (
    <Box>
      <Line data={data} options={options} />
    </Box>
  );
};
