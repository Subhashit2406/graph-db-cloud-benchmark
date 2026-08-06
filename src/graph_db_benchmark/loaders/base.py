"""
Abstract base class definition for dataset loaders.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, Generator


class BaseDatasetLoader(ABC):
    """
    Abstract Base Class for graph dataset loaders.
    """

    def __init__(self, nodes_file_path: str, edges_file_path: str) -> None:
        """
        Initialize dataset loader with paths to node and edge data files.

        Args:
            nodes_file_path: Path to nodes file.
            edges_file_path: Path to edges file.
        """
        self.nodes_file_path = nodes_file_path
        self.edges_file_path = edges_file_path

    @abstractmethod
    def load_nodes(self) -> Generator[Dict[str, Any], None, None]:
        """
        Generator yielding node record dictionaries.

        Yields:
            Dict[str, Any]: Dictionary representing a single graph node.
        """
        pass

    @abstractmethod
    def load_edges(self) -> Generator[Dict[str, Any], None, None]:
        """
        Generator yielding edge record dictionaries.

        Yields:
            Dict[str, Any]: Dictionary representing a single graph edge/relationship.
        """
        pass

    @abstractmethod
    def get_stats(self) -> Dict[str, int]:
        """
        Return basic statistical counts of dataset.

        Returns:
            Dict[str, int]: Dictionary containing total node count and edge count.
        """
        pass
