"""API v1 router."""
from fastapi import APIRouter

from app.api.v1.endpoints import analysis, auth, codebases, dashboard, diagnostics, explain, groups, normalization, projects, queries, suggestions

api_router = APIRouter()

# Include all endpoint routers
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(dashboard.router, prefix="/dashboard", tags=["dashboard"])
api_router.include_router(projects.router, prefix="/projects", tags=["projects"])
api_router.include_router(codebases.router, prefix="/codebases", tags=["codebases"])
api_router.include_router(queries.router, prefix="/queries", tags=["queries"])
api_router.include_router(analysis.router, prefix="/analysis", tags=["analysis"])
api_router.include_router(groups.router, prefix="/groups", tags=["groups"])
api_router.include_router(diagnostics.router, prefix="/diagnostics", tags=["diagnostics"])
api_router.include_router(normalization.router, prefix="/normalization", tags=["normalization"])
api_router.include_router(explain.router, prefix="/explain", tags=["explain"])
api_router.include_router(suggestions.router, prefix="/suggestions", tags=["suggestions"])
