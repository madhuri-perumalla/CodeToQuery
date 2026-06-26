import { QueryClientProvider } from '@tanstack/react-query';
import { ReactQueryDevtools } from '@tanstack/react-query-devtools';
import { ThemeProvider } from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';
import { Toaster } from 'react-hot-toast';

import { queryClient } from '@/lib/react-query/queryClient';
import { darkTheme, lightTheme } from '@/lib/theme/theme';
import { Router } from './router';
import { useUIStore } from '@/lib/zustand/uiStore';

function App() {
  const { theme } = useUIStore();

  return (
    <QueryClientProvider client={queryClient}>
      <ThemeProvider theme={theme === 'dark' ? darkTheme : lightTheme}>
        <CssBaseline />
        <Router />
        <Toaster
          position="bottom-right"
          toastOptions={{
            duration: 4000,
            style: {
              background: theme === 'dark' ? '#1A1D23' : '#FFFFFF',
              color: theme === 'dark' ? '#FFFFFF' : '#111827',
              border: `1px solid ${theme === 'dark' ? '#242830' : '#E5E7EB'}`,
              borderRadius: '8px',
              padding: '12px 16px',
            },
          }}
        />
        <ReactQueryDevtools initialIsOpen={false} />
      </ThemeProvider>
    </QueryClientProvider>
  );
}

export default App;
