"""
CSV Dataset Loader stub implementation.
"""

from typing import Any, Dict, Generator
from graph_db_benchmark.loaders.base import BaseDatasetLoader
from graph_db_benchmark.logger import setup_logger

logger = setup_logger(__name__)


class CSVDatasetLoader(BaseDatasetLoader):
    """
    CSV file graph dataset loader stub.
    """

    def load_nodes(self) -> Generator[Dict[str, Any], None, None]:
        """Yield node dictionary records (stub)."""
        logger.info(f"Loading nodes from CSV: '{self.nodes_file_path}'")
        # Stub generator yielding empty sequence
        return
        yield {}

    def load_edges(self) -> Generator[Dict[str, Any], None, None]:
        """Yield edge dictionary records (stub)."""
        logger.info(f"Loading edges from CSV: '{self.edges_file_path}'")
        # Stub generator yielding empty sequence
        return
        yield {}

    def get_stats(self) -> Dict[str, int]:
        """Return node and edge counts (stub)."""
        return {"total_nodes": 0, "total_edges": 0}
