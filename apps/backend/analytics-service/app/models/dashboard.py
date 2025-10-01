"""
Dashboard configuration model for dynamic dashboard management
"""

from datetime import datetime
from typing import Dict, Any, List, Optional
from sqlmodel import SQLModel, Field, JSON, Column
from uuid import uuid4
from enum import Enum


class DashboardType(str, Enum):
    """Dashboard types."""
    SHELL = "shell"  # Global platform metrics
    ADMIN = "admin"  # Administrative insights
    COMPANY = "company"  # Company/HR metrics
    LEARNER = "learner"  # Individual learner metrics


class WidgetType(str, Enum):
    """Widget types."""
    METRIC_CARD = "metric_card"
    LINE_CHART = "line_chart"
    BAR_CHART = "bar_chart"
    PIE_CHART = "pie_chart"
    TABLE = "table"
    HEATMAP = "heatmap"
    FUNNEL = "funnel"
    GAUGE = "gauge"
    MAP = "map"
    TIMELINE = "timeline"


class DashboardBase(SQLModel):
    """Base dashboard model."""
    name: str = Field(..., description="Dashboard name")
    type: DashboardType = Field(..., description="Dashboard type")
    description: Optional[str] = Field(default=None, description="Dashboard description")
    config: Dict[str, Any] = Field(default_factory=dict, sa_column=Column(JSON), description="Dashboard configuration")
    widgets: List[Dict[str, Any]] = Field(default_factory=list, sa_column=Column(JSON), description="Widget configurations")
    is_active: bool = Field(default=True, description="Whether dashboard is active")
    refresh_interval: int = Field(default=300, description="Refresh interval in seconds")
    access_roles: List[str] = Field(default_factory=list, sa_column=Column(JSON), description="Roles that can access this dashboard")


class Dashboard(DashboardBase, table=True):
    """Dashboard database model."""
    __tablename__ = "dashboards"

    id: Optional[str] = Field(
        default_factory=lambda: str(uuid4()),
        primary_key=True,
        description="Dashboard ID"
    )
    created_by: Optional[str] = Field(default=None, description="User who created the dashboard")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Creation timestamp")
    updated_at: Optional[datetime] = Field(default=None, description="Last update timestamp")

    def get_widget_by_id(self, widget_id: str) -> Optional[Dict[str, Any]]:
        """Get widget configuration by ID."""
        for widget in self.widgets:
            if widget.get("id") == widget_id:
                return widget
        return None

    def add_widget(self, widget_config: Dict[str, Any]) -> bool:
        """Add a widget to the dashboard."""
        if "id" not in widget_config:
            widget_config["id"] = str(uuid4())

        # Validate widget type
        if widget_config.get("type") not in [wt.value for wt in WidgetType]:
            return False

        self.widgets.append(widget_config)
        return True

    def remove_widget(self, widget_id: str) -> bool:
        """Remove a widget from the dashboard."""
        original_length = len(self.widgets)
        self.widgets = [w for w in self.widgets if w.get("id") != widget_id]
        return len(self.widgets) < original_length


class DashboardCreate(DashboardBase):
    """Dashboard creation model."""
    pass


class DashboardRead(DashboardBase):
    """Dashboard read model."""
    id: str
    created_by: Optional[str]
    created_at: datetime
    updated_at: Optional[datetime]


class DashboardUpdate(SQLModel):
    """Dashboard update model."""
    name: Optional[str] = None
    description: Optional[str] = None
    config: Optional[Dict[str, Any]] = None
    widgets: Optional[List[Dict[str, Any]]] = None
    is_active: Optional[bool] = None
    refresh_interval: Optional[int] = None
    access_roles: Optional[List[str]] = None
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class WidgetConfig(SQLModel):
    """Widget configuration model."""
    id: str = Field(default_factory=lambda: str(uuid4()))
    type: WidgetType
    title: str
    position: Dict[str, int] = Field(default_factory=dict)  # x, y, width, height
    data_source: str  # API endpoint or query
    refresh_interval: Optional[int] = Field(default=None, description="Override dashboard refresh interval")
    filters: Dict[str, Any] = Field(default_factory=dict)
    display_options: Dict[str, Any] = Field(default_factory=dict)
    permissions: List[str] = Field(default_factory=list)


# Pre-defined dashboard templates
DEFAULT_SHELL_DASHBOARD = {
    "name": "Shell Platform Overview",
    "type": DashboardType.SHELL,
    "description": "Global platform metrics and insights",
    "widgets": [
        {
            "id": "dau_metric",
            "type": WidgetType.METRIC_CARD.value,
            "title": "Daily Active Users",
            "position": {"x": 0, "y": 0, "width": 3, "height": 2},
            "data_source": "/api/v1/metrics/dau",
            "display_options": {"format": "number", "trend": True}
        },
        {
            "id": "user_growth_chart",
            "type": WidgetType.LINE_CHART.value,
            "title": "User Growth Trend",
            "position": {"x": 3, "y": 0, "width": 6, "height": 4},
            "data_source": "/api/v1/metrics/user-growth",
            "display_options": {"time_range": "30d"}
        },
        {
            "id": "service_health",
            "type": WidgetType.TABLE.value,
            "title": "Service Health",
            "position": {"x": 9, "y": 0, "width": 3, "height": 4},
            "data_source": "/api/v1/metrics/service-health",
            "display_options": {"columns": ["service", "status", "response_time"]}
        }
    ],
    "access_roles": ["admin", "shell_user"]
}

DEFAULT_ADMIN_DASHBOARD = {
    "name": "Admin Business Intelligence",
    "type": DashboardType.ADMIN,
    "description": "Business analytics and administrative insights",
    "widgets": [
        {
            "id": "revenue_metric",
            "type": WidgetType.METRIC_CARD.value,
            "title": "Monthly Revenue",
            "position": {"x": 0, "y": 0, "width": 3, "height": 2},
            "data_source": "/api/v1/metrics/revenue",
            "display_options": {"format": "currency", "trend": True}
        },
        {
            "id": "conversion_funnel",
            "type": WidgetType.FUNNEL.value,
            "title": "User Conversion Funnel",
            "position": {"x": 3, "y": 0, "width": 6, "height": 4},
            "data_source": "/api/v1/metrics/conversion-funnel",
            "display_options": {"funnel_type": "signup"}
        },
        {
            "id": "error_rate",
            "type": WidgetType.GAUGE.value,
            "title": "System Error Rate",
            "position": {"x": 9, "y": 0, "width": 3, "height": 2},
            "data_source": "/api/v1/metrics/error-rate",
            "display_options": {"max_value": 5, "threshold": 2}
        }
    ],
    "access_roles": ["admin", "business_analyst"]
}

DEFAULT_COMPANY_DASHBOARD = {
    "name": "Company HR Analytics",
    "type": DashboardType.COMPANY,
    "description": "Recruitment and talent management metrics",
    "widgets": [
        {
            "id": "active_positions",
            "type": WidgetType.METRIC_CARD.value,
            "title": "Active Job Positions",
            "position": {"x": 0, "y": 0, "width": 3, "height": 2},
            "data_source": "/api/v1/metrics/active-positions",
            "display_options": {"format": "number"}
        },
        {
            "id": "candidate_pipeline",
            "type": WidgetType.BAR_CHART.value,
            "title": "Candidate Pipeline",
            "position": {"x": 3, "y": 0, "width": 6, "height": 4},
            "data_source": "/api/v1/metrics/candidate-pipeline",
            "display_options": {"group_by": "stage"}
        },
        {
            "id": "skills_demand",
            "type": WidgetType.PIE_CHART.value,
            "title": "Skills in Demand",
            "position": {"x": 9, "y": 0, "width": 3, "height": 4},
            "data_source": "/api/v1/metrics/skills-demand",
            "display_options": {"top_n": 10}
        }
    ],
    "access_roles": ["company_admin", "hr_manager"]
}

DEFAULT_LEARNER_DASHBOARD = {
    "name": "Learner Progress Dashboard",
    "type": DashboardType.LEARNER,
    "description": "Personal learning progress and recommendations",
    "widgets": [
        {
            "id": "skill_progress",
            "type": WidgetType.GAUGE.value,
            "title": "Skill Development Progress",
            "position": {"x": 0, "y": 0, "width": 6, "height": 3},
            "data_source": "/api/v1/metrics/skill-progress",
            "display_options": {"max_value": 100, "unit": "%"}
        },
        {
            "id": "project_timeline",
            "type": WidgetType.TIMELINE.value,
            "title": "Project Timeline",
            "position": {"x": 6, "y": 0, "width": 6, "height": 3},
            "data_source": "/api/v1/metrics/project-timeline",
            "display_options": {"time_range": "90d"}
        },
        {
            "id": "recommendations",
            "type": WidgetType.TABLE.value,
            "title": "Personalized Recommendations",
            "position": {"x": 0, "y": 3, "width": 12, "height": 3},
            "data_source": "/api/v1/metrics/recommendations",
            "display_options": {"columns": ["recommendation", "priority", "estimated_time"]}
        }
    ],
    "access_roles": ["learner"]
}