"""
Dataset Preprocessing Pipeline Module.

Supports downloading and processing the SNAP Wiki-Vote graph dataset.
Extracts unique nodes, deduplicates relationships, generates standardized CSVs
(nodes.csv and relationships.csv), validates record counts, and outputs a JSON summary report.
"""

import gzip
import json
import os
import urllib.request
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple, Union

from graph_db_benchmark.logger import setup_logger

logger = setup_logger(__name__)

SNAP_WIKI_VOTE_URL = "https://snap.stanford.edu/data/wiki-Vote.txt.gz"


class WikiVotePreprocessor:
    """
    Dataset engineering preprocessor for SNAP Wiki-Vote graph data.
    """

    def __init__(
        self,
        raw_dir: Union[str, Path] = "datasets/raw",
        processed_dir: Union[str, Path] = "datasets/processed",
    ) -> None:
        """
        Initialize preprocessor with input and output directory paths.

        Args:
            raw_dir: Directory containing raw dataset files.
            processed_dir: Directory where processed CSVs and summary JSON will be stored.
        """
        self.raw_dir = Path(raw_dir)
        self.processed_dir = Path(processed_dir)

        self.raw_dir.mkdir(parents=True, exist_ok=True)
        self.processed_dir.mkdir(parents=True, exist_ok=True)

    def download_snap_wiki_vote(
        self, url: str = SNAP_WIKI_VOTE_URL, filename: str = "wiki-Vote.txt.gz"
    ) -> Path:
        """
        Download SNAP Wiki-Vote dataset file if not present locally.

        Args:
            url: Dataset source URL.
            filename: Target local filename inside raw_dir.

        Returns:
            Path: Absolute path to local raw file.
        """
        target_path = self.raw_dir / filename
        if target_path.exists():
            logger.info(f"Raw dataset file already exists at '{target_path}'. Skipping download.")
            return target_path

        logger.info(f"Downloading SNAP Wiki-Vote dataset from '{url}' to '{target_path}'...")
        try:
            urllib.request.urlretrieve(url, target_path)
            logger.info("Download completed successfully.")
        except Exception as e:
            logger.error(f"Failed to download dataset from '{url}': {str(e)}")
            raise RuntimeError(f"Could not download dataset from {url}: {str(e)}") from e

        return target_path

    def process(
        self,
        raw_file_name: str = "wiki-Vote.txt.gz",
        default_label: str = "User",
        default_rel_type: str = "VOTES",
    ) -> Dict[str, Any]:
        """
        Process raw dataset file, extract unique nodes/edges, output CSVs and JSON report.

        Args:
            raw_file_name: Name of raw file in raw_dir.
            default_label: Label assigned to processed nodes (default: 'User').
            default_rel_type: Relationship type assigned to edges (default: 'VOTES').

        Returns:
            Dict[str, Any]: Summary stats of processed dataset.
        """
        raw_file_path = self.raw_dir / raw_file_name
        if not raw_file_path.exists():
            # Try uncompressed fallback
            alt_path = self.raw_dir / raw_file_name.replace(".gz", "")
            if alt_path.exists():
                raw_file_path = alt_path
            else:
                raise FileNotFoundError(f"Raw dataset file '{raw_file_path}' does not exist.")

        logger.info(f"Processing raw dataset file: '{raw_file_path}'")

        total_lines_read = 0
        comment_lines_skipped = 0
        total_edges_found = 0

        unique_nodes: Set[str] = set()
        unique_relationships: Set[Tuple[str, str]] = set()

        # Open compressed or uncompressed text file
        is_gz = raw_file_path.suffix.lower() == ".gz"
        open_fn = gzip.open if is_gz else open

        with open_fn(raw_file_path, "rt", encoding="utf-8", errors="replace") as f:
            for line in f:
                total_lines_read += 1
                stripped = line.strip()

                if not stripped or stripped.startswith("#"):
                    comment_lines_skipped += 1
                    continue

                parts = stripped.split()
                if len(parts) < 2:
                    continue

                source_id, target_id = parts[0], parts[1]
                total_edges_found += 1

                unique_nodes.add(source_id)
                unique_nodes.add(target_id)
                unique_relationships.add((source_id, target_id))

        duplicate_edges_removed = total_edges_found - len(unique_relationships)
        logger.info(
            f"Extracted {len(unique_nodes)} unique nodes and {len(unique_relationships)} unique relationships "
            f"({duplicate_edges_removed} duplicates removed)."
        )

        # Write nodes.csv
        nodes_csv_path = self.processed_dir / "nodes.csv"
        sorted_nodes = sorted(unique_nodes, key=lambda x: int(x) if x.isdigit() else x)

        with open(nodes_csv_path, "w", encoding="utf-8", newline="") as f:
            f.write("id,label\n")
            for node_id in sorted_nodes:
                f.write(f"{node_id},{default_label}\n")

        logger.info(f"Saved processed nodes to '{nodes_csv_path}'")

        # Write relationships.csv
        relationships_csv_path = self.processed_dir / "relationships.csv"
        sorted_relationships = sorted(
            unique_relationships,
            key=lambda pair: (int(pair[0]) if pair[0].isdigit() else pair[0], int(pair[1]) if pair[1].isdigit() else pair[1]),
        )

        with open(relationships_csv_path, "w", encoding="utf-8", newline="") as f:
            f.write("source,target,relationship_type\n")
            for src, tgt in sorted_relationships:
                f.write(f"{src},{tgt},{default_rel_type}\n")

        logger.info(f"Saved processed relationships to '{relationships_csv_path}'")

        # Validate generated CSV files
        self.validate_processed_files(
            nodes_csv_path=nodes_csv_path,
            relationships_csv_path=relationships_csv_path,
            expected_node_count=len(unique_nodes),
            expected_rel_count=len(unique_relationships),
        )

        # Generate JSON summary report
        summary = {
            "dataset_name": "SNAP Wiki-Vote",
            "raw_file": raw_file_path.name,
            "total_lines_read": total_lines_read,
            "comment_lines_skipped": comment_lines_skipped,
            "unique_nodes": len(unique_nodes),
            "total_edges_found": total_edges_found,
            "duplicate_edges_removed": duplicate_edges_removed,
            "final_relationships": len(unique_relationships),
            "nodes_file": str(nodes_csv_path),
            "relationships_file": str(relationships_csv_path),
            "processed_at": datetime.utcnow().isoformat() + "Z",
        }

        summary_json_path = self.processed_dir / "dataset_summary.json"
        with open(summary_json_path, "w", encoding="utf-8") as f:
            json.dump(summary, f, indent=2)

        logger.info(f"Generated dataset summary report at '{summary_json_path}'")
        return summary

    def validate_processed_files(
        self,
        nodes_csv_path: Path,
        relationships_csv_path: Path,
        expected_node_count: int,
        expected_rel_count: int,
    ) -> None:
        """
        Validate generated CSV file row counts against expected totals.

        Args:
            nodes_csv_path: Path to nodes.csv.
            relationships_csv_path: Path to relationships.csv.
            expected_node_count: Target number of unique nodes.
            expected_rel_count: Target number of relationships.

        Raises:
            ValueError: If validated counts do not match expected totals.
        """
        with open(nodes_csv_path, "r", encoding="utf-8") as f:
            actual_node_count = sum(1 for line in f if line.strip()) - 1  # Exclude header

        with open(relationships_csv_path, "r", encoding="utf-8") as f:
            actual_rel_count = sum(1 for line in f if line.strip()) - 1  # Exclude header

        if actual_node_count != expected_node_count:
            raise ValueError(
                f"Node count validation failed: expected {expected_node_count}, got {actual_node_count} in {nodes_csv_path}"
            )

        if actual_rel_count != expected_rel_count:
            raise ValueError(
                f"Relationship count validation failed: expected {expected_rel_count}, got {actual_rel_count} in {relationships_csv_path}"
            )

        logger.info("Dataset validation check passed: Node and relationship row counts verified.")
