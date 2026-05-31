# Experimental Setup

## Dataset

The experiment uses a processed subset of Alibaba Microservices Trace v2022.

## Processed Autoscaling Dataset

```text
Rows: 1907
Columns: 17
File: data/processed/autoscaling_trace_dataset.csv
```

## Service Graph Edge Dataset

```text
Rows: 299999
Columns: 5
File: data/processed/service_graph_edges_sample.csv
```

## Train-Test Split

The merged data are sorted by `time_step` and divided into:

```text
Training: 80%
Testing: 20%
```

## Action Space

```text
0 = scale down
1 = no change
2 = scale up
```

## Main Parameters

```text
Maximum replicas: 6
SLA threshold: 85 ms
GMM components: 3
```

## Output Location

Generated outputs are saved under:

```text
results/tables/
results/figures/
results/logs/
```
