"""
LLM triage of a flagged flow — explains an alert in plain language using a LOCAL
model served by Ollama (no data leaves the machine).

Usage:
    ollama pull llama3.1:8b
    python src/llm_triage.py --model llama3.1:8b

Author: Karim EL HAOURATI
"""
from __future__ import annotations
import argparse
import json
import ollama   # pip install ollama ; talks to local Ollama daemon (localhost:11434)


SYSTEM = (
    "You are a SOC analyst assistant. Given network-flow features for a connection "
    "that a machine-learning model flagged as a potential botnet / C2 channel, explain "
    "in plain language WHY it looks malicious, how confident one should be, and the next "
    "verification steps. Be concise and factual. Do not invent values not provided."
)

# Example alert — replace with a real flagged row from your model's output
EXAMPLE_ALERT = {
    "src_ip": "10.0.0.23",
    "dst_ip": "185.199.108.153",
    "dst_port": 443,
    "n_flows": 288,
    "iat_mean_seconds": 300.4,
    "iat_cv": 0.02,            # extremely regular -> beaconing
    "beacon_score": 0.98,
    "bytes_ratio": 7.9,        # mostly outbound
    "model_confidence": 0.93,
}


def triage(alert: dict, model: str = "llama3.1:8b") -> str:
    prompt = (
        "Flagged connection (JSON):\n"
        + json.dumps(alert, indent=2)
        + "\n\nExplain the verdict and give 3 concrete verification steps."
    )
    resp = ollama.chat(
        model=model,
        messages=[
            {"role": "system", "content": SYSTEM},
            {"role": "user", "content": prompt},
        ],
    )
    return resp["message"]["content"]


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", default="llama3.1:8b")
    ap.add_argument("--alert", help="path to a JSON file describing the flagged flow")
    args = ap.parse_args()

    alert = EXAMPLE_ALERT
    if args.alert:
        with open(args.alert, encoding="utf-8") as f:
            alert = json.load(f)

    print(triage(alert, model=args.model))
