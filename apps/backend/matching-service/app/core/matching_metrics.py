"""
Prometheus metrics specific to matching functionality
"""

import time
import logging
from typing import Dict, Any
from contextlib import contextmanager
from prometheus_client import Counter, Histogram, Gauge, Info

logger = logging.getLogger(__name__)

# Matching-specific metrics
matching_requests_total = Counter(
    'matching_requests_total',
    'Total number of matching requests',
    ['matching_type', 'status']
)

matching_algorithm_duration = Histogram(
    'matching_algorithm_duration_seconds',
    'Time spent executing matching algorithms',
    ['algorithm_type', 'matching_type'],
    buckets=[0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0, 25.0, 50.0, 100.0]
)

matching_results_count = Histogram(
    'matching_results_count',
    'Number of results returned per matching request',
    ['matching_type'],
    buckets=[1, 5, 10, 20, 50, 100, 200, 500, 1000]
)

matching_scores_distribution = Histogram(
    'matching_scores_distribution',
    'Distribution of matching scores',
    ['matching_type', 'score_type'],
    buckets=[0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]
)

recommendation_accuracy = Gauge(
    'recommendation_accuracy_score',
    'Accuracy score of recommendations based on user feedback',
    ['recommendation_type']
)

cache_hit_ratio = Gauge(
    'matching_cache_hit_ratio',
    'Cache hit ratio for matching operations'
)

active_matching_profiles = Gauge(
    'active_matching_profiles_total',
    'Number of active matching profiles',
    ['user_type']
)

matching_engine_info = Info(
    'matching_engine_info',
    'Information about the matching engine'
)

skill_matcher_performance = Histogram(
    'skill_matcher_duration_seconds',
    'Performance of skill matching algorithms',
    ['method'],
    buckets=[0.001, 0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0]
)

semantic_analysis_duration = Histogram(
    'semantic_analysis_duration_seconds',
    'Time spent on semantic analysis',
    ['model_type'],
    buckets=[0.1, 0.5, 1.0, 2.0, 5.0, 10.0, 30.0, 60.0]
)

batch_processing_metrics = Histogram(
    'batch_processing_duration_seconds',
    'Time spent processing batch matching requests',
    ['batch_size_range'],
    buckets=[1.0, 5.0, 10.0, 30.0, 60.0, 120.0, 300.0, 600.0]
)

user_feedback_scores = Histogram(
    'user_feedback_scores',
    'Distribution of user feedback scores',
    ['feedback_type'],
    buckets=[1, 2, 3, 4, 5]
)

matching_errors_total = Counter(
    'matching_errors_total',
    'Total number of matching errors',
    ['error_type', 'component']
)

ml_model_performance = Gauge(
    'ml_model_performance_score',
    'Performance metrics for ML models',
    ['model_name', 'metric_type']
)


class MatchingMetricsCollector:
    """Collector for matching-specific metrics."""

    def __init__(self):
        """Initialize the metrics collector."""
        self.cache_hits = 0
        self.cache_misses = 0
        self.total_feedback_scores = {}

    def record_matching_request(
        self,
        matching_type: str,
        status: str = "success",
        duration: float = 0.0,
        results_count: int = 0,
        scores: Dict[str, float] = None
    ):
        """Record metrics for a matching request."""
        try:
            # Record basic request metrics
            matching_requests_total.labels(
                matching_type=matching_type,
                status=status
            ).inc()

            # Record duration
            if duration > 0:
                matching_algorithm_duration.labels(
                    algorithm_type="complete",
                    matching_type=matching_type
                ).observe(duration)

            # Record result count
            if results_count > 0:
                matching_results_count.labels(
                    matching_type=matching_type
                ).observe(results_count)

            # Record score distributions
            if scores:
                for score_type, score_value in scores.items():
                    if 0.0 <= score_value <= 1.0:
                        matching_scores_distribution.labels(
                            matching_type=matching_type,
                            score_type=score_type
                        ).observe(score_value)

        except Exception as e:
            logger.error(f"Error recording matching request metrics: {e}")

    def record_skill_matching_performance(
        self,
        method: str,
        duration: float
    ):
        """Record skill matching performance."""
        try:
            skill_matcher_performance.labels(method=method).observe(duration)
        except Exception as e:
            logger.error(f"Error recording skill matching performance: {e}")

    def record_semantic_analysis(
        self,
        model_type: str,
        duration: float
    ):
        """Record semantic analysis performance."""
        try:
            semantic_analysis_duration.labels(model_type=model_type).observe(duration)
        except Exception as e:
            logger.error(f"Error recording semantic analysis metrics: {e}")

    def record_batch_processing(
        self,
        batch_size: int,
        duration: float
    ):
        """Record batch processing metrics."""
        try:
            # Determine batch size range
            if batch_size <= 10:
                batch_range = "1-10"
            elif batch_size <= 25:
                batch_range = "11-25"
            elif batch_size <= 50:
                batch_range = "26-50"
            else:
                batch_range = "50+"

            batch_processing_metrics.labels(
                batch_size_range=batch_range
            ).observe(duration)

        except Exception as e:
            logger.error(f"Error recording batch processing metrics: {e}")

    def record_user_feedback(
        self,
        feedback_type: str,
        score: int
    ):
        """Record user feedback scores."""
        try:
            user_feedback_scores.labels(
                feedback_type=feedback_type
            ).observe(score)

            # Update accuracy calculation
            if feedback_type not in self.total_feedback_scores:
                self.total_feedback_scores[feedback_type] = []

            self.total_feedback_scores[feedback_type].append(score)

            # Calculate and update accuracy (scores >= 4 are considered positive)
            positive_scores = sum(1 for s in self.total_feedback_scores[feedback_type] if s >= 4)
            total_scores = len(self.total_feedback_scores[feedback_type])

            if total_scores > 0:
                accuracy = positive_scores / total_scores
                recommendation_accuracy.labels(
                    recommendation_type=feedback_type
                ).set(accuracy)

        except Exception as e:
            logger.error(f"Error recording user feedback metrics: {e}")

    def record_cache_hit(self):
        """Record a cache hit."""
        self.cache_hits += 1
        self._update_cache_ratio()

    def record_cache_miss(self):
        """Record a cache miss."""
        self.cache_misses += 1
        self._update_cache_ratio()

    def _update_cache_ratio(self):
        """Update cache hit ratio metric."""
        total_requests = self.cache_hits + self.cache_misses
        if total_requests > 0:
            ratio = self.cache_hits / total_requests
            cache_hit_ratio.set(ratio)

    def record_error(
        self,
        error_type: str,
        component: str
    ):
        """Record an error occurrence."""
        try:
            matching_errors_total.labels(
                error_type=error_type,
                component=component
            ).inc()
        except Exception as e:
            logger.error(f"Error recording error metrics: {e}")

    def update_active_profiles_count(
        self,
        user_type: str,
        count: int
    ):
        """Update active profiles count."""
        try:
            active_matching_profiles.labels(user_type=user_type).set(count)
        except Exception as e:
            logger.error(f"Error updating active profiles count: {e}")

    def update_ml_model_performance(
        self,
        model_name: str,
        metric_type: str,
        score: float
    ):
        """Update ML model performance metrics."""
        try:
            ml_model_performance.labels(
                model_name=model_name,
                metric_type=metric_type
            ).set(score)
        except Exception as e:
            logger.error(f"Error updating ML model performance: {e}")

    def set_engine_info(
        self,
        version: str,
        algorithms: list,
        model_versions: dict
    ):
        """Set matching engine information."""
        try:
            matching_engine_info.info({
                'version': version,
                'algorithms': ','.join(algorithms),
                'sentence_transformer_model': model_versions.get('sentence_transformer', 'unknown'),
                'skill_matcher_version': model_versions.get('skill_matcher', '1.0.0'),
                'semantic_analyzer_version': model_versions.get('semantic_analyzer', '1.0.0')
            })
        except Exception as e:
            logger.error(f"Error setting engine info: {e}")

    @contextmanager
    def time_operation(self, operation_type: str, **labels):
        """Context manager to time operations."""
        start_time = time.time()
        try:
            yield
        finally:
            duration = time.time() - start_time
            try:
                if operation_type == "matching_algorithm":
                    matching_algorithm_duration.labels(**labels).observe(duration)
                elif operation_type == "skill_matching":
                    skill_matcher_performance.labels(**labels).observe(duration)
                elif operation_type == "semantic_analysis":
                    semantic_analysis_duration.labels(**labels).observe(duration)
                elif operation_type == "batch_processing":
                    batch_processing_metrics.labels(**labels).observe(duration)
            except Exception as e:
                logger.error(f"Error recording timing metrics: {e}")


# Global metrics collector instance
matching_metrics = MatchingMetricsCollector()


# Convenience functions
def record_matching_success(matching_type: str, duration: float, results_count: int, scores: Dict[str, float] = None):
    """Record a successful matching operation."""
    matching_metrics.record_matching_request(
        matching_type=matching_type,
        status="success",
        duration=duration,
        results_count=results_count,
        scores=scores or {}
    )


def record_matching_error(matching_type: str, error_type: str, component: str = "matching_engine"):
    """Record a matching error."""
    matching_metrics.record_matching_request(
        matching_type=matching_type,
        status="error"
    )
    matching_metrics.record_error(error_type, component)


def record_recommendation_feedback(feedback_type: str, score: int):
    """Record user feedback on recommendations."""
    matching_metrics.record_user_feedback(feedback_type, score)


def update_system_health(active_profiles: Dict[str, int]):
    """Update system health metrics."""
    for user_type, count in active_profiles.items():
        matching_metrics.update_active_profiles_count(user_type, count)


# Initialize engine info (should be called during startup)
def initialize_metrics():
    """Initialize metrics with default values."""
    matching_metrics.set_engine_info(
        version="1.0.0",
        algorithms=["skill_based", "semantic", "experience", "location", "preference"],
        model_versions={
            "sentence_transformer": "all-MiniLM-L6-v2",
            "skill_matcher": "1.0.0",
            "semantic_analyzer": "1.0.0"
        }
    )

    # Initialize cache ratio
    cache_hit_ratio.set(0.0)

    # Initialize recommendation accuracy
    for rec_type in ["project_recommendations", "user_recommendations", "skill_development"]:
        recommendation_accuracy.labels(recommendation_type=rec_type).set(0.0)