"""
Traversal Query Templates and Execution Wrapper.

Defines parameterized 1-hop, 2-hop, and 3-hop graph traversal queries
and provides adapter execution methods.
"""

from typing import Any, Dict, List
from graph_db_benchmark.adapters.base import BaseGraphAdapter
from graph_db_benchmark.workloads.base import QueryItem
from graph_db_benchmark.logger import setup_logger

logger = setup_logger(__name__)


class TraversalQueries:
    """
    Production-ready Traversal Query suite for graph database benchmarking.
    """

    @staticmethod
    def get_1hop_query(user_id: str = "1") -> QueryItem:
        """
        Get parameterized 1-hop outgoing neighbors query template.

        Args:
            user_id: Starting node identifier.

        Returns:
            QueryItem: Configured query item.
        """
        return QueryItem(
            name="1_hop_traversal",
            query_string="MATCH (u:User {id: $user_id})-[:VOTES]->(v:User) RETURN v.id AS neighbor_id",
            query_type="TRAVERSAL",
            parameters={"user_id": str(user_id)},
        )

    @staticmethod
    def get_2hop_query(user_id: str = "1") -> QueryItem:
        """
        Get parameterized 2-hop distinct reach count query template.

        Args:
            user_id: Starting node identifier.

        Returns:
            QueryItem: Configured query item.
        """
        return QueryItem(
            name="2_hop_traversal",
            query_string="MATCH (u:User {id: $user_id})-[:VOTES*2]->(v:User) RETURN count(DISTINCT v) AS total_2hop",
            query_type="TRAVERSAL",
            parameters={"user_id": str(user_id)},
        )

    @staticmethod
    def get_3hop_query(user_id: str = "1") -> QueryItem:
        """
        Get parameterized 3-hop distinct reach count query template.

        Args:
            user_id: Starting node identifier.

        Returns:
            QueryItem: Configured query item.
        """
        return QueryItem(
            name="3_hop_traversal",
            query_string="MATCH (u:User {id: $user_id})-[:VOTES*3]->(v:User) RETURN count(DISTINCT v) AS total_3hop",
            query_type="TRAVERSAL",
            parameters={"user_id": str(user_id)},
        )

    @classmethod
    def execute_1hop(cls, adapter: BaseGraphAdapter, user_id: str = "1") -> List[Dict[str, Any]]:
        """
        Execute 1-hop traversal query using target database adapter.

        Args:
            adapter: Active database adapter instance.
            user_id: Starting node identifier.

        Returns:
            List[Dict[str, Any]]: List of query result record dictionaries.
        """
        item = cls.get_1hop_query(user_id)
        logger.debug(f"Executing 1-hop traversal query for user_id='{user_id}'")
        return adapter.execute_read(item.query_string, item.parameters)

    @classmethod
    def execute_2hop(cls, adapter: BaseGraphAdapter, user_id: str = "1") -> List[Dict[str, Any]]:
        """
        Execute 2-hop traversal query using target database adapter.

        Args:
            adapter: Active database adapter instance.
            user_id: Starting node identifier.

        Returns:
            List[Dict[str, Any]]: List of query result record dictionaries.
        """
        item = cls.get_2hop_query(user_id)
        logger.debug(f"Executing 2-hop traversal query for user_id='{user_id}'")
        return adapter.execute_read(item.query_string, item.parameters)

    @classmethod
    def execute_3hop(cls, adapter: BaseGraphAdapter, user_id: str = "1") -> List[Dict[str, Any]]:
        """
        Execute 3-hop traversal query using target database adapter.

        Args:
            adapter: Active database adapter instance.
            user_id: Starting node identifier.

        Returns:
            List[Dict[str, Any]]: List of query result record dictionaries.
        """
        item = cls.get_3hop_query(user_id)
        logger.debug(f"Executing 3-hop traversal query for user_id='{user_id}'")
        return adapter.execute_read(item.query_string, item.parameters)

    @classmethod
    def get_queries(cls, user_id: str = "1") -> List[QueryItem]:
        """
        Retrieve list of all traversal query items.

        Args:
            user_id: Starting node identifier.

        Returns:
            List[QueryItem]: Collection of 1-hop, 2-hop, and 3-hop traversal query items.
        """
        return [
            cls.get_1hop_query(user_id),
            cls.get_2hop_query(user_id),
            cls.get_3hop_query(user_id),
        ]
