// API Response Types
export interface ApiResponse<T> {
  data: T;
  message?: string;
  status: number;
  success: boolean;
}

export interface ApiError {
  message: string;
  status: number;
  code?: string;
  details?: Record<string, unknown>;
}

// Dashboard Types
export interface DashboardMetrics {
  totalQueries: number;
  highCostQueries: number;
  previousHighCostQueries: number;
  healthScore: number;
  performanceScore: number;
  costEfficiencyScore: number;
  optimizationScore: number;
  optimizationOpportunities: number;
  highCostQueryPercentage: number;
  queryTrend: QueryTrendData[];
  costDistribution: CostDistributionData[];
  queryTypes: QueryTypeData[];
  performanceTrend: PerformanceTrendData[];
}

export interface QueryTrendData {
  date: string;
  count: number;
  cost: number;
}

export interface CostDistributionData {
  category: string;
  cost: number;
  percentage: number;
}

export interface QueryTypeData {
  type: string;
  count: number;
  avgDuration: number;
}

export interface PerformanceTrendData {
  date: string;
  avgDuration: number;
  p95Duration: number;
  p99Duration: number;
}

export interface ActivityItem {
  id: string;
  type: 'analysis' | 'scan' | 'alert';
  message: string;
  timestamp: string;
  projectId?: string;
}

// Query Types
export interface Query {
  id: string;
  projectId: string;
  codebaseId: string;
  name?: string;
  rawSql: string;
  normalizedSql: string;
  queryHash: string;
  dialect: string;
  type?: string;
  tables?: string[];
  cost?: number;
  executionTime?: number;
  healthScore?: number;
  status?: 'healthy' | 'warning' | 'critical' | 'analyzing';
  createdAt: string;
  updatedAt: string;
  locations: QueryLocation[];
  executionPlan?: ExecutionPlan;
  diagnostics?: Diagnostic[];
}

export interface QueryLocation {
  id: string;
  queryId: string;
  filePath: string;
  lineNumber: number;
  column: number;
  function: string;
  context: string;
}

export interface QueryListResponse {
  queries: Query[];
  total: number;
  page: number;
  pageSize: number;
  filters: QueryFilters;
}

export interface QueryFilters {
  projectId?: string;
  codebaseId?: string;
  severity?: 'critical' | 'high' | 'medium' | 'low';
  scanType?: string;
  minCost?: number;
  maxCost?: number;
  search?: string;
}

// Execution Plan Types
export interface ExecutionPlan {
  id: string;
  queryId: string;
  planJson: Record<string, unknown>;
  totalCost: number;
  totalRows: number;
  analyzedAt: string;
  format: 'json' | 'text';
  nodes: PlanNode[];
}

export interface PlanNode {
  nodeId: string;
  nodeType: string;
  relationName?: string;
  startupCost: number;
  totalCost: number;
  planRows: number;
  planWidth: number;
  actualRows?: number;
  actualLoops?: number;
  actualTotalTime?: number;
  actualStartupTime?: number;
  children?: PlanNode[];
  warnings?: string[];
}

// Diagnostic Types
export interface Diagnostic {
  id: string;
  planId: string;
  ruleId: string;
  severity: 'critical' | 'high' | 'medium' | 'low' | 'info';
  message: string;
  description: string;
  location?: string;
  createdAt: string;
  suggestions?: FixSuggestion[];
}

export interface DiagnosticListResponse {
  diagnostics: Diagnostic[];
  total: number;
  summary: DiagnosticSummary;
}

export interface DiagnosticSummary {
  critical: number;
  high: number;
  medium: number;
  low: number;
  info: number;
}

// Pattern Types
export interface Pattern {
  id: string;
  name: string;
  description: string;
  queryCount: number;
  avgCost: number;
  maxCost: number;
  sampleQuery: string;
  detectedAt: string;
}

export interface PatternListResponse {
  patterns: Pattern[];
  total: number;
}

// Summary Types
export interface Summary {
  totalQueries: number;
  totalProjects: number;
  totalCodebases: number;
  criticalIssues: number;
  highIssues: number;
  mediumIssues: number;
  lowIssues: number;
  avgQueryCost: number;
  maxQueryCost: number;
  mostExpensiveQueries: Query[];
  topIssues: Diagnostic[];
  recentAnalyses: AnalysisSummary[];
}

export interface AnalysisSummary {
  id: string;
  projectId: string;
  codebaseId: string;
  status: 'completed' | 'running' | 'failed';
  startedAt: string;
  completedAt?: string;
  queryCount: number;
  issueCount: number;
}

// Fix Suggestion Types
export interface FixSuggestion {
  id: string;
  diagnosticId: string;
  type: 'index' | 'rewrite' | 'filter' | 'other';
  description: string;
  sqlChange?: string;
  impact: string;
  estimatedImprovement: number;
  applied: boolean;
}

// Request Parameters
export interface PaginationParams {
  page?: number;
  pageSize?: number;
  sortBy?: string;
  sortOrder?: 'asc' | 'desc';
}

export interface QueryListParams extends PaginationParams {
  projectId?: string;
  codebaseId?: string;
  codebase_id?: string;
  severity?: string;
  scanType?: string;
  queryType?: string;
  sourceType?: string;
  minCost?: number;
  maxCost?: number;
  search?: string;
}
