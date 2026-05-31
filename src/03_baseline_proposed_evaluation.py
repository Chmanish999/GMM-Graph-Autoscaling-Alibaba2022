import pandas as pd
import matplotlib.pyplot as plt

from config import (
    AUTOSCALING_DATA_FILE,
    SERVICE_GRAPH_FILE,
    MERGED_DATA_FILE,
    TABLES_DIR,
    FIGURES_DIR,
    LOGS_DIR,
    BASELINE_FEATURES,
    PROPOSED_FEATURES,
)
from autoscaling_core import (
    build_graph_features,
    merge_autoscaling_and_graph_features,
    time_ordered_train_test_split,
    evaluate_policy,
    baseline_rule_policy,
    proposed_gmm_graph_policy,
    performance_improvement_table,
)

TABLES_DIR.mkdir(parents=True, exist_ok=True)
FIGURES_DIR.mkdir(parents=True, exist_ok=True)
LOGS_DIR.mkdir(parents=True, exist_ok=True)

if MERGED_DATA_FILE.exists():
    data = pd.read_csv(MERGED_DATA_FILE)
else:
    autoscaling_df = pd.read_csv(AUTOSCALING_DATA_FILE)
    graph_df = pd.read_csv(SERVICE_GRAPH_FILE)
    graph_features = build_graph_features(graph_df)
    data = merge_autoscaling_and_graph_features(autoscaling_df, graph_features)
    data.to_csv(MERGED_DATA_FILE, index=False)

train_data, test_data = time_ordered_train_test_split(data)

rule_results = evaluate_policy(test_data, BASELINE_FEATURES, baseline_rule_policy)
proposed_results = evaluate_policy(test_data, PROPOSED_FEATURES, proposed_gmm_graph_policy)

comparison = pd.DataFrame([
    {"Model": "Baseline Rule/RL State", **rule_results},
    {"Model": "Proposed GMM–Graph State", **proposed_results},
])

comparison["sla_violation_percent"] = comparison["sla_violation_rate"] * 100

improvement = performance_improvement_table(comparison)

comparison.to_csv(TABLES_DIR / "table_baseline_vs_proposed_results.csv", index=False)
improvement.to_csv(TABLES_DIR / "table_performance_improvement_summary.csv", index=False)

print("Baseline vs proposed comparison:")
print(comparison)
print("")
print("Improvement summary:")
print(improvement)

# Save simple action distribution chart
action_df = comparison.set_index("Model")[["scale_down", "no_change", "scale_up"]]
ax = action_df.plot(kind="bar", figsize=(8, 4.5))
plt.title("Autoscaling Action Distribution")
plt.ylabel("Number of Actions")
plt.xticks(rotation=15)
plt.tight_layout()
plt.savefig(FIGURES_DIR / "fig_action_distribution_generated.png", dpi=300, bbox_inches="tight")
plt.close()

log = f'''Baseline vs proposed evaluation completed.

Train shape: {train_data.shape}
Test shape: {test_data.shape}

Saved:
{TABLES_DIR / "table_baseline_vs_proposed_results.csv"}
{TABLES_DIR / "table_performance_improvement_summary.csv"}
{FIGURES_DIR / "fig_action_distribution_generated.png"}
'''

(LOGS_DIR / "baseline_proposed_evaluation_log.txt").write_text(log, encoding="utf-8")
