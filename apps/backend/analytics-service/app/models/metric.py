"""
Metric definition and calculation models
"""

from datetime import datetime
from typing import Dict, Any, Optional, List
from sqlmodel import SQLModel, Field, JSON, Column
from uuid import uuid4
from enum import Enum


class MetricType(str, Enum):
    """Metric types."""
    COUNTER = "counter"  # Incrementing value
    GAUGE = "gauge"  # Current value at point in time
    HISTOGRAM = "histogram"  # Distribution of values
    RATE = "rate"  # Change over time
    PERCENTAGE = "percentage"  # Percentage value
    CURRENCY = "currency"  # Monetary value


class AggregationType(str, Enum):
    """Aggregation types."""
    SUM = "sum"
    COUNT = "count"
    AVERAGE = "average"
    MIN = "min"
    MAX = "max"
    MEDIAN = "median"
    PERCENTILE = "percentile"
    DISTINCT_COUNT = "distinct_count"


class MetricBase(SQLModel):
    """Base metric model."""
    name: str = Field(..., description="Metric name")
    display_name: str = Field(..., description="Human-readable metric name")
    description: Optional[str] = Field(default=None, description="Metric description")
    metric_type: MetricType = Field(..., description="Type of metric")
    unit: Optional[str] = Field(default=None, description="Unit of measurement")
    query: str = Field(..., description="SQL query or calculation logic")
    aggregation_type: AggregationType = Field(default=AggregationType.SUM, description="How to aggregate values")
    filters: Dict[str, Any] = Field(default_factory=dict, sa_column=Column(JSON), description="Default filters")
    dimensions: List[str] = Field(default_factory=list, sa_column=Column(JSON), description="Metric dimensions")
    tags: List[str] = Field(default_factory=list, sa_column=Column(JSON), description="Metric tags")
    is_active: bool = Field(default=True, description="Whether metric is active")
    refresh_interval: int = Field(default=300, description="Refresh interval in seconds")


class Metric(MetricBase, table=True):
    """Metric database model."""
    __tablename__ = "metrics"

    id: Optional[str] = Field(
        default_factory=lambda: str(uuid4()),
        primary_key=True,
        description="Metric ID"
    )
    created_by: Optional[str] = Field(default=None, description="User who created the metric")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Creation timestamp")
    updated_at: Optional[datetime] = Field(default=None, description="Last update timestamp")
    last_calculated: Optional[datetime] = Field(default=None, description="Last calculation timestamp")

    def should_refresh(self) -> bool:
        """Check if metric should be refreshed."""
        if not self.last_calculated:
            return True

        time_diff = datetime.utcnow() - self.last_calculated
        return time_diff.total_seconds() > self.refresh_interval


class MetricCreate(MetricBase):
    """Metric creation model."""
    pass


class MetricRead(MetricBase):
    """Metric read model."""
    id: str
    created_by: Optional[str]
    created_at: datetime
    updated_at: Optional[datetime]
    last_calculated: Optional[datetime]


class MetricUpdate(SQLModel):
    """Metric update model."""
    display_name: Optional[str] = None
    description: Optional[str] = None
    unit: Optional[str] = None
    query: Optional[str] = None
    aggregation_type: Optional[AggregationType] = None
    filters: Optional[Dict[str, Any]] = None
    dimensions: Optional[List[str]] = None
    tags: Optional[List[str]] = None
    is_active: Optional[bool] = None
    refresh_interval: Optional[int] = None
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class MetricValue(SQLModel, table=True):
    """Metric value storage model."""
    __tablename__ = "metric_values"

    id: Optional[str] = Field(
        default_factory=lambda: str(uuid4()),
        primary_key=True,
        description="Value ID"
    )
    metric_id: str = Field(..., description="Metric ID", foreign_key="metrics.id")
    value: float = Field(..., description="Metric value")
    dimensions: Optional[Dict[str, Any]] = Field(default_factory=dict, sa_column=Column(JSON), description="Dimension values")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Value timestamp")
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict, sa_column=Column(JSON), description="Additional metadata")


class MetricValueCreate(SQLModel):
    """Metric value creation model."""
    metric_id: str
    value: float
    dimensions: Optional[Dict[str, Any]] = None
    metadata: Optional[Dict[str, Any]] = None


class MetricValueRead(SQLModel):
    """Metric value read model."""
    id: str
    metric_id: str
    value: float
    dimensions: Optional[Dict[str, Any]]
    timestamp: datetime
    metadata: Optional[Dict[str, Any]]


# Pre-defined metrics
PREDEFINED_METRICS = [
    {
        "name": "daily_active_users",
        "display_name": "Daily Active Users",
        "description": "Number of unique users active in the last 24 hours",
        "metric_type": MetricType.GAUGE,
        "unit": "users",
        "query": """
            SELECT COUNT(DISTINCT user_id) as value
            FROM analytics_events
            WHERE timestamp >= NOW() - INTERVAL '1 day'
            AND event_type IN ('login', 'page_view', 'action')
        """,
        "aggregation_type": AggregationType.COUNT,
        "tags": ["users", "engagement", "daily"],
        "refresh_interval": 3600  # 1 hour
    },
    {
        "name": "weekly_active_users",
        "display_name": "Weekly Active Users",
        "description": "Number of unique users active in the last 7 days",
        "metric_type": MetricType.GAUGE,
        "unit": "users",
        "query": """
            SELECT COUNT(DISTINCT user_id) as value
            FROM analytics_events
            WHERE timestamp >= NOW() - INTERVAL '7 days'
            AND event_type IN ('login', 'page_view', 'action')
        """,
        "aggregation_type": AggregationType.COUNT,
        "tags": ["users", "engagement", "weekly"],
        "refresh_interval": 7200  # 2 hours
    },
    {
        "name": "monthly_active_users",
        "display_name": "Monthly Active Users",
        "description": "Number of unique users active in the last 30 days",
        "metric_type": MetricType.GAUGE,
        "unit": "users",
        "query": """
            SELECT COUNT(DISTINCT user_id) as value
            FROM analytics_events
            WHERE timestamp >= NOW() - INTERVAL '30 days'
            AND event_type IN ('login', 'page_view', 'action')
        """,
        "aggregation_type": AggregationType.COUNT,
        "tags": ["users", "engagement", "monthly"],
        "refresh_interval": 14400  # 4 hours
    },
    {
        "name": "session_count",
        "display_name": "Total Sessions",
        "description": "Total number of user sessions",
        "metric_type": MetricType.COUNTER,
        "unit": "sessions",
        "query": """
            SELECT COUNT(DISTINCT session_id) as value
            FROM analytics_events
            WHERE timestamp >= NOW() - INTERVAL '1 day'
        """,
        "aggregation_type": AggregationType.COUNT,
        "tags": ["sessions", "engagement"],
        "refresh_interval": 1800  # 30 minutes
    },
    {
        "name": "error_rate",
        "display_name": "Error Rate",
        "description": "Percentage of requests resulting in errors",
        "metric_type": MetricType.PERCENTAGE,
        "unit": "%",
        "query": """
            SELECT
                (COUNT(CASE WHEN event_type = 'error_occurred' THEN 1 END) * 100.0 /
                 NULLIF(COUNT(*), 0)) as value
            FROM analytics_events
            WHERE timestamp >= NOW() - INTERVAL '1 hour'
        """,
        "aggregation_type": AggregationType.AVERAGE,
        "tags": ["errors", "performance", "reliability"],
        "refresh_interval": 300  # 5 minutes
    },
    {
        "name": "page_views",
        "display_name": "Page Views",
        "description": "Total number of page views",
        "metric_type": MetricType.COUNTER,
        "unit": "views",
        "query": """
            SELECT COUNT(*) as value
            FROM analytics_events
            WHERE event_type = 'page_view'
            AND timestamp >= NOW() - INTERVAL '1 day'
        """,
        "aggregation_type": AggregationType.COUNT,
        "dimensions": ["page_url", "user_type"],
        "tags": ["navigation", "engagement"],
        "refresh_interval": 900  # 15 minutes
    },
    {
        "name": "conversion_rate",
        "display_name": "Conversion Rate",
        "description": "Percentage of users who complete desired actions",
        "metric_type": MetricType.PERCENTAGE,
        "unit": "%",
        "query": """
            SELECT
                (COUNT(CASE WHEN event_type = 'user_registered' THEN 1 END) * 100.0 /
                 NULLIF(COUNT(CASE WHEN event_type = 'landing_page_view' THEN 1 END), 0)) as value
            FROM analytics_events
            WHERE timestamp >= NOW() - INTERVAL '7 days'
        """,
        "aggregation_type": AggregationType.AVERAGE,
        "tags": ["conversion", "funnel", "business"],
        "refresh_interval": 3600  # 1 hour
    },
    {
        "name": "projects_submitted",
        "display_name": "Projects Submitted",
        "description": "Number of projects submitted",
        "metric_type": MetricType.COUNTER,
        "unit": "projects",
        "query": """
            SELECT COUNT(*) as value
            FROM analytics_events
            WHERE event_type = 'project_submitted'
            AND timestamp >= NOW() - INTERVAL '1 day'
        """,
        "aggregation_type": AggregationType.COUNT,
        "tags": ["projects", "submissions"],
        "refresh_interval": 1800  # 30 minutes
    },
    {
        "name": "match_success_rate",
        "display_name": "Match Success Rate",
        "description": "Percentage of successful matches",
        "metric_type": MetricType.PERCENTAGE,
        "unit": "%",
        "query": """
            SELECT
                (COUNT(CASE WHEN event_type = 'match_successful' THEN 1 END) * 100.0 /
                 NULLIF(COUNT(CASE WHEN event_type = 'match_requested' THEN 1 END), 0)) as value
            FROM analytics_events
            WHERE timestamp >= NOW() - INTERVAL '1 day'
        """,
        "aggregation_type": AggregationType.AVERAGE,
        "tags": ["matching", "success", "business"],
        "refresh_interval": 1800  # 30 minutes
    },
    {
        "name": "response_time",
        "display_name": "Average Response Time",
        "description": "Average API response time",
        "metric_type": MetricType.GAUGE,
        "unit": "ms",
        "query": """
            SELECT AVG(CAST(metadata->>'response_time' AS FLOAT)) as value
            FROM analytics_events
            WHERE event_type = 'api_call'
            AND timestamp >= NOW() - INTERVAL '1 hour'
        """,
        "aggregation_type": AggregationType.AVERAGE,
        "dimensions": ["service", "endpoint"],
        "tags": ["performance", "response_time"],
        "refresh_interval": 300  # 5 minutes
    }
]