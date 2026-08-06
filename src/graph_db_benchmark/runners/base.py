"""
Abstract base class definition for benchmark runners.
"""

from abc import ABC, abstractmethod
from graph_db_benchmark.adapters.base import BaseGraphAdapter
from graph_db_benchmark.workloads.base import BaseWorkload
from graph_db_benchmark.metrics.collector import BenchmarkResultSummary


class BaseRunner(ABC):
    """
    Abstract Base Class for orchestrating benchmark execution.
    """

    def __init__(self, adapter: BaseGraphAdapter, workload: BaseWorkload) -> None:
        """
        Initialize runner with database adapter and target query workload.

        Args:
            adapter: Active database adapter instance.
            workload: Target query workload definition.
        """
        self.adapter = adapter
        self.workload = workload

    @abstractmethod
    def run_warmup(self, iterations: int) -> None:
        """
        Execute warmup phase to prepare database cache.

        Args:
            iterations: Number of warmup query iterations.
        """
        pass

    @abstractmethod
    def run_benchmark(self, iterations: int, concurrency: int) -> BenchmarkResultSummary:
        """
        Execute full benchmark suite under specified concurrency model.

        Args:
            iterations: Number of total query iterations.
            concurrency: Number of parallel execution workers.

        Returns:
            BenchmarkResultSummary: Object containing aggregated benchmark metrics.
        """
        pass
