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

interface QueryTypesChartProps {
  data: Array<{ type: string; count: number; avgDuration: number }>;
}

export const QueryTypesChart: React.FC<QueryTypesChartProps> = ({ data }) => {
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('sm'));

  const chartData = {
    labels: data.map((d) => d.type),
    datasets: [
      {
        label: 'Query Count',
        data: data.map((d) => d.count),
        backgroundColor: '#3F51B5',
        borderColor: '#3F51B5',
        borderWidth: 1,
        borderRadius: 4,
        barThickness: isMobile ? 20 : 30,
      },
      {
        label: 'Avg Duration (ms)',
        data: data.map((d) => d.avgDuration),
        backgroundColor: '#10B981',
        borderColor: '#10B981',
        borderWidth: 1,
        borderRadius: 4,
        barThickness: isMobile ? 20 : 30,
        yAxisID: 'y1',
      },
    ],
  };

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
          maxRotation: 45,
          minRotation: 0,
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
        position: 'left' as const,
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
        position: 'right' as const,
      },
    },
  };

  return (
    <Box sx={{ height: isMobile ? 250 : 350 }}>
      <Bar data={chartData} options={options} />
    </Box>
  );
};
