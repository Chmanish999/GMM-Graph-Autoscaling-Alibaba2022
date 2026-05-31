# Data Folder Description

This folder contains data files used for the private reproducibility package.

## Processed Data

### 1. autoscaling_trace_dataset.csv

Location:

```text
data/processed/autoscaling_trace_dataset.csv
```

Shape:

```text
1907 rows × 17 columns
```

This file contains service-level autoscaling features, including runtime monitoring features, replica count, cost, SLA violation, GMM cluster information, GMM probability values, and workload-regime labels.

### 2. service_graph_edges_sample.csv

Location:

```text
data/processed/service_graph_edges_sample.csv
```

Shape:

```text
299999 rows × 5 columns
```

This file contains service dependency graph edge records, including source service, destination service, RPC type, timestamp, and edge latency.

## Raw Data

The original Alibaba Microservices Trace v2022 raw files should not be uploaded into a public repository. If required, they may be kept locally under:

```text
data/raw/
```

## Sample Data

Small synthetic or anonymized sample files may be placed under:

```text
data/sample/
```

## Data Sharing Recommendation

The full processed dataset may be shared through IEEE DataPort or another controlled research data repository. The code repository should preferably contain either controlled-access data or sample data only, depending on the journal policy.
