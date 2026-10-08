"""
Train & evaluate the embedding-based jailbreak detector.

Expects data/prompts.csv with columns: text,label  (label: 1 = jailbreak, 0 = benign)

Usage:
    python src/evaluate.py --data data/prompts.csv

Author: Karim EL HAOURATI
"""
from __future__ import annotations
import argparse
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, confusion_matrix, roc_auc_score

from detector import JailbreakDetector


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", required=True, help="CSV with columns text,label")
    ap.add_argument("--out", default="models/jailbreak_detector.joblib")
    ap.add_argument("--test-size", type=float, default=0.25)
    args = ap.parse_args()

    df = pd.read_csv(args.data).dropna(subset=["text", "label"])
    df["label"] = df["label"].astype(int)

    tr, te = train_test_split(
        df, test_size=args.test_size, random_state=42, stratify=df["label"]
    )

    det = JailbreakDetector().fit(tr["text"].tolist(), tr["label"].tolist())

    proba = det.predict_proba(te["text"].tolist())
    pred = [int(p >= 0.5) for p in proba]

    print("=== Classification report ===")
    print(classification_report(te["label"], pred, target_names=["benign", "jailbreak"]))
    print("=== Confusion matrix (rows=true, cols=pred) ===")
    print(confusion_matrix(te["label"], pred))
    try:
        print(f"\nROC-AUC: {roc_auc_score(te['label'], proba):.3f}")
    except ValueError:
        pass

    det.save(args.out)
    print(f"\nSaved detector -> {args.out}")


if __name__ == "__main__":
    main()
