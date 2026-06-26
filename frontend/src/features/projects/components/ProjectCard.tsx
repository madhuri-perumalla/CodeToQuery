import React from 'react';
import { Card, CardContent, Typography, Box } from '@mui/material';
import { FolderOpen } from '@mui/icons-material';
import { useNavigate, useLocation } from 'react-router-dom';
import { useProjectContext } from '@/contexts/ProjectContext';

interface ProjectCardProps {
  project: {
    id: number;
    name: string;
    description: string;
    createdAt: string;
  };
}

export const ProjectCard: React.FC<ProjectCardProps> = ({ project }) => {
  const navigate = useNavigate();
  const location = useLocation();
  const { setSelectedProjectId, setSelectedProject } = useProjectContext();

  const handleCardClick = () => {
    setSelectedProjectId(project.id);
    setSelectedProject(project);
    
    // Preserve the current page context when navigating to a project
    const currentPath = location.pathname;
    if (currentPath.startsWith('/queries')) {
      navigate(`/projects/${project.id}/queries`);
    } else if (currentPath.startsWith('/execution-plans')) {
      navigate(`/projects/${project.id}/execution-plans`);
    } else if (currentPath.startsWith('/diagnostics')) {
      navigate(`/projects/${project.id}/diagnostics`);
    } else if (currentPath.startsWith('/query-groups')) {
      navigate(`/projects/${project.id}/analysis`);
    } else if (currentPath.startsWith('/suggestions')) {
      navigate(`/projects/${project.id}/diagnostics`);
    } else if (currentPath.startsWith('/analysis-history')) {
      navigate(`/projects/${project.id}/summary`);
    } else {
      navigate(`/projects/${project.id}`);
    }
  };

  return (
    <Card
      onClick={handleCardClick}
      sx={{
        bgcolor: '#1A1D23',
        border: '1px solid #242830',
        borderRadius: 2,
        height: '100%',
        transition: 'transform 0.2s, box-shadow 0.2s',
        cursor: 'pointer',
        '&:hover': {
          transform: 'translateY(-4px)',
          boxShadow: '0 8px 24px rgba(0, 0, 0, 0.3)',
          borderColor: '#3F51B5',
        },
      }}
    >
      <CardContent>
        <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
          <Box
            sx={{
              width: 48,
              height: 48,
              borderRadius: 2,
              bgcolor: 'rgba(63, 81, 181, 0.1)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              mr: 2,
            }}
          >
            <FolderOpen sx={{ color: '#3F51B5', fontSize: 24 }} />
          </Box>
          <Box sx={{ flex: 1 }}>
            <Typography variant="h6" sx={{ color: '#FFFFFF', fontWeight: 600 }}>
              {project.name}
            </Typography>
            <Typography variant="caption" sx={{ color: '#6B7280' }}>
              Created: {new Date(project.createdAt).toLocaleDateString()}
            </Typography>
          </Box>
        </Box>
        <Typography variant="body2" sx={{ color: '#B0B3B8', minHeight: 40 }}>
          {project.description || 'No description provided'}
        </Typography>
      </CardContent>
    </Card>
  );
};
