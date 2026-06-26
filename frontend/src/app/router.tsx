import { createBrowserRouter, RouterProvider, Navigate, Outlet } from 'react-router-dom';
import { lazy, Suspense } from 'react';
import { ProtectedRoute } from '@/features/auth/components/ProtectedRoute';
import { MainLayout } from '@/shared/components/layout/MainLayout';
import { ErrorBoundary } from '@/shared/components/layout/ErrorBoundary';
import { PageLoading } from '@/shared/components/loading/PageLoading';
import { useAuth } from '@/features/auth/hooks/useAuth';
import { ProjectProvider } from '@/contexts/ProjectContext';

// Protected Route Wrapper
const ProtectedRouteWrapper: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const { isAuthenticated, isLoading } = useAuth();
  return (
    <ProtectedRoute isAuthenticated={isAuthenticated} isLoading={isLoading}>
      {children}
    </ProtectedRoute>
  );
};

// Public routes
const LoginPage = lazy(() => import('@/pages/auth/LoginPage').then(m => ({ default: m.LoginPage })));

// Protected routes
const Dashboard = lazy(() => import('@/pages/Dashboard').then(m => ({ default: m.Dashboard })));
const GlobalQueriesPage = lazy(() => import('@/pages/QueriesPage').then(m => ({ default: m.QueriesPage })));
const GlobalQueryDetailPage = lazy(() => import('@/pages/QueryDetailPage').then(m => ({ default: m.QueryDetailPage })));
const GlobalExecutionPlansPage = lazy(() => import('@/pages/ExecutionPlansPage').then(m => ({ default: m.ExecutionPlansPage })));
const GlobalExecutionPlanViewerPage = lazy(() => import('@/pages/ExecutionPlanViewerPage').then(m => ({ default: m.ExecutionPlanViewerPage })));
const GlobalDiagnosticsPage = lazy(() => import('@/pages/DiagnosticsPage').then(m => ({ default: m.DiagnosticsPage })));
const GlobalPatternsPage = lazy(() => import('@/pages/PatternsPage').then(m => ({ default: m.PatternsPage })));
const GlobalSummaryPage = lazy(() => import('@/pages/SummaryPage').then(m => ({ default: m.SummaryPage })));
const GlobalSuggestionsPage = lazy(() => import('@/pages/SuggestionsPage').then(m => ({ default: m.SuggestionsPage })));
const GlobalHistoryPage = lazy(() => import('@/pages/HistoryPage').then(m => ({ default: m.HistoryPage })));
const AnalysisPage = lazy(() => import('@/pages/AnalysisPage').then(m => ({ default: m.AnalysisPage })));
const ProjectsPage = lazy(() => import('@/pages/projects/ProjectsPage').then(m => ({ default: m.ProjectsPage })));
const ProjectDetailPage = lazy(() => import('@/pages/projects/ProjectDetailPage').then(m => ({ default: m.ProjectDetailPage })));
const ProjectsListPage = lazy(() => import('@/pages/projects/ProjectsListPage').then(m => ({ default: m.ProjectsListPage })));
const ProjectSummary = lazy(() => import('@/pages/ProjectSummary').then(m => ({ default: m.ProjectSummary })));
const QueryInventory = lazy(() => import('@/pages/QueryInventory').then(m => ({ default: m.QueryInventory })));
const QueryDetail = lazy(() => import('@/pages/QueryDetail').then(m => ({ default: m.QueryDetail })));
const ProjectExecutionPlansPage = lazy(() => import('@/pages/projects/execution-plans/ExecutionPlansPage').then(m => ({ default: m.ExecutionPlansPage })));
const ProjectExecutionPlanViewerPage = lazy(() => import('@/pages/projects/execution-plans/ExecutionPlanViewerPage').then(m => ({ default: m.ExecutionPlanViewerPage })));
const Diagnostics = lazy(() => import('@/pages/Diagnostics').then(m => ({ default: m.Diagnostics })));
const DiagnosticDetailPage = lazy(() => import('@/pages/projects/diagnostics/DiagnosticDetailPage').then(m => ({ default: m.DiagnosticDetailPage })));
const PatternAnalysis = lazy(() => import('@/pages/PatternAnalysis').then(m => ({ default: m.PatternAnalysis })));
const CodebasesPage = lazy(() => import('@/pages/codebases/CodebasesPage').then(m => ({ default: m.CodebasesPage })));
const SettingsPage = lazy(() => import('@/pages/settings/SettingsPage').then(m => ({ default: m.SettingsPage })));

// Error pages
const ErrorPage = lazy(() => import('@/pages/error/ErrorPage').then(m => ({ default: m.ErrorPage })));

const router = createBrowserRouter([
  {
    path: '/login',
    element: (
      <Suspense fallback={<PageLoading />}>
        <LoginPage />
      </Suspense>
    ),
  },
  {
    path: '/',
    element: (
      <ProtectedRouteWrapper>
        <MainLayout><Outlet /></MainLayout>
      </ProtectedRouteWrapper>
    ),
    errorElement: <ErrorBoundary><div>Error occurred</div></ErrorBoundary>,
    children: [
      {
        index: true,
        element: <Navigate to="/dashboard" replace />,
      },
      {
        path: 'dashboard',
        element: (
          <Suspense fallback={<PageLoading />}>
            <Dashboard />
          </Suspense>
        ),
      },
      {
        path: 'queries',
        element: (
          <Suspense fallback={<PageLoading />}>
            <GlobalQueriesPage />
          </Suspense>
        ),
      },
      {
        path: 'queries/:id',
        element: (
          <Suspense fallback={<PageLoading />}>
            <GlobalQueryDetailPage />
          </Suspense>
        ),
      },
      {
        path: 'execution-plans',
        element: (
          <Suspense fallback={<PageLoading />}>
            <GlobalExecutionPlansPage />
          </Suspense>
        ),
      },
      {
        path: 'analysis',
        element: (
          <Suspense fallback={<PageLoading />}>
            <AnalysisPage />
          </Suspense>
        ),
      },
      {
        path: 'execution-plans/:id',
        element: (
          <Suspense fallback={<PageLoading />}>
            <GlobalExecutionPlanViewerPage />
          </Suspense>
        ),
      },
      {
        path: 'diagnostics',
        element: (
          <Suspense fallback={<PageLoading />}>
            <GlobalDiagnosticsPage />
          </Suspense>
        ),
      },
      {
        path: 'query-groups',
        element: (
          <Suspense fallback={<PageLoading />}>
            <GlobalPatternsPage />
          </Suspense>
        ),
      },
      {
        path: 'summary',
        element: (
          <Suspense fallback={<PageLoading />}>
            <GlobalSummaryPage />
          </Suspense>
        ),
      },
      {
        path: 'suggestions',
        element: (
          <Suspense fallback={<PageLoading />}>
            <GlobalSuggestionsPage />
          </Suspense>
        ),
      },
      {
        path: 'analysis-history',
        element: (
          <Suspense fallback={<PageLoading />}>
            <GlobalHistoryPage />
          </Suspense>
        ),
      },
      {
        path: 'projects',
        element: (
          <Suspense fallback={<PageLoading />}>
            <ProjectsPage />
          </Suspense>
        ),
        children: [
          {
            index: true,
            element: (
              <Suspense fallback={<PageLoading />}>
                <ProjectsListPage />
              </Suspense>
            ),
          },
          {
            path: ':projectId',
            element: (
              <Suspense fallback={<PageLoading />}>
                <ProjectDetailPage />
              </Suspense>
            ),
            children: [
              {
                index: true,
                element: (
                  <Suspense fallback={<PageLoading />}>
                    <ProjectSummary />
                  </Suspense>
                ),
              },
              {
                path: 'queries',
                element: (
                  <Suspense fallback={<PageLoading />}>
                    <QueryInventory />
                  </Suspense>
                ),
              },
              {
                path: 'queries/:queryId',
                element: (
                  <Suspense fallback={<PageLoading />}>
                    <QueryDetail />
                  </Suspense>
                ),
              },
              {
                path: 'execution-plans',
                element: (
                  <Suspense fallback={<PageLoading />}>
                    <ProjectExecutionPlansPage />
                  </Suspense>
                ),
              },
              {
                path: 'execution-plans/:planId',
                element: (
                  <Suspense fallback={<PageLoading />}>
                    <ProjectExecutionPlanViewerPage />
                  </Suspense>
                ),
              },
              {
                path: 'diagnostics',
                element: (
                  <Suspense fallback={<PageLoading />}>
                    <Diagnostics />
                  </Suspense>
                ),
              },
              {
                path: 'diagnostics/:diagnosticId',
                element: (
                  <Suspense fallback={<PageLoading />}>
                    <DiagnosticDetailPage />
                  </Suspense>
                ),
              },
              {
                path: 'analysis',
                element: (
                  <Suspense fallback={<PageLoading />}>
                    <PatternAnalysis />
                  </Suspense>
                ),
              },
              {
                path: 'summary',
                element: (
                  <Suspense fallback={<PageLoading />}>
                    <ProjectSummary />
                  </Suspense>
                ),
              },
            ],
          },
        ],
      },
      {
        path: 'codebases',
        element: (
          <Suspense fallback={<PageLoading />}>
            <CodebasesPage />
          </Suspense>
        ),
      },
      {
        path: 'settings',
        element: (
          <Suspense fallback={<PageLoading />}>
            <SettingsPage />
          </Suspense>
        ),
      },
      {
        path: '*',
        element: <Navigate to="/error/404" replace />,
      },
    ],
  },
  {
    path: '/error/:code',
    element: (
      <Suspense fallback={<PageLoading />}>
        <ErrorPage />
      </Suspense>
    ),
  },
]);

export const Router = () => {
  return (
    <ProjectProvider>
      <RouterProvider router={router} />
    </ProjectProvider>
  );
};
