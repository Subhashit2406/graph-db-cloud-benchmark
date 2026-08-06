"""
Offline unit tests for bulk dataset import pipeline using unittest.mock.
"""

from pathlib import Path
from unittest.mock import MagicMock, patch
import pytest
from neo4j.exceptions import Neo4jError

from graph_db_benchmark.adapters.cognodb_adapter import CognoDBAdapter
from graph_db_benchmark.adapters.base import QueryExecutionError


@pytest.fixture
def sample_dataset_files(tmp_path: Path):
    """Fixture creating temporary processed nodes.csv, relationships.csv, and dataset_summary.json."""
    nodes_csv = tmp_path / "nodes.csv"
    nodes_csv.write_text("id,label\n1,User\n2,User\n3,User\n", encoding="utf-8")

    rels_csv = tmp_path / "relationships.csv"
    rels_csv.write_text("source,target,relationship_type\n1,2,VOTES\n2,3,VOTES\n", encoding="utf-8")

    summary_json = tmp_path / "dataset_summary.json"
    summary_json.write_text(
        '{"unique_nodes": 3, "final_relationships": 2}', encoding="utf-8"
    )

    return nodes_csv, rels_csv, summary_json


def test_bulk_import_success(sample_dataset_files):
    """Test successful batched bulk import execution, stats calculation, and validation."""
    nodes_csv, rels_csv, summary_json = sample_dataset_files

    with patch("graph_db_benchmark.adapters.cognodb_adapter.GraphDatabase.driver") as mock_driver_fn:
        mock_driver = MagicMock()
        mock_session = MagicMock()

        # Mock execute_read to return count queries validation results
        mock_session.execute_read.side_effect = [
            [{"count": 3}],  # Node count query
            [{"count": 2}],  # Relationship count query
        ]

        mock_driver.session.return_value = mock_session
        mock_driver_fn.return_value = mock_driver

        adapter = CognoDBAdapter({
            "uri": "bolt://localhost:7687",
            "user": "neo4j",
            "password": "pass",
        })

        metrics = adapter.bulk_import(
            nodes_file=str(nodes_csv),
            edges_file=str(rels_csv),
            batch_size=2,  # Forces 2 node batches and 1 rel batch
            summary_file=str(summary_json),
        )

        assert metrics["status"] == "success"
        assert metrics["nodes_imported"] == 3
        assert metrics["relationships_imported"] == 2
        assert metrics["time_taken_sec"] > 0
        assert metrics["throughput"]["total_ops_per_sec"] > 0
        assert metrics["validation"]["db_node_count"] == 3
        assert metrics["validation"]["db_relationship_count"] == 2
        assert metrics["validation"]["nodes_matched"] is True
        assert metrics["validation"]["relationships_matched"] is True

        # Verify execute_write called for node and edge batches
        assert mock_session.execute_write.call_count == 3  # 2 node batches + 1 rel batch


def test_bulk_import_file_not_found():
    """Test that missing dataset files raise FileNotFoundError."""
    adapter = CognoDBAdapter({"uri": "bolt://localhost:7687", "user": "neo4j"})

    with pytest.raises(FileNotFoundError):
        adapter.bulk_import(
            nodes_file="non_existent_nodes.csv",
            edges_file="non_existent_rels.csv",
        )


def test_bulk_import_transaction_rollback_error(sample_dataset_files):
    """Test that transaction failure in batch import raises QueryExecutionError."""
    nodes_csv, rels_csv, _ = sample_dataset_files

    with patch("graph_db_benchmark.adapters.cognodb_adapter.GraphDatabase.driver") as mock_driver_fn:
        mock_driver = MagicMock()
        mock_session = MagicMock()
        mock_session.execute_write.side_effect = Neo4jError("Transaction rolled back due to error")
        mock_driver.session.return_value = mock_session
        mock_driver_fn.return_value = mock_driver

        adapter = CognoDBAdapter({"uri": "bolt://localhost:7687", "user": "neo4j"})

        with pytest.raises(QueryExecutionError) as exc_info:
            adapter.bulk_import(
                nodes_file=str(nodes_csv),
                edges_file=str(rels_csv),
                batch_size=10,
            )

        assert "Batch import transaction failed" in str(exc_info.value)
