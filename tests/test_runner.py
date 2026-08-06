"""
Offline unit tests for BenchmarkRunner and MetricsCollector.
"""

from unittest.mock import MagicMock
import pytest

from graph_db_benchmark.adapters.base import BaseGraphAdapter
from graph_db_benchmark.workloads.base import BaseWorkload, QueryItem
from graph_db_benchmark.metrics.collector import MetricsCollector
from graph_db_benchmark.runners.benchmark_runner import BenchmarkRunner


@pytest.fixture
def mock_adapter():
    """Fixture providing mock BaseGraphAdapter."""
    adapter = MagicMock(spec=BaseGraphAdapter)
    adapter.__class__.__name__ = "MockGraphAdapter"
    adapter.execute_read.return_value = [{"status": "success", "count": 1}]
    adapter.execute_write.return_value = [{"status": "success", "created": True}]
    return adapter


@pytest.fixture
def mock_workload():
    """Fixture providing mock BaseWorkload."""
    workload = MagicMock(spec=BaseWorkload)
    workload.get_warmup_queries.return_value = [
        QueryItem("warmup_read", "MATCH (n) RETURN count(n)", "READ")
    ]
    workload.get_benchmark_queries.return_value = [
        QueryItem("bench_read", "MATCH (u:User {id: $user_id}) RETURN u", "READ", {"user_id": "1"}),
        QueryItem("bench_write", "MERGE (u:User {id: $user_id})", "WRITE", {"user_id": "2"}),
    ]
    return workload


def test_metrics_collector_percentiles_and_stdev():
    """Test MetricsCollector percentile and standard deviation calculations."""
    collector = MetricsCollector("TestAdapter")
    collector.start()

    latencies = [10.0, 20.0, 30.0, 40.0, 50.0, 60.0, 70.0, 80.0, 90.0, 100.0]
    for lat in latencies:
        collector.record_query(lat, success=True)

    collector.stop()
    summary = collector.compute_summary()

    assert summary.total_queries == 10
    assert summary.successful_queries == 10
    assert summary.failed_queries == 0
    assert summary.min_latency_ms == 10.0
    assert summary.max_latency_ms == 100.0
    assert summary.avg_latency_ms == 55.0
    assert summary.latency_p50_ms == 55.0
    assert summary.latency_p95_ms == 95.5
    assert summary.latency_p99_ms == 99.1
    assert round(summary.std_dev_ms, 2) == 30.28
    assert summary.throughput_ops_sec > 0

    d = summary.to_dict()
    assert d["latencies_ms"]["std_dev"] == 30.28
    assert d["latencies_ms"]["p50"] == 55.0
    assert d["latencies_ms"]["p95"] == 95.5


def test_runner_warmup_phase(mock_adapter, mock_workload):
    """Test BenchmarkRunner warmup phase execution."""
    runner = BenchmarkRunner(adapter=mock_adapter, workload=mock_workload)
    runner.run_warmup(iterations=3)

    assert mock_adapter.execute_read.call_count == 3


def test_runner_concurrent_benchmark_execution(mock_adapter, mock_workload):
    """Test multi-threaded concurrent benchmark runner execution."""
    runner = BenchmarkRunner(adapter=mock_adapter, workload=mock_workload)
    summary = runner.run_benchmark(iterations=20, concurrency=4)

    assert summary.adapter_name == "MockGraphAdapter"
    assert summary.total_queries == 20
    assert summary.successful_queries == 20
    assert summary.failed_queries == 0
    assert summary.throughput_ops_sec > 0
    assert mock_adapter.execute_read.call_count + mock_adapter.execute_write.call_count == 20


def test_runner_error_resilience(mock_adapter, mock_workload):
    """Test runner resilience when query execution fails."""
    # Force read query to fail
    mock_adapter.execute_read.side_effect = RuntimeError("Query execution timeout")

    runner = BenchmarkRunner(adapter=mock_adapter, workload=mock_workload)
    summary = runner.run_benchmark(iterations=10, concurrency=2)

    assert summary.total_queries == 10
    assert summary.failed_queries > 0
    assert summary.total_duration_sec > 0
