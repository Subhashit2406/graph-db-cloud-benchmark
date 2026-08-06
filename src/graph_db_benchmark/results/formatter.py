"""
Console formatting utility for rendering benchmark summaries.
"""

from typing import List, Dict, Any
from graph_db_benchmark.metrics.collector import BenchmarkResultSummary


class ResultFormatter:
    """
    Formats benchmark results into readable summary text reports.
    """

    @staticmethod
    def format_summary_text(summary: BenchmarkResultSummary) -> str:
        """
        Format metrics summary as clean multiline plain text.

        Args:
            summary: Result summary metrics.

        Returns:
            str: Formatted string report.
        """
        d = summary.to_dict()
        lat = d["latencies_ms"]

        report_lines = [
            "=================================================================",
            f"          GRAPH DB BENCHMARK SUMMARY ({summary.adapter_name.upper()})",
            "=================================================================",
            f" Total Queries Executed : {d['total_queries']}",
            f" Successful Queries     : {d['successful_queries']}",
            f" Failed Queries         : {d['failed_queries']}",
            f" Total Duration (sec)   : {d['total_duration_sec']} s",
            f" Throughput             : {d['throughput_ops_sec']} ops/sec",
            "-----------------------------------------------------------------",
            " Latency Statistics:",
            f"   - p50 (Median)       : {lat['p50']} ms",
            f"   - p90                : {lat['p90']} ms",
            f"   - p95                : {lat['p95']} ms",
            f"   - p99                : {lat['p99']} ms",
            f"   - Min / Max          : {lat['min']} ms / {lat['max']} ms",
            f"   - Mean (Average)     : {lat['avg']} ms",
            f"   - Std Deviation      : {lat['std_dev']} ms",
            "=================================================================",
        ]
        return "\n".join(report_lines)
