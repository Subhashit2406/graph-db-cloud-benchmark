"""
Mixed Read/Write query workload suite.

Aggregates queries from TraversalQueries, LookupQueries, AggregationQueries, and MixedQueries.
"""

from typing import List
from graph_db_benchmark.workloads.base import BaseWorkload, QueryItem
from graph_db_benchmark.queries import (
    TraversalQueries,
    LookupQueries,
    AggregationQueries,
    MixedQueries,
)


class ReadWriteWorkload(BaseWorkload):
    """
    Production-ready Read & Write Benchmark Workload.
    """

    def __init__(self, sample_user_id: str = "1") -> None:
        """
        Initialize read/write workload.

        Args:
            sample_user_id: Target user ID for parameterized queries.
        """
        super().__init__(workload_name="mixed_read_write")
        self.sample_user_id = sample_user_id

    def get_warmup_queries(self) -> List[QueryItem]:
        """
        Return warmup queries used for database cache warming.

        Returns:
            List[QueryItem]: Warmup query items.
        """
        return [
            LookupQueries.get_point_lookup_query(self.sample_user_id),
            AggregationQueries.get_graph_summary_query(),
        ]

    def get_benchmark_queries(self) -> List[QueryItem]:
        """
        Return complete collection of benchmark query items across all categories.

        Returns:
            List[QueryItem]: Combined list of traversal, lookup, aggregation, and mixed queries.
        """
        queries: List[QueryItem] = []
        queries.extend(LookupQueries.get_queries(self.sample_user_id))
        queries.extend(TraversalQueries.get_queries(self.sample_user_id))
        queries.extend(AggregationQueries.get_queries(limit=10))
        queries.extend(MixedQueries.get_queries(user_id=self.sample_user_id, src_id="1", tgt_id="2"))
        return queries
