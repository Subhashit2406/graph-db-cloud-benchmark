"""
Lookup Query Templates and Execution Wrapper.

Defines point lookup and indexed search Cypher queries
and provides adapter execution methods.
"""

from typing import Any, Dict, List
from graph_db_benchmark.adapters.base import BaseGraphAdapter
from graph_db_benchmark.workloads.base import QueryItem
from graph_db_benchmark.logger import setup_logger

logger = setup_logger(__name__)


class LookupQueries:
    """
    Production-ready Lookup Query suite for point and indexed node searches.
    """

    @staticmethod
    def get_point_lookup_query(user_id: str = "1") -> QueryItem:
        """
        Get parameterized point node lookup query template.

        Args:
            user_id: Node primary key identifier.

        Returns:
            QueryItem: Configured query item.
        """
        return QueryItem(
            name="point_node_lookup",
            query_string="MATCH (u:User {id: $user_id}) RETURN u",
            query_type="LOOKUP",
            parameters={"user_id": str(user_id)},
        )

    @staticmethod
    def get_indexed_lookup_query(prefix: str = "1", limit: int = 10) -> QueryItem:
        """
        Get parameterized indexed attribute prefix search query template.

        Args:
            prefix: Starting prefix filter for user ID search.
            limit: Maximum result count.

        Returns:
            QueryItem: Configured query item.
        """
        return QueryItem(
            name="indexed_prefix_lookup",
            query_string="MATCH (u:User) WHERE u.id STARTS WITH $prefix RETURN u.id AS id, u.label AS label LIMIT $limit",
            query_type="LOOKUP",
            parameters={"prefix": str(prefix), "limit": int(limit)},
        )

    @classmethod
    def execute_point_lookup(cls, adapter: BaseGraphAdapter, user_id: str = "1") -> List[Dict[str, Any]]:
        """
        Execute point lookup query using target database adapter.

        Args:
            adapter: Active database adapter instance.
            user_id: Target node identifier.

        Returns:
            List[Dict[str, Any]]: List of query result record dictionaries.
        """
        item = cls.get_point_lookup_query(user_id)
        logger.debug(f"Executing point lookup query for user_id='{user_id}'")
        return adapter.execute_read(item.query_string, item.parameters)

    @classmethod
    def execute_indexed_lookup(
        cls, adapter: BaseGraphAdapter, prefix: str = "1", limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Execute indexed prefix search query using target database adapter.

        Args:
            adapter: Active database adapter instance.
            prefix: User ID prefix filter string.
            limit: Maximum results limit.

        Returns:
            List[Dict[str, Any]]: List of query result record dictionaries.
        """
        item = cls.get_indexed_lookup_query(prefix, limit)
        logger.debug(f"Executing indexed lookup query for prefix='{prefix}', limit={limit}")
        return adapter.execute_read(item.query_string, item.parameters)

    @classmethod
    def get_queries(cls, user_id: str = "1") -> List[QueryItem]:
        """
        Retrieve list of all lookup query items.

        Args:
            user_id: Node primary key identifier.

        Returns:
            List[QueryItem]: Collection of point and indexed lookup query items.
        """
        return [
            cls.get_point_lookup_query(user_id),
            cls.get_indexed_lookup_query(prefix=user_id[:1] if user_id else "1", limit=10),
        ]
