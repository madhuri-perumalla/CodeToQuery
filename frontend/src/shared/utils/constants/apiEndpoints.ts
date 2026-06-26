export const API_ENDPOINTS = {
  AUTH: {
    LOGIN: '/auth/login',
    LOGOUT: '/auth/logout',
    REFRESH: '/auth/refresh',
    ME: '/auth/me',
  },
  PROJECTS: {
    LIST: '/projects',
    DETAIL: (id: number) => `/projects/${id}`,
    STATS: (id: number) => `/projects/${id}/stats`,
  },
  CODEBASES: {
    LIST: '/codebases',
    DETAIL: (id: number) => `/codebases/${id}`,
    SCAN: (id: number) => `/codebases/${id}/scan`,
  },
  QUERIES: {
    LIST: '/queries',
    DETAIL: (id: number) => `/queries/${id}`,
  },
  DIAGNOSTICS: {
    LIST: '/diagnostics',
    DETAIL: (id: number) => `/diagnostics/${id}`,
  },
  SUGGESTIONS: {
    LIST: '/suggestions',
    DETAIL: (id: number) => `/suggestions/${id}`,
    APPLY: (id: number) => `/suggestions/${id}/apply`,
  },
  GROUPS: {
    LIST: '/groups',
    DETAIL: (id: number) => `/groups/${id}`,
  },
  ANALYSIS: {
    LIST: '/analysis',
    DETAIL: (id: number) => `/analysis/${id}`,
  },
};
