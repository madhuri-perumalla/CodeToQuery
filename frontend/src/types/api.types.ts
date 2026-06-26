/**
 * Common API type definitions for CodeToQuery frontend
 */

// ============================================================================
// Base API Response Types
// ============================================================================

export interface ApiResponse<T> {
  data: T;
  message?: string;
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}

export interface ApiError {
  error: {
    code: string;
    message: string;
    details?: Record<string, unknown>;
  };
}

// ============================================================================
// Query Parameter Types
// ============================================================================

export interface PaginationParams {
  page?: number;
  page_size?: number;
  search?: string;
  sort_by?: string;
  sort_order?: 'asc' | 'desc';
}

export interface FilterParams extends PaginationParams {
  severity?: string;
  status?: string;
  codebase_id?: number;
  project_id?: number;
}

export interface QueryListParams extends FilterParams {
  dialect?: string;
  query_type?: string;
  health_score_min?: number;
}

// ============================================================================
// Dashboard Types
// ============================================================================

export interface DashboardMetrics {
  total_projects: number;
  total_codebases: number;
  total_queries: number;
  totalQueries?: number;
  total_diagnostics: number;
  critical_issues: number;
  recent_analyses: number;
  performanceTrend?: unknown[];
  topQueries?: unknown[];
  recentActivity?: unknown[];
  highCostQueries?: number;
  previousHighCostQueries?: number;
  highCostQueryPercentage?: number;
  healthScore?: number;
  optimizationOpportunities?: number;
  queryTrend?: unknown[];
  costDistribution?: unknown[];
  queryTypes?: unknown[];
}

// ============================================================================
// Execution Plan Types
// ============================================================================

export interface ExecutionPlanNode {
  id: string;
  type: string;
  relation_name?: string;
  startup_cost: number;
  total_cost: number;
  plan_rows: number;
  plan_width: number;
  filter?: string;
  sort_key?: string[];
  plans?: ExecutionPlanNode[];
}

export interface ExecutionPlan {
  id: number;
  query_id: number;
  plan_json: Record<string, unknown>;
  planJson?: Record<string, unknown>;
  totalCost?: number;
  totalRows?: number;
  created_at: string;
}

// ============================================================================
// Diagnostic Types
// ============================================================================

export type Severity = 'info' | 'warning' | 'error' | 'critical';

export interface Diagnostic {
  id: number;
  id_str?: string;
  query_id: number;
  rule_id: string;
  ruleId?: string;
  severity: Severity;
  message: string;
  description: string;
  location?: QueryLocation;
  created_at: string;
  createdAt?: string;
  suggestions?: FixSuggestion[];
  planId?: string;
}

export interface QueryLocation {
  id: number;
  query_id: number;
  file_path: string;
  line_number: number;
  function_name?: string;
  context_snippet: string;
}

export interface FixSuggestion {
  id: number;
  diagnostic_id: number;
  suggestion_type: string;
  description: string;
  code_before: string;
  code_after: string;
  estimated_impact: string;
}

export interface DiagnosticListResponse extends PaginatedResponse<Diagnostic> {
  diagnostics?: Diagnostic[];
}

// ============================================================================
// Query Types
// ============================================================================

export type QueryStatus = 'analyzing' | 'completed' | 'error';

export interface Query {
  id: number;
  codebase_id: number;
  raw_sql: string;
  rawSql?: string;
  normalized_sql: string;
  normalizedSql?: string;
  query_hash: string;
  queryHash?: string;
  dialect: string;
  query_type: string;
  type?: string;
  source_type: string;
  cost: number;
  execution_time: number;
  executionTime?: number;
  health_score: number;
  healthScore?: number;
  status: QueryStatus;
  created_at: string;
  createdAt?: string;
  updated_at: string;
  updatedAt?: string;
  metadata?: Record<string, unknown>;
  executionPlan?: ExecutionPlan;
  locations?: QueryLocation[];
  name?: string;
  tables?: string[];
}

export interface QueryListResponse extends PaginatedResponse<Query> {
  queries?: Query[];
}

// ============================================================================
// Pattern Types
// ============================================================================

export type RiskLevel = 'low' | 'medium' | 'high' | 'critical';

export interface QueryPattern {
  id: number;
  name: string;
  query_count: number;
  queryCount?: number;
  risk_level: RiskLevel;
  optimization_potential: number;
  avg_cost: number;
  avg_execution_time: number;
  sample_queries: string[];
}

export interface PatternListResponse extends PaginatedResponse<QueryPattern> {
  patterns?: QueryPattern[];
}

// ============================================================================
// Group Types
// ============================================================================

export interface QueryGroup {
  id: number;
  name: string;
  description?: string;
  similarity_threshold: number;
  created_at: string;
  updated_at: string;
}

export interface GroupMember {
  id: number;
  group_id: number;
  query_id: number;
  similarity_score: number;
  created_at: string;
}

// ============================================================================
// Analysis Types
// ============================================================================

export type AnalysisStatus = 'pending' | 'running' | 'completed' | 'failed';

export interface AnalysisRun {
  id: number;
  codebase_id: number;
  status: AnalysisStatus;
  started_at: string;
  completed_at?: string;
  query_count: number;
  diagnostic_count: number;
}

// ============================================================================
// Codebase Types
// ============================================================================

export interface Codebase {
  id: number;
  project_id: number;
  name: string;
  path: string;
  language: string;
  created_at: string;
  updated_at: string;
}

// ============================================================================
// Project Types
// ============================================================================

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
  target_db: {
    host: string;
    port: number;
    database: string;
    user: string;
  };
  extraction: {
    include_patterns: string[];
    exclude_patterns: string[];
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

// ============================================================================
// Summary Types
// ============================================================================

export interface Summary {
  project_id: number;
  total_queries: number;
  totalQueries?: number;
  total_diagnostics: number;
  critical_issues: number;
  criticalIssues?: number;
  high_risk_queries: number;
  highIssues?: number;
  mediumIssues?: number;
  optimization_potential: number;
  avgQueryCost?: number;
  maxQueryCost?: number;
  last_analysis_date: string;
  mostExpensiveQueries?: unknown[];
  recentAnalyses?: unknown[];
}
