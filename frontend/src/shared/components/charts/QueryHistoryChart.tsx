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

interface QueryHistoryChartProps {
  data: Array<{ date: string; duration: number; cost: number; rows: number }>;
}

export const QueryHistoryChart: React.FC<QueryHistoryChartProps> = ({ data }) => {
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('sm'));

  const chartData = {
    labels: data.map((d) => d.date),
    datasets: [
      {
        label: 'Duration (ms)',
        data: data.map((d) => d.duration),
        borderColor: '#3F51B5',
        backgroundColor: 'rgba(63, 81, 181, 0.1)',
        fill: true,
        tension: 0.4,
        borderWidth: 2,
        pointRadius: isMobile ? 2 : 4,
        pointHoverRadius: 6,
        yAxisID: 'y',
      },
      {
        label: 'Cost ($)',
        data: data.map((d) => d.cost),
        borderColor: '#10B981',
        backgroundColor: 'rgba(16, 185, 129, 0.1)',
        fill: true,
        tension: 0.4,
        borderWidth: 2,
        pointRadius: isMobile ? 2 : 4,
        pointHoverRadius: 6,
        yAxisID: 'y1',
      },
      {
        label: 'Rows',
        data: data.map((d) => d.rows),
        borderColor: '#F59E0B',
        backgroundColor: 'rgba(245, 158, 11, 0.1)',
        fill: true,
        tension: 0.4,
        borderWidth: 2,
        pointRadius: isMobile ? 2 : 4,
        pointHoverRadius: 6,
        yAxisID: 'y2',
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
        position: 'left' as const,
        title: {
          display: true,
          text: 'Duration (ms)',
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
        position: 'right' as const,
        title: {
          display: true,
          text: 'Cost ($)',
          color: '#6B7280',
          font: { size: 10 },
        },
      },
      y2: {
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
        title: {
          display: true,
          text: 'Rows',
          color: '#6B7280',
          font: { size: 10 },
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
