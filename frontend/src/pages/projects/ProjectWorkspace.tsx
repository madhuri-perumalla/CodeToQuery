import React from 'react';
import { Box, Typography, Tabs, Tab } from '@mui/material';
import { Outlet, useNavigate, useLocation, useParams } from 'react-router-dom';
import { useProjectContext } from '@/contexts/ProjectContext';
import { useProjectById } from '@/lib/react-query';

export const ProjectWorkspace: React.FC = () => {
  const { projectId } = useParams<{ projectId: string }>();
  const navigate = useNavigate();
  const location = useLocation();
  const { setSelectedProjectId, setSelectedProject } = useProjectContext();
  const { data: project, isLoading } = useProjectById(projectId || '');

  React.useEffect(() => {
    if (projectId) {
      setSelectedProjectId(parseInt(projectId));
      if (project) {
        setSelectedProject(project);
      }
    }
  }, [projectId, project, setSelectedProjectId, setSelectedProject]);

  const getTabValue = () => {
    const path = location.pathname;
    if (path.endsWith('/overview')) return 0;
    if (path.endsWith('/queries')) return 1;
    if (path.endsWith('/execution-plans')) return 2;
    if (path.endsWith('/diagnostics')) return 3;
    if (path.endsWith('/suggestions')) return 4;
    if (path.endsWith('/query-groups')) return 5;
    if (path.endsWith('/history')) return 6;
    return 0;
  };

  const handleTabChange = (_event: React.SyntheticEvent, newValue: number) => {
    const routes = ['overview', 'queries', 'execution-plans', 'diagnostics', 'suggestions', 'query-groups', 'history'];
    navigate(`/projects/${projectId}/${routes[newValue]}`);
  };

  if (isLoading) {
    return <Box sx={{ p: 3 }}>Loading...</Box>;
  }

  return (
    <Box sx={{ bgcolor: '#0F1115', minHeight: '100vh' }}>
      {/* Project Header */}
      <Box sx={{ p: 3, borderBottom: '1px solid #242830' }}>
        <Typography variant="h4" sx={{ color: '#FFFFFF', fontWeight: 600, mb: 1 }}>
          {project?.name || 'Project'}
        </Typography>
        <Typography variant="body2" sx={{ color: '#B0B3B8', mb: 2 }}>
          {project?.description || 'No description'}
        </Typography>
        
        {/* Project Stats */}
        <Box sx={{ display: 'flex', gap: 3, flexWrap: 'wrap' }}>
          <Box>
            <Typography variant="caption" sx={{ color: '#6B7280' }}>Last Scan</Typography>
            <Typography variant="body2" sx={{ color: '#E5E7EB' }}>
              {project?.updated_at ? new Date(project.updated_at).toLocaleDateString() : 'Never'}
            </Typography>
          </Box>
          <Box>
            <Typography variant="caption" sx={{ color: '#6B7280' }}>Created</Typography>
            <Typography variant="body2" sx={{ color: '#E5E7EB' }}>
              {project?.created_at ? new Date(project.created_at).toLocaleDateString() : 'N/A'}
            </Typography>
          </Box>
        </Box>
      </Box>

      {/* Project Navigation Tabs */}
      <Box sx={{ bgcolor: '#1A1D23', borderBottom: '1px solid #242830' }}>
        <Tabs
          value={getTabValue()}
          onChange={handleTabChange}
          sx={{
            '& .MuiTabs-indicator': { bgcolor: '#3F51B5' },
            '& .MuiTab-root': { color: '#B0B3B8' },
            '& .MuiTab-root.Mui-selected': { color: '#FFFFFF' },
          }}
        >
          <Tab label="Overview" />
          <Tab label="Queries" />
          <Tab label="Execution Plans" />
          <Tab label="Diagnostics" />
          <Tab label="Suggestions" />
          <Tab label="Query Groups" />
          <Tab label="History" />
        </Tabs>
      </Box>

      {/* Page Content */}
      <Box sx={{ p: 3 }}>
        <Outlet />
      </Box>
    </Box>
  );
};
