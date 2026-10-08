"""
Train & evaluate a botnet/C2 flow classifier (RandomForest baseline).

Usage:
    python src/train.py --data data/flows.csv --label-col label --out models/botnet_rf.joblib

Author: Karim EL HAOURATI
"""
from __future__ import annotations
import argparse
import joblib
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, confusion_matrix

from features import build_features, FEATURE_COLUMNS


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", required=True, help="raw flows CSV (must contain a label column)")
    ap.add_argument("--label-col", default="label")
    ap.add_argument("--out", default="models/botnet_rf.joblib")
    ap.add_argument("--test-size", type=float, default=0.25)
    args = ap.parse_args()

    raw = pd.read_csv(args.data)
    feats = build_features(raw)
    if "label" not in feats.columns:
        raise SystemExit("No label produced — check your dataset's label column.")

    X = feats[FEATURE_COLUMNS].fillna(0.0)
    y = feats["label"].astype(int)

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=args.test_size, random_state=42, stratify=y
    )

    clf = RandomForestClassifier(
        n_estimators=300, class_weight="balanced", n_jobs=-1, random_state=42
    )
    clf.fit(X_train, y_train)

    y_pred = clf.predict(X_test)
    print("=== Classification report ===")
    print(classification_report(y_test, y_pred, target_names=["benign", "botnet"]))
    print("=== Confusion matrix (rows=true, cols=pred) ===")
    print(confusion_matrix(y_test, y_pred))

    print("\n=== Feature importances ===")
    for name, imp in sorted(
        zip(FEATURE_COLUMNS, clf.feature_importances_), key=lambda x: -x[1]
    ):
        print(f"  {name:16s} {imp:.3f}")

    joblib.dump(clf, args.out)
    print(f"\nSaved model -> {args.out}")


if __name__ == "__main__":
    main()
