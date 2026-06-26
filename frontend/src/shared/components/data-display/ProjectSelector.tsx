import React from 'react';
import { Box, Select, MenuItem, FormControl, InputLabel, Typography, Chip } from '@mui/material';
import { Folder } from '@mui/icons-material';
import { useProjects } from '@/lib/react-query/hooks';
import { useProjectContext } from '@/contexts/ProjectContext';
import { LoadingSkeleton } from '@/shared/components/loading';
import { useCodebases } from '@/lib/react-query/hooks';

interface ProjectSelectorProps {
  label?: string;
  size?: 'small' | 'medium';
  sx?: any;
}

export const ProjectSelector: React.FC<ProjectSelectorProps> = ({
  label = 'Project',
  size = 'small',
  sx = {},
}) => {
  const { selectedProjectId, setSelectedProjectId, selectedProject, setSelectedProject, selectedCodebaseId, setSelectedCodebaseId, selectedCodebase, setSelectedCodebase } = useProjectContext();
  const { data: projectsData, isLoading, error } = useProjects(1, 100);
  const { data: codebasesData } = useCodebases(selectedProjectId || undefined);

  const projects = projectsData?.items || [];
  const codebases = codebasesData?.items || [];

  const handleProjectChange = (event: any) => {
    const projectId = event.target.value;
    const project = projects.find((p: any) => p.id === projectId);
    
    if (project) {
      setSelectedProjectId(projectId);
      setSelectedProject(project);
      
      // Auto-select the first codebase for this project
      const projectCodebases = codebases.filter((c: any) => c.project_id === projectId);
      if (projectCodebases.length > 0) {
        setSelectedCodebaseId(projectCodebases[0].id);
        setSelectedCodebase(projectCodebases[0]);
      } else {
        setSelectedCodebaseId(null);
        setSelectedCodebase(null);
      }
    }
  };

  const handleCodebaseChange = (event: any) => {
    const codebaseId = event.target.value;
    const codebase = codebases.find((c: any) => c.id === codebaseId);
    
    if (codebase) {
      setSelectedCodebaseId(codebaseId);
      setSelectedCodebase(codebase);
    }
  };

  if (isLoading) {
    return (
      <Box sx={{ minWidth: 200, ...sx }}>
        <LoadingSkeleton variant="text" width={200} />
      </Box>
    );
  }

  if (error) {
    return (
      <Box sx={{ minWidth: 200, ...sx }}>
        <Typography variant="body2" sx={{ color: '#DC2626' }}>
          Error loading projects
        </Typography>
      </Box>
    );
  }

  if (projects.length === 0) {
    return (
      <Box sx={{ minWidth: 200, ...sx }}>
        <Typography variant="body2" sx={{ color: '#6B7280' }}>
          No projects available
        </Typography>
      </Box>
    );
  }

  return (
    <Box sx={{ minWidth: 200, ...sx }}>
      <FormControl fullWidth size={size} sx={{ mb: 1 }}>
        <InputLabel 
          sx={{ 
            color: '#B0B3B8',
            '&.Mui-focused': { color: '#3F51B5' },
          }}
        >
          {label}
        </InputLabel>
        <Select
          value={selectedProjectId || ''}
          onChange={handleProjectChange}
          label={label}
          sx={{
            bgcolor: '#1A1D23',
            color: '#E5E7EB',
            border: '1px solid #242830',
            '& .MuiOutlinedInput-notchedOutline': {
              borderColor: '#242830',
            },
            '&:hover .MuiOutlinedInput-notchedOutline': {
              borderColor: '#3F51B5',
            },
            '& .MuiSvgIcon-root': {
              color: '#B0B3B8',
            },
          }}
          MenuProps={{
            PaperProps: {
              sx: {
                bgcolor: '#1A1D23',
                border: '1px solid #242830',
                '& .MuiMenuItem-root': {
                  color: '#E5E7EB',
                  '&:hover': {
                    bgcolor: '#242830',
                  },
                  '&.Mui-selected': {
                    bgcolor: '#242830',
                  },
                },
              },
            },
          }}
        >
          {projects.map((project: any) => (
            <MenuItem key={project.id} value={project.id}>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, width: '100%' }}>
                <Folder sx={{ fontSize: 18, color: '#3F51B5' }} />
                <Typography variant="body2">{project.name}</Typography>
                {project.status && (
                  <Chip
                    label={project.status}
                    size="small"
                    sx={{
                      ml: 'auto',
                      bgcolor: project.status === 'active' ? 'rgba(16, 185, 129, 0.1)' : 'rgba(107, 114, 128, 0.1)',
                      color: project.status === 'active' ? '#10B981' : '#6B7280',
                      fontSize: '0.7rem',
                      height: 20,
                    }}
                  />
                )}
              </Box>
            </MenuItem>
          ))}
        </Select>
      </FormControl>

      {selectedProjectId && codebases.length > 0 && (
        <FormControl fullWidth size={size}>
          <InputLabel 
            sx={{ 
              color: '#B0B3B8',
              '&.Mui-focused': { color: '#3F51B5' },
            }}
          >
            Codebase
          </InputLabel>
          <Select
            value={selectedCodebaseId || ''}
            onChange={handleCodebaseChange}
            label="Codebase"
            sx={{
              bgcolor: '#1A1D23',
              color: '#E5E7EB',
              border: '1px solid #242830',
              '& .MuiOutlinedInput-notchedOutline': {
                borderColor: '#242830',
              },
              '&:hover .MuiOutlinedInput-notchedOutline': {
                borderColor: '#3F51B5',
              },
              '& .MuiSvgIcon-root': {
                color: '#B0B3B8',
              },
            }}
            MenuProps={{
              PaperProps: {
                sx: {
                  bgcolor: '#1A1D23',
                  border: '1px solid #242830',
                  '& .MuiMenuItem-root': {
                    color: '#E5E7EB',
                    '&:hover': {
                      bgcolor: '#242830',
                    },
                    '&.Mui-selected': {
                      bgcolor: '#242830',
                    },
                  },
                },
              },
            }}
          >
            {codebases
              .filter((c: any) => c.project_id === selectedProjectId)
              .map((codebase: any) => (
              <MenuItem key={codebase.id} value={codebase.id}>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, width: '100%' }}>
                  <Typography variant="body2">{codebase.scan_path || `Codebase #${codebase.id}`}</Typography>
                  <Chip
                    label={codebase.status}
                    size="small"
                    sx={{
                      ml: 'auto',
                      bgcolor: codebase.status === 'completed' ? 'rgba(16, 185, 129, 0.1)' : 
                             codebase.status === 'scanning' ? 'rgba(245, 158, 11, 0.1)' : 'rgba(107, 114, 128, 0.1)',
                      color: codebase.status === 'completed' ? '#10B981' : 
                             codebase.status === 'scanning' ? '#F59E0B' : '#6B7280',
                      fontSize: '0.7rem',
                      height: 20,
                    }}
                  />
                </Box>
              </MenuItem>
            ))}
          </Select>
        </FormControl>
      )}
    </Box>
  );
};
