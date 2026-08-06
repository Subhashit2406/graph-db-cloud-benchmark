#!/usr/bin/env python3
"""
Environment and project setup verification script.
"""

import sys
from pathlib import Path

# Ensure src/ is on python path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from graph_db_benchmark.config import get_settings
from graph_db_benchmark.logger import setup_logger

logger = setup_logger("setup_env")


def mask_secret(secret: str) -> str:
    """Mask secret value for safe console rendering."""
    if not secret:
        return "<EMPTY>"
    return secret[:2] + "********" if len(secret) > 2 else "********"


def main() -> None:
    """Verify python setup, dotenv configuration, and package status."""
    logger.info("Verifying Python Virtual Environment and Project Setup...")

    python_ver = sys.version.split()[0]
    logger.info(f"Python Version: {python_ver}")

    settings = get_settings()
    logger.info(f"App Environment: {settings.app_env}")
    logger.info(f"Target Database Adapter: {settings.benchmark.target_db_adapter}")
    logger.info(f"Benchmark Concurrency: {settings.benchmark.concurrency}")

    logger.info("--------------------------------------------------")
    logger.info("Database Credentials Config Check:")
    logger.info(f"  Neo4j URI      : {settings.neo4j.uri}")
    logger.info(f"  Neo4j User     : {settings.neo4j.user}")
    logger.info(f"  Neo4j Password : {mask_secret(settings.neo4j.password)}")
    logger.info(f"  Neptune Endpoint: {settings.neptune.endpoint}")
    logger.info(f"  Memgraph Host  : {settings.memgraph.host}")
    logger.info("--------------------------------------------------")

    logger.info("Project scaffold verification complete. All configuration modules loaded successfully!")


if __name__ == "__main__":
    main()
