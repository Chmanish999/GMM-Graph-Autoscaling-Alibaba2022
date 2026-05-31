import pandas as pd

from config import (
    AUTOSCALING_DATA_FILE,
    SERVICE_GRAPH_FILE,
    GRAPH_FEATURES_FILE,
    MERGED_DATA_FILE,
    LOGS_DIR,
)
from autoscaling_core import (
    build_graph_features,
    merge_autoscaling_and_graph_features,
)

LOGS_DIR.mkdir(parents=True, exist_ok=True)

autoscaling_df = pd.read_csv(AUTOSCALING_DATA_FILE)
graph_df = pd.read_csv(SERVICE_GRAPH_FILE)

graph_features = build_graph_features(graph_df)
merged_data = merge_autoscaling_and_graph_features(autoscaling_df, graph_features)

graph_features.to_csv(GRAPH_FEATURES_FILE, index=False)
merged_data.to_csv(MERGED_DATA_FILE, index=False)

log = f'''Graph feature construction completed.

Graph features shape: {graph_features.shape}
Merged dataset shape: {merged_data.shape}

Saved graph features:
{GRAPH_FEATURES_FILE}

Saved merged dataset:
{MERGED_DATA_FILE}
'''

print(log)
(LOGS_DIR / "graph_feature_construction_log.txt").write_text(log, encoding="utf-8")
