"""
Feature engineering for botnet / C2 flow detection.

Takes a DataFrame of network flows and produces per-(src_ip, dst_ip) features
that capture C2 'beaconing' behaviour (temporal regularity, byte ratios, repetition).

Author: Karim EL HAOURATI
"""
from __future__ import annotations
import numpy as np
import pandas as pd


# Expected (configurable) column names in the raw flow CSV
COLS = {
    "src": "src_ip",
    "dst": "dst_ip",
    "port": "dst_port",
    "proto": "proto",
    "duration": "duration",
    "bytes_out": "bytes_out",
    "bytes_in": "bytes_in",
    "packets": "packets",
    "ts": "timestamp",     # epoch seconds or parseable datetime
    "label": "label",
}


def _inter_arrival_stats(timestamps: pd.Series) -> tuple[float, float, float]:
    """Mean, std and coefficient of variation of inter-arrival times.
    A low coefficient of variation = very regular => beaconing."""
    t = np.sort(timestamps.astype("float64").values)
    if len(t) < 3:
        return 0.0, 0.0, 0.0
    deltas = np.diff(t)
    mean = float(np.mean(deltas))
    std = float(np.std(deltas))
    cv = float(std / mean) if mean > 0 else 0.0
    return mean, std, cv


def build_features(df: pd.DataFrame, cols: dict | None = None) -> pd.DataFrame:
    """Aggregate raw flows into per-(src,dst) behavioural features.

    Returns one row per (src_ip, dst_ip) pair with engineered features and,
    if a label column is present, a propagated `label` (1 = botnet, 0 = benign).
    """
    c = {**COLS, **(cols or {})}
    # normalise timestamp to epoch seconds
    if not np.issubdtype(df[c["ts"]].dtype, np.number):
        df = df.copy()
        df[c["ts"]] = pd.to_datetime(df[c["ts"]], errors="coerce").astype("int64") // 10**9

    rows = []
    group_cols = [c["src"], c["dst"]]
    for (src, dst), g in df.groupby(group_cols):
        mean_iat, std_iat, cv_iat = _inter_arrival_stats(g[c["ts"]])
        bytes_out = g[c["bytes_out"]].sum()
        bytes_in = g[c["bytes_in"]].sum()
        feat = {
            "src_ip": src,
            "dst_ip": dst,
            "n_flows": len(g),
            "n_dst_ports": g[c["port"]].nunique(),
            "mean_duration": float(g[c["duration"]].mean()),
            "total_bytes_out": float(bytes_out),
            "total_bytes_in": float(bytes_in),
            "bytes_ratio": float(bytes_out / bytes_in) if bytes_in else 0.0,
            "mean_packets": float(g[c["packets"]].mean()),
            "iat_mean": mean_iat,
            "iat_std": std_iat,
            "iat_cv": cv_iat,                       # <-- key beaconing signal
            "beacon_score": 1.0 / (1.0 + cv_iat),   # high when very regular
        }
        if c["label"] in g.columns:
            # botnet if ANY flow in the pair is malicious
            lab = g[c["label"]].astype(str).str.lower()
            feat["label"] = int(lab.str.contains("bot|malicious|c2|attack").any())
        rows.append(feat)

    return pd.DataFrame(rows)


FEATURE_COLUMNS = [
    "n_flows", "n_dst_ports", "mean_duration", "total_bytes_out",
    "total_bytes_in", "bytes_ratio", "mean_packets",
    "iat_mean", "iat_std", "iat_cv", "beacon_score",
]


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", required=True, help="raw flows CSV")
    ap.add_argument("--out", default="data/features.csv")
    args = ap.parse_args()
    raw = pd.read_csv(args.data)
    feats = build_features(raw)
    feats.to_csv(args.out, index=False)
    print(f"Wrote {len(feats)} feature rows -> {args.out}")
