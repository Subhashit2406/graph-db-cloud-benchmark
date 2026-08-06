"""
Aggregation Query Templates and Execution Wrapper.

Defines global graph degree aggregation, top connected node analytics, and graph summary queries.
"""

from typing import Any, Dict, List
from graph_db_benchmark.adapters.base import BaseGraphAdapter
from graph_db_benchmark.workloads.base import QueryItem
from graph_db_benchmark.logger import setup_logger

logger = setup_logger(__name__)


class AggregationQueries:
    """
    Production-ready Aggregation Query suite for graph database analytics.
    """

    @staticmethod
    def get_out_degree_query(limit: int = 10) -> QueryItem:
        """
        Get parameterized outgoing degree count aggregation query template.

        Args:
            limit: Top N results limit.

        Returns:
            QueryItem: Configured query item.
        """
        return QueryItem(
            name="out_degree_aggregation",
            query_string="MATCH (u:User)-[r:VOTES]->() RETURN u.id AS user_id, count(r) AS out_degree ORDER BY out_degree DESC LIMIT $limit",
            query_type="AGGREGATION",
            parameters={"limit": int(limit)},
        )

    @staticmethod
    def get_in_degree_query(limit: int = 10) -> QueryItem:
        """
        Get parameterized incoming degree count aggregation query template.

        Args:
            limit: Top N results limit.

        Returns:
            QueryItem: Configured query item.
        """
        return QueryItem(
            name="in_degree_aggregation",
            query_string="MATCH (u:User)<-[r:VOTES]-() RETURN u.id AS user_id, count(r) AS in_degree ORDER BY in_degree DESC LIMIT $limit",
            query_type="AGGREGATION",
            parameters={"limit": int(limit)},
        )

    @staticmethod
    def get_graph_summary_query() -> QueryItem:
        """
        Get total node and relationship summary counts query template.

        Returns:
            QueryItem: Configured query item.
        """
        return QueryItem(
            name="graph_summary_counts",
            query_string="MATCH (u:User) OPTIONAL MATCH (u)-[r:VOTES]->() RETURN count(DISTINCT u) AS total_users, count(r) AS total_votes",
            query_type="AGGREGATION",
            parameters={},
        )

    @classmethod
    def execute_out_degree(cls, adapter: BaseGraphAdapter, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Execute out-degree aggregation query using target database adapter.

        Args:
            adapter: Active database adapter instance.
            limit: Top N limit.

        Returns:
            List[Dict[str, Any]]: List of query result record dictionaries.
        """
        item = cls.get_out_degree_query(limit)
        logger.debug(f"Executing out-degree aggregation query with limit={limit}")
        return adapter.execute_read(item.query_string, item.parameters)

    @classmethod
    def execute_in_degree(cls, adapter: BaseGraphAdapter, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Execute in-degree aggregation query using target database adapter.

        Args:
            adapter: Active database adapter instance.
            limit: Top N limit.

        Returns:
            List[Dict[str, Any]]: List of query result record dictionaries.
        """
        item = cls.get_in_degree_query(limit)
        logger.debug(f"Executing in-degree aggregation query with limit={limit}")
        return adapter.execute_read(item.query_string, item.parameters)

    @classmethod
    def execute_graph_summary(cls, adapter: BaseGraphAdapter) -> List[Dict[str, Any]]:
        """
        Execute graph summary counts query using target database adapter.

        Args:
            adapter: Active database adapter instance.

        Returns:
            List[Dict[str, Any]]: List of query result record dictionaries.
        """
        item = cls.get_graph_summary_query()
        logger.debug("Executing graph summary counts query")
        return adapter.execute_read(item.query_string, item.parameters)

    @classmethod
    def get_queries(cls, limit: int = 10) -> List[QueryItem]:
        """
        Retrieve list of all aggregation query items.

        Args:
            limit: Top N limit.

        Returns:
            List[QueryItem]: Collection of out-degree, in-degree, and graph summary query items.
        """
        return [
            cls.get_out_degree_query(limit),
            cls.get_in_degree_query(limit),
            cls.get_graph_summary_query(),
        ]
