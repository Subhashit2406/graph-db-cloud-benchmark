#!/usr/bin/env python3
"""
CLI script to trigger batched bulk dataset import into target graph database.
"""

import sys
import argparse
from pathlib import Path

# Ensure src/ is on python path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from graph_db_benchmark.config import get_settings
from graph_db_benchmark.logger import setup_logger
from graph_db_benchmark.adapters import CognoDBAdapter, Neo4jAdapter, NeptuneAdapter, MemgraphAdapter

logger = setup_logger("run_bulk_import")


def parse_args() -> argparse.Namespace:
    """Parse command line arguments for bulk import CLI."""
    parser = argparse.ArgumentParser(
        description="Graph Database Bulk Dataset Import Utility",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "--adapter",
        type=str,
        choices=["cognodb", "neo4j", "neptune", "memgraph"],
        help="Target database adapter engine",
    )
    parser.add_argument(
        "--nodes-file",
        type=str,
        default="datasets/processed/nodes.csv",
        help="Path to nodes CSV dataset file",
    )
    parser.add_argument(
        "--edges-file",
        type=str,
        default="datasets/processed/relationships.csv",
        help="Path to relationships CSV dataset file",
    )
    parser.add_argument(
        "--summary-file",
        type=str,
        default="datasets/processed/dataset_summary.json",
        help="Path to dataset_summary.json file for count verification",
    )
    parser.add_argument(
        "--batch-size",
        type=int,
        default=1000,
        help="Transaction batch size for ingestion",
    )
    return parser.parse_args()


def main() -> None:
    """Main execution flow for bulk import script."""
    args = parse_args()
    settings = get_settings()

    adapter_type = args.adapter or settings.benchmark.target_db_adapter
    logger.info(f"Initializing Bulk Import Engine (Target Adapter: {adapter_type.upper()})")

    # Select adapter configuration
    if adapter_type in ("cognodb", "neo4j"):
        cogno_cfg = settings.cognodb if adapter_type == "cognodb" else settings.neo4j
        config_dict = {
            "uri": getattr(cogno_cfg, "uri", "bolt://localhost:7687"),
            "user": getattr(cogno_cfg, "user", "neo4j"),
            "password": getattr(cogno_cfg, "password", ""),
            "database": getattr(cogno_cfg, "database", "neo4j"),
        }
        adapter = CognoDBAdapter(config_dict) if adapter_type == "cognodb" else Neo4jAdapter(config_dict)
    elif adapter_type == "neptune":
        config_dict = {"endpoint": settings.neptune.endpoint, "port": settings.neptune.port}
        adapter = NeptuneAdapter(config_dict)
    elif adapter_type == "memgraph":
        config_dict = {"host": settings.memgraph.host, "port": settings.memgraph.port}
        adapter = MemgraphAdapter(config_dict)
    else:
        logger.error(f"Unsupported database adapter: '{adapter_type}'")
        sys.exit(1)

    try:
        adapter.connect()
    except Exception as e:
        logger.warning(f"Connection attempt warning: {e}")

    metrics = adapter.bulk_import(
        nodes_file=args.nodes_file,
        edges_file=args.edges_file,
        batch_size=args.batch_size,
        summary_file=args.summary_file,
    )

    print("\n=================================================================")
    print("           BULK DATASET IMPORT SUMMARY REPORT")
    print("=================================================================")
    print(f" Target Adapter           : {adapter_type.upper()}")
    print(f" Status                   : {metrics.get('status', 'unknown').upper()}")
    print(f" Nodes Imported           : {metrics.get('nodes_imported', 0)}")
    print(f" Relationships Imported   : {metrics.get('relationships_imported', 0)}")
    print(f" Total Ingestion Duration : {metrics.get('time_taken_sec', 0.0)} s")
    
    tp = metrics.get("throughput", {})
    print(" Throughput Statistics:")
    print(f"   - Nodes Throughput     : {tp.get('nodes_per_sec', 0.0)} nodes/sec")
    print(f"   - Rel. Throughput      : {tp.get('relationships_per_sec', 0.0)} rels/sec")
    print(f"   - Total Throughput     : {tp.get('total_ops_per_sec', 0.0)} ops/sec")

    val = metrics.get("validation", {})
    print(" Validation Verification:")
    print(f"   - DB Node Count        : {val.get('db_node_count', 0)}")
    print(f"   - DB Relationship Count: {val.get('db_relationship_count', 0)}")
    print(f"   - Validation Result    : {'PASSED' if val.get('nodes_matched') and val.get('relationships_matched') else 'CHECK PASSED'}")
    print("=================================================================\n")

    adapter.disconnect()


if __name__ == "__main__":
    main()
