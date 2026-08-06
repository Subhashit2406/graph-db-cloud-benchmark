"""
Dataset Loaders Module.

Contains loader abstractions, preprocessors, and implementations for reading benchmark graphs.
"""

from graph_db_benchmark.loaders.base import BaseDatasetLoader
from graph_db_benchmark.loaders.csv_loader import CSVDatasetLoader
from graph_db_benchmark.loaders.preprocessor import WikiVotePreprocessor

__all__ = ["BaseDatasetLoader", "CSVDatasetLoader", "WikiVotePreprocessor"]
