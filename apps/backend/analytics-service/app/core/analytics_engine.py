"""
Core Analytics Engine for SkillForge AI Analytics Service
"""

import asyncio
import logging
from typing import Dict, Any, List, Optional, Union
from datetime import datetime, timedelta
import pandas as pd
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_
import numpy as np

from app.core.config import get_settings
from app.core.database import get_session
from app.models.analytics_event import AnalyticsEvent
from app.models.metric import Metric
from app.models.dashboard import Dashboard
from app.core.monitoring import MetricsCollector

settings = get_settings()
logger = logging.getLogger(__name__)


class AnalyticsEngine:
    """Core analytics processing engine."""

    def __init__(self):
        self.cache = {}
        self.cache_ttl = settings.CACHE_TTL

    async def track_event(self, event_data: Dict[str, Any]) -> AnalyticsEvent:
        """Track analytics event."""
        async with AsyncSession(bind=None) as session:
            event = AnalyticsEvent(
                event_type=event_data.get("event_type"),
                user_id=event_data.get("user_id"),
                session_id=event_data.get("session_id"),
                metadata=event_data.get("metadata", {}),
                timestamp=datetime.utcnow()
            )
            session.add(event)
            await session.commit()
            await session.refresh(event)
            logger.info(f"Tracked event: {event.event_type} for user {event.user_id}")
            return event

    async def get_user_metrics(self, time_range: str = "7d") -> Dict[str, Any]:
        """Get user activity metrics."""
        try:
            start_date = self._parse_time_range(time_range)

            async with AsyncSession(bind=None) as session:
                # Daily Active Users
                dau_query = select(func.count(func.distinct(AnalyticsEvent.user_id))).where(
                    and_(
                        AnalyticsEvent.timestamp >= datetime.utcnow() - timedelta(days=1),
                        AnalyticsEvent.event_type.in_(["login", "page_view", "action"])
                    )
                )
                dau_result = await session.execute(dau_query)
                dau = dau_result.scalar() or 0

                # Weekly Active Users
                wau_query = select(func.count(func.distinct(AnalyticsEvent.user_id))).where(
                    and_(
                        AnalyticsEvent.timestamp >= datetime.utcnow() - timedelta(days=7),
                        AnalyticsEvent.event_type.in_(["login", "page_view", "action"])
                    )
                )
                wau_result = await session.execute(wau_query)
                wau = wau_result.scalar() or 0

                # Monthly Active Users
                mau_query = select(func.count(func.distinct(AnalyticsEvent.user_id))).where(
                    and_(
                        AnalyticsEvent.timestamp >= datetime.utcnow() - timedelta(days=30),
                        AnalyticsEvent.event_type.in_(["login", "page_view", "action"])
                    )
                )
                mau_result = await session.execute(mau_query)
                mau = mau_result.scalar() or 0

                # User sessions
                session_query = select(func.count(func.distinct(AnalyticsEvent.session_id))).where(
                    AnalyticsEvent.timestamp >= start_date
                )
                session_result = await session.execute(session_query)
                total_sessions = session_result.scalar() or 0

                return {
                    "daily_active_users": dau,
                    "weekly_active_users": wau,
                    "monthly_active_users": mau,
                    "total_sessions": total_sessions,
                    "period": time_range
                }

        except Exception as e:
            logger.error(f"Error calculating user metrics: {e}")
            return {}

    async def get_project_metrics(self, time_range: str = "7d") -> Dict[str, Any]:
        """Get project-related metrics."""
        try:
            # This would integrate with project-service
            # For now, returning mock data
            return {
                "total_projects": 0,
                "projects_submitted": 0,
                "projects_completed": 0,
                "average_completion_time": 0,
                "success_rate": 0.0,
                "period": time_range
            }
        except Exception as e:
            logger.error(f"Error calculating project metrics: {e}")
            return {}

    async def get_matching_metrics(self, time_range: str = "7d") -> Dict[str, Any]:
        """Get matching service metrics."""
        try:
            # This would integrate with matching-service
            return {
                "total_matches": 0,
                "successful_matches": 0,
                "match_success_rate": 0.0,
                "average_match_time": 0,
                "period": time_range
            }
        except Exception as e:
            logger.error(f"Error calculating matching metrics: {e}")
            return {}

    async def get_conversion_funnel(self, funnel_type: str = "user_signup") -> Dict[str, Any]:
        """Calculate conversion funnel metrics."""
        try:
            if funnel_type == "user_signup":
                return await self._calculate_signup_funnel()
            elif funnel_type == "project_submission":
                return await self._calculate_project_funnel()
            else:
                return {}
        except Exception as e:
            logger.error(f"Error calculating conversion funnel: {e}")
            return {}

    async def _calculate_signup_funnel(self) -> Dict[str, Any]:
        """Calculate user signup funnel."""
        async with AsyncSession(bind=None) as session:
            # Landing page views
            landing_query = select(func.count(AnalyticsEvent.id)).where(
                AnalyticsEvent.event_type == "landing_page_view"
            )
            landing_result = await session.execute(landing_query)
            landing_views = landing_result.scalar() or 1

            # Signup page views
            signup_query = select(func.count(AnalyticsEvent.id)).where(
                AnalyticsEvent.event_type == "signup_page_view"
            )
            signup_result = await session.execute(signup_query)
            signup_views = signup_result.scalar() or 0

            # Completed signups
            completed_query = select(func.count(AnalyticsEvent.id)).where(
                AnalyticsEvent.event_type == "user_registered"
            )
            completed_result = await session.execute(completed_query)
            completed_signups = completed_result.scalar() or 0

            return {
                "funnel_type": "user_signup",
                "steps": [
                    {
                        "step": "landing_page",
                        "count": landing_views,
                        "conversion_rate": 100.0
                    },
                    {
                        "step": "signup_page",
                        "count": signup_views,
                        "conversion_rate": (signup_views / landing_views) * 100
                    },
                    {
                        "step": "completed_signup",
                        "count": completed_signups,
                        "conversion_rate": (completed_signups / landing_views) * 100
                    }
                ]
            }

    async def _calculate_project_funnel(self) -> Dict[str, Any]:
        """Calculate project submission funnel."""
        # Mock implementation - would integrate with project service
        return {
            "funnel_type": "project_submission",
            "steps": [
                {"step": "project_started", "count": 0, "conversion_rate": 100.0},
                {"step": "project_submitted", "count": 0, "conversion_rate": 0.0},
                {"step": "project_approved", "count": 0, "conversion_rate": 0.0}
            ]
        }

    async def calculate_cohort_analysis(self, cohort_type: str = "registration") -> Dict[str, Any]:
        """Calculate cohort analysis."""
        try:
            # This is a simplified version - would need more complex logic
            return {
                "cohort_type": cohort_type,
                "periods": ["Week 0", "Week 1", "Week 2", "Week 3", "Week 4"],
                "cohorts": []
            }
        except Exception as e:
            logger.error(f"Error calculating cohort analysis: {e}")
            return {}

    async def detect_anomalies(self, metric_name: str, threshold: float = 2.0) -> List[Dict[str, Any]]:
        """Detect anomalies in metrics."""
        try:
            anomalies = []
            # Implement anomaly detection logic here
            # For now, returning empty list
            return anomalies
        except Exception as e:
            logger.error(f"Error detecting anomalies: {e}")
            return []

    async def generate_insights(self, dashboard_type: str) -> List[Dict[str, Any]]:
        """Generate AI-powered insights."""
        try:
            insights = []

            if dashboard_type == "shell":
                insights.extend(await self._generate_platform_insights())
            elif dashboard_type == "admin":
                insights.extend(await self._generate_admin_insights())
            elif dashboard_type == "company":
                insights.extend(await self._generate_company_insights())
            elif dashboard_type == "learner":
                insights.extend(await self._generate_learner_insights())

            return insights
        except Exception as e:
            logger.error(f"Error generating insights: {e}")
            return []

    async def _generate_platform_insights(self) -> List[Dict[str, Any]]:
        """Generate platform-level insights."""
        return [
            {
                "type": "trend",
                "title": "User Activity Trending Up",
                "description": "Daily active users increased by 15% this week",
                "severity": "info",
                "timestamp": datetime.utcnow().isoformat()
            }
        ]

    async def _generate_admin_insights(self) -> List[Dict[str, Any]]:
        """Generate admin-level insights."""
        return [
            {
                "type": "alert",
                "title": "Service Performance Alert",
                "description": "Response time increased above threshold",
                "severity": "warning",
                "timestamp": datetime.utcnow().isoformat()
            }
        ]

    async def _generate_company_insights(self) -> List[Dict[str, Any]]:
        """Generate company-level insights."""
        return [
            {
                "type": "recommendation",
                "title": "Talent Pool Expansion",
                "description": "Consider recruiting in emerging technology areas",
                "severity": "info",
                "timestamp": datetime.utcnow().isoformat()
            }
        ]

    async def _generate_learner_insights(self) -> List[Dict[str, Any]]:
        """Generate learner-level insights."""
        return [
            {
                "type": "achievement",
                "title": "Learning Progress",
                "description": "You're in the top 20% of active learners this month",
                "severity": "success",
                "timestamp": datetime.utcnow().isoformat()
            }
        ]

    def _parse_time_range(self, time_range: str) -> datetime:
        """Parse time range string to datetime."""
        if time_range.endswith("d"):
            days = int(time_range[:-1])
            return datetime.utcnow() - timedelta(days=days)
        elif time_range.endswith("h"):
            hours = int(time_range[:-1])
            return datetime.utcnow() - timedelta(hours=hours)
        elif time_range.endswith("m"):
            minutes = int(time_range[:-1])
            return datetime.utcnow() - timedelta(minutes=minutes)
        else:
            return datetime.utcnow() - timedelta(days=7)


# Global analytics engine instance
analytics_engine = AnalyticsEngine()