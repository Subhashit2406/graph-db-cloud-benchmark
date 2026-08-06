#!/usr/bin/env python3
"""
CLI entrypoint script to launch graph database benchmark suite.
"""

import sys
import argparse
from pathlib import Path

# Ensure src/ is on python path for script execution
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from graph_db_benchmark.config import get_settings
from graph_db_benchmark.logger import setup_logger
from graph_db_benchmark.adapters import CognoDBAdapter, Neo4jAdapter, NeptuneAdapter, MemgraphAdapter
from graph_db_benchmark.workloads import ReadWriteWorkload
from graph_db_benchmark.runners import BenchmarkRunner
from graph_db_benchmark.results import ResultExporter, ResultFormatter

logger = setup_logger("run_benchmark")


def parse_args() -> argparse.Namespace:
    """Parse command line arguments for benchmark runner CLI."""
    parser = argparse.ArgumentParser(
        description="Graph Database Cloud Benchmark CLI Utility",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "--adapter",
        type=str,
        choices=["cognodb", "neo4j", "neptune", "memgraph"],
        help="Target database adapter engine",
    )
    parser.add_argument(
        "--concurrency",
        type=int,
        help="Number of concurrent worker threads",
    )
    parser.add_argument(
        "--iterations",
        type=int,
        help="Total query execution iterations",
    )
    parser.add_argument(
        "--export-format",
        type=str,
        choices=["json", "csv"],
        default="json",
        help="Format to export benchmark results",
    )
    return parser.parse_args()


def main() -> None:
    """Main CLI entrypoint execution flow."""
    args = parse_args()
    settings = get_settings()

    adapter_type = args.adapter or settings.benchmark.target_db_adapter
    concurrency = args.concurrency or settings.benchmark.concurrency
    iterations = args.iterations or settings.benchmark.measure_iterations

    logger.info(f"Initializing Graph Database Benchmark (Target Adapter: {adapter_type.upper()})")

    # Select adapter configuration
    if adapter_type in ("cognodb", "neo4j"):
        cogno_cfg = settings.cognodb if adapter_type == "cognodb" else settings.neo4j
        config_dict = {
            "uri": getattr(cogno_cfg, "uri", "bolt://localhost:7687"),
            "user": getattr(cogno_cfg, "user", "neo4j"),
            "password": getattr(cogno_cfg, "password", ""),
            "database": getattr(cogno_cfg, "database", "neo4j"),
            "max_connection_pool_size": getattr(cogno_cfg, "max_connection_pool_size", 50),
            "connection_timeout_seconds": getattr(cogno_cfg, "connection_timeout_seconds", 30.0),
        }
        adapter = CognoDBAdapter(config_dict) if adapter_type == "cognodb" else Neo4jAdapter(config_dict)
    elif adapter_type == "neptune":
        config_dict = {
            "endpoint": settings.neptune.endpoint,
            "port": settings.neptune.port,
            "region": settings.neptune.region,
            "use_ssl": settings.neptune.use_ssl,
        }
        adapter = NeptuneAdapter(config_dict)
    elif adapter_type == "memgraph":
        config_dict = {
            "host": settings.memgraph.host,
            "port": settings.memgraph.port,
            "user": settings.memgraph.user,
            "password": settings.memgraph.password,
        }
        adapter = MemgraphAdapter(config_dict)
    else:
        logger.error(f"Unsupported database adapter: '{adapter_type}'")
        sys.exit(1)

    # Establish connection
    try:
        adapter.connect()
    except Exception as e:
        logger.warning(f"Note: Connection attempt returned ({e}). Continuing run simulation.")

    # Instantiate workload & runner
    workload = ReadWriteWorkload()
    runner = BenchmarkRunner(adapter=adapter, workload=workload)

    # Run warmup & benchmark
    runner.run_warmup(iterations=settings.benchmark.warmup_iterations)
    summary = runner.run_benchmark(iterations=iterations, concurrency=concurrency)

    # Output results
    formatted_report = ResultFormatter.format_summary_text(summary)
    print("\n" + formatted_report + "\n")

    exporter = ResultExporter(output_dir=settings.benchmark.results_dir)
    if args.export_format == "csv":
        exporter.export_csv(summary)
    else:
        exporter.export_json(summary)

    # Clean up connection
    adapter.disconnect()


if __name__ == "__main__":
    main()
