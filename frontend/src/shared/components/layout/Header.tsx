import React from 'react';
import {
  Box,
  Toolbar,
  IconButton,
  Typography,
  Avatar,
  Badge,
  Menu,
  MenuItem,
  Divider,
  useMediaQuery,
  useTheme,
} from '@mui/material';
import {
  Menu as MenuIcon,
  Search,
  Notifications,
  AccountCircle,
  Brightness4,
  Brightness7,
  Logout,
  Settings,
} from '@mui/icons-material';
import { useUIStore } from '@/lib/zustand/uiStore';
import { useNavigate } from 'react-router-dom';
import { useProjectContext } from '@/contexts/ProjectContext';
import { ProjectSelector } from '@/shared/components/data-display/ProjectSelector';

export const Header: React.FC = () => {
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('md'));
  const navigate = useNavigate();
  const { theme: currentTheme, setTheme, toggleSidebar, notifications } = useUIStore();
  const { selectedProjectId, setSelectedProjectId, selectedProject } = useProjectContext();
  const [anchorEl, setAnchorEl] = React.useState<null | HTMLElement>(null);
  const [notificationAnchor, setNotificationAnchor] = React.useState<null | HTMLElement>(null);

  const handleProfileMenuOpen = (event: React.MouseEvent<HTMLElement>) => {
    setAnchorEl(event.currentTarget);
  };

  const handleNotificationMenuOpen = (event: React.MouseEvent<HTMLElement>) => {
    setNotificationAnchor(event.currentTarget);
  };

  const handleMenuClose = () => {
    setAnchorEl(null);
    setNotificationAnchor(null);
  };

  const handleThemeToggle = () => {
    setTheme(currentTheme === 'dark' ? 'light' : 'dark');
  };

  const handleLogout = () => {
    handleMenuClose();
    navigate('/login');
  };

  return (
    <Box
      sx={{
        bgcolor: '#14171C',
        borderBottom: '1px solid #242830',
        height: 64,
        position: 'fixed',
        top: 0,
        right: 0,
        left: 0,
        zIndex: 1000,
        ml: { lg: '72px' },
      }}
    >
      <Toolbar
        sx={{
          minHeight: '64px !important',
          px: { xs: 2, sm: 3 },
        }}
      >
        {/* Mobile Menu Button */}
        {isMobile && (
          <IconButton
            edge="start"
            onClick={toggleSidebar}
            sx={{ mr: 2, color: '#B0B3B8' }}
          >
            <MenuIcon />
          </IconButton>
        )}

        {/* Project Selector */}
        <ProjectSelector />

        {/* Page Title */}
        <Typography
          variant="h6"
          sx={{
            flexGrow: 1,
            color: '#FFFFFF',
            fontWeight: 600,
            fontSize: { xs: '1rem', sm: '1.25rem' },
          }}
        >
          {selectedProject ? selectedProject.name : 'Dashboard'}
        </Typography>

        {/* Right Actions */}
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          {/* Theme Toggle */}
          <IconButton
            onClick={handleThemeToggle}
            sx={{ color: '#B0B3B8', '&:hover': { bgcolor: 'rgba(255, 255, 255, 0.05)' } }}
          >
            {currentTheme === 'dark' ? <Brightness7 /> : <Brightness4 />}
          </IconButton>

          {/* Search Button */}
          <IconButton
            sx={{ color: '#B0B3B8', '&:hover': { bgcolor: 'rgba(255, 255, 255, 0.05)' } }}
          >
            <Search />
          </IconButton>

          {/* Notifications */}
          <IconButton
            onClick={handleNotificationMenuOpen}
            sx={{ color: '#B0B3B8', '&:hover': { bgcolor: 'rgba(255, 255, 255, 0.05)' } }}
          >
            <Badge badgeContent={notifications} color="error">
              <Notifications />
            </Badge>
          </IconButton>

          {/* Profile */}
          <IconButton
            onClick={handleProfileMenuOpen}
            sx={{ color: '#B0B3B8', '&:hover': { bgcolor: 'rgba(255, 255, 255, 0.05)' } }}
          >
            <Avatar sx={{ bgcolor: '#3F51B5', width: 32, height: 32 }}>
              <AccountCircle />
            </Avatar>
          </IconButton>
        </Box>
      </Toolbar>

      {/* Profile Menu */}
      <Menu
        anchorEl={anchorEl}
        open={Boolean(anchorEl)}
        onClose={handleMenuClose}
        anchorOrigin={{ vertical: 'bottom', horizontal: 'right' }}
        transformOrigin={{ vertical: 'top', horizontal: 'right' }}
        PaperProps={{
          sx: {
            bgcolor: '#1A1D23',
            border: '1px solid #242830',
            minWidth: 200,
            mt: 1,
          },
        }}
      >
        <MenuItem
          onClick={() => {
            handleMenuClose();
            navigate('/settings');
          }}
          sx={{ color: '#FFFFFF', '&:hover': { bgcolor: 'rgba(63, 81, 181, 0.1)' } }}
        >
          <Settings sx={{ mr: 2, fontSize: 20 }} />
          Settings
        </MenuItem>
        <Divider sx={{ borderColor: '#242830' }} />
        <MenuItem
          onClick={handleLogout}
          sx={{ color: '#EF4444', '&:hover': { bgcolor: 'rgba(239, 68, 68, 0.1)' } }}
        >
          <Logout sx={{ mr: 2, fontSize: 20 }} />
          Logout
        </MenuItem>
      </Menu>

      {/* Notification Menu */}
      <Menu
        anchorEl={notificationAnchor}
        open={Boolean(notificationAnchor)}
        onClose={handleMenuClose}
        anchorOrigin={{ vertical: 'bottom', horizontal: 'right' }}
        transformOrigin={{ vertical: 'top', horizontal: 'right' }}
        PaperProps={{
          sx: {
            bgcolor: '#1A1D23',
            border: '1px solid #242830',
            minWidth: 320,
            maxHeight: 400,
            mt: 1,
          },
        }}
      >
        <Box sx={{ p: 2, borderBottom: '1px solid #242830' }}>
          <Typography variant="subtitle2" sx={{ color: '#FFFFFF', fontWeight: 600 }}>
            Notifications
          </Typography>
        </Box>
        <Box sx={{ maxHeight: 300, overflowY: 'auto' }}>
          {[1, 2, 3].map((item) => (
            <MenuItem
              key={item}
              onClick={handleMenuClose}
              sx={{
                color: '#FFFFFF',
                py: 2,
                px: 2,
                borderBottom: '1px solid #242830',
                '&:hover': { bgcolor: 'rgba(63, 81, 181, 0.1)' },
              }}
            >
              <Box>
                <Typography variant="body2" sx={{ fontWeight: 500, mb: 0.5 }}>
                  Query Analysis Complete
                </Typography>
                <Typography variant="caption" sx={{ color: '#B0B3B8' }}>
                  Analysis for project {item} has completed successfully
                </Typography>
              </Box>
            </MenuItem>
          ))}
        </Box>
        <Box sx={{ p: 2, borderTop: '1px solid #242830' }}>
          <Typography
            variant="caption"
            sx={{ color: '#3F51B5', cursor: 'pointer', '&:hover': { textDecoration: 'underline' } }}
          >
            View all notifications
          </Typography>
        </Box>
      </Menu>
    </Box>
  );
};
