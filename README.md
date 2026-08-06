# Graph Database Cloud Benchmark (`graph-db-cloud-benchmark`)

[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![Tests](https://img.shields.io/badge/tests-28%20passed-brightgreen.svg)](https://docs.pytest.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

A production-ready, high-performance Python benchmarking framework designed to evaluate and compare graph database engines—including **CognoDB**, **Neo4j**, **AWS Neptune**, and **Memgraph**—across standardized workloads, concurrent execution models, and realistic datasets.

Built adhering to **Clean Architecture**, **PEP 8**, **strict type annotations**, and **zero-hardcoded-credentials** security practices, this framework provides end-to-end capabilities from raw dataset ingestion and preprocessing to multi-threaded workload generation, real-time metrics collection, and JSON/CSV reporting.

---

## ✨ Features

- **Modular Adapter-Based Architecture**: Extensible database interface supporting pluggable drivers for both embedded and cloud-hosted graph databases.
- **Multi-Database Support**: Native integration with **CognoDB** (embedded) and **Neo4j** (Cypher/Bolt driver), alongside scaffold adapters for **AWS Neptune** (Gremlin) and **Memgraph**.
- **Dataset Preprocessing Pipeline**: Automated downloader and parser that processes raw graph dumps (such as SNAP edge-lists) into standardized node and relationship CSV schemas.
- **Bulk Graph Data Import**: High-performance batch loaders capable of ingesting thousands of nodes and relationships into target graph databases with transaction batching.
- **Concurrent Benchmark Execution**: Multi-threaded workload runner supporting configurable concurrency levels, total iteration bounds, and operation timing.
- **Comprehensive Workload Types**: Built-in query generators for **Point Lookups**, **Multi-hop Traversals** (1-hop, 2-hop neighbor searches), **Aggregations** (degree count, structural metrics), and **Read/Write Mixed Workloads**.
- **Automated Latency & Throughput Metrics**: Real-time performance tracking including operations per second (throughput), minimum, maximum, mean latency, and percentile statistics (p50, p90, p99).
- **JSON & CSV Result Export**: Formatted console summaries with structured JSON and CSV report generation for downstream visualization and CI integration.
- **Structured Logging**: Context-aware logger output supporting file and console outputs with configurable log levels (`INFO`, `DEBUG`, `ERROR`).
- **Environment-Based Configuration**: Dynamic configuration parsing via `python-dotenv` and `pydantic`-style environment validation ensuring secure, decoupled credential management.
- **28 Passing Unit Tests**: Fully covered test suite validating adapters, preprocessors, query generators, bulk importers, runner mechanics, and metrics collectors.

---

## 🗄️ Supported Databases

| Database | Status | Adapter / Driver | Query Interface |
| :--- | :---: | :--- | :--- |
| **CognoDB** | ✅ Fully Implemented | Embedded Graph Engine | Native Python API |
| **Neo4j** | ✅ Fully Implemented | `neo4j` Python Driver | Cypher Query Language |
| **AWS Neptune** | 🚧 Scaffold Ready | Gremlin / HTTP Client | Gremlin / SPARQL |
| **Memgraph** | 🚧 Scaffold Ready | `pymgql` / Bolt Driver | Cypher Query Language |

> [!NOTE]
> Additional graph database engines can be integrated seamlessly by subclassing `BaseGraphAdapter` in `src/graph_db_benchmark/adapters/base.py`.

---

## 🏗️ System Architecture

```text
Dataset (SNAP Wiki-Vote)
           │
           ▼
  Preprocessor Pipeline
           │
           ▼
Formatted CSV Files (Nodes & Relationships)
           │
           ▼
    Bulk Import Engine
           │
           ▼
 Target Graph Database (Neo4j / CognoDB)
           │
           ▼
 Concurrent Benchmark Runner
           │
           ▼
    Metrics Collector
           │
           ▼
 JSON / CSV Performance Reports
```

### Component Responsibilities

1. **Preprocessor Pipeline** (`src/graph_db_benchmark/loaders/` & `scripts/preprocess_dataset.py`): Downloads raw compressed graph edge-lists, cleans metadata headers, extracts unique node IDs, assigns node properties, and formats directed relationships into normalized CSV files.
2. **Bulk Import Engine** (`scripts/run_bulk_import.py` & `src/graph_db_benchmark/loaders/csv_loader.py`): Ingests preprocessed CSV data in batches into the target graph database, constructing graph nodes, labels, and directed edges with optimized index structures.
3. **Database Adapters** (`src/graph_db_benchmark/adapters/`): Encapsulate connection management, session lifecycle, transaction handling, and database-specific query translation behind a unified `BaseGraphAdapter` API.
4. **Benchmark Runner** (`src/graph_db_benchmark/runners/` & `scripts/run_benchmark.py`): Orchestrates concurrent worker threads executing multi-query workload suites (lookups, traversals, aggregations, writes) against the connected target database.
5. **Metrics Collector** (`src/graph_db_benchmark/metrics/collector.py`): Captures nanosecond-precision operation latencies, tracks success/failure rates, computes summary statistics (mean, p50, p90, p99), and measures throughput (ops/sec).
6. **Result Exporter** (`src/graph_db_benchmark/results/`): Serializes benchmark metrics into structured JSON files, CSV summary tables, and formatted ASCII console output.

---

## 📁 Project Architecture & Directory Structure

```text
graph-db-cloud-benchmark/
├── .env.example                # Sample environment configuration template
├── .gitignore                  # Git ignore rules for virtual environments & secrets
├── pyproject.toml              # Build system, pytest, and package metadata
├── requirements.txt            # Dependency definitions
├── README.md                   # Project documentation
├── datasets/                   # Graph benchmark datasets directory
│   ├── raw/                    # Raw source dataset files (e.g., wiki-Vote.txt.gz)
│   ├── processed/              # Formatted node and relationship CSV files
│   └── README.md               # Dataset overview and schemas
├── results_data/               # Output directory for exported benchmark results
├── scripts/
│   ├── setup_env.py            # Environment validation script
│   ├── preprocess_dataset.py   # Dataset download & preprocessing pipeline
│   ├── run_bulk_import.py      # Bulk graph data ingestion script
│   └── run_benchmark.py        # CLI entrypoint for running benchmark suites
├── src/
│   └── graph_db_benchmark/
│       ├── __init__.py         # Package root
│       ├── config.py           # Structured Settings via python-dotenv
│       ├── logger.py           # Structured logging utility
│       ├── adapters/           # Database drivers & cloud adapters
│       │   ├── __init__.py
│       │   ├── base.py         # Abstract Base Class BaseGraphAdapter
│       │   ├── cognodb_adapter.py # CognoDB embedded graph engine adapter
│       │   ├── neo4j_adapter.py   # Neo4j property graph adapter
│       │   ├── neptune_adapter.py # AWS Neptune graph adapter
│       │   └── memgraph_adapter.py# Memgraph graph adapter
│       ├── loaders/            # Dataset ingestion modules
│       │   ├── __init__.py
│       │   ├── base.py         # Abstract Base Class BaseDatasetLoader
│       │   └── csv_loader.py   # High-performance CSV parser & batch loader
│       ├── metrics/            # Performance metrics tracking (latency & throughput)
│       │   ├── __init__.py
│       │   └── collector.py    # Latency tracking (p50, p90, p99, throughput)
│       ├── queries/            # Query template definitions
│       │   ├── __init__.py
│       │   ├── traversal.py    # Multi-hop graph traversal queries
│       │   ├── lookup.py       # Node lookup queries
│       │   ├── aggregation.py  # Degree count & centrality aggregation queries
│       │   └── mixed.py        # Mixed workload query suites
│       ├── results/            # Results serialization (JSON/CSV) & formatting
│       │   ├── __init__.py
│       │   ├── exporter.py     # JSON and CSV result exporter
│       │   └── formatter.py    # Console table output formatter
│       ├── runners/            # Concurrent benchmark execution engine
│       │   ├── __init__.py
│       │   ├── base.py         # Abstract Base Class BaseRunner
│       │   └── benchmark_runner.py # Multi-threaded benchmark execution engine
│       └── workloads/          # Read/Write query workload definitions
│           ├── __init__.py
│           ├── base.py         # Abstract Base Class BaseWorkload
│           └── read_write_workload.py # Read, write, traversal, and aggregation workloads
└── tests/                      # Automated test suite
    ├── __init__.py
    ├── conftest.py             # Test fixtures and database mocks
    ├── test_bulk_import.py     # Ingestion & bulk import unit tests
    ├── test_cognodb_adapter.py # CognoDB adapter unit tests
    ├── test_config.py          # Configuration and environment tests
    ├── test_preprocessor.py    # Dataset preprocessor tests
    ├── test_queries.py         # Graph query generator tests
    └── test_runner.py          # Benchmark runner & metrics tests
```

---

## 📊 Dataset Overview: SNAP Wiki-Vote

The default benchmark suite utilizes the **SNAP Wiki-Vote** graph dataset maintained by the Stanford Network Analysis Platform.

### Dataset Specifications

- **Source**: Stanford Network Analysis Platform (SNAP) — [wiki-Vote.txt.gz](https://snap.stanford.edu/data/wiki-Vote.html)
- **Graph Type**: Directed Graph (Wikipedia Administrator Election Voting Network)
- **Nodes**: `7,115` Wikipedia users
- **Relationships (Edges)**: `103,689` directed votes (`VOTED_FOR`)

### Preprocessing Pipeline

Executing `preprocess_dataset.py` processes raw edge-lists into structured relational CSV schemas:
- `datasets/processed/nodes.csv`: Header `node_id:ID,id:int,:LABEL` (Labels: `User`)
- `datasets/processed/relationships.csv`: Header `:START_ID,:END_ID,:TYPE` (Type: `VOTED_FOR`)

---

## ⚙️ Installation & Setup

Follow these steps to set up the benchmarking framework locally.

### 1. Clone Repository

```bash
git clone https://github.com/your-username/graph-db-cloud-benchmark.git
cd graph-db-cloud-benchmark
```

### 2. Create Virtual Environment

```bash
# On Linux / macOS
python3 -m venv venv
source venv/bin/activate

# On Windows (PowerShell)
python -m venv venv
.\venv\Scripts\Activate.ps1
```

### 3. Install Requirements

Install dependencies in editable mode to allow package imports across scripts:

```bash
pip install -r requirements.txt
pip install -e .
```

### 4. Configure Environment Variables

Copy the template `.env.example` file to `.env` and set your database connection credentials:

```bash
cp .env.example .env
```

Example `.env` configuration:

```env
# Target Database Choice: neo4j | cognodb | neptune | memgraph
GRAPH_DB_ADAPTER=neo4j

# Neo4j Connection Settings
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=password

# CognoDB Connection Settings
COGNODB_PATH=./datasets/cognodb_data

# Benchmark Run Settings
BENCHMARK_CONCURRENCY=5
BENCHMARK_ITERATIONS=20
BENCHMARK_EXPORT_FORMAT=json
```

> [!IMPORTANT]
> Ensure `.env` is populated with valid database endpoints before running benchmarks. Never check `.env` into version control.

### 5. Verify Environment Setup

Run the built-in diagnostic script to verify Python dependencies and configuration parsing:

```bash
python scripts/setup_env.py
```

---

## 🔄 Complete Usage Workflow

The full benchmarking workflow follows a 4-stage pipeline: **Environment Verification** ➔ **Dataset Preprocessing** ➔ **Bulk Data Import** ➔ **Benchmark Execution**.

### Step 1: Environment Verification

Verify environment variables, package dependencies, and directory structures:

```bash
python scripts/setup_env.py
```

### Step 2: Dataset Preprocessing

Download the SNAP Wiki-Vote dataset and generate processed node and relationship CSV files:

```bash
python scripts/preprocess_dataset.py --download --filename wiki-Vote.txt.gz
```

### Step 3: Bulk Data Import

Ingest processed nodes (`7,115`) and relationships (`103,689`) into the target graph database (e.g., Neo4j or CognoDB):

```bash
# Import into Neo4j
python scripts/run_bulk_import.py --adapter neo4j

# Import into CognoDB
python scripts/run_bulk_import.py --adapter cognodb
```

### Step 4: Running Benchmarks

Execute multi-threaded workload evaluations with configurable concurrency and iteration counts:

```bash
# Run benchmark against Neo4j with 5 threads across 20 iterations
python scripts/run_benchmark.py --adapter neo4j --iterations 20 --concurrency 5

# Run benchmark against CognoDB
python scripts/run_benchmark.py --adapter cognodb --iterations 20 --concurrency 5
```

### Step 5: Running Unit Tests

Run the full automated test suite using `pytest`:

```bash
pytest -v
```

---

## 📈 Benchmark Results

Below are benchmark comparison metrics recorded on the **SNAP Wiki-Vote** graph dataset (`7,115` nodes, `103,689` relationships) across 20 query iterations with a concurrency factor of 5:

### Performance Comparison Table

| Metric | CognoDB | Neo4j |
| :--- | :---: | :---: |
| **Total Queries Executed** | `20` | `20` |
| **Successful Queries** | `20` | `20` |
| **Failed Queries** | `0` | `0` |
| **Throughput (ops/sec)** | **`2.88 ops/sec`** | **`22.10 ops/sec`** |
| **Average Latency (ms)** | **`1532.18 ms`** | **`217.34 ms`** |

> [!NOTE]
> **Performance Disclaimer**: Benchmark results depend on underlying host hardware, containerized/cloud deployment environments, database indexing strategies, memory allocation, dataset scale, and active concurrency settings. Neo4j demonstrates significantly higher throughput due to native binary indexes and optimized memory-mapped page caching.

---

## 🧪 Testing

The repository features comprehensive unit test coverage built with `pytest`. Tests cover configuration parsing, preprocessor transformations, query generation, bulk import pipelines, runner concurrency, and metrics collection.

- **Total Automated Unit Tests**: `28`
- **Test Status**: `28 Passed` (100% pass rate)
- **Framework**: `pytest`

Execute unit tests in verbose mode:

```bash
pytest -v
```

Expected output snippet:

```text
==================================== test session starts ====================================
platform win32 -- Python 3.11.7, pytest-7.4.0
collected 28 items

tests\test_bulk_import.py ...                                                        [ 10%]
tests\test_cognodb_adapter.py .......                                                 [ 35%]
tests\test_config.py ...                                                              [ 46%]
tests\test_preprocessor.py ....                                                       [ 60%]
tests\test_queries.py ......                                                          [ 82%]
tests\test_runner.py ....                                                             [100%]

==================================== 28 passed in 1.66s =====================================
```

---

## 📐 Project Design Principles

1. **Clean Architecture**: Strong architectural boundaries separating database drivers, business logic (workloads/runners), dataset loaders, and output exporters.
2. **Adapter Pattern**: Uniform interface (`BaseGraphAdapter`) standardizing database operations (`execute_query`, `bulk_import`, `connect`, `close`) regardless of the underlying database protocol or driver.
3. **Dependency Injection**: Adapters and workload generators are injected into benchmark runners dynamically, enabling unit testing with lightweight mock adapters.
4. **Separation of Concerns**: Modular responsibility distribution—loaders handle CSV parsing, adapters handle driver interaction, metrics collectors track timing, and runners handle multi-threading.
5. **Security First**: Absolute protection of credentials via strict environment variable isolation (`python-dotenv`). Credentials are never hardcoded or logged.
6. **Type Annotations**: Comprehensive Python type hinting across functions and classes (PEP 484) ensuring code safety, IDE autocomplete support, and static analysis compatibility.
7. **Structured Logging**: Uniform logging across all modules using structured formatting with configurable log levels (`INFO`, `DEBUG`, `ERROR`).
8. **Extensibility**: Simple, open-closed design allowing users to add new graph database adapters or workload types without modifying core benchmark execution engines.

---

## 🔮 Future Improvements

- [ ] **Docker Compose Deployment**: Single-command environment orchestration spinning up Neo4j, Memgraph, and benchmark runners simultaneously.
- [ ] **Kubernetes Support**: Helm charts and K8s Job manifests for running automated benchmarks in cloud-native clusters.
- [ ] **Grafana Dashboards**: Real-time Prometheus metrics exporter and Grafana dashboard templates for visual benchmarking telemetry.
- [ ] **Additional Benchmark Workloads**: Support for graph algorithm workloads (PageRank, Shortest Path, Community Detection / Louvain).
- [ ] **Expanded Graph Datasets**: Ingestion support for large-scale graphs (e.g., LDBC Social Network Benchmark, SNAP Twitter follower network).
- [ ] **Cloud Infrastructure Automation**: Terraform modules for auto-provisioning AWS Neptune and Neo4j Aura clusters for cloud benchmarks.
- [ ] **Continuous Benchmarking CI/CD**: Automated GitHub Actions workflow performing regression testing and throughput tracking on every pull request.

---

## 📄 License

This project is open-source software licensed under the [MIT License](LICENSE).
