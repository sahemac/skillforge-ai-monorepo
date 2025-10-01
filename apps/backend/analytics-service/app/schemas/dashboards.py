"""
Dashboard API schemas for request/response models
"""

from datetime import datetime
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
from app.models.dashboard import DashboardType, WidgetType


class DashboardConfigurationSchema(BaseModel):
    """Schema for dashboard configuration."""
    theme: str = Field(default="light", description="Dashboard theme")
    layout: str = Field(default="grid", description="Layout type")
    auto_refresh: bool = Field(default=True, description="Auto-refresh enabled")
    show_filters: bool = Field(default=True, description="Show filter controls")
    show_export: bool = Field(default=True, description="Show export options")
    custom_css: Optional[str] = Field(default=None, description="Custom CSS styles")


class WidgetPositionSchema(BaseModel):
    """Schema for widget position."""
    x: int = Field(..., ge=0, description="X coordinate")
    y: int = Field(..., ge=0, description="Y coordinate")
    width: int = Field(..., ge=1, description="Widget width")
    height: int = Field(..., ge=1, description="Widget height")


class WidgetDisplayOptionsSchema(BaseModel):
    """Schema for widget display options."""
    format: Optional[str] = Field(default=None, description="Data format (number, currency, percentage)")
    color_scheme: Optional[str] = Field(default="default", description="Color scheme")
    show_legend: bool = Field(default=True, description="Show chart legend")
    show_grid: bool = Field(default=True, description="Show grid lines")
    animation_enabled: bool = Field(default=True, description="Enable animations")
    decimal_places: int = Field(default=2, ge=0, le=10, description="Decimal places for numbers")
    time_format: str = Field(default="YYYY-MM-DD HH:mm", description="Time format string")


class WidgetFiltersSchema(BaseModel):
    """Schema for widget filters."""
    time_range: Optional[str] = Field(default="7d", description="Time range filter")
    user_segment: Optional[str] = Field(default=None, description="User segment filter")
    company_id: Optional[str] = Field(default=None, description="Company filter")
    custom_filters: Dict[str, Any] = Field(default_factory=dict, description="Custom filter values")


class WidgetCreateSchema(BaseModel):
    """Schema for creating a widget."""
    type: WidgetType = Field(..., description="Widget type")
    title: str = Field(..., min_length=1, max_length=100, description="Widget title")
    position: WidgetPositionSchema = Field(..., description="Widget position")
    data_source: str = Field(..., description="Data source endpoint or query")
    refresh_interval: Optional[int] = Field(default=None, ge=30, description="Refresh interval in seconds")
    filters: WidgetFiltersSchema = Field(default_factory=WidgetFiltersSchema, description="Widget filters")
    display_options: WidgetDisplayOptionsSchema = Field(default_factory=WidgetDisplayOptionsSchema, description="Display options")
    permissions: List[str] = Field(default_factory=list, description="Required permissions")


class WidgetSchema(WidgetCreateSchema):
    """Schema for widget with ID."""
    id: str = Field(..., description="Widget ID")


class WidgetUpdateSchema(BaseModel):
    """Schema for updating a widget."""
    type: Optional[WidgetType] = Field(default=None, description="Widget type")
    title: Optional[str] = Field(default=None, min_length=1, max_length=100, description="Widget title")
    position: Optional[WidgetPositionSchema] = Field(default=None, description="Widget position")
    data_source: Optional[str] = Field(default=None, description="Data source endpoint or query")
    refresh_interval: Optional[int] = Field(default=None, ge=30, description="Refresh interval in seconds")
    filters: Optional[WidgetFiltersSchema] = Field(default=None, description="Widget filters")
    display_options: Optional[WidgetDisplayOptionsSchema] = Field(default=None, description="Display options")
    permissions: Optional[List[str]] = Field(default=None, description="Required permissions")


class DashboardCreateSchema(BaseModel):
    """Schema for creating a dashboard."""
    name: str = Field(..., min_length=1, max_length=100, description="Dashboard name")
    type: DashboardType = Field(..., description="Dashboard type")
    description: Optional[str] = Field(default=None, max_length=500, description="Dashboard description")
    config: DashboardConfigurationSchema = Field(default_factory=DashboardConfigurationSchema, description="Dashboard configuration")
    widgets: List[WidgetCreateSchema] = Field(default_factory=list, description="Initial widgets")
    refresh_interval: int = Field(default=300, ge=30, description="Default refresh interval in seconds")
    access_roles: List[str] = Field(default_factory=list, description="Roles that can access this dashboard")


class DashboardUpdateSchema(BaseModel):
    """Schema for updating a dashboard."""
    name: Optional[str] = Field(default=None, min_length=1, max_length=100, description="Dashboard name")
    description: Optional[str] = Field(default=None, max_length=500, description="Dashboard description")
    config: Optional[DashboardConfigurationSchema] = Field(default=None, description="Dashboard configuration")
    widgets: Optional[List[WidgetSchema]] = Field(default=None, description="Widget configurations")
    is_active: Optional[bool] = Field(default=None, description="Whether dashboard is active")
    refresh_interval: Optional[int] = Field(default=None, ge=30, description="Default refresh interval in seconds")
    access_roles: Optional[List[str]] = Field(default=None, description="Roles that can access this dashboard")


class DashboardResponseSchema(BaseModel):
    """Schema for dashboard response."""
    id: str = Field(..., description="Dashboard ID")
    name: str = Field(..., description="Dashboard name")
    type: DashboardType = Field(..., description="Dashboard type")
    description: Optional[str] = Field(default=None, description="Dashboard description")
    config: Dict[str, Any] = Field(..., description="Dashboard configuration")
    widgets: List[Dict[str, Any]] = Field(..., description="Widget configurations")
    is_active: bool = Field(..., description="Whether dashboard is active")
    refresh_interval: int = Field(..., description="Refresh interval in seconds")
    access_roles: List[str] = Field(..., description="Access roles")
    created_by: Optional[str] = Field(default=None, description="Created by user ID")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: Optional[datetime] = Field(default=None, description="Last update timestamp")

    class Config:
        from_attributes = True


class DashboardListResponseSchema(BaseModel):
    """Schema for dashboard list response."""
    dashboards: List[DashboardResponseSchema] = Field(..., description="List of dashboards")
    total: int = Field(..., ge=0, description="Total number of dashboards")
    page: int = Field(..., ge=1, description="Current page number")
    size: int = Field(..., ge=1, description="Page size")


class DashboardDataResponseSchema(BaseModel):
    """Schema for dashboard data response."""
    dashboard_id: str = Field(..., description="Dashboard ID")
    data: Dict[str, Any] = Field(..., description="Dashboard data")
    timestamp: datetime = Field(..., description="Data timestamp")
    cache_status: str = Field(..., description="Cache status (hit/miss)")


class WidgetDataResponseSchema(BaseModel):
    """Schema for widget data response."""
    widget_id: str = Field(..., description="Widget ID")
    data: Any = Field(..., description="Widget data")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Data metadata")
    timestamp: datetime = Field(..., description="Data timestamp")
    error: Optional[str] = Field(default=None, description="Error message if any")


class DashboardExportRequestSchema(BaseModel):
    """Schema for dashboard export request."""
    format: str = Field(..., regex="^(pdf|png|jpeg|svg)$", description="Export format")
    width: int = Field(default=1920, ge=800, le=4000, description="Export width")
    height: int = Field(default=1080, ge=600, le=3000, description="Export height")
    include_data: bool = Field(default=False, description="Include raw data")
    time_range: Optional[str] = Field(default=None, description="Time range for data")


class DashboardExportResponseSchema(BaseModel):
    """Schema for dashboard export response."""
    export_id: str = Field(..., description="Export task ID")
    status: str = Field(..., description="Export status")
    download_url: Optional[str] = Field(default=None, description="Download URL when ready")
    expires_at: Optional[datetime] = Field(default=None, description="Export expiration time")


class DashboardShareRequestSchema(BaseModel):
    """Schema for dashboard share request."""
    expires_at: Optional[datetime] = Field(default=None, description="Share link expiration")
    password: Optional[str] = Field(default=None, description="Optional password protection")
    allowed_ips: List[str] = Field(default_factory=list, description="Allowed IP addresses")
    view_only: bool = Field(default=True, description="View-only access")


class DashboardShareResponseSchema(BaseModel):
    """Schema for dashboard share response."""
    share_id: str = Field(..., description="Share ID")
    share_url: str = Field(..., description="Shareable URL")
    expires_at: Optional[datetime] = Field(default=None, description="Expiration time")
    created_at: datetime = Field(..., description="Creation time")


class DashboardTemplateSchema(BaseModel):
    """Schema for dashboard template."""
    name: str = Field(..., description="Template name")
    type: DashboardType = Field(..., description="Dashboard type")
    description: str = Field(..., description="Template description")
    config: Dict[str, Any] = Field(..., description="Template configuration")
    widgets: List[Dict[str, Any]] = Field(..., description="Template widgets")
    preview_image: Optional[str] = Field(default=None, description="Preview image URL")
    tags: List[str] = Field(default_factory=list, description="Template tags")


class DashboardInsightsResponseSchema(BaseModel):
    """Schema for dashboard insights response."""
    dashboard_id: str = Field(..., description="Dashboard ID")
    insights: List[Dict[str, Any]] = Field(..., description="Generated insights")
    generated_at: datetime = Field(..., description="Generation timestamp")
    next_update: Optional[datetime] = Field(default=None, description="Next scheduled update")