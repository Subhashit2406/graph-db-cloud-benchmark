"""
Abstract base class for benchmark query workloads.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Dict, List, Optional


@dataclass
class QueryItem:
    """
    Dataclass holding query execution details.
    """
    name: str
    query_string: str
    query_type: str  # e.g., 'READ', 'WRITE', 'TRAVERSAL', 'AGGREGATION'
    parameters: Optional[Dict[str, Any]] = None


class BaseWorkload(ABC):
    """
    Abstract Base Class representing a benchmark query workload.
    """

    def __init__(self, workload_name: str) -> None:
        """
        Initialize query workload suite.

        Args:
            workload_name: Identifier for workload scenario.
        """
        self.workload_name = workload_name

    @abstractmethod
    def get_warmup_queries(self) -> List[QueryItem]:
        """
        Get list of queries used for database cache warming.

        Returns:
            List[QueryItem]: List of query items.
        """
        pass

    @abstractmethod
    def get_benchmark_queries(self) -> List[QueryItem]:
        """
        Get main suite of queries for performance benchmarking.

        Returns:
            List[QueryItem]: List of query items.
        """
        pass
