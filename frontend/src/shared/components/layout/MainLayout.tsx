import React from 'react';
import { Box, useMediaQuery, useTheme, SwipeableDrawer, Backdrop } from '@mui/material';
import { Sidebar } from './Sidebar';
import { Header } from './Header';
import { Footer } from './Footer';
import { Breadcrumbs } from '../data-display/Breadcrumbs';
import { SearchBar } from '../data-display/SearchBar';
import { useUIStore } from '@/lib/zustand/uiStore';

export const MainLayout: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('md'));
  const { sidebarOpen, setSidebarOpen, sidebarCollapsed } = useUIStore();

  const handleSidebarClose = () => {
    setSidebarOpen(false);
  };

  const sidebarWidth = sidebarCollapsed ? 72 : 280;

  return (
    <Box sx={{ display: 'flex', minHeight: '100vh', bgcolor: '#0F1115' }}>
      {/* Desktop Sidebar */}
      {!isMobile && <Sidebar />}

      {/* Mobile Sidebar Drawer */}
      {isMobile && (
        <>
          <SwipeableDrawer
            anchor="left"
            open={sidebarOpen}
            onClose={handleSidebarClose}
            onOpen={() => setSidebarOpen(true)}
            sx={{
              '& .MuiDrawer-paper': {
                width: 280,
                bgcolor: '#14171C',
                borderRight: '1px solid #242830',
              },
            }}
          >
            <Sidebar />
          </SwipeableDrawer>
          <Backdrop
            sx={{ color: '#fff', zIndex: 999 }}
            open={sidebarOpen}
            onClick={handleSidebarClose}
          />
        </>
      )}

      {/* Main Content Area */}
      <Box
        sx={{
          flex: 1,
          display: 'flex',
          flexDirection: 'column',
          ml: isMobile ? 0 : sidebarWidth,
          transition: 'margin-left 0.3s ease',
          width: isMobile ? '100%' : `calc(100% - ${sidebarWidth}px)`,
        }}
      >
        {/* Header */}
        <Header />

        {/* Main Content */}
        <Box
          component="main"
          sx={{
            flex: 1,
            display: 'flex',
            flexDirection: 'column',
            overflow: 'hidden',
            pt: '64px', // Header height
          }}
        >
          {/* Content Container */}
          <Box
            sx={{
              flex: 1,
              overflowY: 'auto',
              p: { xs: 2, sm: 3, md: 4 },
            }}
          >
            {/* Breadcrumbs */}
            <Breadcrumbs />

            {/* Search Bar */}
            <Box sx={{ mb: 3 }}>
              <SearchBar fullWidth={isMobile} />
            </Box>

            {/* Page Content */}
            {children}
          </Box>

          {/* Footer */}
          <Footer showFullFooter={!isMobile} />
        </Box>
      </Box>
    </Box>
  );
};
