"""
Unit tests for benchmark workload query layer and BaseGraphAdapter integration.
"""

from unittest.mock import MagicMock
import pytest

from graph_db_benchmark.adapters.base import BaseGraphAdapter
from graph_db_benchmark.queries import (
    TraversalQueries,
    LookupQueries,
    AggregationQueries,
    MixedQueries,
)
from graph_db_benchmark.workloads import ReadWriteWorkload


@pytest.fixture
def mock_adapter():
    """Fixture providing mock BaseGraphAdapter."""
    adapter = MagicMock(spec=BaseGraphAdapter)
    adapter.execute_read.return_value = [{"status": "success", "count": 1}]
    adapter.execute_write.return_value = [{"status": "success", "created": True}]
    return adapter


def test_traversal_queries_generation():
    """Test TraversalQueries parameterized template generation."""
    q1 = TraversalQueries.get_1hop_query("101")
    assert q1.name == "1_hop_traversal"
    assert "MATCH (u:User {id: $user_id})-[:VOTES]->(v:User)" in q1.query_string
    assert q1.parameters == {"user_id": "101"}

    q2 = TraversalQueries.get_2hop_query("101")
    assert "[:VOTES*2]" in q2.query_string

    q3 = TraversalQueries.get_3hop_query("101")
    assert "[:VOTES*3]" in q3.query_string

    all_queries = TraversalQueries.get_queries("101")
    assert len(all_queries) == 3


def test_traversal_queries_execution(mock_adapter):
    """Test TraversalQueries execution through adapter.execute_read."""
    res1 = TraversalQueries.execute_1hop(mock_adapter, "101")
    assert len(res1) == 1
    mock_adapter.execute_read.assert_called_with(
        "MATCH (u:User {id: $user_id})-[:VOTES]->(v:User) RETURN v.id AS neighbor_id",
        {"user_id": "101"},
    )

    res2 = TraversalQueries.execute_2hop(mock_adapter, "101")
    assert len(res2) == 1

    res3 = TraversalQueries.execute_3hop(mock_adapter, "101")
    assert len(res3) == 1


def test_lookup_queries_generation_and_execution(mock_adapter):
    """Test LookupQueries generation and adapter execution."""
    p_item = LookupQueries.get_point_lookup_query("202")
    assert p_item.query_type == "LOOKUP"
    assert p_item.parameters == {"user_id": "202"}

    idx_item = LookupQueries.get_indexed_lookup_query("pref", 5)
    assert idx_item.parameters == {"prefix": "pref", "limit": 5}

    res_point = LookupQueries.execute_point_lookup(mock_adapter, "202")
    assert len(res_point) == 1
    mock_adapter.execute_read.assert_called_with(p_item.query_string, p_item.parameters)

    res_idx = LookupQueries.execute_indexed_lookup(mock_adapter, "pref", 5)
    assert len(res_idx) == 1


def test_aggregation_queries_generation_and_execution(mock_adapter):
    """Test AggregationQueries generation and adapter execution."""
    out_q = AggregationQueries.get_out_degree_query(15)
    assert out_q.parameters == {"limit": 15}

    in_q = AggregationQueries.get_in_degree_query(15)
    assert in_q.parameters == {"limit": 15}

    summary_q = AggregationQueries.get_graph_summary_query()
    assert summary_q.name == "graph_summary_counts"

    res_out = AggregationQueries.execute_out_degree(mock_adapter, 15)
    assert len(res_out) == 1

    res_in = AggregationQueries.execute_in_degree(mock_adapter, 15)
    assert len(res_in) == 1

    res_summary = AggregationQueries.execute_graph_summary(mock_adapter)
    assert len(res_summary) == 1


def test_mixed_queries_generation_and_execution(mock_adapter):
    """Test MixedQueries creation templates and ratio execution workload."""
    node_q = MixedQueries.get_create_node_query("303", "User")
    assert node_q.query_type == "WRITE"
    assert node_q.parameters == {"user_id": "303", "label": "User"}

    vote_q = MixedQueries.get_create_vote_query("303", "304")
    assert vote_q.query_type == "WRITE"
    assert vote_q.parameters == {"src_id": "303", "tgt_id": "304"}

    # Execute 10 operations with read_ratio=0.8 (8 reads, 2 writes)
    results = MixedQueries.execute_mixed_workload(
        mock_adapter, read_ratio=0.8, num_ops=10, user_id="303"
    )
    assert len(results) == 10
    assert mock_adapter.execute_read.call_count == 8
    assert mock_adapter.execute_write.call_count == 2


def test_read_write_workload_integration():
    """Test ReadWriteWorkload query aggregation."""
    workload = ReadWriteWorkload("505")
    warmup = workload.get_warmup_queries()
    benchmark = workload.get_benchmark_queries()

    assert len(warmup) == 2
    assert len(benchmark) >= 10
