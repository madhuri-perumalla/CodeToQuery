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

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend
);

interface PerformanceTrendChartProps {
  data: Array<{ date: string; avgDuration: number; p95Duration: number; p99Duration: number }>;
}

export const PerformanceTrendChart: React.FC<PerformanceTrendChartProps> = ({ data }) => {
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('sm'));

  const chartData = {
    labels: data.map((d) => d.date),
    datasets: [
      {
        label: 'Avg Duration (ms)',
        data: data.map((d) => d.avgDuration),
        borderColor: '#3F51B5',
        backgroundColor: 'rgba(63, 81, 181, 0.1)',
        tension: 0.4,
        borderWidth: 2,
        pointRadius: isMobile ? 2 : 4,
        pointHoverRadius: 6,
      },
      {
        label: 'P95 Duration (ms)',
        data: data.map((d) => d.p95Duration),
        borderColor: '#F59E0B',
        backgroundColor: 'rgba(245, 158, 11, 0.1)',
        tension: 0.4,
        borderWidth: 2,
        pointRadius: isMobile ? 2 : 4,
        pointHoverRadius: 6,
      },
      {
        label: 'P99 Duration (ms)',
        data: data.map((d) => d.p99Duration),
        borderColor: '#EF4444',
        backgroundColor: 'rgba(239, 68, 68, 0.1)',
        tension: 0.4,
        borderWidth: 2,
        pointRadius: isMobile ? 2 : 4,
        pointHoverRadius: 6,
      },
    ],
  };

  const options = {
    responsive: true,
    maintainAspectRatio: false,
    interaction: {
      mode: 'index' as const,
      intersect: false,
    },
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
          maxTicksLimit: isMobile ? 6 : 12,
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
      },
    },
  };

  return (
    <Box sx={{ height: isMobile ? 250 : 350 }}>
      <Line data={chartData} options={options} />
    </Box>
  );
};
