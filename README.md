# Graph Database Cloud Benchmark (`graph-db-cloud-benchmark`)

A production-ready, modular Python benchmark suite designed to evaluate managed cloud graph databases (e.g., **Neo4j Aura**, **AWS Neptune**, **Memgraph Cloud**).

## 🚀 Overview

`graph-db-cloud-benchmark` provides a extensible scaffold for benchmarking graph database engines across standardized workloads, datasets, and concurrency models. Built adhering to **Clean Architecture**, **PEP 8**, **strict type hints**, and **zero-hardcoded-credentials** security practices.

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
│   ├── raw/                    # Raw source dataset files
│   ├── processed/              # Formatted & benchmark-ready node and edge CSV files
│   └── README.md               # Dataset overview and schemas
├── scripts/
│   ├── run_benchmark.py        # CLI entrypoint for running benchmark suites
│   └── setup_env.py            # Environment validation script
├── src/
│   └── graph_db_benchmark/
│       ├── __init__.py         # Package root
│       ├── config.py           # Structured Settings via python-dotenv
│       ├── logger.py           # Structured logging utility
│       ├── adapters/           # Database drivers & cloud adapters
│       │   ├── __init__.py
│       │   ├── base.py         # Abstract Base Class BaseGraphAdapter
│       │   ├── neo4j_adapter.py
│       │   ├── neptune_adapter.py
│       │   └── memgraph_adapter.py
│       ├── loaders/            # Dataset ingestion modules
│       │   ├── __init__.py
│       │   ├── base.py         # Abstract Base Class BaseDatasetLoader
│       │   └── csv_loader.py
│       ├── metrics/            # Performance metrics tracking (p50, p90, p99)
│       │   ├── __init__.py
│       │   └── collector.py
│       ├── queries/            # Query template definitions
│       │   ├── __init__.py
│       │   ├── traversal.py
│       │   ├── lookup.py
│       │   ├── aggregation.py
│       │   └── mixed.py
│       ├── results/            # Results serialization (JSON/CSV) & formatting
│       │   ├── __init__.py
│       │   ├── exporter.py
│       │   └── formatter.py
│       ├── runners/            # Concurrent benchmark execution engine
│       │   ├── __init__.py
│       │   ├── base.py         # Abstract Base Class BaseRunner
│       │   └── benchmark_runner.py
│       └── workloads/          # Read/Write query workload definitions
│           ├── __init__.py
│           ├── base.py         # Abstract Base Class BaseWorkload
│           └── read_write_workload.py
└── tests/                      # Suite test scaffold
    ├── __init__.py
    ├── conftest.py
    └── test_config.py
```

---

## ⚙️ Installation & Setup

### 1. Prerequisites
- **Python 3.9+**
- Virtual environment support (`venv` or `conda`)

### 2. Virtual Environment Setup
Create and activate a fresh virtual environment:

```bash
# On Linux / macOS
python3 -m venv venv
source venv/bin/activate

# On Windows (PowerShell)
python -m venv venv
.\venv\Scripts\Activate.ps1
```

### 3. Install Dependencies
Install core dependencies in editable mode:

```bash
pip install -r requirements.txt
pip install -e .
```

### 4. Configure Environment Variables
Copy `.env.example` to `.env` and populate your target database connection details:

```bash
cp .env.example .env
```

Ensure credentials are strictly populated in `.env` and **never hardcoded in source files**.

---

## 🧪 Validating Environment Setup

Run the built-in setup validation script to check python dependencies and `.env` parsing:

```bash
python scripts/setup_env.py
```

Run test suite:

```bash
pytest
```

---

## 💻 CLI Usage

Execute the main benchmark CLI:

```bash
python scripts/run_benchmark.py --adapter neo4j --concurrency 10 --iterations 50
```

### Command Line Options

| Argument | Description | Default |
|---|---|---|
| `--adapter` | Target database adapter (`neo4j`, `neptune`, `memgraph`) | Value from `.env` |
| `--concurrency` | Number of concurrent worker threads | Value from `.env` |
| `--iterations` | Total benchmark measure iterations | Value from `.env` |
| `--export` | Output format (`json`, `csv`) | `json` |

---

## 🛡️ Best Practices & Design Principles

- **Clean Architecture & Decoupling**: Database adapters, workloads, dataset loaders, metrics, and runners are strictly isolated behind Python Abstract Base Classes (`abc.ABC`).
- **Security First**: Secrets and connection URIs are dynamically injected via `python-dotenv` and standard OS environment variables.
- **Type Annotations**: All standard functions, methods, and classes use PEP 484 type hints.
- **Logging**: Configurable logging setup across stdout and file handlers.

---

## 📄 License

MIT License. See [LICENSE](LICENSE) for details.
