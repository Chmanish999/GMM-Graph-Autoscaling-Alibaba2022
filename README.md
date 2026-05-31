GMM–Graph Autoscaling Alibaba2022 Private Research Code Package
. Paper Title
-GMM–EM Enhanced Graph-Aware Autoscaling Evaluation for Container-Based Microservice Cloud Environments-

. Repository Name

`GMM-Graph-Autoscaling-Alibaba2022`

. Programming Language

Python

. Purpose of this Repository

This repository is prepared as a -private research authentication and reproducibility package- for the above manuscript. It is not intended as a public open-source release at this stage. The package is meant to preserve the code, processed datasets, execution workflow, and result-generation files in a structured form so that the work can be verified by the author, editor, or reviewers if required.

. Main Research Workflow Covered

1. Load processed Alibaba Microservices Trace v2022 service-level autoscaling data.
2. Load service dependency graph edge data.
3. Construct graph-derived features such as in-degree, out-degree, and average edge latency.
4. Merge runtime monitoring features, GMM–EM workload-regime probabilities, and graph-derived features.
5. Construct baseline and proposed autoscaling state representations.
6. Run the RL-style autoscaling simulation.
7. Compare baseline Rule/RL state and proposed GMM–Graph state.
8. Run ablation study for HPA/CPU, baseline, GMM-only, graph-only, and GMM–Graph variants.
9. Save tables, figures, and execution logs for reproducibility tracking.

. Uploaded Data Files Preserved in This Package

| File | Location | Shape |
|---|---|---|
| `autoscaling_trace_dataset.csv` | `data/processed/` | 1907 rows × 17 columns |
| `service_graph_edges_sample.csv` | `data/processed/` | 299999 rows × 5 columns |
| `Alibaba_GMM_Graph_RL_Autoscaling_Ablation_Extension.ipynb` | `notebooks/` | original notebook uploaded by the author |

. Autoscaling Dataset Columns

```text
time_step, timestamp, service_id, cpu_utilization, memory_utilization, request_rate, latency_ms, queue_length, replica_count, cost, sla_violation, load_pressure, gmm_cluster, gmm_prob_0, gmm_prob_1, gmm_prob_2, workload_regime
```

. Service Graph Dataset Columns

```text
timestamp, source_service, rpc_type, destination_service, edge_latency_ms
```

. Workload Regime Distribution in Uploaded Dataset

```text
{
  "low_load": 1189,
  "high_load": 636,
  "medium_load": 82
}
```

. Suggested Local Execution Order

From the repository root folder, run:

```bash
python src/01_dataset_inventory.py
python src/02_graph_feature_construction.py
python src/03_baseline_proposed_evaluation.py
python src/04_ablation_study.py
python src/05_generate_paper_figures_reference.py
```

. Important Protection Note

The repository is maintained for private authentication and controlled reproducibility only. The author does not grant permission for reuse, redistribution, modification, or derivative work without prior written permission.

