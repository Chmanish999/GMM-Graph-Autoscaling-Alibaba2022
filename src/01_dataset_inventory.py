import pandas as pd

from config import (
    AUTOSCALING_DATA_FILE,
    SERVICE_GRAPH_FILE,
    LOGS_DIR,
)

LOGS_DIR.mkdir(parents=True, exist_ok=True)

autoscaling_df = pd.read_csv(AUTOSCALING_DATA_FILE)
graph_df = pd.read_csv(SERVICE_GRAPH_FILE)

lines = []
lines.append("DATASET INVENTORY")
lines.append("=" * 60)
lines.append(f"Autoscaling dataset: {AUTOSCALING_DATA_FILE}")
lines.append(f"Shape: {autoscaling_df.shape}")
lines.append("")
lines.append("Autoscaling columns:")
for col in autoscaling_df.columns:
    lines.append(f"- {col}")

lines.append("")
lines.append(f"Service graph dataset: {SERVICE_GRAPH_FILE}")
lines.append(f"Shape: {graph_df.shape}")
lines.append("")
lines.append("Service graph columns:")
for col in graph_df.columns:
    lines.append(f"- {col}")

if "workload_regime" in autoscaling_df.columns:
    lines.append("")
    lines.append("Workload regime distribution:")
    counts = autoscaling_df["workload_regime"].value_counts()
    for regime, count in counts.items():
        percent = (count / len(autoscaling_df)) * 100
        lines.append(f"- {regime}: {count} ({percent:.2f}%)")

output = "\n".join(lines)
print(output)

(LOGS_DIR / "dataset_inventory.txt").write_text(output, encoding="utf-8")
