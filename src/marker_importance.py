"""
marker_importance.py
--------------------
"Which markers and signals are actually driving the model's classifications?"

Two complementary, deliberately-transparent views of what lexical markers separate the
themes assigned by the deployed prompt (v3_theme by default):

1. Weighted log-odds (Monroe, Colaresi & Quinn 2008, "Fightin' Words") with an informative
   Dirichlet prior — for each theme, the tokens most distinctive of that theme vs the rest
   of the corpus. Robust for small samples and easy to read.
2. L2-regularised multinomial logistic regression on binary token features — the top
   positive coefficient per theme, as a model-based cross-check.

Outputs (aggregate, no response text or IDs):
  results/marker_importance_<dataset>.md
  results/figures/markers_<dataset>.png   (top distinctive markers for the largest theme)

Usage:
  python src/marker_importance.py                 # real set (git-ignored)
  python src/marker_importance.py --demo          # synthetic committed set
  python src/marker_importance.py --target manual_theme
"""
from __future__ import annotations
import sys, re
from collections import Counter, defaultdict
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.linear_model import LogisticRegression

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results"
FIGS = RESULTS / "figures"
FIGS.mkdir(parents=True, exist_ok=True)

STOP = "english"
TOKEN = r"(?u)\b[a-zA-Z][a-zA-Z']+\b"


def weighted_log_odds(docs: list[str], labels: list[str], top_k: int = 6, alpha: float = 0.25):
    """Monroe et al. informative-Dirichlet weighted log-odds, per class vs rest."""
    vec = CountVectorizer(stop_words=STOP, token_pattern=TOKEN, min_df=2)
    X = vec.fit_transform(docs).toarray()
    vocab = np.array(vec.get_feature_names_out())
    total = X.sum(axis=0).astype(float)               # corpus counts per token
    a0 = alpha * len(vocab)
    out = {}
    for cls in sorted(set(labels)):
        mask = np.array([l == cls for l in labels])
        y = X[mask].sum(axis=0).astype(float)         # counts in class
        n = X[~mask].sum(axis=0).astype(float)        # counts in rest
        ny, nn = y.sum(), n.sum()
        # log-odds with informative prior (prior = corpus frequency)
        eps = 1e-9
        num = (y + alpha * total)
        den_y = np.clip(ny + a0 - num, eps, None)
        num_n = (n + alpha * total)
        den_n = np.clip(nn + a0 - num_n, eps, None)
        with np.errstate(divide="ignore", invalid="ignore"):
            delta = np.log(num / den_y) - np.log(num_n / den_n)
            var = 1.0 / (y + alpha * total) + 1.0 / (n + alpha * total)
            z = np.nan_to_num(delta / np.sqrt(var))    # z-scored log-odds
        order = np.argsort(z)[::-1][:top_k]
        out[cls] = [(vocab[i], round(float(z[i]), 2)) for i in order if z[i] > 0]
    return out


def logreg_importance(docs: list[str], labels: list[str], top_k: int = 6):
    vec = CountVectorizer(stop_words=STOP, token_pattern=TOKEN, min_df=2, binary=True)
    X = vec.fit_transform(docs)
    vocab = np.array(vec.get_feature_names_out())
    clf = LogisticRegression(penalty="l2", C=1.0, max_iter=2000)
    clf.fit(X, labels)
    out = {}
    if len(clf.classes_) == 2:                        # binary -> single coef row
        coefs = {clf.classes_[1]: clf.coef_[0], clf.classes_[0]: -clf.coef_[0]}
    else:
        coefs = {c: clf.coef_[i] for i, c in enumerate(clf.classes_)}
    for c, w in coefs.items():
        order = np.argsort(w)[::-1][:top_k]
        out[c] = [(vocab[i], round(float(w[i]), 2)) for i in order if w[i] > 0]
    return out


def main():
    demo = "--demo" in sys.argv
    target = "manual_theme" if "manual_theme" in sys.argv else "v3_theme"
    if "--target" in sys.argv:
        target = sys.argv[sys.argv.index("--target") + 1]
    name = "reference_set_demo" if demo else "reference_set_real"
    ds = ROOT / "data" / "reference" / f"{name}.csv"
    if not ds.exists():
        raise SystemExit(f"{ds} not found. Run: python src/build_reference_sets.py")

    df = pd.read_csv(ds)
    docs, labels = df["response"].astype(str).tolist(), df[target].astype(str).tolist()
    lo = weighted_log_odds(docs, labels)
    lr = logreg_importance(docs, labels)

    lines = [f"# Marker importance — `{name}` (target: `{target}`, n={len(df)})",
             "",
             "Which lexical markers most distinguish each theme the pipeline assigns. Small-n "
             "diagnostic — read as indicative, not confirmatory.\n",
             "## Weighted log-odds (distinctive markers per theme)",
             "| theme | top markers (z-scored log-odds) |",
             "|-------|----------------------------------|"]
    for cls, toks in lo.items():
        lines.append(f"| {cls} | " + (", ".join(f"{w} ({s})" for w, s in toks) or "—") + " |")
    lines += ["", "## Logistic-regression importance (top positive coefficients)",
              "| theme | top markers (coef) |", "|-------|--------------------|"]
    for cls, toks in lr.items():
        lines.append(f"| {cls} | " + (", ".join(f"{w} ({s})" for w, s in toks) or "—") + " |")

    out_md = RESULTS / f"marker_importance_{name}.md"
    out_md.write_text("\n".join(lines) + "\n")
    print(f"+ wrote {out_md.relative_to(ROOT)}")

    # figure: largest theme's distinctive markers
    biggest = Counter(labels).most_common(1)[0][0]
    toks = lo.get(biggest, [])
    if toks:
        words, scores = zip(*toks)
        fig, ax = plt.subplots(figsize=(5, 3.2))
        ax.barh(list(words)[::-1], list(scores)[::-1], color="#2E4756")
        ax.set_xlabel("weighted log-odds (z)")
        ax.set_title(f"Markers driving '{biggest}' — {name}")
        fig.tight_layout(); fig.savefig(FIGS / f"markers_{name}.png", dpi=140); plt.close(fig)
        print(f"+ wrote results/figures/markers_{name}.png")

    print(f"\nTop distinctive markers by theme (target={target}):")
    for cls, tk in lo.items():
        print(f"  {cls:<15} {', '.join(w for w, _ in tk) if tk else '—'}")


if __name__ == "__main__":
    main()
