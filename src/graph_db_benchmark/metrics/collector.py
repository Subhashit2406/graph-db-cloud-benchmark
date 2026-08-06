"""
Metrics collection and statistic calculations module.

Provides thread-safe metrics tracking and statistical calculation of latency
percentiles (p50, p90, p95, p99), mean, min, max, standard deviation, and throughput.
"""

import math
import statistics
import threading
import time
from dataclasses import dataclass
from typing import Any, Dict, List


@dataclass
class BenchmarkResultSummary:
    """
    Data holder summarizing benchmark performance metrics.
    """
    adapter_name: str
    total_queries: int
    successful_queries: int
    failed_queries: int
    total_duration_sec: float
    throughput_ops_sec: float
    latency_p50_ms: float
    latency_p90_ms: float
    latency_p95_ms: float
    latency_p99_ms: float
    min_latency_ms: float
    max_latency_ms: float
    avg_latency_ms: float
    std_dev_ms: float

    def to_dict(self) -> Dict[str, Any]:
        """Convert metrics summary to serializable dictionary."""
        return {
            "adapter_name": self.adapter_name,
            "total_queries": self.total_queries,
            "successful_queries": self.successful_queries,
            "failed_queries": self.failed_queries,
            "total_duration_sec": round(self.total_duration_sec, 4),
            "throughput_ops_sec": round(self.throughput_ops_sec, 2),
            "latencies_ms": {
                "p50": round(self.latency_p50_ms, 2),
                "p90": round(self.latency_p90_ms, 2),
                "p95": round(self.latency_p95_ms, 2),
                "p99": round(self.latency_p99_ms, 2),
                "min": round(self.min_latency_ms, 2),
                "max": round(self.max_latency_ms, 2),
                "avg": round(self.avg_latency_ms, 2),
                "std_dev": round(self.std_dev_ms, 2),
            },
        }


class MetricsCollector:
    """
    Thread-safe benchmark metrics collector.
    """

    def __init__(self, adapter_name: str) -> None:
        self.adapter_name = adapter_name
        self.latencies_ms: List[float] = []
        self.success_count: int = 0
        self.failure_count: int = 0
        self.start_time: float = 0.0
        self.end_time: float = 0.0
        self.lock = threading.Lock()

    def start(self) -> None:
        """Start total execution timer."""
        self.start_time = time.perf_counter()

    def stop(self) -> None:
        """Stop total execution timer."""
        self.end_time = time.perf_counter()

    def record_query(self, latency_ms: float, success: bool = True) -> None:
        """
        Thread-safely record single query outcome and execution duration.

        Args:
            latency_ms: Execution duration in milliseconds.
            success: Whether operation completed successfully.
        """
        with self.lock:
            self.latencies_ms.append(latency_ms)
            if success:
                self.success_count += 1
            else:
                self.failure_count += 1

    def compute_summary(self) -> BenchmarkResultSummary:
        """
        Compute summary metrics including percentiles, throughput, and standard deviation.

        Returns:
            BenchmarkResultSummary: Object containing calculated summary stats.
        """
        with self.lock:
            latencies = list(self.latencies_ms)
            success_cnt = self.success_count
            fail_cnt = self.failure_count

        total_duration = max(self.end_time - self.start_time, 0.0001)
        total_ops = len(latencies)

        if not latencies:
            return BenchmarkResultSummary(
                adapter_name=self.adapter_name,
                total_queries=0,
                successful_queries=0,
                failed_queries=0,
                total_duration_sec=total_duration,
                throughput_ops_sec=0.0,
                latency_p50_ms=0.0,
                latency_p90_ms=0.0,
                latency_p95_ms=0.0,
                latency_p99_ms=0.0,
                min_latency_ms=0.0,
                max_latency_ms=0.0,
                avg_latency_ms=0.0,
                std_dev_ms=0.0,
            )

        sorted_latencies = sorted(latencies)

        def percentile(pct: float) -> float:
            if not sorted_latencies:
                return 0.0
            k = (len(sorted_latencies) - 1) * pct
            f = math.floor(k)
            c = math.ceil(k)
            if f == c:
                return sorted_latencies[int(k)]
            d0 = sorted_latencies[int(f)] * (c - k)
            d1 = sorted_latencies[int(c)] * (k - f)
            return d0 + d1

        std_dev = statistics.stdev(sorted_latencies) if len(sorted_latencies) > 1 else 0.0

        return BenchmarkResultSummary(
            adapter_name=self.adapter_name,
            total_queries=total_ops,
            successful_queries=success_cnt,
            failed_queries=fail_cnt,
            total_duration_sec=total_duration,
            throughput_ops_sec=total_ops / total_duration,
            latency_p50_ms=percentile(0.50),
            latency_p90_ms=percentile(0.90),
            latency_p95_ms=percentile(0.95),
            latency_p99_ms=percentile(0.99),
            min_latency_ms=sorted_latencies[0],
            max_latency_ms=sorted_latencies[-1],
            avg_latency_ms=sum(sorted_latencies) / total_ops,
            std_dev_ms=std_dev,
        )
