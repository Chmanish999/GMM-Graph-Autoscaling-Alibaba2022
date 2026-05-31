import pandas as pd
import matplotlib.pyplot as plt

from config import TABLES_DIR, FIGURES_DIR, LOGS_DIR

TABLES_DIR.mkdir(parents=True, exist_ok=True)
FIGURES_DIR.mkdir(parents=True, exist_ok=True)
LOGS_DIR.mkdir(parents=True, exist_ok=True)

# Final manuscript reference values preserved separately.
# Use this script when you want to regenerate paper figures from the final corrected table values.
plot_df = pd.DataFrame({
    "Model": ["Baseline", "Proposed GMM–Graph"],
    "avg_reward": [-0.7578, -0.7448],
    "avg_latency": [86.9681, 84.3534],
    "avg_cost": [5.0866, 5.0446],
    "sla_violation_percent": [4.7244, 5.7743],
})

plot_df.to_csv(TABLES_DIR / "table_manuscript_reference_values.csv", index=False)

def plot_separate_bar(metric, ylabel, title, filename, decimals=2):
    plt.figure(figsize=(6, 4))
    bars = plt.bar(plot_df["Model"], plot_df[metric])

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
            fontsize=10,
        )

    plt.tight_layout()
    plt.savefig(FIGURES_DIR / filename, dpi=600, bbox_inches="tight")
    plt.close()

plot_separate_bar(
    metric="avg_reward",
    ylabel="Average Reward",
    title="Average Reward Comparison",
    filename="fig_average_reward_comparison_reference.png",
    decimals=4,
)

plot_separate_bar(
    metric="avg_latency",
    ylabel="Average Latency (ms)",
    title="Average Latency Comparison",
    filename="fig_average_latency_comparison_reference.png",
    decimals=4,
)

plot_separate_bar(
    metric="avg_cost",
    ylabel="Average Cost",
    title="Average Cost Comparison",
    filename="fig_average_cost_comparison_reference.png",
    decimals=4,
)

plot_separate_bar(
    metric="sla_violation_percent",
    ylabel="SLA Violation Rate (%)",
    title="SLA Violation Rate Comparison",
    filename="fig_sla_violation_comparison_reference.png",
    decimals=2,
)

log = f'''Manuscript reference figures generated.

Saved table:
{TABLES_DIR / "table_manuscript_reference_values.csv"}

Saved figures:
{FIGURES_DIR / "fig_average_reward_comparison_reference.png"}
{FIGURES_DIR / "fig_average_latency_comparison_reference.png"}
{FIGURES_DIR / "fig_average_cost_comparison_reference.png"}
{FIGURES_DIR / "fig_sla_violation_comparison_reference.png"}
'''

print(log)
(LOGS_DIR / "paper_reference_figures_log.txt").write_text(log, encoding="utf-8")
