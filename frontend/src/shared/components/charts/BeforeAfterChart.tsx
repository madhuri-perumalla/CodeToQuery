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

interface BeforeAfterChartProps {
  data: {
    labels: string[];
    datasets: Array<{
      label: string;
      data: number[];
      backgroundColor: string;
      borderColor: string;
      borderWidth: number;
    }>;
  };
}

export const BeforeAfterChart: React.FC<BeforeAfterChartProps> = ({ data }) => {
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
      },
    },
  };

  return (
    <Box>
      <Bar data={data} options={options} />
    </Box>
  );
};
