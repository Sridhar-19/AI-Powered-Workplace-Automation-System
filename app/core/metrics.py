"""
Metrics collection for monitoring.
"""
import time
from typing import Dict, Any
from collections import defaultdict
import threading


class MetricsCollector:
    """
    Simple metrics collector for monitoring application performance.
    """

    def __init__(self):
        self._metrics: Dict[str, Any] = defaultdict(lambda: {
            "count": 0,
            "total_time": 0.0,
            "errors": 0,
            "successes": 0
        })
        self._lock = threading.Lock()

    def record_request(self, endpoint: str, duration: float, success: bool = True):
        """
        Record a request metric.
        
        Args:
            endpoint: API endpoint
            duration: Request duration in seconds
            success: Whether request was successful
        """
        with self._lock:
            metrics = self._metrics[endpoint]
            metrics["count"] += 1
            metrics["total_time"] += duration
            
            if success:
                metrics["successes"] += 1
            else:
                metrics["errors"] += 1

    def record_llm_call(self, model: str, tokens: int, cost: float):
        """Record LLM API call metrics."""
        with self._lock:
            metrics = self._metrics[f"llm_{model}"]
            metrics["count"] += 1
            metrics["tokens"] = metrics.get("tokens", 0) + tokens
            metrics["cost"] = metrics.get("cost", 0.0) + cost

    def get_metrics(self) -> Dict[str, Any]:
        """Get all collected metrics."""
        with self._lock:
            return dict(self._metrics)

    def get_endpoint_metrics(self, endpoint: str) -> Dict[str, Any]:
        """Get metrics for specific endpoint."""
        with self._lock:
            metrics = self._metrics.get(endpoint, {})
            if metrics.get("count", 0) > 0:
                metrics["avg_time"] = metrics["total_time"] / metrics["count"]
                metrics["error_rate"] = metrics["errors"] / metrics["count"]
            return dict(metrics)

    def reset(self):
        """Reset all metrics."""
        with self._lock:
            self._metrics.clear()


# Global metrics collector
_metrics_collector = None


def get_metrics_collector() -> MetricsCollector:
    """Get or create metrics collector."""
    global _metrics_collector
    if _metrics_collector is None:
        _metrics_collector = MetricsCollector()
    return _metrics_collector
