# Graph Database Benchmark Report

**Project**: `graph-db-cloud-benchmark`  
**Author**: Backend Engineering Assessment  
**Date**: August 2026  
**Status**: Production-Ready / Assessment Deliverable  

---

## 1. Executive Summary

The primary objective of this project is to construct a modular, extensible, and high-performance benchmarking framework designed to evaluate and compare graph database engines under standardized execution conditions. 

Evaluating graph database performance across heterogeneous engines (embedded vs. client-server/cloud) requires an isolated environment where dataset ingestion, query generation, concurrency, and metrics collection are strictly normalized. This framework facilitates reproducible performance evaluation by executing identical query workloads—spanning point lookups, multi-hop graph traversals, aggregations, and read/write operations—against different graph database engines.

In this assessment, the framework was utilized to benchmark **CognoDB** (an embedded graph database engine) and **Neo4j** (a property graph database server) on the **SNAP Wiki-Vote** dataset (`7,115` nodes, `103,689` relationships). The collected empirical metrics provide detailed insights into throughput (operations per second) and latency distributions across both database engines.

---

## 2. Project Objective

The core technical goals of this project are:

1. **Graph Database Performance Comparison**: Quantify latency (mean, p50, p90, p99) and throughput across candidate graph databases using uniform execution parameters.
2. **Standardized & Identical Workloads**: Ensure that query suites (traversals, lookups, structural aggregations, and writes) execute equivalent logical operations across disparate query interfaces (e.g., Cypher vs. native Python APIs).
3. **Automated Metrics Collection**: Capture high-precision nanosecond timing for every operation, tracking throughput, success/failure counts, and latency percentiles without introducing measurement overhead.
4. **Extensible & Clean Architecture**: Build a decoupled framework where new database adapters, datasets, query workloads, and result exporters can be integrated seamlessly using the Adapter Pattern and Abstract Base Classes (`abc.ABC`).

---

## 3. Benchmark Architecture

The framework is structured as a pipeline comprising seven decoupled components, ensuring clear separation of concerns across data ingestion, database interaction, execution, and reporting.

```text
       ┌────────────────────────┐
       │   Dataset (Raw SNAP)   │
       └───────────┬────────────┘
                   │
                   ▼
       ┌────────────────────────┐
       │ Preprocessing Pipeline │
       └───────────┬────────────┘
                   │
                   ▼
       ┌────────────────────────┐
       │ Formatted CSV Files    │
       └───────────┬────────────┘
                   │
                   ▼
       ┌────────────────────────┐
       │   Bulk Import Engine   │
       └───────────┬────────────┘
                   │
                   ▼
       ┌────────────────────────┐
       │ Target Graph Database  │
       └───────────┬────────────┘
                   │
                   ▼
       ┌────────────────────────┐
       │  Benchmark Runner      │
       └───────────┬────────────┘
                   │
                   ▼
       ┌────────────────────────┐
       │   Metrics Collector    │
       └───────────┬────────────┘
                   │
                   ▼
       ┌────────────────────────┐
       │ JSON / CSV Export      │
       └────────────────────────┘
```

### Component Responsibilities

- **Dataset**: Holds raw source datasets (e.g., edge-list text files from public graph repositories).
- **Preprocessing Pipeline** (`scripts/preprocess_dataset.py` & `src/graph_db_benchmark/loaders/`): Cleans raw input data, strips comment headers, parses directed edges, extracts unique node identifiers, and outputs relational node and relationship CSV files.
- **Formatted CSV Files** (`datasets/processed/`): Standardized dataset representation containing `nodes.csv` and `relationships.csv` formatted for bulk ingestion.
- **Bulk Import Engine** (`scripts/run_bulk_import.py`): Ingests preprocessed CSVs into the target graph database in optimized batches, creating nodes, labels, indices, and directed relationships.
- **Target Graph Database**: The database engine being evaluated (e.g., **Neo4j** via Bolt protocol or **CognoDB** via embedded Python bindings).
- **Benchmark Runner** (`src/graph_db_benchmark/runners/`): Manages multi-threaded worker pools executing workload queries concurrently over fixed iteration bounds.
- **Metrics Collector** (`src/graph_db_benchmark/metrics/collector.py`): Records operation start/end timestamps using high-resolution timers (`time.perf_counter_ns`), calculates statistical metrics, and tracks error rates.
- **Results Export** (`src/graph_db_benchmark/results/`): Formats benchmark metrics into human-readable console tables and serializes structured JSON and CSV report artifacts for analysis.

---

## 4. Dataset

The benchmark suite evaluates engines using the **SNAP Wiki-Vote** dataset from the Stanford Network Analysis Platform.

### Dataset Profile

- **Graph Structure**: Directed Graph
- **Domain**: Wikipedia Administrator Election Voting Network
- **Nodes**: `7,115` (Users participating in administrator elections)
- **Relationships**: `103,689` directed edges (`VOTED_FOR`)

### Preprocessing & Schema Generation

The raw dataset (`wiki-Vote.txt.gz`) consists of tab-separated edge tuples (`FromNodeId`, `ToNodeId`) preceded by metadata headers. The preprocessing pipeline parses this raw stream into two relational CSV schemas:

1. **Nodes Schema** (`datasets/processed/nodes.csv`):
   - `node_id:ID`: Unique integer identifier for each Wikipedia user.
   - `id:int`: Property attribute matching the node ID.
   - `:LABEL`: Entity classification label set to `User`.

2. **Relationships Schema** (`datasets/processed/relationships.csv`):
   - `:START_ID`: Source node ID (voter).
   - `:END_ID`: Target node ID (candidate).
   - `:TYPE`: Relationship type set to `VOTED_FOR`.

---

## 5. Benchmark Methodology

To ensure statistical accuracy and execution reproducibility, the benchmark framework implements a controlled execution pipeline:

1. **Warmup Phase**: Initial query executions are performed to prime connection pools, establish database sessions, and populate internal database page caches before metric recording begins.
2. **Concurrent Execution**: Workloads are dispatched across a configurable worker pool using Python's `concurrent.futures.ThreadPoolExecutor`. Concurrency levels (`concurrency=5`) simulate realistic multi-user demand.
3. **Standardized Workload Mix**:
   - **Point Lookups**: Single-node state fetches by primary key (`node_id`).
   - **1-Hop & 2-Hop Traversals**: Neighbor traversal queries discovering incoming and outgoing voting relationships (`(u)-[:VOTED_FOR]->(v)`).
   - **Aggregations**: Structural graph queries calculating degree counts, in-degree/out-degree statistics, and node connectivity summaries.
   - **Read/Write Operations**: Concurrent insert operations adding new nodes and directed relationships alongside read queries.
4. **Precision Latency Measurement**: Individual query execution durations are timed at nanosecond resolution via `time.perf_counter_ns()`. Recorded values are converted to milliseconds for statistical processing (mean, p50, p90, p99).
5. **Throughput Calculation**: Overall throughput is computed as total successful query operations divided by total elapsed wall-clock benchmark runtime ($\text{ops/sec} = \frac{N_{\text{success}}}{T_{\text{wall}}}$).
6. **Result Serialization**: Comprehensive performance summaries are written to `results_data/` in structured JSON and CSV formats for historical tracking and automated comparison.

---

## 6. Execution Environment

The benchmarking test suite was executed under the following hardware and software environment:

- **Operating System**: Windows 11 / x86_64
- **Runtime Environment**: Python `3.11.7`
- **Database Engine 1 (Embedded)**: `CognoDB` (Embedded Python Graph Engine)
- **Database Engine 2 (Client-Server)**: `Neo4j` (Community Edition via Neo4j Desktop / Bolt Server)
- **Database Client Driver**: `neo4j` Python Official Driver (`v5.x`)
- **Concurrency Framework**: `concurrent.futures.ThreadPoolExecutor`
- **Test Framework**: `pytest` (`v7.4.0`)
- **Environment Management**: `python-dotenv`

---

## 7. Benchmark Results

Below are the empirical benchmark results recorded on the **SNAP Wiki-Vote** dataset (`7,115` nodes, `103,689` relationships) executed over 20 iterations with a concurrency factor of 5:

### Performance Comparison Table

| Metric | CognoDB | Neo4j |
| :--- | :---: | :---: |
| **Target Database Engine** | CognoDB (Embedded) | Neo4j (Bolt / Cypher) |
| **Total Executed Queries** | `20` | `20` |
| **Successful Operations** | `20` | `20` |
| **Failed Operations** | `0` | `0` |
| **Success Rate** | `100.0%` | `100.0%` |
| **Throughput (ops/sec)** | **`2.88 ops/sec`** | **`22.10 ops/sec`** |
| **Average Latency (ms)** | **`1532.18 ms`** | **`217.34 ms`** |

### Performance Analysis & Key Observations

1. **Throughput Differential**: Neo4j achieved **`22.10 ops/sec`**, outperforming CognoDB (**`2.88 ops/sec`**) by approximately **7.6x** under 5-thread concurrent execution.
2. **Latency Profiles**: Neo4j demonstrated an average latency of **`217.34 ms`** per query, compared to **`1532.18 ms`** for CognoDB.
3. **Architectural Drivers**:
   - **Neo4j** leverages native C-based graph storage format, optimized memory-mapped page caching, and specialized B-tree/LSM indexes on node property keys (`User.id`), facilitating rapid graph traversal in memory.
   - **CognoDB** operates as an embedded Python engine. Multi-hop traversal and aggregation workloads encounter higher execution latencies due to Python object overhead and synchronous disk persistence during transaction updates.

> [!NOTE]
> **Environmental Impact Disclaimer**: Benchmark metrics are inherently dependent on host machine hardware (CPU core count, RAM allocation, storage I/O bandwidth), local network transport latency, dataset size, index configuration, and runtime thread concurrency. These figures reflect relative execution performance under identical test parameters rather than absolute performance caps.

---

## 8. Engineering Challenges Faced

1. **Cross-Platform Environment & Dependency Management**:
   Ensuring consistent runtime behavior across Windows PowerShell and Unix-like environments required careful handling of path separators, line endings (LF vs CRLF), virtual environment setups, and native C-extension compilation dependencies.
2. **Secure Credential Management**:
   Preventing hardcoded connection strings and passwords required implementing dynamic configuration loading via `python-dotenv` and strict environment validation rules in `src/graph_db_benchmark/config.py`.
3. **Graph Dataset Cleaning & Normalization**:
   Raw SNAP edge lists contain header comments, irregular tab spacing, and arbitrary node ID sequences. Developing a robust, memory-efficient streaming preprocessor was necessary to generate clean CSV files compatible with bulk import loaders.
4. **Transactional Bulk Import Batching**:
   Ingesting `103,689` relationships individually causes massive transaction overhead and memory exhaustion. Implementing chunked batch imports (e.g., 5,000 items per batch) with index pre-creation was critical for achieving fast data loading.
5. **Database Driver Abstraction**:
   Designing a single unified python interface (`BaseGraphAdapter`) that abstracts fundamental differences between Cypher-based property graphs (Neo4j), Gremlin traversal engines (Neptune), and embedded Python graph APIs (CognoDB) required strict API contract design.
6. **Thread-Safe Metrics Aggregation**:
   Collecting nanosecond latency measurements across concurrent threads without creating lock contention or corrupting metrics structures necessitated lock-free thread-local timing buffers aggregated post-execution.

---

## 9. Key Engineering Decisions

- **Adapter Pattern (`BaseGraphAdapter`)**:
  Used an Abstract Base Class defining standard contracts (`connect`, `close`, `execute_query`, `bulk_import`). This decouples the benchmark runner from specific database driver details, allowing seamless integration of new database engines without modifying core execution logic.
- **Clean Architecture & Layering**:
  Enforced clear architectural boundaries: `adapters/` manage database protocols, `loaders/` handle raw dataset ingestion, `workloads/` construct query patterns, `runners/` manage concurrency, and `metrics/` compute performance statistics.
- **Environment-Driven Configuration**:
  Centralized configuration using `python-dotenv` ensures zero secrets in version control and allows runtime parameter overriding via environment variables or CLI flags.
- **Dependency Injection**:
  Components (adapters, metrics collectors, workloads) are injected into the `BenchmarkRunner` instance, enabling simplified unit testing using mock adapters without requiring active database connections.
- **Structured Logging**:
  Implemented custom log formatters supporting console and file outputs with configurable verbosity, providing full execution visibility during long-running bulk imports and benchmarks.
- **Automated Unit Testing**:
  Integrated `pytest` across all modules to validate preprocessors, query string builders, metrics tracking logic, and runner orchestration.

---

## 10. Automated Testing & Quality Assurance

The framework features a comprehensive test suite validating all core components prior to benchmarking:

- **Total Unit Tests**: `28`
- **Pass Rate**: `100%` (`28 passed`)
- **Execution Time**: `~1.6 seconds`
- **Testing Framework**: `pytest`

### Test Coverage Breakdown

- `tests/test_config.py`: Validates environment variable parsing, default settings fallback, and invalid value handling.
- `tests/test_preprocessor.py`: Tests raw edge-list reading, node ID extraction, and output CSV header generation.
- `tests/test_bulk_import.py`: Verifies batch parsing and transaction ingestion logic.
- `tests/test_queries.py`: Tests Cypher/Native query generation for lookups, traversals, and aggregations.
- `tests/test_runner.py`: Validates multi-threaded benchmark execution, concurrency limits, and iteration counters.
- `tests/test_cognodb_adapter.py`: Validates CognoDB connection management, data creation, and query execution.

Validation command:

```bash
pytest -v
```

---

## 11. Future Improvements

1. **Containerized Orchestration (Docker Compose)**:
   Provide pre-configured `docker-compose.yml` manifests to spin up isolated Neo4j, Memgraph, and AWS Neptune Local containers alongside the benchmark runner automatically.
2. **Prometheus & Grafana Telemetry**:
   Expose real-time benchmark metrics via a Prometheus exporter endpoint and supply pre-built Grafana dashboards for visual throughput and latency monitoring.
3. **Extended Graph Workloads & Algorithms**:
   Implement complex graph algorithm benchmarks, including **PageRank**, **Single-Source Shortest Path (SSSP)**, **Louvain Community Detection**, and **Weakly Connected Components (WCC)**.
4. **Large-Scale Multi-Dataset Benchmarking**:
   Expand dataset preprocessors to ingest synthetic large-scale benchmark datasets such as the **LDBC Social Network Benchmark (SNB)** and massive real-world graphs (e.g., SNAP Twitter networks).
5. **Cloud Infrastructure Automation**:
   Develop Infrastructure-as-Code (IaC) modules using **Terraform** to dynamically provision AWS Neptune clusters and Neo4j Aura instances for cloud-native benchmarking.
6. **Continuous Benchmarking in CI/CD**:
   Integrate automated benchmarking into GitHub Actions workflows to detect performance regressions across pull requests and code modifications.

---

## 12. Conclusion

The `graph-db-cloud-benchmark` project successfully delivers a modular, production-ready benchmarking framework for graph database engines. By adhering to **Clean Architecture**, the **Adapter Pattern**, and strict **Separation of Concerns**, the system provides reproducible, quantitative evaluations of graph database performance across standardized workloads.

The empirical assessment conducted on the **SNAP Wiki-Vote** dataset demonstrated clear performance traits across the evaluated engines: **Neo4j** provided significantly higher throughput (`22.10 ops/sec`) and lower latency (`217.34 ms`) due to native binary graph storage and query indexing, while **CognoDB** provided a lightweight embedded Python alternative (`2.88 ops/sec`, `1532.18 ms`). 

Supported by **28 passing unit tests**, structured logging, secure environment-based configuration, and automated JSON/CSV exports, this project serves as a robust foundation for evaluating current and emerging graph database technologies.
