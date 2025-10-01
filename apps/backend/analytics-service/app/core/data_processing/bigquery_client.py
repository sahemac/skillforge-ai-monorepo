"""
BigQuery integration for analytics data warehouse
"""

import asyncio
import logging
from typing import Dict, Any, List, Optional, Union
from datetime import datetime, timedelta
import pandas as pd
from google.cloud import bigquery
from google.cloud.exceptions import NotFound
import json

from app.core.config import get_settings
from app.core.monitoring import MetricsCollector

settings = get_settings()
logger = logging.getLogger(__name__)


class BigQueryClient:
    """BigQuery client for analytics data operations."""

    def __init__(self):
        self.project_id = settings.GOOGLE_CLOUD_PROJECT
        self.dataset_id = settings.BIGQUERY_DATASET
        self.location = settings.BIGQUERY_LOCATION
        self.client = None
        self._initialize_client()

    def _initialize_client(self):
        """Initialize BigQuery client."""
        try:
            if settings.GOOGLE_APPLICATION_CREDENTIALS:
                self.client = bigquery.Client(
                    project=self.project_id,
                    location=self.location
                )
                logger.info("BigQuery client initialized successfully")
            else:
                logger.warning("No Google Cloud credentials provided, BigQuery disabled")
        except Exception as e:
            logger.error(f"Failed to initialize BigQuery client: {e}")

    async def ensure_dataset_exists(self):
        """Ensure the analytics dataset exists."""
        if not self.client:
            return False

        try:
            dataset_ref = self.client.dataset(self.dataset_id)
            try:
                self.client.get_dataset(dataset_ref)
                logger.info(f"Dataset {self.dataset_id} already exists")
                return True
            except NotFound:
                # Create dataset
                dataset = bigquery.Dataset(dataset_ref)
                dataset.location = self.location
                dataset = self.client.create_dataset(dataset)
                logger.info(f"Created dataset {self.dataset_id}")
                return True
        except Exception as e:
            logger.error(f"Error ensuring dataset exists: {e}")
            return False

    async def create_tables_if_not_exist(self):
        """Create BigQuery tables if they don't exist."""
        if not self.client:
            return False

        try:
            tables_to_create = [
                ("user_events", self._get_user_events_schema()),
                ("user_sessions", self._get_user_sessions_schema()),
                ("project_metrics", self._get_project_metrics_schema()),
                ("matching_metrics", self._get_matching_metrics_schema()),
                ("service_performance", self._get_service_performance_schema()),
                ("daily_aggregates", self._get_daily_aggregates_schema()),
            ]

            for table_name, schema in tables_to_create:
                await self._create_table_if_not_exists(table_name, schema)

            return True
        except Exception as e:
            logger.error(f"Error creating tables: {e}")
            return False

    async def _create_table_if_not_exists(self, table_name: str, schema: List[bigquery.SchemaField]):
        """Create a table if it doesn't exist."""
        table_ref = self.client.dataset(self.dataset_id).table(table_name)

        try:
            self.client.get_table(table_ref)
            logger.info(f"Table {table_name} already exists")
        except NotFound:
            table = bigquery.Table(table_ref, schema=schema)
            table = self.client.create_table(table)
            logger.info(f"Created table {table_name}")

    def _get_user_events_schema(self) -> List[bigquery.SchemaField]:
        """Get schema for user_events table."""
        return [
            bigquery.SchemaField("event_id", "STRING", mode="REQUIRED"),
            bigquery.SchemaField("user_id", "STRING", mode="NULLABLE"),
            bigquery.SchemaField("session_id", "STRING", mode="NULLABLE"),
            bigquery.SchemaField("event_type", "STRING", mode="REQUIRED"),
            bigquery.SchemaField("event_data", "JSON", mode="NULLABLE"),
            bigquery.SchemaField("timestamp", "TIMESTAMP", mode="REQUIRED"),
            bigquery.SchemaField("user_agent", "STRING", mode="NULLABLE"),
            bigquery.SchemaField("ip_address", "STRING", mode="NULLABLE"),
        ]

    def _get_user_sessions_schema(self) -> List[bigquery.SchemaField]:
        """Get schema for user_sessions table."""
        return [
            bigquery.SchemaField("session_id", "STRING", mode="REQUIRED"),
            bigquery.SchemaField("user_id", "STRING", mode="NULLABLE"),
            bigquery.SchemaField("start_time", "TIMESTAMP", mode="REQUIRED"),
            bigquery.SchemaField("end_time", "TIMESTAMP", mode="NULLABLE"),
            bigquery.SchemaField("duration_seconds", "INTEGER", mode="NULLABLE"),
            bigquery.SchemaField("page_views", "INTEGER", mode="NULLABLE"),
            bigquery.SchemaField("events_count", "INTEGER", mode="NULLABLE"),
        ]

    def _get_project_metrics_schema(self) -> List[bigquery.SchemaField]:
        """Get schema for project_metrics table."""
        return [
            bigquery.SchemaField("project_id", "STRING", mode="REQUIRED"),
            bigquery.SchemaField("user_id", "STRING", mode="REQUIRED"),
            bigquery.SchemaField("company_id", "STRING", mode="NULLABLE"),
            bigquery.SchemaField("status", "STRING", mode="REQUIRED"),
            bigquery.SchemaField("created_at", "TIMESTAMP", mode="REQUIRED"),
            bigquery.SchemaField("submitted_at", "TIMESTAMP", mode="NULLABLE"),
            bigquery.SchemaField("completed_at", "TIMESTAMP", mode="NULLABLE"),
            bigquery.SchemaField("metrics", "JSON", mode="NULLABLE"),
        ]

    def _get_matching_metrics_schema(self) -> List[bigquery.SchemaField]:
        """Get schema for matching_metrics table."""
        return [
            bigquery.SchemaField("match_id", "STRING", mode="REQUIRED"),
            bigquery.SchemaField("user_id", "STRING", mode="REQUIRED"),
            bigquery.SchemaField("project_id", "STRING", mode="REQUIRED"),
            bigquery.SchemaField("match_score", "FLOAT", mode="REQUIRED"),
            bigquery.SchemaField("match_type", "STRING", mode="REQUIRED"),
            bigquery.SchemaField("success", "BOOLEAN", mode="REQUIRED"),
            bigquery.SchemaField("timestamp", "TIMESTAMP", mode="REQUIRED"),
        ]

    def _get_service_performance_schema(self) -> List[bigquery.SchemaField]:
        """Get schema for service_performance table."""
        return [
            bigquery.SchemaField("service_name", "STRING", mode="REQUIRED"),
            bigquery.SchemaField("metric_name", "STRING", mode="REQUIRED"),
            bigquery.SchemaField("metric_value", "FLOAT", mode="REQUIRED"),
            bigquery.SchemaField("timestamp", "TIMESTAMP", mode="REQUIRED"),
            bigquery.SchemaField("labels", "JSON", mode="NULLABLE"),
        ]

    def _get_daily_aggregates_schema(self) -> List[bigquery.SchemaField]:
        """Get schema for daily_aggregates table."""
        return [
            bigquery.SchemaField("date", "DATE", mode="REQUIRED"),
            bigquery.SchemaField("metric_type", "STRING", mode="REQUIRED"),
            bigquery.SchemaField("metric_value", "FLOAT", mode="REQUIRED"),
            bigquery.SchemaField("aggregation_type", "STRING", mode="REQUIRED"),
            bigquery.SchemaField("metadata", "JSON", mode="NULLABLE"),
        ]

    async def insert_user_events(self, events: List[Dict[str, Any]]) -> bool:
        """Insert user events into BigQuery."""
        if not self.client or not events:
            return False

        try:
            table_ref = self.client.dataset(self.dataset_id).table("user_events")
            table = self.client.get_table(table_ref)

            # Prepare rows for insertion
            rows = []
            for event in events:
                rows.append({
                    "event_id": event.get("event_id"),
                    "user_id": event.get("user_id"),
                    "session_id": event.get("session_id"),
                    "event_type": event.get("event_type"),
                    "event_data": json.dumps(event.get("event_data", {})),
                    "timestamp": event.get("timestamp"),
                    "user_agent": event.get("user_agent"),
                    "ip_address": event.get("ip_address"),
                })

            errors = self.client.insert_rows_json(table, rows)
            if not errors:
                await MetricsCollector.record_bigquery_query("insert_user_events", "success")
                logger.info(f"Successfully inserted {len(events)} user events")
                return True
            else:
                await MetricsCollector.record_bigquery_query("insert_user_events", "error")
                logger.error(f"Errors inserting events: {errors}")
                return False

        except Exception as e:
            await MetricsCollector.record_bigquery_query("insert_user_events", "error")
            logger.error(f"Error inserting user events: {e}")
            return False

    async def query_user_metrics(self, start_date: datetime, end_date: datetime) -> Optional[Dict[str, Any]]:
        """Query user metrics from BigQuery."""
        if not self.client:
            return None

        try:
            query = f"""
            SELECT
                COUNT(DISTINCT user_id) as unique_users,
                COUNT(DISTINCT session_id) as unique_sessions,
                COUNT(*) as total_events,
                COUNT(DISTINCT DATE(timestamp)) as active_days
            FROM `{self.project_id}.{self.dataset_id}.user_events`
            WHERE timestamp BETWEEN @start_date AND @end_date
            """

            job_config = bigquery.QueryJobConfig(
                query_parameters=[
                    bigquery.ScalarQueryParameter("start_date", "TIMESTAMP", start_date),
                    bigquery.ScalarQueryParameter("end_date", "TIMESTAMP", end_date),
                ]
            )

            query_job = self.client.query(query, job_config=job_config)
            results = query_job.result()

            for row in results:
                await MetricsCollector.record_bigquery_query("query_user_metrics", "success")
                return {
                    "unique_users": row.unique_users,
                    "unique_sessions": row.unique_sessions,
                    "total_events": row.total_events,
                    "active_days": row.active_days,
                }

            return None

        except Exception as e:
            await MetricsCollector.record_bigquery_query("query_user_metrics", "error")
            logger.error(f"Error querying user metrics: {e}")
            return None

    async def get_daily_active_users(self, days: int = 30) -> Optional[List[Dict[str, Any]]]:
        """Get daily active users for the past N days."""
        if not self.client:
            return None

        try:
            query = f"""
            SELECT
                DATE(timestamp) as date,
                COUNT(DISTINCT user_id) as active_users
            FROM `{self.project_id}.{self.dataset_id}.user_events`
            WHERE timestamp >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL @days DAY)
            GROUP BY DATE(timestamp)
            ORDER BY date
            """

            job_config = bigquery.QueryJobConfig(
                query_parameters=[
                    bigquery.ScalarQueryParameter("days", "INT64", days),
                ]
            )

            query_job = self.client.query(query, job_config=job_config)
            results = query_job.result()

            data = []
            for row in results:
                data.append({
                    "date": row.date.isoformat(),
                    "active_users": row.active_users
                })

            await MetricsCollector.record_bigquery_query("get_daily_active_users", "success")
            return data

        except Exception as e:
            await MetricsCollector.record_bigquery_query("get_daily_active_users", "error")
            logger.error(f"Error querying daily active users: {e}")
            return None

    async def get_event_funnel(self, events: List[str], time_window_hours: int = 24) -> Optional[Dict[str, Any]]:
        """Get conversion funnel for a sequence of events."""
        if not self.client or not events:
            return None

        try:
            funnel_queries = []
            for i, event in enumerate(events):
                funnel_queries.append(f"""
                SELECT '{event}' as step, COUNT(DISTINCT user_id) as users
                FROM `{self.project_id}.{self.dataset_id}.user_events`
                WHERE event_type = '{event}'
                AND timestamp >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL {time_window_hours} HOUR)
                """)

            query = " UNION ALL ".join(funnel_queries) + " ORDER BY users DESC"

            query_job = self.client.query(query)
            results = query_job.result()

            funnel_data = []
            for row in results:
                funnel_data.append({
                    "step": row.step,
                    "users": row.users
                })

            await MetricsCollector.record_bigquery_query("get_event_funnel", "success")
            return {"funnel": funnel_data}

        except Exception as e:
            await MetricsCollector.record_bigquery_query("get_event_funnel", "error")
            logger.error(f"Error querying event funnel: {e}")
            return None

    async def close(self):
        """Close BigQuery client."""
        if self.client:
            self.client.close()
            logger.info("BigQuery client closed")


# Global BigQuery client instance
bigquery_client = BigQueryClient()