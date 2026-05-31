from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]

DATA_DIR = ROOT_DIR / "data"
PROCESSED_DATA_DIR = DATA_DIR / "processed"
RESULTS_DIR = ROOT_DIR / "results"
TABLES_DIR = RESULTS_DIR / "tables"
FIGURES_DIR = RESULTS_DIR / "figures"
LOGS_DIR = RESULTS_DIR / "logs"

AUTOSCALING_DATA_FILE = PROCESSED_DATA_DIR / "autoscaling_trace_dataset.csv"
SERVICE_GRAPH_FILE = PROCESSED_DATA_DIR / "service_graph_edges_sample.csv"

GRAPH_FEATURES_FILE = PROCESSED_DATA_DIR / "graph_features.csv"
MERGED_DATA_FILE = PROCESSED_DATA_DIR / "final_merged_autoscaling_graph_dataset.csv"

SLA_THRESHOLD = 85
MAX_REPLICAS = 6
TRAIN_RATIO = 0.80

RAW_FEATURES = [
    "cpu_utilization",
    "memory_utilization",
    "request_rate",
    "latency_ms",
    "queue_length",
    "replica_count",
]

GMM_FEATURES = [
    "gmm_prob_0",
    "gmm_prob_1",
    "gmm_prob_2",
]

GRAPH_FEATURES = [
    "out_degree",
    "in_degree",
    "avg_edge_latency",
]

BASELINE_FEATURES = RAW_FEATURES
PROPOSED_FEATURES = RAW_FEATURES + GMM_FEATURES + GRAPH_FEATURES
