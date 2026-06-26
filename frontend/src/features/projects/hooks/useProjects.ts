import { useQuery } from '@tanstack/react-query';
import { projectService } from '../services/projectService';
import { queryKeys } from '@/lib/react-query/queryKeys';
import type { PaginatedResponse, Project } from '../types/project.types';

export const useProjects = (params: { page?: number; page_size?: number; search?: string } = {}) => {
  return useQuery<PaginatedResponse<Project>>({
    queryKey: queryKeys.projects.list(params),
    queryFn: () => projectService.list(params),
  });
};

export const useProject = (id: number) => {
  return useQuery<Project>({
    queryKey: queryKeys.projects.detail(id),
    queryFn: () => projectService.get(id),
    enabled: !!id,
  });
};

export const useProjectStats = (id: number) => {
  return useQuery({
    queryKey: queryKeys.projects.stats(id),
    queryFn: () => projectService.getStats(id),
    enabled: !!id,
  });
};
