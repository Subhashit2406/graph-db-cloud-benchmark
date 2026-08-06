"""
Query Workloads Module.

Contains workload definitions and query templates for benchmarking operations.
"""

from graph_db_benchmark.workloads.base import BaseWorkload, QueryItem
from graph_db_benchmark.workloads.read_write_workload import ReadWriteWorkload

__all__ = ["BaseWorkload", "QueryItem", "ReadWriteWorkload"]
