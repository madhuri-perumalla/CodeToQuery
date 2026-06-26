import React, { createContext, useContext, useState, ReactNode, useEffect } from 'react';

interface ProjectContextType {
  selectedProjectId: number | null;
  setSelectedProjectId: (id: number | null) => void;
  selectedProject: any | null;
  setSelectedProject: (project: any) => void;
  selectedCodebaseId: number | null;
  setSelectedCodebaseId: (id: number | null) => void;
  selectedCodebase: any | null;
  setSelectedCodebase: (codebase: any) => void;
}

const ProjectContext = createContext<ProjectContextType | undefined>(undefined);

export const ProjectProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const [selectedProjectId, setSelectedProjectId] = useState<number | null>(null);
  const [selectedProject, setSelectedProject] = useState<any | null>(null);
  const [selectedCodebaseId, setSelectedCodebaseId] = useState<number | null>(null);
  const [selectedCodebase, setSelectedCodebase] = useState<any | null>(null);

  // Load selected project from localStorage on mount
  useEffect(() => {
    const savedProjectId = localStorage.getItem('selected_project_id');
    const savedProject = localStorage.getItem('selected_project');
    if (savedProjectId && savedProject) {
      setSelectedProjectId(parseInt(savedProjectId));
      setSelectedProject(JSON.parse(savedProject));
    }
  }, []);

  // Save to localStorage when project changes
  useEffect(() => {
    if (selectedProjectId) {
      localStorage.setItem('selected_project_id', selectedProjectId.toString());
    } else {
      localStorage.removeItem('selected_project_id');
    }
  }, [selectedProjectId]);

  useEffect(() => {
    if (selectedProject) {
      localStorage.setItem('selected_project', JSON.stringify(selectedProject));
    } else {
      localStorage.removeItem('selected_project');
    }
  }, [selectedProject]);

  // Save to localStorage when codebase changes
  useEffect(() => {
    if (selectedCodebaseId) {
      localStorage.setItem('selected_codebase_id', selectedCodebaseId.toString());
    } else {
      localStorage.removeItem('selected_codebase_id');
    }
  }, [selectedCodebaseId]);

  useEffect(() => {
    if (selectedCodebase) {
      localStorage.setItem('selected_codebase', JSON.stringify(selectedCodebase));
    } else {
      localStorage.removeItem('selected_codebase');
    }
  }, [selectedCodebase]);

  return (
    <ProjectContext.Provider value={{ 
      selectedProjectId, 
      setSelectedProjectId, 
      selectedProject, 
      setSelectedProject,
      selectedCodebaseId,
      setSelectedCodebaseId,
      selectedCodebase,
      setSelectedCodebase
    }}>
      {children}
    </ProjectContext.Provider>
  );
};

export const useProjectContext = () => {
  const context = useContext(ProjectContext);
  if (!context) throw new Error('useProjectContext must be used within ProjectProvider');
  return context;
};
