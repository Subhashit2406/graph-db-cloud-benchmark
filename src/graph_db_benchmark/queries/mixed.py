"""
Mixed Query Templates and Execution Wrapper.

Defines transactional read and write queries and configurable ratio execution workloads.
"""

from typing import Any, Dict, List
from graph_db_benchmark.adapters.base import BaseGraphAdapter
from graph_db_benchmark.workloads.base import QueryItem
from graph_db_benchmark.logger import setup_logger

logger = setup_logger(__name__)


class MixedQueries:
    """
    Production-ready Mixed Read/Write Query suite for transactional graph workloads.
    """

    @staticmethod
    def get_create_node_query(user_id: str, label: str = "User") -> QueryItem:
        """
        Get parameterized node creation/merge query template.

        Args:
            user_id: Node primary key identifier.
            label: Node label.

        Returns:
            QueryItem: Configured query item.
        """
        return QueryItem(
            name="create_node",
            query_string="MERGE (u:User {id: $user_id}) SET u.label = $label RETURN u",
            query_type="WRITE",
            parameters={"user_id": str(user_id), "label": str(label)},
        )

    @staticmethod
    def get_create_vote_query(src_id: str, tgt_id: str) -> QueryItem:
        """
        Get parameterized relationship creation/merge query template.

        Args:
            src_id: Source node identifier.
            tgt_id: Target node identifier.

        Returns:
            QueryItem: Configured query item.
        """
        return QueryItem(
            name="create_vote_edge",
            query_string="MATCH (src:User {id: $src_id}), (tgt:User {id: $tgt_id}) MERGE (src)-[r:VOTES]->(tgt) RETURN r",
            query_type="WRITE",
            parameters={"src_id": str(src_id), "tgt_id": str(tgt_id)},
        )

    @classmethod
    def execute_read_op(cls, adapter: BaseGraphAdapter, user_id: str = "1") -> List[Dict[str, Any]]:
        """
        Execute read operation against target database adapter.

        Args:
            adapter: Active database adapter.
            user_id: Target user ID.

        Returns:
            List[Dict[str, Any]]: Query record list.
        """
        query = "MATCH (u:User {id: $user_id}) RETURN u"
        return adapter.execute_read(query, {"user_id": str(user_id)})

    @classmethod
    def execute_write_op(
        cls, adapter: BaseGraphAdapter, src_id: str = "1", tgt_id: str = "2"
    ) -> List[Dict[str, Any]]:
        """
        Execute write operation against target database adapter.

        Args:
            adapter: Active database adapter.
            src_id: Source node ID.
            tgt_id: Target node ID.

        Returns:
            List[Dict[str, Any]]: Query record list.
        """
        item = cls.get_create_vote_query(src_id, tgt_id)
        return adapter.execute_write(item.query_string, item.parameters)

    @classmethod
    def execute_mixed_workload(
        cls,
        adapter: BaseGraphAdapter,
        read_ratio: float = 0.8,
        num_ops: int = 10,
        user_id: str = "1",
    ) -> List[Dict[str, Any]]:
        """
        Execute a mixed sequence of read and write queries according to specified ratio.

        Args:
            adapter: Active database adapter.
            read_ratio: Proportion of read operations (0.0 to 1.0). Default: 0.8 (80% read, 20% write).
            num_ops: Total number of operations to execute.
            user_id: Sample user ID for read/write operations.

        Returns:
            List[Dict[str, Any]]: List of combined query execution results.
        """
        logger.info(
            f"Executing mixed workload ({num_ops} operations, read_ratio={read_ratio:.2f})"
        )
        results: List[Dict[str, Any]] = []

        read_count = int(num_ops * read_ratio)
        for i in range(num_ops):
            if i < read_count:
                res = cls.execute_read_op(adapter, user_id=user_id)
            else:
                res = cls.execute_write_op(adapter, src_id=user_id, tgt_id=f"target_{i}")
            results.extend(res)

        return results

    @classmethod
    def get_queries(
        cls, user_id: str = "1", src_id: str = "1", tgt_id: str = "2"
    ) -> List[QueryItem]:
        """
        Retrieve list of all mixed workload query items.

        Args:
            user_id: Sample node ID.
            src_id: Sample source ID.
            tgt_id: Sample target ID.

        Returns:
            List[QueryItem]: Collection of node and edge creation query items.
        """
        return [
            cls.get_create_node_query(user_id),
            cls.get_create_vote_query(src_id, tgt_id),
        ]
