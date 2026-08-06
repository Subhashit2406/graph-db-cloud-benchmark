"""
Queries Package.

Contains query template definitions and generators categorized by operation type:
- Traversal queries (k-hop, shortest path)
- Lookup queries (point lookup, indexed search)
- Aggregation queries (grouping, counting, metrics)
- Mixed queries (combined read/write workloads)
"""

from graph_db_benchmark.queries.traversal import TraversalQueries
from graph_db_benchmark.queries.lookup import LookupQueries
from graph_db_benchmark.queries.aggregation import AggregationQueries
from graph_db_benchmark.queries.mixed import MixedQueries

__all__ = [
    "TraversalQueries",
    "LookupQueries",
    "AggregationQueries",
    "MixedQueries",
]
