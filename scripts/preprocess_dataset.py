#!/usr/bin/env python3
"""
CLI script to trigger dataset downloading, preprocessing, deduplication, validation, and summary generation.
"""

import sys
import argparse
from pathlib import Path

# Ensure src/ is on python path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from graph_db_benchmark.logger import setup_logger
from graph_db_benchmark.loaders.preprocessor import WikiVotePreprocessor

logger = setup_logger("preprocess_dataset")


def parse_args() -> argparse.Namespace:
    """Parse command line arguments for dataset preprocessor CLI."""
    parser = argparse.ArgumentParser(
        description="SNAP Wiki-Vote Dataset Preprocessing Utility",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "--download",
        action="store_true",
        help="Download raw dataset file from SNAP web repository if missing locally",
    )
    parser.add_argument(
        "--raw-dir",
        type=str,
        default="datasets/raw",
        help="Directory containing raw dataset files",
    )
    parser.add_argument(
        "--processed-dir",
        type=str,
        default="datasets/processed",
        help="Directory to save processed nodes.csv, relationships.csv, and summary JSON",
    )
    parser.add_argument(
        "--filename",
        type=str,
        default="wiki-Vote.txt.gz",
        help="Raw dataset filename",
    )
    parser.add_argument(
        "--default-label",
        type=str,
        default="User",
        help="Node label assigned in nodes.csv",
    )
    parser.add_argument(
        "--default-rel-type",
        type=str,
        default="VOTES",
        help="Relationship type assigned in relationships.csv",
    )
    return parser.parse_args()


def main() -> None:
    """Main execution flow for dataset preprocessor script."""
    args = parse_args()

    preprocessor = WikiVotePreprocessor(
        raw_dir=args.raw_dir,
        processed_dir=args.processed_dir,
    )

    if args.download:
        preprocessor.download_snap_wiki_vote(filename=args.filename)

    summary = preprocessor.process(
        raw_file_name=args.filename,
        default_label=args.default_label,
        default_rel_type=args.default_rel_type,
    )

    print("\n=================================================================")
    print("           DATASET PREPROCESSING SUMMARY")
    print("=================================================================")
    print(f" Dataset Name             : {summary['dataset_name']}")
    print(f" Raw Source File          : {summary['raw_file']}")
    print(f" Total Lines Read         : {summary['total_lines_read']}")
    print(f" Comment Lines Skipped    : {summary['comment_lines_skipped']}")
    print(f" Unique Nodes Extracted   : {summary['unique_nodes']}")
    print(f" Total Edges Found        : {summary['total_edges_found']}")
    print(f" Duplicate Edges Removed  : {summary['duplicate_edges_removed']}")
    print(f" Final Unique Relationships: {summary['final_relationships']}")
    print(f" Nodes CSV Output         : {summary['nodes_file']}")
    print(f" Relationships CSV Output : {summary['relationships_file']}")
    print(" Validation Status        : PASSED")
    print("=================================================================\n")


if __name__ == "__main__":
    main()
