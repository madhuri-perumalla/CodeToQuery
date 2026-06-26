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

interface PatternFrequencyChartProps {
  data: {
    labels: string[];
    datasets: Array<{
      label: string;
      data: number[];
      backgroundColor: string[];
      borderColor: string[];
      borderWidth: number;
    }>;
  };
}

export const PatternFrequencyChart: React.FC<PatternFrequencyChartProps> = ({ data }) => {
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('sm'));

  const options = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        display: false,
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
            const total = (context as any).dataset.data.reduce((a: number, b: number) => a + b, 0);
            const value = (context as any).raw;
            const percentage = ((value / total) * 100).toFixed(1);
            return `${(context as any).dataset.label}: ${value} (${percentage}%)`;
          },
        },
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
