"""
Unit tests for CognoDBAdapter using unittest.mock.
"""

from unittest.mock import MagicMock, patch
import pytest
from neo4j.exceptions import ServiceUnavailable, Neo4jError

from graph_db_benchmark.adapters.cognodb_adapter import CognoDBAdapter
from graph_db_benchmark.adapters.base import AdapterConnectionError, QueryExecutionError


@pytest.fixture
def adapter_config():
    return {
        "uri": "bolt://localhost:7687",
        "user": "neo4j",
        "password": "secretpassword",
        "database": "cognodb_test",
        "max_connection_pool_size": 20,
        "connection_timeout_seconds": 10.0,
    }


def test_connect_success(adapter_config):
    """Test successful connection and connectivity verification."""
    with patch("graph_db_benchmark.adapters.cognodb_adapter.GraphDatabase.driver") as mock_driver_fn:
        mock_driver = MagicMock()
        mock_driver_fn.return_value = mock_driver

        adapter = CognoDBAdapter(adapter_config)
        adapter.connect()

        assert adapter.is_connected is True
        mock_driver_fn.assert_called_once_with(
            "bolt://localhost:7687",
            auth=("neo4j", "secretpassword"),
            max_connection_pool_size=20,
            connection_timeout=10.0,
        )
        mock_driver.verify_connectivity.assert_called_once()
        assert adapter.verify_connection() is True


def test_connect_failure(adapter_config):
    """Test connection failure raises AdapterConnectionError."""
    with patch("graph_db_benchmark.adapters.cognodb_adapter.GraphDatabase.driver") as mock_driver_fn:
        mock_driver = MagicMock()
        mock_driver.verify_connectivity.side_effect = ServiceUnavailable("Unable to connect")
        mock_driver_fn.return_value = mock_driver

        adapter = CognoDBAdapter(adapter_config)
        with pytest.raises(AdapterConnectionError) as exc_info:
            adapter.connect()

        assert "Could not connect to CognoDB" in str(exc_info.value)
        assert adapter.is_connected is False
        assert adapter.driver is None


def test_disconnect(adapter_config):
    """Test driver disconnection and cleanup."""
    with patch("graph_db_benchmark.adapters.cognodb_adapter.GraphDatabase.driver") as mock_driver_fn:
        mock_driver = MagicMock()
        mock_driver_fn.return_value = mock_driver

        adapter = CognoDBAdapter(adapter_config)
        adapter.connect()
        assert adapter.is_connected is True

        adapter.disconnect()
        assert adapter.is_connected is False
        assert adapter.driver is None
        mock_driver.close.assert_called_once()


def test_execute_read_success(adapter_config):
    """Test execute_read returning formatted list of record dicts."""
    with patch("graph_db_benchmark.adapters.cognodb_adapter.GraphDatabase.driver") as mock_driver_fn:
        mock_driver = MagicMock()
        mock_session = MagicMock()
        mock_driver.session.return_value = mock_session
        mock_driver_fn.return_value = mock_driver

        # Mock execute_read callback execution
        expected_records = [{"name": "Alice", "age": 30}]
        mock_session.execute_read.return_value = expected_records

        adapter = CognoDBAdapter(adapter_config)
        adapter.connect()

        results = adapter.execute_read("MATCH (p:Person {name: $name}) RETURN p", {"name": "Alice"})
        assert results == expected_records
        mock_driver.session.assert_called_once_with(database="cognodb_test")
        mock_session.close.assert_called_once()


def test_execute_write_success(adapter_config):
    """Test execute_write returning formatted list of record dicts."""
    with patch("graph_db_benchmark.adapters.cognodb_adapter.GraphDatabase.driver") as mock_driver_fn:
        mock_driver = MagicMock()
        mock_session = MagicMock()
        mock_driver.session.return_value = mock_session
        mock_driver_fn.return_value = mock_driver

        expected_records = [{"id": "user_101", "created": True}]
        mock_session.execute_write.return_value = expected_records

        adapter = CognoDBAdapter(adapter_config)
        adapter.connect()

        results = adapter.execute_write("CREATE (p:Person {id: $id}) RETURN p", {"id": "user_101"})
        assert results == expected_records
        mock_session.execute_write.assert_called_once()


def test_execute_query_routing(adapter_config):
    """Test execute_query routes write statements to execute_write and read to execute_read."""
    adapter = CognoDBAdapter(adapter_config)
    adapter.execute_read = MagicMock(return_value=[{"type": "read"}])
    adapter.execute_write = MagicMock(return_value=[{"type": "write"}])

    read_res = adapter.execute_query("MATCH (n) RETURN n")
    assert read_res == [{"type": "read"}]
    adapter.execute_read.assert_called_once()

    write_res = adapter.execute_query("CREATE (n:Person {id: 1})")
    assert write_res == [{"type": "write"}]
    adapter.execute_write.assert_called_once()


def test_query_execution_error(adapter_config):
    """Test that query failure raises QueryExecutionError."""
    with patch("graph_db_benchmark.adapters.cognodb_adapter.GraphDatabase.driver") as mock_driver_fn:
        mock_driver = MagicMock()
        mock_session = MagicMock()
        mock_session.execute_read.side_effect = Neo4jError("Syntax error in Cypher")
        mock_driver.session.return_value = mock_session
        mock_driver_fn.return_value = mock_driver

        adapter = CognoDBAdapter(adapter_config)
        adapter.connect()

        with pytest.raises(QueryExecutionError) as exc_info:
            adapter.execute_read("INVALID QUERY")

        assert "Error executing read query" in str(exc_info.value)
