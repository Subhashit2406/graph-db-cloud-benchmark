"""
Result export module for persisting benchmark outputs to disk.
"""

import json
import csv
from pathlib import Path
from typing import Any, Dict
from graph_db_benchmark.metrics.collector import BenchmarkResultSummary
from graph_db_benchmark.logger import setup_logger

logger = setup_logger(__name__)


class ResultExporter:
    """
    Exports benchmark summary metrics to JSON or CSV format.
    """

    def __init__(self, output_dir: str = "results_data") -> None:
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def export_json(self, summary: BenchmarkResultSummary, filename: str = "benchmark_results.json") -> Path:
        """
        Export benchmark summary to JSON file.

        Args:
            summary: Benchmark summary metrics object.
            filename: Output filename.

        Returns:
            Path: Path to saved file.
        """
        file_path = self.output_dir / filename
        data = summary.to_dict()

        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

        logger.info(f"Successfully exported benchmark results to '{file_path}'")
        return file_path

    def export_csv(self, summary: BenchmarkResultSummary, filename: str = "benchmark_results.csv") -> Path:
        """
        Export benchmark summary to CSV file.

        Args:
            summary: Benchmark summary metrics object.
            filename: Output filename.

        Returns:
            Path: Path to saved file.
        """
        file_path = self.output_dir / filename
        data = summary.to_dict()

        flat_data = {
            "adapter_name": data["adapter_name"],
            "total_queries": data["total_queries"],
            "successful_queries": data["successful_queries"],
            "failed_queries": data["failed_queries"],
            "total_duration_sec": data["total_duration_sec"],
            "throughput_ops_sec": data["throughput_ops_sec"],
            "p50_ms": data["latencies_ms"]["p50"],
            "p90_ms": data["latencies_ms"]["p90"],
            "p95_ms": data["latencies_ms"]["p95"],
            "p99_ms": data["latencies_ms"]["p99"],
            "min_ms": data["latencies_ms"]["min"],
            "max_ms": data["latencies_ms"]["max"],
            "avg_ms": data["latencies_ms"]["avg"],
            "std_dev_ms": data["latencies_ms"]["std_dev"],
        }

        with open(file_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=list(flat_data.keys()))
            writer.writeheader()
            writer.writerow(flat_data)

        logger.info(f"Successfully exported benchmark results to '{file_path}'")
        return file_path
