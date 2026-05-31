# Workflow Description

The research workflow follows a trace-driven autoscaling evaluation process.

## Step 1: Service-Level Dataset Loading

The processed service-level autoscaling dataset is loaded from `data/processed/autoscaling_trace_dataset.csv`.

## Step 2: Service Dependency Graph Loading

The service graph edge dataset is loaded from `data/processed/service_graph_edges_sample.csv`.

## Step 3: Graph Feature Construction

The service dependency graph is cleaned by removing missing or unknown destination services. The following graph-derived features are constructed:

- out-degree
- in-degree
- average edge latency

## Step 4: Feature Merging

Graph-derived features are merged with the service-level autoscaling dataset using `service_id`.

## Step 5: State Representation

Two major state representations are used:

1. Baseline Rule/RL State:
   - CPU utilization
   - memory utilization
   - request rate
   - latency
   - queue length
   - replica count

2. Proposed GMM–Graph State:
   - baseline runtime features
   - GMM–EM workload-regime probabilities
   - graph-derived dependency features

## Step 6: Autoscaling Simulation

A rule-based RL-style simulation environment evaluates scale-down, no-change, and scale-up actions.

## Step 7: Performance Evaluation

The following metrics are computed:

- average reward
- average latency
- average cost
- SLA violation rate
- action distribution

## Step 8: Ablation Study

Five variants are evaluated:

1. HPA/CPU Threshold
2. Baseline Rule/RL State
3. GMM-only State
4. Graph-only State
5. Proposed GMM–Graph State
