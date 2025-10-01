"""
Metrics API schemas for request/response models
"""

from datetime import datetime
from typing import Dict, Any, List, Optional, Union
from pydantic import BaseModel, Field
from app.models.metric import MetricType, AggregationType


class MetricFiltersSchema(BaseModel):
    """Schema for metric filters."""
    time_range: Optional[str] = Field(default="7d", description="Time range (e.g., '7d', '24h', '1m')")
    start_date: Optional[datetime] = Field(default=None, description="Start date for custom range")
    end_date: Optional[datetime] = Field(default=None, description="End date for custom range")
    user_segment: Optional[str] = Field(default=None, description="User segment filter")
    company_id: Optional[str] = Field(default=None, description="Company ID filter")
    project_status: Optional[str] = Field(default=None, description="Project status filter")
    custom_filters: Dict[str, Any] = Field(default_factory=dict, description="Custom filter values")


class MetricDimensionsSchema(BaseModel):
    """Schema for metric dimensions."""
    group_by: Optional[List[str]] = Field(default=None, description="Dimensions to group by")
    limit: Optional[int] = Field(default=10, ge=1, le=1000, description="Limit results")
    sort_by: Optional[str] = Field(default=None, description="Sort dimension")
    sort_order: Optional[str] = Field(default="desc", regex="^(asc|desc)$", description="Sort order")


class MetricRequestSchema(BaseModel):
    """Schema for metric data request."""
    metrics: List[str] = Field(..., min_items=1, description="List of metric names")
    filters: MetricFiltersSchema = Field(default_factory=MetricFiltersSchema, description="Filters to apply")
    dimensions: MetricDimensionsSchema = Field(default_factory=MetricDimensionsSchema, description="Dimension options")
    include_metadata: bool = Field(default=False, description="Include metric metadata")
    format: str = Field(default="json", regex="^(json|csv|table)$", description="Response format")


class MetricValueSchema(BaseModel):
    """Schema for a metric value."""
    value: Union[float, int, str] = Field(..., description="Metric value")
    timestamp: datetime = Field(..., description="Value timestamp")
    dimensions: Dict[str, Any] = Field(default_factory=dict, description="Dimension values")


class MetricDataSchema(BaseModel):
    """Schema for metric data."""
    name: str = Field(..., description="Metric name")
    display_name: str = Field(..., description="Display name")
    unit: Optional[str] = Field(default=None, description="Unit of measurement")
    type: MetricType = Field(..., description="Metric type")
    values: List[MetricValueSchema] = Field(..., description="Metric values")
    metadata: Optional[Dict[str, Any]] = Field(default=None, description="Metric metadata")
    aggregation: Optional[str] = Field(default=None, description="Applied aggregation")
    trend: Optional[Dict[str, Any]] = Field(default=None, description="Trend information")


class MetricsResponseSchema(BaseModel):
    """Schema for metrics response."""
    metrics: List[MetricDataSchema] = Field(..., description="Metric data")
    filters_applied: Dict[str, Any] = Field(..., description="Applied filters")
    timestamp: datetime = Field(..., description="Response timestamp")
    cache_status: str = Field(..., description="Cache status")
    execution_time_ms: float = Field(..., description="Query execution time in milliseconds")


class MetricCreateSchema(BaseModel):
    """Schema for creating a metric."""
    name: str = Field(..., min_length=1, max_length=100, regex="^[a-zA-Z][a-zA-Z0-9_]*$", description="Metric name (alphanumeric + underscore)")
    display_name: str = Field(..., min_length=1, max_length=200, description="Human-readable metric name")
    description: Optional[str] = Field(default=None, max_length=1000, description="Metric description")
    metric_type: MetricType = Field(..., description="Type of metric")
    unit: Optional[str] = Field(default=None, max_length=20, description="Unit of measurement")
    query: str = Field(..., min_length=1, description="SQL query or calculation logic")
    aggregation_type: AggregationType = Field(default=AggregationType.SUM, description="How to aggregate values")
    filters: Dict[str, Any] = Field(default_factory=dict, description="Default filters")
    dimensions: List[str] = Field(default_factory=list, description="Metric dimensions")
    tags: List[str] = Field(default_factory=list, description="Metric tags")
    refresh_interval: int = Field(default=300, ge=30, description="Refresh interval in seconds")


class MetricUpdateSchema(BaseModel):
    """Schema for updating a metric."""
    display_name: Optional[str] = Field(default=None, min_length=1, max_length=200, description="Human-readable metric name")
    description: Optional[str] = Field(default=None, max_length=1000, description="Metric description")
    unit: Optional[str] = Field(default=None, max_length=20, description="Unit of measurement")
    query: Optional[str] = Field(default=None, min_length=1, description="SQL query or calculation logic")
    aggregation_type: Optional[AggregationType] = Field(default=None, description="How to aggregate values")
    filters: Optional[Dict[str, Any]] = Field(default=None, description="Default filters")
    dimensions: Optional[List[str]] = Field(default=None, description="Metric dimensions")
    tags: Optional[List[str]] = Field(default=None, description="Metric tags")
    is_active: Optional[bool] = Field(default=None, description="Whether metric is active")
    refresh_interval: Optional[int] = Field(default=None, ge=30, description="Refresh interval in seconds")


class MetricResponseSchema(BaseModel):
    """Schema for metric response."""
    id: str = Field(..., description="Metric ID")
    name: str = Field(..., description="Metric name")
    display_name: str = Field(..., description="Display name")
    description: Optional[str] = Field(default=None, description="Metric description")
    metric_type: MetricType = Field(..., description="Metric type")
    unit: Optional[str] = Field(default=None, description="Unit of measurement")
    query: str = Field(..., description="SQL query")
    aggregation_type: AggregationType = Field(..., description="Aggregation type")
    filters: Dict[str, Any] = Field(..., description="Default filters")
    dimensions: List[str] = Field(..., description="Metric dimensions")
    tags: List[str] = Field(..., description="Metric tags")
    is_active: bool = Field(..., description="Whether metric is active")
    refresh_interval: int = Field(..., description="Refresh interval in seconds")
    created_by: Optional[str] = Field(default=None, description="Created by user")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: Optional[datetime] = Field(default=None, description="Last update timestamp")
    last_calculated: Optional[datetime] = Field(default=None, description="Last calculation timestamp")

    class Config:
        from_attributes = True


class MetricListResponseSchema(BaseModel):
    """Schema for metric list response."""
    metrics: List[MetricResponseSchema] = Field(..., description="List of metrics")
    total: int = Field(..., ge=0, description="Total number of metrics")
    page: int = Field(..., ge=1, description="Current page number")
    size: int = Field(..., ge=1, description="Page size")


class RealTimeMetricSchema(BaseModel):
    """Schema for real-time metric update."""
    metric_name: str = Field(..., description="Metric name")
    value: Union[float, int] = Field(..., description="Current metric value")
    change: Optional[float] = Field(default=None, description="Change from previous value")
    change_percent: Optional[float] = Field(default=None, description="Percentage change")
    timestamp: datetime = Field(..., description="Update timestamp")
    trend: Optional[str] = Field(default=None, regex="^(up|down|stable)$", description="Trend direction")


class AlertRuleSchema(BaseModel):
    """Schema for metric alert rule."""
    metric_name: str = Field(..., description="Metric to monitor")
    condition: str = Field(..., regex="^(gt|gte|lt|lte|eq|neq)$", description="Alert condition")
    threshold: float = Field(..., description="Alert threshold value")
    duration: int = Field(..., ge=60, description="Duration in seconds before triggering")
    severity: str = Field(..., regex="^(low|medium|high|critical)$", description="Alert severity")
    message: str = Field(..., description="Alert message template")
    channels: List[str] = Field(..., description="Notification channels")
    is_active: bool = Field(default=True, description="Whether alert is active")


class AlertTriggerSchema(BaseModel):
    """Schema for alert trigger."""
    alert_rule_id: str = Field(..., description="Alert rule ID")
    metric_name: str = Field(..., description="Metric name")
    current_value: float = Field(..., description="Current metric value")
    threshold: float = Field(..., description="Alert threshold")
    condition: str = Field(..., description="Alert condition")
    severity: str = Field(..., description="Alert severity")
    message: str = Field(..., description="Alert message")
    triggered_at: datetime = Field(..., description="Trigger timestamp")
    resolved_at: Optional[datetime] = Field(default=None, description="Resolution timestamp")


class MetricComparisonSchema(BaseModel):
    """Schema for metric comparison."""
    metric_name: str = Field(..., description="Metric name")
    current_period: Dict[str, Any] = Field(..., description="Current period data")
    previous_period: Dict[str, Any] = Field(..., description="Previous period data")
    change_absolute: float = Field(..., description="Absolute change")
    change_percent: float = Field(..., description="Percentage change")
    trend: str = Field(..., description="Trend direction")
    significance: Optional[str] = Field(default=None, description="Statistical significance")


class MetricForecastSchema(BaseModel):
    """Schema for metric forecast."""
    metric_name: str = Field(..., description="Metric name")
    historical_data: List[MetricValueSchema] = Field(..., description="Historical data points")
    forecast_data: List[Dict[str, Any]] = Field(..., description="Forecasted values")
    confidence_interval: Dict[str, List[float]] = Field(..., description="Confidence intervals")
    model_accuracy: Optional[float] = Field(default=None, description="Model accuracy score")
    generated_at: datetime = Field(..., description="Forecast generation time")


class CustomMetricQuerySchema(BaseModel):
    """Schema for custom metric query."""
    query: str = Field(..., description="Custom SQL query")
    parameters: Dict[str, Any] = Field(default_factory=dict, description="Query parameters")
    cache_ttl: int = Field(default=300, ge=0, description="Cache TTL in seconds")
    timeout: int = Field(default=30, ge=1, le=300, description="Query timeout in seconds")


class MetricExportRequestSchema(BaseModel):
    """Schema for metric export request."""
    metrics: List[str] = Field(..., description="Metrics to export")
    format: str = Field(..., regex="^(csv|excel|json|pdf)$", description="Export format")
    filters: MetricFiltersSchema = Field(default_factory=MetricFiltersSchema, description="Export filters")
    include_charts: bool = Field(default=False, description="Include charts in export")
    email_recipients: List[str] = Field(default_factory=list, description="Email recipients")


class MetricExportResponseSchema(BaseModel):
    """Schema for metric export response."""
    export_id: str = Field(..., description="Export task ID")
    status: str = Field(..., description="Export status")
    download_url: Optional[str] = Field(default=None, description="Download URL when ready")
    expires_at: Optional[datetime] = Field(default=None, description="Export expiration time")