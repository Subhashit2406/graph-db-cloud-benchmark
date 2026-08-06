"""
Unit tests for configuration loading and adapter stubs.
"""

from graph_db_benchmark.config import get_settings
from graph_db_benchmark.adapters import Neo4jAdapter, NeptuneAdapter, MemgraphAdapter
from graph_db_benchmark.metrics import MetricsCollector
from graph_db_benchmark.workloads import ReadWriteWorkload


def test_settings_load(mock_env_vars):
    """Test that environment variables are loaded properly into Settings."""
    settings = get_settings()
    assert settings.benchmark.target_db_adapter == "neo4j"
    assert settings.neo4j.user == "test_user"
    assert settings.neo4j.password == "test_password"


def test_neo4j_adapter_lifecycle():
    """Test Neo4j adapter stub lifecycle with mock driver."""
    from unittest.mock import patch, MagicMock

    with patch("graph_db_benchmark.adapters.cognodb_adapter.GraphDatabase.driver") as mock_driver_fn:
        mock_driver = MagicMock()
        mock_session = MagicMock()
        mock_session.execute_read.return_value = [{"status": "success", "result_count": 1}]
        mock_driver.session.return_value = mock_session
        mock_driver_fn.return_value = mock_driver

        adapter = Neo4jAdapter({"uri": "bolt://localhost:7687", "user": "neo4j"})
        assert not adapter.is_connected
        adapter.connect()
        assert adapter.is_connected
        assert adapter.health_check() is True
        res = adapter.execute_query("MATCH (n) RETURN n")
        assert len(res) > 0
        adapter.disconnect()
        assert not adapter.is_connected


def test_metrics_collector():
    """Test metrics calculation."""
    collector = MetricsCollector("Neo4jAdapter")
    collector.start()
    collector.record_query(10.0, success=True)
    collector.record_query(20.0, success=True)
    collector.record_query(30.0, success=False)
    collector.stop()

    summary = collector.compute_summary()
    assert summary.total_queries == 3
    assert summary.successful_queries == 2
    assert summary.failed_queries == 1
    assert summary.min_latency_ms == 10.0
    assert summary.max_latency_ms == 30.0


def test_workload_queries():
    """Test workload query loading."""
    workload = ReadWriteWorkload()
    warmup = workload.get_warmup_queries()
    benchmark = workload.get_benchmark_queries()
    assert len(warmup) > 0
    assert len(benchmark) > 0


def test_queries_package():
    """Test queries package modules and placeholder query items."""
    from graph_db_benchmark.queries import (
        TraversalQueries,
        LookupQueries,
        AggregationQueries,
        MixedQueries,
    )
    assert len(TraversalQueries.get_queries()) > 0
    assert len(LookupQueries.get_queries()) > 0
    assert len(AggregationQueries.get_queries()) > 0
    assert len(MixedQueries.get_queries()) > 0

