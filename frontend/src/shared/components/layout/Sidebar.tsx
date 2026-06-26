import React, { useState } from 'react';
import {
  Box,
  List,
  ListItem,
  ListItemButton,
  ListItemIcon,
  ListItemText,
  Typography,
  Collapse,
  Divider,
  Tooltip,
  IconButton,
} from '@mui/material';
import {
  Dashboard,
  FolderOpen,
  Settings,
  ExpandLess,
  ExpandMore,
  Storage,
  Assessment,
  Warning,
  Lightbulb,
  GroupWork,
  History,
  ChevronLeft,
  ChevronRight,
  PlayArrow,
  Code,
} from '@mui/icons-material';
import { useNavigate, useLocation } from 'react-router-dom';
import { useUIStore } from '@/lib/zustand/uiStore';
import { NAVIGATION_ITEMS } from '@/lib/routes/constants';

interface NavItem {
  id: string;
  label: string;
  icon: React.ReactNode;
  path?: string;
  children?: NavItem[];
  group?: string;
}

const iconMap: Record<string, React.ReactNode> = {
  Dashboard: <Dashboard />,
  FolderOpen: <FolderOpen />,
  PlayArrow: <PlayArrow />,
  Search: <Storage />,
  Timeline: <Assessment />,
  Warning: <Warning />,
  Lightbulb: <Lightbulb />,
  GroupWork: <GroupWork />,
  History: <History />,
  Code: <Code />,
  Settings: <Settings />,
};

const navigationItems: NavItem[] = NAVIGATION_ITEMS.map((item) => ({
  id: item.label.toLowerCase().replace(/\s+/g, '-'),
  label: item.label,
  icon: iconMap[item.icon] || <Storage />,
  path: item.path,
  group: item.label === 'Dashboard' || item.label === 'Projects' ? 'Main' : 
        item.label === 'Codebases' || item.label === 'Settings' ? 'System' : 'Analysis',
}));

export const Sidebar: React.FC = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const { sidebarCollapsed, toggleSidebarCollapse } = useUIStore();
  const [expandedGroups, setExpandedGroups] = useState<Record<string, boolean>>({
    Main: true,
    Analysis: true,
    System: false,
  });

  const handleGroupToggle = (group: string) => {
    setExpandedGroups((prev) => ({ ...prev, [group]: !prev[group] }));
  };

  const handleNavigation = (path: string) => {
    navigate(path);
  };

  const isActive = (path: string) => {
    return location.pathname === path || location.pathname.startsWith(path + '/');
  };

  // Group items by group
  const groupedItems = navigationItems.reduce((acc, item) => {
    const group = item.group || 'Other';
    if (!acc[group]) {
      acc[group] = [];
    }
    acc[group].push(item);
    return acc;
  }, {} as Record<string, NavItem[]>);

  return (
    <Box
      sx={{
        width: sidebarCollapsed ? 72 : 280,
        bgcolor: '#14171C',
        borderRight: '1px solid #242830',
        height: '100vh',
        display: 'flex',
        flexDirection: 'column',
        transition: 'width 0.3s ease',
        position: 'fixed',
        left: 0,
        top: 0,
        zIndex: 1100,
      }}
    >
      {/* Logo Section */}
      <Box
        sx={{
          height: 64,
          display: 'flex',
          alignItems: 'center',
          justifyContent: sidebarCollapsed ? 'center' : 'space-between',
          px: sidebarCollapsed ? 0 : 2,
          borderBottom: '1px solid #242830',
        }}
      >
        {!sidebarCollapsed && (
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <Box
              sx={{
                width: 32,
                height: 32,
                bgcolor: '#3F51B5',
                borderRadius: 1,
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
              }}
            >
              <Storage sx={{ color: '#FFFFFF', fontSize: 20 }} />
            </Box>
            <Typography variant="h6" sx={{ color: '#FFFFFF', fontWeight: 700 }}>
              CodeToQuery
            </Typography>
          </Box>
        )}
        <IconButton
          onClick={toggleSidebarCollapse}
          sx={{
            color: '#B0B3B8',
            mx: sidebarCollapsed ? 0 : 1,
            '&:hover': { bgcolor: 'rgba(255, 255, 255, 0.05)' },
          }}
        >
          {sidebarCollapsed ? <ChevronRight /> : <ChevronLeft />}
        </IconButton>
      </Box>

      {/* Navigation */}
      <Box sx={{ flex: 1, overflowY: 'auto', py: 2 }}>
        {Object.entries(groupedItems).map(([group, items]) => (
          <Box key={group}>
            {!sidebarCollapsed && (
              <Box
                sx={{
                  px: 3,
                  py: 1,
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'space-between',
                  cursor: 'pointer',
                  '&:hover': { bgcolor: 'rgba(255, 255, 255, 0.02)' },
                }}
                onClick={() => handleGroupToggle(group)}
              >
                <Typography
                  variant="caption"
                  sx={{
                    color: '#6B7280',
                    fontWeight: 600,
                    textTransform: 'uppercase',
                    letterSpacing: '0.05em',
                    fontSize: '0.75rem',
                  }}
                >
                  {group}
                </Typography>
                {expandedGroups[group] ? (
                  <ExpandLess sx={{ color: '#6B7280', fontSize: 16 }} />
                ) : (
                  <ExpandMore sx={{ color: '#6B7280', fontSize: 16 }} />
                )}
              </Box>
            )}
            <Collapse in={sidebarCollapsed || expandedGroups[group]}>
              <List sx={{ px: sidebarCollapsed ? 1 : 2 }}>
                {items.map((item) => (
                  <ListItem key={item.id} disablePadding sx={{ mb: 0.5 }}>
                    <Tooltip title={sidebarCollapsed ? item.label : ''} placement="right">
                      <ListItemButton
                        onClick={() => item.path && handleNavigation(item.path)}
                        selected={item.path ? isActive(item.path) : false}
                        sx={{
                          borderRadius: 2,
                          py: 1,
                          px: sidebarCollapsed ? 1.5 : 2,
                          minHeight: 40,
                          '&.Mui-selected': {
                            bgcolor: '#3F51B5',
                            '&:hover': {
                              bgcolor: '#3949AB',
                            },
                          },
                          '&:hover': {
                            bgcolor: 'rgba(255, 255, 255, 0.05)',
                          },
                        }}
                      >
                        <ListItemIcon
                          sx={{
                            color: item.path && isActive(item.path) ? '#FFFFFF' : '#B0B3B8',
                            minWidth: sidebarCollapsed ? 'auto' : 40,
                            justifyContent: sidebarCollapsed ? 'center' : 'flex-start',
                          }}
                        >
                          {item.icon}
                        </ListItemIcon>
                        {!sidebarCollapsed && (
                          <ListItemText
                            primary={item.label}
                            sx={{
                              color: item.path && isActive(item.path) ? '#FFFFFF' : '#B0B3B8',
                              '& .MuiTypography-root': {
                                fontSize: '0.875rem',
                                fontWeight: item.path && isActive(item.path) ? 600 : 500,
                              },
                            }}
                          />
                        )}
                      </ListItemButton>
                    </Tooltip>
                  </ListItem>
                ))}
              </List>
            </Collapse>
            {!sidebarCollapsed && <Divider sx={{ my: 1, borderColor: '#242830' }} />}
          </Box>
        ))}
      </Box>

      {/* Footer Section */}
      {!sidebarCollapsed && (
        <Box
          sx={{
            p: 2,
            borderTop: '1px solid #242830',
            bgcolor: '#0F1115',
          }}
        >
          <Typography variant="caption" sx={{ color: '#6B7280', display: 'block', mb: 1 }}>
            Version 1.0.0
          </Typography>
          <Typography variant="caption" sx={{ color: '#4B5563', display: 'block' }}>
            © 2024 CodeToQuery
          </Typography>
        </Box>
      )}
    </Box>
  );
};
