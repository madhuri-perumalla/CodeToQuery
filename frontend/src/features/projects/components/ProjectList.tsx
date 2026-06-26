import React, { useState } from 'react';
import { Box, Typography, Button, Grid, Dialog, DialogTitle, DialogContent, DialogActions, TextField, MenuItem, FormControl, InputLabel, Select, Tabs, Tab, Box as MuiBox, Paper, Chip } from '@mui/material';
import { GitHub, Folder } from '@mui/icons-material';
import { useProjects } from '@/lib/react-query';
import { useCreateProject } from '@/features/projects/services/projectService';
import { ProjectCard } from './ProjectCard';

interface TabPanelProps {
  children?: React.ReactNode;
  index: number;
  value: number;
}

function TabPanel(props: TabPanelProps) {
  const { children, value, index, ...other } = props;
  return (
    <div
      role="tabpanel"
      hidden={value !== index}
      id={`project-tabpanel-${index}`}
      aria-labelledby={`project-tab-${index}`}
      {...other}
    >
      {value === index && <MuiBox sx={{ py: 3 }}>{children}</MuiBox>}
    </div>
  );
}

export const ProjectList: React.FC = () => {
  const { data: projects, isLoading, error } = useProjects();
  const createProject = useCreateProject();
  const [open, setOpen] = useState(false);
  const [tabValue, setTabValue] = useState(0);
  const [projectName, setProjectName] = useState('');
  const [codebaseType, setCodebaseType] = useState<'github' | 'local' | 'upload'>('github');
  const [repoUrl, setRepoUrl] = useState('');
  const [localPath, setLocalPath] = useState('');
  const [techStack, setTechStack] = useState<string[]>([]);

  const handleCreateProject = async () => {
    try {
      const config = {
        codebase: {
          type: codebaseType,
          source: codebaseType === 'github' ? repoUrl : localPath,
        },
        extraction: {
          include_patterns: ['*.sql', '*.py', '*.js', '*.ts', '*.java'],
          exclude_patterns: ['node_modules', 'venv', '.git', '__pycache__', 'dist'],
        },
        techStack: techStack,
      };

      await createProject.mutateAsync({
        name: projectName,
        description: `Codebase analysis for ${codebaseType === 'github' ? repoUrl : localPath}`,
        config: config,
      });
      setOpen(false);
      resetForm();
    } catch (error) {
      console.error('Failed to create project:', error);
    }
  };

  const resetForm = () => {
    setProjectName('');
    setCodebaseType('github');
    setRepoUrl('');
    setLocalPath('');
    setTechStack([]);
    setTabValue(0);
  };

  if (isLoading) return <div>Loading...</div>;
  if (error) return <div>Error loading projects</div>;

  return (
    <Box>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Box>
          <Typography variant="h4">Codebase Analysis Projects</Typography>
          <Typography variant="body2" sx={{ color: '#9CA3AF', mt: 1 }}>
            Analyze SQL queries and patterns from your codebase
          </Typography>
        </Box>
        <Button variant="contained" onClick={() => setOpen(true)}>Analyze Codebase</Button>
      </Box>

      <Grid container spacing={3}>
        {projects?.items.map((project) => (
          <Grid item xs={12} sm={6} md={4} key={project.id}>
            <ProjectCard project={project} />
          </Grid>
        ))}
      </Grid>

      <Dialog open={open} onClose={() => setOpen(false)} maxWidth="md" fullWidth>
        <DialogTitle>Analyze New Codebase</DialogTitle>
        <DialogContent>
          <Tabs value={tabValue} onChange={(_e, newValue) => setTabValue(newValue)} sx={{ borderBottom: 1, borderColor: 'divider' }}>
            <Tab label="Codebase Source" />
            <Tab label="Analysis Settings" />
          </Tabs>

          <TabPanel value={tabValue} index={0}>
            <TextField
              autoFocus
              margin="dense"
              label="Project Name"
              fullWidth
              variant="outlined"
              value={projectName}
              onChange={(e) => setProjectName(e.target.value)}
              helperText="Name for this codebase analysis"
            />
            
            <Box sx={{ mt: 3 }}>
              <Typography variant="subtitle1" sx={{ mb: 2, color: '#FFFFFF' }}>Select Codebase Source</Typography>
              
              <Grid container spacing={2}>
                <Grid item xs={12}>
                  <Paper
                    onClick={() => setCodebaseType('github')}
                    sx={{
                      p: 2,
                      border: codebaseType === 'github' ? '2px solid #3F51B5' : '1px solid #242830',
                      bgcolor: codebaseType === 'github' ? 'rgba(63, 81, 181, 0.1)' : '#1A1D23',
                      cursor: 'pointer',
                      display: 'flex',
                      alignItems: 'center',
                      gap: 2,
                    }}
                  >
                    <GitHub sx={{ color: '#FFFFFF' }} />
                    <Box>
                      <Typography variant="subtitle2" sx={{ color: '#FFFFFF' }}>GitHub Repository</Typography>
                      <Typography variant="caption" sx={{ color: '#9CA3AF' }}>Analyze a public or private GitHub repository</Typography>
                    </Box>
                  </Paper>
                </Grid>
                
                <Grid item xs={12}>
                  <Paper
                    onClick={() => setCodebaseType('local')}
                    sx={{
                      p: 2,
                      border: codebaseType === 'local' ? '2px solid #3F51B5' : '1px solid #242830',
                      bgcolor: codebaseType === 'local' ? 'rgba(63, 81, 181, 0.1)' : '#1A1D23',
                      cursor: 'pointer',
                      display: 'flex',
                      alignItems: 'center',
                      gap: 2,
                    }}
                  >
                    <Folder sx={{ color: '#FFFFFF' }} />
                    <Box>
                      <Typography variant="subtitle2" sx={{ color: '#FFFFFF' }}>Local Folder</Typography>
                      <Typography variant="caption" sx={{ color: '#9CA3AF' }}>Analyze a local directory on your machine</Typography>
                    </Box>
                  </Paper>
                </Grid>
              </Grid>

              {codebaseType === 'github' && (
                <TextField
                  margin="dense"
                  label="Repository URL"
                  fullWidth
                  variant="outlined"
                  placeholder="https://github.com/username/repo"
                  value={repoUrl}
                  onChange={(e) => setRepoUrl(e.target.value)}
                  sx={{ mt: 2 }}
                  helperText="Enter the full GitHub repository URL"
                />
              )}

              {codebaseType === 'local' && (
                <TextField
                  margin="dense"
                  label="Local Path"
                  fullWidth
                  variant="outlined"
                  placeholder="/path/to/your/codebase"
                  value={localPath}
                  onChange={(e) => setLocalPath(e.target.value)}
                  sx={{ mt: 2 }}
                  helperText="Enter the absolute path to your codebase directory"
                />
              )}
            </Box>
          </TabPanel>

          <TabPanel value={tabValue} index={1}>
            <FormControl fullWidth margin="dense">
              <InputLabel>Technology Stack</InputLabel>
              <Select
                multiple
                value={techStack}
                onChange={(e) => setTechStack(typeof e.target.value === 'string' ? e.target.value.split(',') : e.target.value)}
                label="Technology Stack"
                renderValue={(selected) => (
                  <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5 }}>
                    {selected.map((value) => (
                      <Chip key={value} label={value} />
                    ))}
                  </Box>
                )}
              >
                <MenuItem value="python">Python</MenuItem>
                <MenuItem value="javascript">JavaScript</MenuItem>
                <MenuItem value="typescript">TypeScript</MenuItem>
                <MenuItem value="java">Java</MenuItem>
                <MenuItem value="csharp">C#</MenuItem>
                <MenuItem value="go">Go</MenuItem>
                <MenuItem value="rust">Rust</MenuItem>
                <MenuItem value="php">PHP</MenuItem>
                <MenuItem value="ruby">Ruby</MenuItem>
                <MenuItem value="sql">SQL</MenuItem>
                <MenuItem value="django">Django</MenuItem>
                <MenuItem value="flask">Flask</MenuItem>
                <MenuItem value="spring">Spring Boot</MenuItem>
                <MenuItem value="express">Express.js</MenuItem>
              </Select>
            </FormControl>

            <Box sx={{ mt: 3, p: 2, bgcolor: 'rgba(63, 81, 181, 0.1)', borderRadius: 1 }}>
              <Typography variant="subtitle2" sx={{ color: '#3F51B5', mb: 1 }}>
                What will be analyzed:
              </Typography>
              <Typography variant="body2" sx={{ color: '#FFFFFF', fontSize: '0.875rem' }}>
                • SQL queries in code files (*.py, *.js, *.ts, *.java, *.sql)
                <br />
                • ORM usage patterns
                <br />
                • Database connection configurations
                <br />
                • Query performance patterns
              </Typography>
            </Box>
          </TabPanel>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setOpen(false)}>Cancel</Button>
          <Button 
            onClick={() => setTabValue(Math.max(0, tabValue - 1))}
            disabled={tabValue === 0}
          >
            Back
          </Button>
          <Button 
            onClick={() => tabValue < 1 ? setTabValue(tabValue + 1) : handleCreateProject()}
            variant="contained"
            disabled={!projectName || (codebaseType === 'github' && !repoUrl.trim()) || (codebaseType === 'local' && !localPath.trim()) || createProject.isPending}
          >
            {tabValue < 1 ? 'Next' : (createProject.isPending ? 'Analyzing...' : 'Start Analysis')}
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};
