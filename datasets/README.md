# Graph Benchmark Datasets Directory

This directory stores datasets used by `graph-db-cloud-benchmark` for graph ingestion and query evaluation.

## Directory Structure

```text
datasets/
├── raw/        # Raw, unformatted source data files (e.g. initial CSV, JSON, TSV, or graph dumps)
├── processed/  # Preprocessed, cleaned, and benchmark-ready node and edge CSV files
└── README.md   # Dataset directory overview and format specifications
```

---

## 📌 Usage Guidelines

- **`datasets/raw/`**: Place raw, unmodified graph data files here (e.g., LDBC Social Network, SNAP benchmarks, custom graph exports).
- **`datasets/processed/`**: Place formatted nodes and edges files ready for database ingestion loaders (e.g., `nodes.csv`, `edges.csv`).

### Expected CSV Formats (Standard Schema)

#### Nodes (`processed/nodes.csv`)
```csv
id,label,properties
node_1,Person,{"name": "Alice", "age": 30}
node_2,Person,{"name": "Bob", "age": 25}
```

#### Edges (`processed/edges.csv`)
```csv
source_id,target_id,type,properties
node_1,node_2,KNOWS,{"since": 2020}
```
