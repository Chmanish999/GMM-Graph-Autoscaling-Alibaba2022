import pandas as pd
import matplotlib.pyplot as plt

from config import (
    AUTOSCALING_DATA_FILE,
    SERVICE_GRAPH_FILE,
    MERGED_DATA_FILE,
    TABLES_DIR,
    FIGURES_DIR,
    LOGS_DIR,
    RAW_FEATURES,
    GMM_FEATURES,
    GRAPH_FEATURES,
)
from autoscaling_core import (
    build_graph_features,
    merge_autoscaling_and_graph_features,
    add_graph_risk,
    time_ordered_train_test_split,
    evaluate_policy,
    hpa_cpu_policy,
    baseline_rule_policy,
    gmm_only_policy,
    graph_only_policy,
    proposed_gmm_graph_ablation_policy,
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

data = add_graph_risk(data)
train_data, test_data = time_ordered_train_test_split(data)

feature_sets = {
    "HPA/CPU Threshold": RAW_FEATURES,
    "Baseline Rule/RL State": RAW_FEATURES,
    "GMM-only State": RAW_FEATURES + GMM_FEATURES,
    "Graph-only State": RAW_FEATURES + GRAPH_FEATURES,
    "Proposed GMM–Graph State": RAW_FEATURES + GMM_FEATURES + GRAPH_FEATURES,
}

policy_map = {
    "HPA/CPU Threshold": hpa_cpu_policy,
    "Baseline Rule/RL State": baseline_rule_policy,
    "GMM-only State": gmm_only_policy,
    "Graph-only State": graph_only_policy,
    "Proposed GMM–Graph State": proposed_gmm_graph_ablation_policy,
}

rows = []
for model_name, features in feature_sets.items():
    result = evaluate_policy(test_data, features, policy_map[model_name])
    rows.append({"Model": model_name, **result})

ablation_results = pd.DataFrame(rows)
ablation_results["sla_violation_percent"] = ablation_results["sla_violation_rate"] * 100

reference = ablation_results[
    ablation_results["Model"] == "Baseline Rule/RL State"
].iloc[0]

summary_rows = []
for _, row in ablation_results.iterrows():
    reward_change = ((row["avg_reward"] - reference["avg_reward"]) / abs(reference["avg_reward"])) * 100
    latency_change = ((reference["avg_latency"] - row["avg_latency"]) / reference["avg_latency"]) * 100
    cost_change = ((reference["avg_cost"] - row["avg_cost"]) / reference["avg_cost"]) * 100
    sla_pp_change = (row["sla_violation_rate"] - reference["sla_violation_rate"]) * 100

    summary_rows.append({
        "Model": row["Model"],
        "Reward Change (%)": reward_change,
        "Latency Reduction (%)": latency_change,
        "Cost Reduction (%)": cost_change,
        "SLA Change (percentage points)": sla_pp_change,
    })

ablation_relative_changes = pd.DataFrame(summary_rows)

ablation_results.to_csv(TABLES_DIR / "table_ablation_results.csv", index=False)
ablation_relative_changes.to_csv(TABLES_DIR / "table_ablation_relative_changes.csv", index=False)

print("Ablation results:")
print(ablation_results)
print("")
print("Relative changes:")
print(ablation_relative_changes)

plot_table = ablation_results.copy()
plot_table["Short Model"] = plot_table["Model"].replace({
    "HPA/CPU Threshold": "HPA",
    "Baseline Rule/RL State": "Baseline",
    "GMM-only State": "GMM-only",
    "Graph-only State": "Graph-only",
    "Proposed GMM–Graph State": "GMM–Graph",
})

def save_bar(metric, ylabel, title, filename, decimals=2):
    plt.figure(figsize=(8, 4.5))
    bars = plt.bar(plot_table["Short Model"], plot_table[metric])
    plt.title(title)
    plt.xlabel("Model")
    plt.ylabel(ylabel)

    for bar in bars:
        value = bar.get_height()
        plt.text(
            bar.get_x() + bar.get_width() / 2,
            value,
            f"{value:.{decimals}f}",
            ha="center",
            va="bottom" if value >= 0 else "top",
            fontsize=9,
        )

    plt.xticks(rotation=15)
    plt.tight_layout()
    plt.savefig(FIGURES_DIR / filename, dpi=300, bbox_inches="tight")
    plt.close()

save_bar("avg_reward", "Average Reward", "Ablation Study: Average Reward", "fig_ablation_average_reward.png", 4)
save_bar("avg_latency", "Average Latency (ms)", "Ablation Study: Average Latency", "fig_ablation_average_latency.png", 2)
save_bar("avg_cost", "Average Cost", "Ablation Study: Average Cost", "fig_ablation_average_cost.png", 4)
save_bar("sla_violation_percent", "SLA Violation Rate (%)", "Ablation Study: SLA Violation Rate", "fig_ablation_sla_violation.png", 2)

action_plot = plot_table.set_index("Short Model")[["scale_down", "no_change", "scale_up"]]
ax = action_plot.plot(kind="bar", figsize=(9, 5))
plt.title("Ablation Study: Autoscaling Action Distribution")
plt.xlabel("Model")
plt.ylabel("Number of Actions")
plt.xticks(rotation=15)
plt.tight_layout()
plt.savefig(FIGURES_DIR / "fig_ablation_action_distribution.png", dpi=300, bbox_inches="tight")
plt.close()

log = f'''Ablation study completed.

Train shape: {train_data.shape}
Test shape: {test_data.shape}

Saved:
{TABLES_DIR / "table_ablation_results.csv"}
{TABLES_DIR / "table_ablation_relative_changes.csv"}
{FIGURES_DIR / "fig_ablation_average_reward.png"}
{FIGURES_DIR / "fig_ablation_average_latency.png"}
{FIGURES_DIR / "fig_ablation_average_cost.png"}
{FIGURES_DIR / "fig_ablation_sla_violation.png"}
{FIGURES_DIR / "fig_ablation_action_distribution.png"}
'''

(LOGS_DIR / "ablation_study_log.txt").write_text(log, encoding="utf-8")
