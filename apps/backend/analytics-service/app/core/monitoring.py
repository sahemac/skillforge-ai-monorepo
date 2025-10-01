"""
Prometheus monitoring and metrics collection for Analytics Service
"""

import time
import logging
from typing import Dict, Any, Optional
import asyncio
import httpx
from prometheus_client import Counter, Histogram, Gauge, generate_latest, CONTENT_TYPE_LATEST
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from app.core.config import get_settings

settings = get_settings()
logger = logging.getLogger(__name__)

# Prometheus metrics
REQUEST_COUNT = Counter(
    'analytics_requests_total',
    'Total number of analytics requests',
    ['method', 'endpoint', 'status_code']
)

REQUEST_DURATION = Histogram(
    'analytics_request_duration_seconds',
    'Request duration in seconds',
    ['method', 'endpoint']
)

DASHBOARD_LOAD_TIME = Histogram(
    'dashboard_load_time_seconds',
    'Time taken to load dashboard data',
    ['dashboard_type']
)

REPORT_GENERATION_TIME = Histogram(
    'report_generation_duration_seconds',
    'Time taken to generate reports',
    ['report_type']
)

ACTIVE_WEBSOCKET_CONNECTIONS = Gauge(
    'realtime_connections_active',
    'Number of active WebSocket connections'
)

DATA_PROCESSING_LAG = Gauge(
    'data_processing_lag_seconds',
    'Lag in data processing pipeline'
)

ALERT_TRIGGERS = Counter(
    'alert_triggers_total',
    'Total number of alert triggers',
    ['alert_type', 'severity']
)

BIGQUERY_QUERIES = Counter(
    'bigquery_queries_total',
    'Total number of BigQuery queries executed',
    ['query_type', 'status']
)

CACHE_HITS = Counter(
    'analytics_cache_hits_total',
    'Total cache hits',
    ['cache_type']
)

CACHE_MISSES = Counter(
    'analytics_cache_misses_total',
    'Total cache misses',
    ['cache_type']
)


class PrometheusMiddleware(BaseHTTPMiddleware):
    """Middleware to collect Prometheus metrics."""

    async def dispatch(self, request: Request, call_next):
        """Process request and collect metrics."""
        start_time = time.time()
        method = request.method
        path = request.url.path

        # Get route pattern for better grouping
        endpoint = path
        if hasattr(request, "path_info"):
            endpoint = request.path_info

        response = await call_next(request)

        # Record metrics
        duration = time.time() - start_time
        status_code = str(response.status_code)

        REQUEST_COUNT.labels(
            method=method,
            endpoint=endpoint,
            status_code=status_code
        ).inc()

        REQUEST_DURATION.labels(
            method=method,
            endpoint=endpoint
        ).observe(duration)

        return response


class MetricsCollector:
    """Collect custom analytics metrics."""

    @staticmethod
    async def record_dashboard_load(dashboard_type: str, duration: float):
        """Record dashboard load time."""
        DASHBOARD_LOAD_TIME.labels(dashboard_type=dashboard_type).observe(duration)

    @staticmethod
    async def record_report_generation(report_type: str, duration: float):
        """Record report generation time."""
        REPORT_GENERATION_TIME.labels(report_type=report_type).observe(duration)

    @staticmethod
    async def update_websocket_connections(count: int):
        """Update active WebSocket connections count."""
        ACTIVE_WEBSOCKET_CONNECTIONS.set(count)

    @staticmethod
    async def update_data_processing_lag(lag_seconds: float):
        """Update data processing lag."""
        DATA_PROCESSING_LAG.set(lag_seconds)

    @staticmethod
    async def record_alert_trigger(alert_type: str, severity: str):
        """Record alert trigger."""
        ALERT_TRIGGERS.labels(alert_type=alert_type, severity=severity).inc()

    @staticmethod
    async def record_bigquery_query(query_type: str, status: str):
        """Record BigQuery query execution."""
        BIGQUERY_QUERIES.labels(query_type=query_type, status=status).inc()

    @staticmethod
    async def record_cache_hit(cache_type: str):
        """Record cache hit."""
        CACHE_HITS.labels(cache_type=cache_type).inc()

    @staticmethod
    async def record_cache_miss(cache_type: str):
        """Record cache miss."""
        CACHE_MISSES.labels(cache_type=cache_type).inc()

    @staticmethod
    async def collect_all():
        """Collect all available metrics."""
        try:
            # You can add custom metric collection logic here
            # For example, querying database for current states
            logger.debug("Collecting analytics metrics...")
        except Exception as e:
            logger.error(f"Error collecting metrics: {e}")


class PrometheusIntegration:
    """Integration with external Prometheus instance."""

    def __init__(self):
        self.prometheus_url = settings.PROMETHEUS_URL
        self.client = httpx.AsyncClient(timeout=10.0)

    async def query_metric(self, query: str) -> Optional[Dict[str, Any]]:
        """Query Prometheus for metrics."""
        try:
            response = await self.client.get(
                f"{self.prometheus_url}/api/v1/query",
                params={"query": query}
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Error querying Prometheus: {e}")
            return None

    async def query_range(self, query: str, start: str, end: str, step: str) -> Optional[Dict[str, Any]]:
        """Query Prometheus for range data."""
        try:
            response = await self.client.get(
                f"{self.prometheus_url}/api/v1/query_range",
                params={
                    "query": query,
                    "start": start,
                    "end": end,
                    "step": step
                }
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Error querying Prometheus range: {e}")
            return None

    async def get_service_metrics(self, service_name: str) -> Dict[str, Any]:
        """Get metrics for a specific service."""
        metrics = {}

        # CPU usage
        cpu_query = f'rate(process_cpu_seconds_total{{job="{service_name}"}}[5m]) * 100'
        cpu_data = await self.query_metric(cpu_query)
        if cpu_data and cpu_data.get("data", {}).get("result"):
            metrics["cpu_usage"] = float(cpu_data["data"]["result"][0]["value"][1])

        # Memory usage
        memory_query = f'process_resident_memory_bytes{{job="{service_name}"}}'
        memory_data = await self.query_metric(memory_query)
        if memory_data and memory_data.get("data", {}).get("result"):
            metrics["memory_usage"] = float(memory_data["data"]["result"][0]["value"][1])

        # Request rate
        request_query = f'rate(http_requests_total{{job="{service_name}"}}[5m])'
        request_data = await self.query_metric(request_query)
        if request_data and request_data.get("data", {}).get("result"):
            metrics["request_rate"] = float(request_data["data"]["result"][0]["value"][1])

        return metrics

    async def close(self):
        """Close HTTP client."""
        await self.client.aclose()


# Global Prometheus integration instance
prometheus_integration = PrometheusIntegration()


def get_metrics() -> str:
    """Get Prometheus metrics."""
    return generate_latest()


def get_metrics_content_type() -> str:
    """Get Prometheus metrics content type."""
    return CONTENT_TYPE_LATEST