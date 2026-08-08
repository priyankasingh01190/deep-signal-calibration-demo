"""
evaluate.py
-----------
Compare an LLM prompt version's codes against the manual reference codes.

Produces, for one prompt version:
  - overall agreement + Cohen's kappa
  - per-theme precision / recall / F1 / support
  - a confusion matrix (manual x model)
  - the list of disagreements (for error review)

And, across versions, a flip report: responses whose classification CHANGED between
versions — the "a change we thought was minor moved someone's classification" signal.

Usage:
  from evaluate import evaluate_version, confusion, flip_report
  python src/evaluate.py data/reference/reference_set_real.csv
"""
from __future__ import annotations
import sys
from pathlib import Path
import pandas as pd
from sklearn.metrics import cohen_kappa_score, classification_report, confusion_matrix

THEMES = ["PRIVACY", "ACCURACY", "EMPATHY", "SAFETY", "ACCOUNTABILITY", "ACCESS_BENEFIT", "OTHER"]


def evaluate_version(df: pd.DataFrame, version_col: str, gold_col: str = "manual_theme") -> dict:
    """Metrics for one prompt version against the gold column."""
    gold = df[gold_col].astype(str)
    pred = df[version_col].astype(str)
    agree = (gold == pred)
    labels = sorted(set(gold) | set(pred))
    report = classification_report(
        gold, pred, labels=labels, output_dict=True, zero_division=0
    )
    return {
        "version": version_col,
        "n": len(df),
        "agreement": round(agree.mean(), 4),
        "n_agree": int(agree.sum()),
        "cohen_kappa": round(cohen_kappa_score(gold, pred), 4),
        "macro_f1": round(report["macro avg"]["f1-score"], 4),
        "weighted_f1": round(report["weighted avg"]["f1-score"], 4),
        "per_theme": {
            t: {
                "precision": round(report[t]["precision"], 3),
                "recall": round(report[t]["recall"], 3),
                "f1": round(report[t]["f1-score"], 3),
                "support": int(report[t]["support"]),
            }
            for t in labels
        },
        "disagreements": [
            {"response_id": r["response_id"], "manual": r[gold_col], "pred": r[version_col]}
            for _, r in df[~agree].iterrows()
        ],
    }


def confusion(df: pd.DataFrame, version_col: str, gold_col: str = "manual_theme") -> pd.DataFrame:
    labels = sorted(set(df[gold_col]) | set(df[version_col]))
    cm = confusion_matrix(df[gold_col], df[version_col], labels=labels)
    return pd.DataFrame(cm, index=[f"manual:{l}" for l in labels],
                        columns=[f"pred:{l}" for l in labels])


def flip_report(df: pd.DataFrame, version_cols: list[str], gold_col: str = "manual_theme") -> pd.DataFrame:
    """Responses whose label changed across ANY pair of consecutive versions."""
    rows = []
    for _, r in df.iterrows():
        seq = [r[v] for v in version_cols]
        if len(set(seq)) > 1:
            rows.append({
                "response_id": r["response_id"],
                **{v: r[v] for v in version_cols},
                "manual": r[gold_col],
                "final_correct": r[version_cols[-1]] == r[gold_col],
            })
    return pd.DataFrame(rows)


def _print_summary(df: pd.DataFrame):
    version_cols = [c for c in ["v1_theme", "v2_theme", "v3_theme"] if c in df.columns]
    print(f"Reference set: {len(df)} responses\n")
    print(f"{'version':<10}{'agreement':>11}{'kappa':>9}{'macro_F1':>10}")
    for v in version_cols:
        m = evaluate_version(df, v)
        print(f"{v:<10}{m['agreement']*100:>10.1f}%{m['cohen_kappa']:>9.3f}{m['macro_f1']:>10.3f}")
    print("\nConfusion matrix — best version (" + version_cols[-1] + "):")
    print(confusion(df, version_cols[-1]).to_string())
    flips = flip_report(df, version_cols)
    print(f"\nClassification flips across versions: {len(flips)}")
    if len(flips):
        print(flips.to_string(index=False))


if __name__ == "__main__":
    path = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("data/reference/reference_set_real.csv")
    _print_summary(pd.read_csv(path))
