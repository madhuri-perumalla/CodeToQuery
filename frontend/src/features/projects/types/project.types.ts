export interface Project {
  id: number;
  name: string;
  description: string;
  created_at: string;
  createdAt: string;
  updated_at: string;
  config: ProjectConfig;
}

export interface ProjectConfig {
  codebase: {
    type: 'github' | 'local' | 'upload';
    source: string;
  };
  extraction: {
    include_patterns: string[];
    exclude_patterns: string[];
  };
  techStack?: string[];
  target_db?: {
    host: string;
    port: number;
    database: string;
    user: string;
  };
}

export interface ProjectCreate {
  name: string;
  description?: string;
  config: ProjectConfig;
}

export interface ProjectUpdate {
  name?: string;
  description?: string;
  config?: Partial<ProjectConfig>;
}

export interface ProjectStats {
  total_queries: number;
  total_diagnostics: number;
  critical_issues: number;
  codebases_count: number;
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}
