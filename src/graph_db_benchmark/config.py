"""
Configuration management module.

Uses python-dotenv to load environment variables from a .env file and provides
structured, type-safe settings for all modules in the application.
"""

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv

# Automatically load environment variables from .env file if available
dotenv_path = Path(__file__).resolve().parents[2] / ".env"
if dotenv_path.exists():
    load_dotenv(dotenv_path=dotenv_path, override=True)
else:
    load_dotenv(override=True)


@dataclass(frozen=True)
class CognoDBSettings:
    """Settings for CognoDB (Neo4j driver based) Database Connection."""
    uri: str = field(
        default_factory=lambda: os.getenv(
            "COGNODB_URI", os.getenv("NEO4J_URI", "bolt://localhost:7687")
        )
    )
    user: str = field(
        default_factory=lambda: os.getenv(
            "COGNODB_USER", os.getenv("NEO4J_USER", "neo4j")
        )
    )
    password: str = field(
        default_factory=lambda: os.getenv(
            "COGNODB_PASSWORD", os.getenv("NEO4J_PASSWORD", "")
        )
    )
    database: str = field(
        default_factory=lambda: os.getenv(
            "COGNODB_DATABASE", os.getenv("NEO4J_DATABASE", "neo4j")
        )
    )
    max_connection_pool_size: int = field(
        default_factory=lambda: int(os.getenv("COGNODB_MAX_POOL_SIZE", "50"))
    )
    connection_timeout_seconds: float = field(
        default_factory=lambda: float(os.getenv("COGNODB_CONN_TIMEOUT", "30.0"))
    )


@dataclass(frozen=True)
class Neo4jSettings:
    """Settings for Neo4j Database Connection."""
    uri: str = field(default_factory=lambda: os.getenv("NEO4J_URI", "bolt://localhost:7687"))
    user: str = field(default_factory=lambda: os.getenv("NEO4J_USER", "neo4j"))
    password: str = field(default_factory=lambda: os.getenv("NEO4J_PASSWORD", ""))
    database: str = field(default_factory=lambda: os.getenv("NEO4J_DATABASE", "neo4j"))


@dataclass(frozen=True)
class NeptuneSettings:
    """Settings for AWS Neptune Connection."""
    endpoint: str = field(default_factory=lambda: os.getenv("NEPTUNE_ENDPOINT", "localhost"))
    port: int = field(default_factory=lambda: int(os.getenv("NEPTUNE_PORT", "8182")))
    region: str = field(default_factory=lambda: os.getenv("NEPTUNE_REGION", "us-east-1"))
    use_ssl: bool = field(
        default_factory=lambda: os.getenv("NEPTUNE_USE_SSL", "true").lower() == "true"
    )


@dataclass(frozen=True)
class MemgraphSettings:
    """Settings for Memgraph Connection."""
    host: str = field(default_factory=lambda: os.getenv("MEMGRAPH_HOST", "localhost"))
    port: int = field(default_factory=lambda: int(os.getenv("MEMGRAPH_PORT", "7687")))
    user: str = field(default_factory=lambda: os.getenv("MEMGRAPH_USER", "memgraph"))
    password: str = field(default_factory=lambda: os.getenv("MEMGRAPH_PASSWORD", ""))


@dataclass(frozen=True)
class BenchmarkSettings:
    """Settings controlling benchmark execution parameters."""
    target_db_adapter: str = field(
        default_factory=lambda: os.getenv("TARGET_DB_ADAPTER", "cognodb").lower()
    )
    concurrency: int = field(
        default_factory=lambda: int(os.getenv("BENCHMARK_CONCURRENCY", "5"))
    )
    warmup_iterations: int = field(
        default_factory=lambda: int(os.getenv("BENCHMARK_WARMUP_ITERATIONS", "10"))
    )
    measure_iterations: int = field(
        default_factory=lambda: int(os.getenv("BENCHMARK_MEASURE_ITERATIONS", "100"))
    )
    timeout_seconds: float = field(
        default_factory=lambda: float(os.getenv("BENCHMARK_TIMEOUT_SECONDS", "60.0"))
    )
    dataset_nodes_path: str = field(
        default_factory=lambda: os.getenv("DATASET_NODES_PATH", "datasets/processed/nodes.csv")
    )
    dataset_edges_path: str = field(
        default_factory=lambda: os.getenv("DATASET_EDGES_PATH", "datasets/processed/edges.csv")
    )
    results_dir: str = field(
        default_factory=lambda: os.getenv("RESULTS_DIR", "results_data")
    )
    results_export_format: str = field(
        default_factory=lambda: os.getenv("RESULTS_EXPORT_FORMAT", "json")
    )


@dataclass(frozen=True)
class Settings:
    """Global Application Settings."""
    app_env: str = field(default_factory=lambda: os.getenv("APP_ENV", "development"))
    log_level: str = field(default_factory=lambda: os.getenv("LOG_LEVEL", "INFO").upper())
    benchmark: BenchmarkSettings = field(default_factory=BenchmarkSettings)
    cognodb: CognoDBSettings = field(default_factory=CognoDBSettings)
    neo4j: Neo4jSettings = field(default_factory=Neo4jSettings)
    neptune: NeptuneSettings = field(default_factory=NeptuneSettings)
    memgraph: MemgraphSettings = field(default_factory=MemgraphSettings)


def get_settings() -> Settings:
    """
    Factory function returning global application settings populated from environment.

    Returns:
        Settings: Instantiated typed settings hierarchy.
    """
    return Settings()
