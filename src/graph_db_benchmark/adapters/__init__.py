"""
Database Adapters Module.

Provides abstract interface definitions and database connection drivers
for managed cloud graph databases.
"""

from graph_db_benchmark.adapters.base import (
    BaseGraphAdapter,
    AdapterError,
    AdapterConnectionError,
    QueryExecutionError,
)
from graph_db_benchmark.adapters.cognodb_adapter import CognoDBAdapter
from graph_db_benchmark.adapters.neo4j_adapter import Neo4jAdapter
from graph_db_benchmark.adapters.neptune_adapter import NeptuneAdapter
from graph_db_benchmark.adapters.memgraph_adapter import MemgraphAdapter

__all__ = [
    "BaseGraphAdapter",
    "AdapterError",
    "AdapterConnectionError",
    "QueryExecutionError",
    "CognoDBAdapter",
    "Neo4jAdapter",
    "NeptuneAdapter",
    "MemgraphAdapter",
]
