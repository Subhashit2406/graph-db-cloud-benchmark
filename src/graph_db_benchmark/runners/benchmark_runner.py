"""
Concurrent benchmark runner implementation.

Orchestrates database cache warmup, multi-threaded benchmark workload execution,
high-resolution timing measurement, latency percentile analysis, and result packaging.
"""

import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Optional

from graph_db_benchmark.adapters.base import BaseGraphAdapter
from graph_db_benchmark.workloads.base import BaseWorkload, QueryItem
from graph_db_benchmark.runners.base import BaseRunner
from graph_db_benchmark.metrics.collector import MetricsCollector, BenchmarkResultSummary
from graph_db_benchmark.logger import setup_logger

logger = setup_logger(__name__)


class BenchmarkRunner(BaseRunner):
    """
    Production-ready Benchmark Runner orchestrating warm-up runs,
    concurrent thread-pool workload execution, and metric reporting.
    """

    def __init__(self, adapter: BaseGraphAdapter, workload: BaseWorkload) -> None:
        """
        Initialize benchmark runner.

        Args:
            adapter: Active database connection adapter.
            workload: Target benchmark query workload.
        """
        super().__init__(adapter=adapter, workload=workload)

    def run_warmup(self, iterations: int = 10) -> None:
        """
        Execute warmup phase to prepare database cache and connection pool.

        Args:
            iterations: Number of warmup query passes.
        """
        logger.info(f"Starting database warmup phase ({iterations} passes)...")
        warmup_queries = self.workload.get_warmup_queries()

        if not warmup_queries:
            logger.info("No warmup queries defined. Skipping warmup phase.")
            return

        for pass_idx in range(iterations):
            for query_item in warmup_queries:
                try:
                    if query_item.query_type == "WRITE":
                        self.adapter.execute_write(query_item.query_string, query_item.parameters)
                    else:
                        self.adapter.execute_read(query_item.query_string, query_item.parameters)
                except Exception as e:
                    logger.debug(f"Warmup query warning on pass {pass_idx + 1}: {str(e)}")

        logger.info("Database warmup phase completed successfully.")

    def run_benchmark(self, iterations: int = 100, concurrency: int = 5) -> BenchmarkResultSummary:
        """
        Execute full benchmark suite under specified worker concurrency.

        Args:
            iterations: Total number of query execution tasks to run.
            concurrency: Number of concurrent worker threads.

        Returns:
            BenchmarkResultSummary: Object containing latency statistics and throughput.
        """
        adapter_name = self.adapter.__class__.__name__
        logger.info(
            f"Starting benchmark execution for '{adapter_name}' "
            f"(concurrency={concurrency}, iterations={iterations})"
        )

        queries = self.workload.get_benchmark_queries()
        if not queries:
            raise ValueError("Workload returned zero benchmark queries.")

        collector = MetricsCollector(adapter_name=adapter_name)
        collector.start()

        def _execute_single(query_item: QueryItem) -> None:
            t0 = time.perf_counter()
            try:
                if query_item.query_type == "WRITE":
                    self.adapter.execute_write(query_item.query_string, query_item.parameters)
                else:
                    self.adapter.execute_read(query_item.query_string, query_item.parameters)
                t1 = time.perf_counter()
                latency_ms = (t1 - t0) * 1000.0
                collector.record_query(latency_ms=latency_ms, success=True)
            except Exception as e:
                t1 = time.perf_counter()
                latency_ms = (t1 - t0) * 1000.0
                collector.record_query(latency_ms=latency_ms, success=False)
                logger.warning(f"Query execution failure during benchmark: {str(e)}")

        # Multi-threaded concurrent worker execution
        workers = max(1, concurrency)
        completed_count = 0
        log_interval = max(1, iterations // 5)

        with ThreadPoolExecutor(max_workers=workers) as executor:
            # Distribute iterations across queries in round-robin sequence
            futures = [
                executor.submit(_execute_single, queries[i % len(queries)])
                for i in range(iterations)
            ]

            for future in as_completed(futures):
                completed_count += 1
                if completed_count % log_interval == 0 or completed_count == iterations:
                    pct = (completed_count / iterations) * 100.0
                    logger.info(f"Benchmark progress: {completed_count}/{iterations} tasks ({pct:.0f}%)")

        collector.stop()
        summary = collector.compute_summary()
        logger.info("Benchmark execution completed successfully.")
        return summary
