"""
Results Module.

Handles export of benchmark outputs to file storage and console formatting.
"""

from graph_db_benchmark.results.exporter import ResultExporter
from graph_db_benchmark.results.formatter import ResultFormatter

__all__ = ["ResultExporter", "ResultFormatter"]
