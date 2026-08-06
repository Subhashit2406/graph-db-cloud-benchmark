"""
Pytest configuration and shared fixtures.
"""

import sys
from pathlib import Path
import pytest

# Add src to path for pytest discovery
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))


@pytest.fixture
def mock_env_vars(monkeypatch):
    """Fixture providing dummy environment variables for tests."""
    monkeypatch.setenv("TARGET_DB_ADAPTER", "neo4j")
    monkeypatch.setenv("NEO4J_URI", "bolt://localhost:7687")
    monkeypatch.setenv("NEO4J_USER", "test_user")
    monkeypatch.setenv("NEO4J_PASSWORD", "test_password")
