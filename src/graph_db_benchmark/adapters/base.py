"""
Abstract base class definition for database adapters.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional


class AdapterError(Exception):
    """Base exception class for database adapter failures."""
    pass


class AdapterConnectionError(AdapterError):
    """Raised when establishing or verifying connection to database fails."""
    pass


class QueryExecutionError(AdapterError):
    """Raised when query execution encounters database runtime errors."""
    pass


class BaseGraphAdapter(ABC):
    """
    Abstract Base Class representing a graph database connection adapter.
    All managed graph database drivers must implement this interface.
    """

    def __init__(self, connection_config: Dict[str, Any]) -> None:
        """
        Initialize database adapter with configuration dictionary.

        Args:
            connection_config: Dictionary containing database connection parameters.
        """
        self.config = connection_config
        self.is_connected: bool = False

    @abstractmethod
    def connect(self) -> None:
        """
        Establish driver connection pool to database instance.
        """
        pass

    @abstractmethod
    def disconnect(self) -> None:
        """
        Close active database connection pool and release resources.
        """
        pass

    @abstractmethod
    def verify_connection(self) -> bool:
        """
        Actively ping database instance to verify connection readiness.

        Returns:
            bool: True if connection is alive and verified, False otherwise.
        """
        pass

    @abstractmethod
    def execute_query(
        self, query: str, parameters: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Execute arbitrary Cypher/Gremlin query string against database.

        Args:
            query: Query string.
            parameters: Optional query parameters dictionary.

        Returns:
            List[Dict[str, Any]]: List of record dictionaries.
        """
        pass

    @abstractmethod
    def execute_read(
        self, query: str, parameters: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Execute read-only query within read transaction context.

        Args:
            query: Read query string.
            parameters: Optional query parameters.

        Returns:
            List[Dict[str, Any]]: List of record dictionaries.
        """
        pass

    @abstractmethod
    def execute_write(
        self, query: str, parameters: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Execute write query within write transaction context.

        Args:
            query: Write query string.
            parameters: Optional query parameters.

        Returns:
            List[Dict[str, Any]]: List of record dictionaries.
        """
        pass

    @abstractmethod
    def bulk_import(
        self,
        nodes_file: str,
        edges_file: str,
        batch_size: int = 1000,
        summary_file: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Execute bulk data ingestion for node and edge datasets.

        Args:
            nodes_file: Path to node dataset file.
            edges_file: Path to edge dataset file.
            batch_size: Transaction batch size for ingestion.
            summary_file: Optional path to dataset_summary.json for count validation.

        Returns:
            Dict[str, Any]: Ingestion metrics dictionary.
        """
        pass

    def health_check(self) -> bool:
        """
        Check database connection health by delegating to verify_connection.

        Returns:
            bool: True if connection is healthy, False otherwise.
        """
        return self.verify_connection()
