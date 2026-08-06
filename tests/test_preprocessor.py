"""
Offline unit tests for WikiVotePreprocessor and dataset engineering pipeline.
"""

import gzip
import json
from pathlib import Path
import pytest

from graph_db_benchmark.loaders.preprocessor import WikiVotePreprocessor


@pytest.fixture
def sample_snap_raw_content() -> str:
    """Fixture returning synthetic SNAP raw graph dataset with comments and duplicate edges."""
    return """# Directed graph (wiki-Vote)
# Nodes: 4 Edges: 5
# FromNodeId\tToNodeId
1\t2
2\t3
1\t2
3\t4
4\t1
"""


def test_preprocess_uncompressed_raw_file(tmp_path: Path, sample_snap_raw_content: str):
    """Test preprocessing of uncompressed raw graph file."""
    raw_dir = tmp_path / "raw"
    processed_dir = tmp_path / "processed"

    raw_dir.mkdir()
    raw_file = raw_dir / "wiki-Vote.txt"
    raw_file.write_text(sample_snap_raw_content, encoding="utf-8")

    preprocessor = WikiVotePreprocessor(raw_dir=raw_dir, processed_dir=processed_dir)
    summary = preprocessor.process(raw_file_name="wiki-Vote.txt", default_label="User", default_rel_type="VOTES")

    # Assert processing totals
    assert summary["unique_nodes"] == 4
    assert summary["total_edges_found"] == 5
    assert summary["duplicate_edges_removed"] == 1
    assert summary["final_relationships"] == 4

    # Assert nodes.csv output
    nodes_csv = processed_dir / "nodes.csv"
    assert nodes_csv.exists()
    nodes_lines = [line.strip() for line in nodes_csv.read_text(encoding="utf-8").splitlines() if line.strip()]
    assert nodes_lines[0] == "id,label"
    assert len(nodes_lines) == 5  # header + 4 nodes
    assert "1,User" in nodes_lines
    assert "4,User" in nodes_lines

    # Assert relationships.csv output
    rel_csv = processed_dir / "relationships.csv"
    assert rel_csv.exists()
    rel_lines = [line.strip() for line in rel_csv.read_text(encoding="utf-8").splitlines() if line.strip()]
    assert rel_lines[0] == "source,target,relationship_type"
    assert len(rel_lines) == 5  # header + 4 unique edges
    assert "1,2,VOTES" in rel_lines

    # Assert summary JSON report
    summary_json = processed_dir / "dataset_summary.json"
    assert summary_json.exists()
    summary_data = json.loads(summary_json.read_text(encoding="utf-8"))
    assert summary_data["dataset_name"] == "SNAP Wiki-Vote"
    assert summary_data["unique_nodes"] == 4


def test_preprocess_gzip_raw_file(tmp_path: Path, sample_snap_raw_content: str):
    """Test preprocessing of gzipped raw file."""
    raw_dir = tmp_path / "raw"
    processed_dir = tmp_path / "processed"

    raw_dir.mkdir()
    raw_gz_file = raw_dir / "wiki-Vote.txt.gz"
    with gzip.open(raw_gz_file, "wt", encoding="utf-8") as f:
        f.write(sample_snap_raw_content)

    preprocessor = WikiVotePreprocessor(raw_dir=raw_dir, processed_dir=processed_dir)
    summary = preprocessor.process(raw_file_name="wiki-Vote.txt.gz")

    assert summary["unique_nodes"] == 4
    assert summary["final_relationships"] == 4


def test_validation_failure_on_corrupted_count(tmp_path: Path):
    """Test that validate_processed_files raises ValueError on mismatch."""
    raw_dir = tmp_path / "raw"
    processed_dir = tmp_path / "processed"
    processed_dir.mkdir(parents=True)

    nodes_csv = processed_dir / "nodes.csv"
    nodes_csv.write_text("id,label\n1,User\n2,User\n", encoding="utf-8")

    rel_csv = processed_dir / "relationships.csv"
    rel_csv.write_text("source,target,relationship_type\n1,2,VOTES\n", encoding="utf-8")

    preprocessor = WikiVotePreprocessor(raw_dir=raw_dir, processed_dir=processed_dir)

    with pytest.raises(ValueError) as exc_info:
        preprocessor.validate_processed_files(
            nodes_csv_path=nodes_csv,
            relationships_csv_path=rel_csv,
            expected_node_count=5,  # Mismatch (actual is 2)
            expected_rel_count=1,
        )

    assert "Node count validation failed" in str(exc_info.value)
