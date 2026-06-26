import React, { useRef } from 'react';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  Filler,
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
  Legend,
  Filler
);

interface QueryTrendChartProps {
  data: Array<{ date: string; count: number; cost: number }>;
}

export const QueryTrendChart: React.FC<QueryTrendChartProps> = ({ data }) => {
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('sm'));
  const chartRef = useRef<ChartJS<'line'>>(null);

  const chartData = {
    labels: data.map((d) => d.date),
    datasets: [
      {
        label: 'Query Count',
        data: data.map((d) => d.count),
        borderColor: '#3F51B5',
        backgroundColor: 'rgba(63, 81, 181, 0.1)',
        fill: true,
        tension: 0.4,
        borderWidth: 2,
        pointRadius: isMobile ? 2 : 4,
        pointHoverRadius: 6,
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
      <Line ref={chartRef} data={chartData} options={options} />
    </Box>
  );
};
