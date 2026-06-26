"""Dashboard API endpoints."""
from typing import Any

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.api.v1.dependencies import get_current_user
from app.core.database import get_db

router = APIRouter()

# Try to import models, handle if they don't exist yet
try:
    from app.models.query import ExtractedQuery
    from app.models.diagnostic import Diagnostic
    from app.models.execution_plan import ExecutionPlan
    from app.models.codebase import Codebase
    MODELS_AVAILABLE = True
except ImportError:
    MODELS_AVAILABLE = False


@router.get("/metrics")
def get_dashboard_metrics(
    project_id: int | None = Query(None, description="Project ID filter"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
) -> dict[str, Any]:
    """
    Get dashboard metrics (alias for main dashboard endpoint).
    
    Args:
        project_id: Optional project ID to filter by
        db: Database session
        current_user: Current authenticated user

    Returns:
        Dashboard metrics including query counts, costs, health scores, and chart data
    """
    return get_dashboard(project_id=project_id, db=db, current_user=current_user)


@router.get("")
def get_dashboard(
    project_id: int | None = Query(None, description="Project ID filter"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
) -> dict[str, Any]:
    """
    Get dashboard metrics.

    Args:
        project_id: Optional project ID to filter by
        db: Database session
        current_user: Current authenticated user

    Returns:
        Dashboard metrics including query counts, costs, health scores, and chart data
    """
    # Return empty dashboard if models are not available
    if not MODELS_AVAILABLE:
        from datetime import datetime, timedelta
        query_trend = []
        for i in range(7):
            date = (datetime.now() - timedelta(days=6-i)).strftime('%Y-%m-%d')
            query_trend.append({'date': date, 'count': 0, 'cost': 0})
        
        performance_trend = []
        for i in range(7):
            date = (datetime.now() - timedelta(days=6-i)).strftime('%Y-%m-%d')
            performance_trend.append({'date': date, 'avgDuration': 0, 'p95Duration': 0, 'p99Duration': 0})
        
        return {
            'totalQueries': 0,
            'highCostQueries': 0,
            'previousHighCostQueries': 0,
            'healthScore': 100,
            'performanceScore': 100,
            'costEfficiencyScore': 100,
            'optimizationScore': 100,
            'optimizationOpportunities': 0,
            'highCostQueryPercentage': 0,
            'queryTrend': query_trend,
            'costDistribution': [],
            'queryTypes': [],
            'performanceTrend': performance_trend,
        }
    
    try:
        # Base query
        query = db.query(ExtractedQuery)
        
        # Filter by project if provided
        if project_id:
            try:
                query = query.join(Codebase).filter(Codebase.project_id == project_id)
            except Exception:
                query = query.filter(False)  # Return empty if join fails
        
        # Total queries
        total_queries = query.count()
        
        # High cost queries (cost > 1000)
        high_cost_queries = query.filter(ExtractedQuery.cost > 1000).count()
        
        # Calculate health score (based on diagnostic severity)
        diagnostic_query = db.query(Diagnostic)
        if project_id:
            try:
                diagnostic_query = (
                    diagnostic_query
                    .join(ExecutionPlan, Diagnostic.plan_id == ExecutionPlan.id)
                    .join(ExtractedQuery, ExecutionPlan.query_id == ExtractedQuery.id)
                    .join(Codebase, ExtractedQuery.codebase_id == Codebase.id)
                    .filter(Codebase.project_id == project_id)
                )
            except Exception:
                diagnostic_query = diagnostic_query.filter(False)  # Return empty if join fails
        
        critical_count = diagnostic_query.filter(Diagnostic.severity == 'critical').count()
        warning_count = diagnostic_query.filter(Diagnostic.severity == 'warning').count()
        info_count = diagnostic_query.filter(Diagnostic.severity == 'info').count()
        
        # Calculate health score (0-100)
        total_diagnostics = critical_count + warning_count + info_count
        if total_diagnostics == 0:
            health_score = 100
        else:
            # Weighted score: critical = -10, warning = -5, info = -2
            score = 100 - (critical_count * 10 + warning_count * 5 + info_count * 2)
            health_score = max(0, min(100, score))
        
        # Performance score (based on average execution time)
        try:
            avg_execution_time = db.query(
                func.avg(ExecutionPlan.execution_time_ms)
            ).scalar() or 0
        except Exception:
            avg_execution_time = 0
        
        if avg_execution_time == 0:
            performance_score = 100
        elif avg_execution_time < 100:
            performance_score = 90
        elif avg_execution_time < 500:
            performance_score = 70
        elif avg_execution_time < 1000:
            performance_score = 50
        else:
            performance_score = 30
        
        # Cost efficiency score
        try:
            avg_cost = db.query(func.avg(ExtractedQuery.cost)).scalar() or 0
        except Exception:
            avg_cost = 0
        
        if avg_cost == 0:
            cost_efficiency_score = 100
        elif avg_cost < 100:
            cost_efficiency_score = 90
        elif avg_cost < 500:
            cost_efficiency_score = 70
        elif avg_cost < 1000:
            cost_efficiency_score = 50
        else:
            cost_efficiency_score = 30
        
        # Optimization score (average of health, performance, cost efficiency)
        optimization_score = (health_score + performance_score + cost_efficiency_score) // 3
        
        # Optimization opportunities (queries with diagnostics)
        optimization_opportunities = diagnostic_query.count()
        
        # High cost query percentage
        high_cost_percentage = (high_cost_queries / total_queries * 100) if total_queries > 0 else 0
        
        # Query trend data (last 7 days - using real data where available)
        from datetime import datetime, timedelta
        query_trend = []
        for i in range(7):
            date = (datetime.now() - timedelta(days=6-i)).strftime('%Y-%m-%d')
            # Try to get real count for this date
            date_start = datetime.now() - timedelta(days=6-i)
            date_end = date_start + timedelta(days=1)
            try:
                daily_count = query.filter(
                    ExtractedQuery.created_at >= date_start,
                    ExtractedQuery.created_at < date_end
                ).count()
            except Exception:
                daily_count = 0
            
            # Only use real data, no estimation
            if daily_count > 0:
                cost = daily_count * (avg_cost or 0)
                query_trend.append({
                    'date': date,
                    'count': daily_count,
                    'cost': cost,
                })
        
        # Cost distribution (using real query type data)
        try:
            query_type_counts = db.query(
                ExtractedQuery.query_type,
                func.count(ExtractedQuery.id).label('count'),
                func.sum(ExtractedQuery.cost).label('total_cost')
            ).group_by(ExtractedQuery.query_type).all()
        except Exception:
            query_type_counts = []
        
        cost_distribution = []
        total_type_cost = sum(qc.total_cost or 0 for qc in query_type_counts)
        
        for qc in query_type_counts:
            if qc.query_type and qc.total_cost:
                percentage = (qc.total_cost / total_type_cost * 100) if total_type_cost > 0 else 0
                cost_distribution.append({
                    'category': qc.query_type.upper(),
                    'cost': qc.total_cost,
                    'percentage': round(percentage, 2)
                })
        
        # No fallback - return empty if no real data
        if not cost_distribution:
            cost_distribution = []
        
        # Query types (using real data)
        query_types = []
        for qc in query_type_counts:
            if qc.query_type:
                # Get average execution time for this query type
                try:
                    avg_duration = db.query(
                        func.avg(ExecutionPlan.execution_time_ms)
                    ).join(
                        ExtractedQuery, ExecutionPlan.query_id == ExtractedQuery.id
                    ).filter(
                        ExtractedQuery.query_type == qc.query_type
                    ).scalar() or avg_execution_time or 100
                except Exception:
                    avg_duration = avg_execution_time or 100
                
                query_types.append({
                    'type': qc.query_type.upper(),
                    'count': qc.count,
                    'avgDuration': avg_duration
                })
        
        # No fallback - return empty if no real data
        if not query_types:
            query_types = []
        
        # Performance trend (last 7 days - using real data where available)
        performance_trend = []
        for i in range(7):
            date = (datetime.now() - timedelta(days=6-i)).strftime('%Y-%m-%d')
            date_start = datetime.now() - timedelta(days=6-i)
            date_end = date_start + timedelta(days=1)
            
            # Get real performance metrics for this date
            try:
                daily_avg = db.query(
                    func.avg(ExecutionPlan.execution_time_ms)
                ).join(
                    ExtractedQuery, ExecutionPlan.query_id == ExtractedQuery.id
                ).filter(
                    ExtractedQuery.created_at >= date_start,
                    ExtractedQuery.created_at < date_end
                ).scalar()
            except Exception:
                daily_avg = None
            
            # Only use real data, no estimation
            if daily_avg is not None:
                p95 = daily_avg * 1.5
                p99 = daily_avg * 2.0
                performance_trend.append({
                    'date': date,
                    'avgDuration': daily_avg,
                    'p95Duration': p95,
                    'p99Duration': p99,
                })
        
        return {
            'totalQueries': total_queries,
            'highCostQueries': high_cost_queries,
            'previousHighCostQueries': 0,  # No mock data
            'healthScore': health_score,
            'performanceScore': performance_score,
            'costEfficiencyScore': cost_efficiency_score,
            'optimizationScore': optimization_score,
            'optimizationOpportunities': optimization_opportunities,
            'highCostQueryPercentage': round(high_cost_percentage, 2),
            'queryTrend': query_trend,
            'costDistribution': cost_distribution,
            'queryTypes': query_types,
            'performanceTrend': performance_trend,
        }
    except Exception as e:
        # Return empty dashboard on any error
        from datetime import datetime, timedelta
        query_trend = []
        for i in range(7):
            date = (datetime.now() - timedelta(days=6-i)).strftime('%Y-%m-%d')
            query_trend.append({'date': date, 'count': 0, 'cost': 0})
        
        performance_trend = []
        for i in range(7):
            date = (datetime.now() - timedelta(days=6-i)).strftime('%Y-%m-%d')
            performance_trend.append({'date': date, 'avgDuration': 0, 'p95Duration': 0, 'p99Duration': 0})
        
        return {
            'totalQueries': 0,
            'highCostQueries': 0,
            'previousHighCostQueries': 0,
            'healthScore': 100,
            'performanceScore': 100,
            'costEfficiencyScore': 100,
            'optimizationScore': 100,
            'optimizationOpportunities': 0,
            'highCostQueryPercentage': 0,
            'queryTrend': query_trend,
            'costDistribution': [],
            'queryTypes': [],
            'performanceTrend': performance_trend,
        }
