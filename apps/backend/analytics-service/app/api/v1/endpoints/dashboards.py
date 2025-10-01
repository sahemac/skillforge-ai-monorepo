"""
Dashboard API endpoints for SkillForge Analytics Service
"""

import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from uuid import uuid4
from fastapi import APIRouter, Depends, HTTPException, Query, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete, func

from app.core.database import get_session
from app.core.analytics_engine import analytics_engine
from app.core.monitoring import MetricsCollector
from app.models.dashboard import Dashboard, DashboardType
from app.schemas.dashboards import (
    DashboardCreateSchema,
    DashboardUpdateSchema,
    DashboardResponseSchema,
    DashboardListResponseSchema,
    DashboardDataResponseSchema,
    WidgetCreateSchema,
    WidgetUpdateSchema,
    WidgetDataResponseSchema,
    DashboardExportRequestSchema,
    DashboardExportResponseSchema,
    DashboardShareRequestSchema,
    DashboardShareResponseSchema,
    DashboardTemplateSchema,
    DashboardInsightsResponseSchema
)

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/", response_model=DashboardResponseSchema, status_code=201)
async def create_dashboard(
    dashboard: DashboardCreateSchema,
    session: AsyncSession = Depends(get_session)
):
    """Create a new dashboard."""
    try:
        # Create dashboard with widgets
        db_dashboard = Dashboard(
            name=dashboard.name,
            type=dashboard.type,
            description=dashboard.description,
            config=dashboard.config.model_dump(),
            widgets=[widget.model_dump() for widget in dashboard.widgets],
            refresh_interval=dashboard.refresh_interval,
            access_roles=dashboard.access_roles,
            created_by="current_user_id"  # TODO: Get from auth
        )

        session.add(db_dashboard)
        await session.commit()
        await session.refresh(db_dashboard)

        logger.info(f"Created dashboard: {db_dashboard.name} ({db_dashboard.id})")
        return db_dashboard

    except Exception as e:
        logger.error(f"Error creating dashboard: {e}")
        await session.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/", response_model=DashboardListResponseSchema)
async def list_dashboards(
    type: Optional[DashboardType] = Query(None, description="Filter by dashboard type"),
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(20, ge=1, le=100, description="Page size"),
    session: AsyncSession = Depends(get_session)
):
    """Get list of dashboards."""
    try:
        # Build query
        query = select(Dashboard)

        if type:
            query = query.where(Dashboard.type == type)
        if is_active is not None:
            query = query.where(Dashboard.is_active == is_active)

        # Get total count
        count_query = select(func.count(Dashboard.id))
        if type:
            count_query = count_query.where(Dashboard.type == type)
        if is_active is not None:
            count_query = count_query.where(Dashboard.is_active == is_active)

        total_result = await session.execute(count_query)
        total = total_result.scalar()

        # Get paginated results
        query = query.offset((page - 1) * size).limit(size)
        query = query.order_by(Dashboard.created_at.desc())

        result = await session.execute(query)
        dashboards = result.scalars().all()

        return DashboardListResponseSchema(
            dashboards=[DashboardResponseSchema.from_orm(dashboard) for dashboard in dashboards],
            total=total,
            page=page,
            size=size
        )

    except Exception as e:
        logger.error(f"Error listing dashboards: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{dashboard_id}", response_model=DashboardResponseSchema)
async def get_dashboard(
    dashboard_id: str,
    session: AsyncSession = Depends(get_session)
):
    """Get dashboard by ID."""
    try:
        result = await session.execute(
            select(Dashboard).where(Dashboard.id == dashboard_id)
        )
        dashboard = result.scalar_one_or_none()

        if not dashboard:
            raise HTTPException(status_code=404, detail="Dashboard not found")

        return DashboardResponseSchema.from_orm(dashboard)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting dashboard {dashboard_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{dashboard_id}", response_model=DashboardResponseSchema)
async def update_dashboard(
    dashboard_id: str,
    dashboard_update: DashboardUpdateSchema,
    session: AsyncSession = Depends(get_session)
):
    """Update dashboard."""
    try:
        result = await session.execute(
            select(Dashboard).where(Dashboard.id == dashboard_id)
        )
        dashboard = result.scalar_one_or_none()

        if not dashboard:
            raise HTTPException(status_code=404, detail="Dashboard not found")

        # Update fields
        update_data = dashboard_update.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            if field == "config" and value is not None:
                value = value.model_dump()
            elif field == "widgets" and value is not None:
                value = [widget.model_dump() for widget in value]
            setattr(dashboard, field, value)

        dashboard.updated_at = datetime.utcnow()
        await session.commit()

        logger.info(f"Updated dashboard: {dashboard_id}")
        return DashboardResponseSchema.from_orm(dashboard)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating dashboard {dashboard_id}: {e}")
        await session.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{dashboard_id}")
async def delete_dashboard(
    dashboard_id: str,
    session: AsyncSession = Depends(get_session)
):
    """Delete dashboard."""
    try:
        result = await session.execute(
            select(Dashboard).where(Dashboard.id == dashboard_id)
        )
        dashboard = result.scalar_one_or_none()

        if not dashboard:
            raise HTTPException(status_code=404, detail="Dashboard not found")

        await session.execute(
            delete(Dashboard).where(Dashboard.id == dashboard_id)
        )
        await session.commit()

        logger.info(f"Deleted dashboard: {dashboard_id}")
        return {"message": "Dashboard deleted successfully"}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting dashboard {dashboard_id}: {e}")
        await session.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{dashboard_id}/data", response_model=DashboardDataResponseSchema)
async def get_dashboard_data(
    dashboard_id: str,
    time_range: Optional[str] = Query("7d", description="Time range for data"),
    session: AsyncSession = Depends(get_session)
):
    """Get dashboard data."""
    try:
        start_time = datetime.utcnow()

        # Get dashboard
        result = await session.execute(
            select(Dashboard).where(Dashboard.id == dashboard_id)
        )
        dashboard = result.scalar_one_or_none()

        if not dashboard:
            raise HTTPException(status_code=404, detail="Dashboard not found")

        # Get data based on dashboard type
        dashboard_data = {}

        if dashboard.type == DashboardType.SHELL:
            dashboard_data = await get_shell_dashboard_data(time_range)
        elif dashboard.type == DashboardType.ADMIN:
            dashboard_data = await get_admin_dashboard_data(time_range)
        elif dashboard.type == DashboardType.COMPANY:
            dashboard_data = await get_company_dashboard_data(time_range)
        elif dashboard.type == DashboardType.LEARNER:
            dashboard_data = await get_learner_dashboard_data(time_range)

        # Record metrics
        duration = (datetime.utcnow() - start_time).total_seconds()
        await MetricsCollector.record_dashboard_load(dashboard.type.value, duration)

        return DashboardDataResponseSchema(
            dashboard_id=dashboard_id,
            data=dashboard_data,
            timestamp=datetime.utcnow(),
            cache_status="miss"  # TODO: Implement caching
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting dashboard data {dashboard_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{dashboard_id}/widgets", response_model=WidgetDataResponseSchema)
async def add_widget_to_dashboard(
    dashboard_id: str,
    widget: WidgetCreateSchema,
    session: AsyncSession = Depends(get_session)
):
    """Add widget to dashboard."""
    try:
        result = await session.execute(
            select(Dashboard).where(Dashboard.id == dashboard_id)
        )
        dashboard = result.scalar_one_or_none()

        if not dashboard:
            raise HTTPException(status_code=404, detail="Dashboard not found")

        # Add widget
        widget_data = widget.model_dump()
        widget_id = str(uuid4())
        widget_data["id"] = widget_id

        dashboard.widgets.append(widget_data)
        dashboard.updated_at = datetime.utcnow()

        await session.commit()

        logger.info(f"Added widget {widget_id} to dashboard {dashboard_id}")

        return WidgetDataResponseSchema(
            widget_id=widget_id,
            data=widget_data,
            timestamp=datetime.utcnow()
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error adding widget to dashboard {dashboard_id}: {e}")
        await session.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{dashboard_id}/widgets/{widget_id}/data")
async def get_widget_data(
    dashboard_id: str,
    widget_id: str,
    session: AsyncSession = Depends(get_session)
):
    """Get specific widget data."""
    try:
        result = await session.execute(
            select(Dashboard).where(Dashboard.id == dashboard_id)
        )
        dashboard = result.scalar_one_or_none()

        if not dashboard:
            raise HTTPException(status_code=404, detail="Dashboard not found")

        # Find widget
        widget = dashboard.get_widget_by_id(widget_id)
        if not widget:
            raise HTTPException(status_code=404, detail="Widget not found")

        # Get widget data based on data source
        widget_data = await fetch_widget_data(widget)

        return WidgetDataResponseSchema(
            widget_id=widget_id,
            data=widget_data,
            timestamp=datetime.utcnow()
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting widget data {widget_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{dashboard_id}/export", response_model=DashboardExportResponseSchema)
async def export_dashboard(
    dashboard_id: str,
    export_request: DashboardExportRequestSchema,
    background_tasks: BackgroundTasks,
    session: AsyncSession = Depends(get_session)
):
    """Export dashboard."""
    try:
        result = await session.execute(
            select(Dashboard).where(Dashboard.id == dashboard_id)
        )
        dashboard = result.scalar_one_or_none()

        if not dashboard:
            raise HTTPException(status_code=404, detail="Dashboard not found")

        # Start export in background
        export_id = str(uuid4())
        background_tasks.add_task(
            export_dashboard_task,
            export_id,
            dashboard_id,
            export_request.model_dump()
        )

        return DashboardExportResponseSchema(
            export_id=export_id,
            status="processing",
            expires_at=datetime.utcnow() + timedelta(hours=24)
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error exporting dashboard {dashboard_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{dashboard_id}/insights", response_model=DashboardInsightsResponseSchema)
async def get_dashboard_insights(
    dashboard_id: str,
    session: AsyncSession = Depends(get_session)
):
    """Get AI-generated insights for dashboard."""
    try:
        result = await session.execute(
            select(Dashboard).where(Dashboard.id == dashboard_id)
        )
        dashboard = result.scalar_one_or_none()

        if not dashboard:
            raise HTTPException(status_code=404, detail="Dashboard not found")

        # Generate insights
        insights = await analytics_engine.generate_insights(dashboard.type.value)

        return DashboardInsightsResponseSchema(
            dashboard_id=dashboard_id,
            insights=insights,
            generated_at=datetime.utcnow()
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating insights for dashboard {dashboard_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Helper functions

async def get_shell_dashboard_data(time_range: str) -> Dict[str, Any]:
    """Get shell dashboard specific data."""
    return {
        "user_metrics": await analytics_engine.get_user_metrics(time_range),
        "project_metrics": await analytics_engine.get_project_metrics(time_range),
        "system_health": {"status": "healthy", "services": 12, "uptime": "99.9%"}
    }


async def get_admin_dashboard_data(time_range: str) -> Dict[str, Any]:
    """Get admin dashboard specific data."""
    return {
        "user_metrics": await analytics_engine.get_user_metrics(time_range),
        "business_metrics": {"revenue": 50000, "conversion_rate": 3.2},
        "conversion_funnel": await analytics_engine.get_conversion_funnel("user_signup")
    }


async def get_company_dashboard_data(time_range: str) -> Dict[str, Any]:
    """Get company dashboard specific data."""
    return {
        "hiring_metrics": {"active_positions": 15, "applications": 240},
        "talent_pipeline": {"screening": 45, "interviews": 12, "offers": 3},
        "skills_demand": {"javascript": 25, "python": 18, "react": 20}
    }


async def get_learner_dashboard_data(time_range: str) -> Dict[str, Any]:
    """Get learner dashboard specific data."""
    return {
        "progress_metrics": {"skills_completed": 8, "projects_submitted": 3},
        "recommendations": [
            {"title": "JavaScript Advanced", "priority": "high"},
            {"title": "React Hooks", "priority": "medium"}
        ]
    }


async def fetch_widget_data(widget: Dict[str, Any]) -> Any:
    """Fetch data for a specific widget."""
    data_source = widget.get("data_source")

    # Mock data fetching based on data source
    if data_source == "/api/v1/metrics/dau":
        return {"value": 1250, "change": "+12%"}
    elif data_source == "/api/v1/metrics/user-growth":
        return {"data": [{"date": "2024-01-01", "users": 1000}, {"date": "2024-01-02", "users": 1050}]}
    else:
        return {"message": "No data available"}


async def export_dashboard_task(export_id: str, dashboard_id: str, export_config: Dict[str, Any]):
    """Background task to export dashboard."""
    try:
        # Mock export process
        logger.info(f"Starting export {export_id} for dashboard {dashboard_id}")
        # Implementation would generate PDF/PNG/etc.
        logger.info(f"Export {export_id} completed")
    except Exception as e:
        logger.error(f"Export {export_id} failed: {e}")