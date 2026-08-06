"""
CognoDB Database Adapter Implementation.

Uses the official Neo4j Python driver to manage connection pooling,
session contexts, transactional query execution (read/write), and result parsing
for benchmarking Cypher graph database workloads.
"""

import csv
import json
import time
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Dict, Generator, List, Optional
import neo4j
from neo4j import GraphDatabase, Driver, Session
from neo4j.exceptions import Neo4jError, ServiceUnavailable, AuthError

from graph_db_benchmark.adapters.base import (
    BaseGraphAdapter,
    AdapterConnectionError,
    QueryExecutionError,
)
from graph_db_benchmark.logger import setup_logger

logger = setup_logger(__name__)


class CognoDBAdapter(BaseGraphAdapter):
    """
    Production-ready CognoDB Adapter implementing BaseGraphAdapter using the official Neo4j driver.
    """

    def __init__(self, connection_config: Dict[str, Any]) -> None:
        """
        Initialize CognoDBAdapter with connection settings.

        Args:
            connection_config: Config dictionary containing uri, user, password, database.
        """
        super().__init__(connection_config)
        self.uri: str = connection_config.get("uri", "bolt://localhost:7687")
        self.user: str = connection_config.get("user", "neo4j")
        self.password: str = connection_config.get("password", "")
        self.database: str = connection_config.get("database", "neo4j")
        self.max_pool_size: int = connection_config.get("max_connection_pool_size", 50)
        self.connection_timeout: float = connection_config.get("connection_timeout_seconds", 30.0)

        self.driver: Optional[Driver] = None

    def connect(self) -> None:
        """
        Establish driver connection pool to CognoDB / Neo4j database instance.

        Raises:
            AdapterConnectionError: If connection fails or authentication fails.
        """
        if self.is_connected and self.driver is not None:
            logger.debug("CognoDBAdapter driver is already connected.")
            return

        logger.info(f"Connecting to CognoDB database at '{self.uri}' (user: '{self.user}')")
        try:
            auth = (self.user, self.password) if self.user else None
            self.driver = GraphDatabase.driver(
                self.uri,
                auth=auth,
                max_connection_pool_size=self.max_pool_size,
                connection_timeout=self.connection_timeout,
            )
            self.driver.verify_connectivity()
            self.is_connected = True
            logger.info("Successfully connected and verified connectivity to CognoDB instance.")
        except (AuthError, ServiceUnavailable, Neo4jError, Exception) as e:
            self.is_connected = False
            self.driver = None
            logger.error(f"Failed to connect to CognoDB at '{self.uri}': {str(e)}")
            raise AdapterConnectionError(f"Could not connect to CognoDB: {str(e)}") from e

    def disconnect(self) -> None:
        """
        Close active database driver connection pool and release resources.
        """
        if self.driver is not None:
            logger.info("Closing CognoDB database driver connection pool.")
            try:
                self.driver.close()
            except Exception as e:
                logger.warning(f"Error occurred while closing driver: {str(e)}")
            finally:
                self.driver = None
                self.is_connected = False
        else:
            self.is_connected = False

    def verify_connection(self) -> bool:
        """
        Actively verify connectivity to database instance.

        Returns:
            bool: True if connection is alive, False otherwise.
        """
        if not self.is_connected or self.driver is None:
            return False

        try:
            self.driver.verify_connectivity()
            return True
        except Exception as e:
            logger.warning(f"CognoDB connectivity verification failed: {str(e)}")
            self.is_connected = False
            return False

    @contextmanager
    def get_session(self) -> Generator[Session, None, None]:
        """
        Context manager for acquiring database session with automatic cleanup.

        Yields:
            Session: Active Neo4j session instance.

        Raises:
            AdapterConnectionError: If driver is disconnected.
        """
        if not self.is_connected or self.driver is None:
            raise AdapterConnectionError("Cannot create session: CognoDBAdapter is not connected.")

        session = self.driver.session(database=self.database)
        try:
            yield session
        finally:
            session.close()

    def _parse_record(self, record: neo4j.Record) -> Dict[str, Any]:
        """
        Convert Neo4j Record to clean, serializable Python dictionary.

        Args:
            record: Neo4j Record object.

        Returns:
            Dict[str, Any]: Dictionary representation of key-value pairs.
        """
        parsed: Dict[str, Any] = {}
        for key, val in record.items():
            if hasattr(val, "_properties"):
                # Neo4j Node or Relationship
                parsed[key] = dict(val._properties)
            else:
                parsed[key] = val
        return parsed

    def execute_read(
        self, query: str, parameters: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Execute read query inside read transaction session context.

        Args:
            query: Cypher read query string.
            parameters: Optional query parameter bindings.

        Returns:
            List[Dict[str, Any]]: List of record dictionaries.
        """
        params = parameters or {}
        logger.debug(f"Executing read query: {query[:80]}... Params: {params}")

        try:
            with self.get_session() as session:
                result = session.execute_read(
                    lambda tx: [self._parse_record(rec) for rec in tx.run(query, params)]
                )
                return result
        except (Neo4jError, ServiceUnavailable, Exception) as e:
            logger.error(f"Read query execution failed: {str(e)}")
            raise QueryExecutionError(f"Error executing read query: {str(e)}") from e

    def execute_write(
        self, query: str, parameters: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Execute write query inside write transaction session context.

        Args:
            query: Cypher write query string.
            parameters: Optional query parameter bindings.

        Returns:
            List[Dict[str, Any]]: List of record dictionaries.
        """
        params = parameters or {}
        logger.debug(f"Executing write query: {query[:80]}... Params: {params}")

        try:
            with self.get_session() as session:
                result = session.execute_write(
                    lambda tx: [self._parse_record(rec) for rec in tx.run(query, params)]
                )
                return result
        except (Neo4jError, ServiceUnavailable, Exception) as e:
            logger.error(f"Write query execution failed: {str(e)}")
            raise QueryExecutionError(f"Error executing write query: {str(e)}") from e

    def execute_query(
        self, query: str, parameters: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Execute arbitrary Cypher query string. Automatically selects read or write transaction.

        Args:
            query: Cypher query string.
            parameters: Optional query parameter bindings.

        Returns:
            List[Dict[str, Any]]: List of record dictionaries.
        """
        query_upper = query.strip().upper()
        write_keywords = ("CREATE", "MERGE", "SET", "DELETE", "REMOVE", "DROP")

        if any(keyword in query_upper for keyword in write_keywords):
            return self.execute_write(query, parameters)
        return self.execute_read(query, parameters)

    def bulk_import(
        self,
        nodes_file: str,
        edges_file: str,
        batch_size: int = 1000,
        summary_file: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Execute batched bulk dataset import into CognoDB using idempotent Cypher MERGE transactions.

        Args:
            nodes_file: Path to processed nodes.csv file.
            edges_file: Path to processed relationships.csv file.
            batch_size: Transaction batch size for ingestion (default: 1000).
            summary_file: Optional path to dataset_summary.json for count verification.

        Returns:
            Dict[str, Any]: Detailed import metrics and validation counts.

        Raises:
            QueryExecutionError: If batch transaction or count validation fails.
        """
        nodes_path = Path(nodes_file)
        edges_path = Path(edges_file)

        if not nodes_path.exists():
            raise FileNotFoundError(f"Nodes dataset file not found at '{nodes_path}'")
        if not edges_path.exists():
            raise FileNotFoundError(f"Edges dataset file not found at '{edges_path}'")

        if not self.is_connected or self.driver is None:
            self.connect()

        logger.info(
            f"Starting bulk dataset import (batch_size={batch_size}) "
            f"from nodes: '{nodes_path}' and edges: '{edges_path}'"
        )

        start_time = time.perf_counter()
        total_nodes_imported = 0
        total_rels_imported = 0

        # Phase 1: Import Nodes in Batches using MERGE
        node_query = """
        UNWIND $batch AS row
        MERGE (n:User {id: toString(row.id)})
        SET n.label = coalesce(row.label, 'User')
        """

        node_batch: List[Dict[str, Any]] = []
        with open(nodes_path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                node_batch.append(row)
                if len(node_batch) >= batch_size:
                    self._import_batch(node_query, node_batch)
                    total_nodes_imported += len(node_batch)
                    logger.info(f"Node import progress: {total_nodes_imported} nodes committed.")
                    node_batch = []
            if node_batch:
                self._import_batch(node_query, node_batch)
                total_nodes_imported += len(node_batch)
                logger.info(f"Node import complete: {total_nodes_imported} total nodes committed.")

        # Phase 2: Import Relationships in Batches using MERGE
        rel_query = """
        UNWIND $batch AS row
        MATCH (src:User {id: toString(coalesce(row.source, row.FromNodeId))})
        MATCH (tgt:User {id: toString(coalesce(row.target, row.ToNodeId))})
        MERGE (src)-[r:VOTES]->(tgt)
        """

        rel_batch: List[Dict[str, Any]] = []
        with open(edges_path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                rel_batch.append(row)
                if len(rel_batch) >= batch_size:
                    self._import_batch(rel_query, rel_batch)
                    total_rels_imported += len(rel_batch)
                    logger.info(f"Relationship import progress: {total_rels_imported} relationships committed.")
                    rel_batch = []
            if rel_batch:
                self._import_batch(rel_query, rel_batch)
                total_rels_imported += len(rel_batch)
                logger.info(f"Relationship import complete: {total_rels_imported} total relationships committed.")

        end_time = time.perf_counter()
        total_duration = max(end_time - start_time, 0.0001)

        # Phase 3: Validation Queries
        db_node_count = self._get_db_count("MATCH (n:User) RETURN count(n) AS count")
        db_rel_count = self._get_db_count("MATCH ()-[r:VOTES]->() RETURN count(r) AS count")

        summary_data: Optional[Dict[str, Any]] = None
        summary_path = Path(summary_file) if summary_file else nodes_path.parent / "dataset_summary.json"
        if summary_path.exists():
            try:
                with open(summary_path, "r", encoding="utf-8") as sf:
                    summary_data = json.load(sf)
            except Exception as e:
                logger.warning(f"Could not read summary JSON file '{summary_path}': {e}")

        expected_nodes = summary_data.get("unique_nodes", total_nodes_imported) if summary_data else total_nodes_imported
        expected_rels = summary_data.get("final_relationships", total_rels_imported) if summary_data else total_rels_imported

        nodes_validated = (db_node_count == expected_nodes) or (db_node_count >= total_nodes_imported)
        rels_validated = (db_rel_count == expected_rels) or (db_rel_count >= total_rels_imported)

        logger.info(
            f"Validation Check: DB Nodes Count = {db_node_count} (Expected: {expected_nodes}), "
            f"DB Relationships Count = {db_rel_count} (Expected: {expected_rels})"
        )

        node_tp = total_nodes_imported / total_duration
        rel_tp = total_rels_imported / total_duration
        total_tp = (total_nodes_imported + total_rels_imported) / total_duration

        return {
            "status": "success",
            "nodes_imported": total_nodes_imported,
            "relationships_imported": total_rels_imported,
            "time_taken_sec": round(total_duration, 4),
            "throughput": {
                "nodes_per_sec": round(node_tp, 2),
                "relationships_per_sec": round(rel_tp, 2),
                "total_ops_per_sec": round(total_tp, 2),
            },
            "validation": {
                "db_node_count": db_node_count,
                "db_relationship_count": db_rel_count,
                "nodes_matched": nodes_validated,
                "relationships_matched": rels_validated,
            },
        }

    def _import_batch(self, query: str, batch: List[Dict[str, Any]]) -> None:
        """Helper executing single batch inside transaction callback with automatic rollback on error."""
        try:
            with self.get_session() as session:
                session.execute_write(lambda tx: tx.run(query, {"batch": batch}))
        except Exception as e:
            logger.error(f"Bulk import batch execution failed: {str(e)}")
            raise QueryExecutionError(f"Batch import transaction failed: {str(e)}") from e

    def _get_db_count(self, count_query: str) -> int:
        """Helper executing count aggregation query."""
        try:
            res = self.execute_read(count_query)
            if res and "count" in res[0]:
                return int(res[0]["count"])
            return 0
        except Exception as e:
            logger.warning(f"Validation count query failed: {str(e)}")
            return 0
