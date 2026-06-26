import axiosInstance from '@/lib/api/axiosInstance';
import { queryKeys } from '@/lib/react-query/queryKeys';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import type { ProjectCreate, ProjectUpdate, Project, ProjectStats, PaginatedResponse } from '@/features/projects/types/project.types';

export const projectService = {
  list: async (params: { page?: number; page_size?: number; search?: string }): Promise<PaginatedResponse<Project>> => {
    const response = await axiosInstance.get<PaginatedResponse<Project>>('/projects', { params });
    return response.data;
  },

  get: async (id: number): Promise<Project> => {
    const response = await axiosInstance.get<Project>(`/projects/${id}`);
    return response.data;
  },

  create: async (data: ProjectCreate): Promise<Project> => {
    const response = await axiosInstance.post<Project>('/projects', data);
    return response.data;
  },

  update: async (id: number, data: ProjectUpdate): Promise<Project> => {
    const response = await axiosInstance.put<Project>(`/projects/${id}`, data);
    return response.data;
  },

  delete: async (id: number): Promise<void> => {
    await axiosInstance.delete(`/projects/${id}`);
  },

  getStats: async (id: number): Promise<ProjectStats> => {
    const response = await axiosInstance.get<ProjectStats>(`/projects/${id}/stats`);
    return response.data;
  },
};

export const useCreateProject = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: projectService.create,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.projects.lists() });
    },
  });
};

export const useUpdateProject = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ id, data }: { id: number; data: ProjectUpdate }) => projectService.update(id, data),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: queryKeys.projects.detail(variables.id) });
      queryClient.invalidateQueries({ queryKey: queryKeys.projects.lists() });
    },
  });
};

export const useDeleteProject = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: projectService.delete,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.projects.lists() });
    },
  });
};
