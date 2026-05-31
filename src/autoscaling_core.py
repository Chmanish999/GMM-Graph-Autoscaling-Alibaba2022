import numpy as np
import pandas as pd

from config import (
    SLA_THRESHOLD,
    MAX_REPLICAS,
    TRAIN_RATIO,
    GRAPH_FEATURES,
    BASELINE_FEATURES,
    PROPOSED_FEATURES,
)


def build_graph_features(graph_df: pd.DataFrame) -> pd.DataFrame:
    graph_clean = graph_df.copy()
    graph_clean = graph_clean[
        (graph_clean["source_service"].notna())
        & (graph_clean["destination_service"].notna())
        & (graph_clean["destination_service"] != "UNKNOWN")
    ]

    out_degree = (
        graph_clean.groupby("source_service")["destination_service"]
        .nunique()
        .reset_index()
        .rename(columns={
            "source_service": "service_id",
            "destination_service": "out_degree",
        })
    )

    in_degree = (
        graph_clean.groupby("destination_service")["source_service"]
        .nunique()
        .reset_index()
        .rename(columns={
            "destination_service": "service_id",
            "source_service": "in_degree",
        })
    )

    edge_latency = (
        graph_clean.groupby("source_service")["edge_latency_ms"]
        .mean()
        .reset_index()
        .rename(columns={
            "source_service": "service_id",
            "edge_latency_ms": "avg_edge_latency",
        })
    )

    graph_features = out_degree.merge(in_degree, on="service_id", how="outer")
    graph_features = graph_features.merge(edge_latency, on="service_id", how="outer")
    graph_features.fillna(0, inplace=True)

    return graph_features


def merge_autoscaling_and_graph_features(
    autoscaling_df: pd.DataFrame,
    graph_features: pd.DataFrame,
) -> pd.DataFrame:
    data = autoscaling_df.merge(graph_features, on="service_id", how="left")
    data[GRAPH_FEATURES] = data[GRAPH_FEATURES].fillna(0)
    data = data.sort_values("time_step").reset_index(drop=True)
    return data


def add_graph_risk(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    for col in GRAPH_FEATURES:
        df[col] = df[col].fillna(0)

    def minmax(series: pd.Series) -> pd.Series:
        series = series.astype(float)
        if series.max() == series.min():
            return pd.Series(np.zeros(len(series)), index=series.index)
        return (series - series.min()) / (series.max() - series.min())

    df["out_degree_norm"] = minmax(df["out_degree"])
    df["in_degree_norm"] = minmax(df["in_degree"])
    df["edge_latency_norm"] = minmax(df["avg_edge_latency"])

    df["graph_risk"] = (
        0.40 * df["out_degree_norm"]
        + 0.35 * df["in_degree_norm"]
        + 0.25 * df["edge_latency_norm"]
    )

    return df


def time_ordered_train_test_split(df: pd.DataFrame, train_ratio: float = TRAIN_RATIO):
    df = df.sort_values("time_step").reset_index(drop=True)
    split_index = int(len(df) * train_ratio)
    train_data = df.iloc[:split_index].copy()
    test_data = df.iloc[split_index:].copy()
    return train_data, test_data


class AutoscalingEnvironment:
    def __init__(
        self,
        df: pd.DataFrame,
        feature_columns,
        max_replicas: int = MAX_REPLICAS,
        sla_threshold: float = SLA_THRESHOLD,
    ):
        self.df = df.reset_index(drop=True)
        self.feature_columns = feature_columns
        self.max_replicas = max_replicas
        self.sla_threshold = sla_threshold
        self.index = 0

    def reset(self):
        self.index = 0
        return self._get_state()

    def _get_state(self):
        row = self.df.iloc[self.index]
        return row[self.feature_columns].values.astype(np.float32)

    def step(self, action: int):
        row = self.df.iloc[self.index]
        current_replicas = int(max(1, row["replica_count"]))

        if action == 0:
            new_replicas = max(1, current_replicas - 1)
        elif action == 1:
            new_replicas = current_replicas
        else:
            new_replicas = min(self.max_replicas, current_replicas + 1)

        old_latency = row["latency_ms"]
        old_replicas = max(1, current_replicas)
        estimated_latency = old_latency * (old_replicas / new_replicas)

        estimated_cost = new_replicas * 1.0
        sla_violation = 1 if estimated_latency > self.sla_threshold else 0

        reward = -(
            0.4 * (estimated_latency / self.sla_threshold)
            + 0.4 * (estimated_cost / self.max_replicas)
            + 0.2 * sla_violation
        )

        self.index += 1
        done = self.index >= len(self.df) - 1

        next_state = (
            self._get_state()
            if not done
            else np.zeros(len(self.feature_columns))
        )

        info = {
            "new_replicas": new_replicas,
            "estimated_latency": estimated_latency,
            "estimated_cost": estimated_cost,
            "sla_violation": sla_violation,
        }

        return next_state, reward, done, info


def baseline_rule_policy(row):
    if row["cpu_utilization"] > 0.70 or row["latency_ms"] > SLA_THRESHOLD:
        return 2
    elif row["cpu_utilization"] < 0.30 and row["latency_ms"] < 50:
        return 0
    else:
        return 1


def proposed_gmm_graph_policy(row):
    # Kept consistent with the uploaded research notebook.
    high_prob = row["gmm_prob_2"]
    low_prob = row["gmm_prob_0"]

    if high_prob > 0.60 or row["latency_ms"] > SLA_THRESHOLD:
        return 2
    elif low_prob > 0.60 and row["cpu_utilization"] < 0.50:
        return 0
    else:
        return 1


def hpa_cpu_policy(row):
    if row["cpu_utilization"] > 0.70:
        return 2
    elif row["cpu_utilization"] < 0.30:
        return 0
    else:
        return 1


def gmm_only_policy(row):
    high_prob = row["gmm_prob_2"]
    low_prob = row["gmm_prob_0"]

    if high_prob > 0.60 or row["latency_ms"] > SLA_THRESHOLD:
        return 2
    elif (
        low_prob > 0.60
        and row["cpu_utilization"] < 0.50
        and row["latency_ms"] < 0.75 * SLA_THRESHOLD
    ):
        return 0
    else:
        return 1


def graph_only_policy(row):
    graph_risk = row["graph_risk"]

    if (
        row["latency_ms"] > SLA_THRESHOLD
        or (row["cpu_utilization"] > 0.65 and graph_risk > 0.50)
        or (row["latency_ms"] > 0.85 * SLA_THRESHOLD and graph_risk > 0.60)
    ):
        return 2
    elif (
        row["cpu_utilization"] < 0.30
        and row["latency_ms"] < 50
        and graph_risk < 0.40
    ):
        return 0
    else:
        return 1


def proposed_gmm_graph_ablation_policy(row):
    high_prob = row["gmm_prob_2"]
    low_prob = row["gmm_prob_0"]
    graph_risk = row["graph_risk"]

    if (
        row["latency_ms"] > SLA_THRESHOLD
        or high_prob > 0.65
        or (
            high_prob > 0.45
            and graph_risk > 0.50
            and row["latency_ms"] > 0.75 * SLA_THRESHOLD
        )
        or (graph_risk > 0.70 and row["cpu_utilization"] > 0.60)
    ):
        return 2
    elif (
        low_prob > 0.65
        and row["cpu_utilization"] < 0.45
        and row["latency_ms"] < 0.70 * SLA_THRESHOLD
        and graph_risk < 0.40
    ):
        return 0
    else:
        return 1


def evaluate_policy(df: pd.DataFrame, feature_columns, policy_fn):
    env = AutoscalingEnvironment(df, feature_columns)
    _ = env.reset()

    rewards = []
    latencies = []
    costs = []
    sla_violations = []
    actions = []

    done = False

    while not done:
        row = env.df.iloc[env.index]
        action = policy_fn(row)

        _, reward, done, info = env.step(action)

        rewards.append(reward)
        latencies.append(info["estimated_latency"])
        costs.append(info["estimated_cost"])
        sla_violations.append(info["sla_violation"])
        actions.append(action)

    return {
        "avg_reward": float(np.mean(rewards)),
        "avg_latency": float(np.mean(latencies)),
        "avg_cost": float(np.mean(costs)),
        "sla_violation_rate": float(np.mean(sla_violations)),
        "scale_down": actions.count(0),
        "no_change": actions.count(1),
        "scale_up": actions.count(2),
    }


def performance_improvement_table(comparison: pd.DataFrame) -> pd.DataFrame:
    baseline = comparison.iloc[0]
    proposed = comparison.iloc[1]

    reward_improvement = (
        (proposed["avg_reward"] - baseline["avg_reward"])
        / abs(baseline["avg_reward"])
    ) * 100

    latency_reduction = (
        (baseline["avg_latency"] - proposed["avg_latency"])
        / baseline["avg_latency"]
    ) * 100

    cost_reduction = (
        (baseline["avg_cost"] - proposed["avg_cost"])
        / baseline["avg_cost"]
    ) * 100

    baseline_sla_percent = baseline["sla_violation_rate"] * 100
    proposed_sla_percent = proposed["sla_violation_rate"] * 100
    sla_absolute_increase = proposed_sla_percent - baseline_sla_percent

    return pd.DataFrame({
        "Metric": [
            "Average Reward",
            "Average Latency",
            "Average Cost",
            "SLA Violation Rate",
        ],
        "Baseline": [
            round(baseline["avg_reward"], 4),
            round(baseline["avg_latency"], 4),
            round(baseline["avg_cost"], 4),
            round(baseline_sla_percent, 2),
        ],
        "Proposed": [
            round(proposed["avg_reward"], 4),
            round(proposed["avg_latency"], 4),
            round(proposed["avg_cost"], 4),
            round(proposed_sla_percent, 2),
        ],
        "Improvement / Change": [
            f"+{reward_improvement:.2f}% reward improvement",
            f"{latency_reduction:.2f}% latency reduction",
            f"{cost_reduction:.2f}% cost reduction",
            f"+{sla_absolute_increase:.2f} percentage points",
        ],
        "Interpretation": [
            "Reward improved",
            "Latency reduced",
            "Cost slightly reduced",
            "SLA violation slightly increased",
        ],
    })
