"""
run_experiment.py
-----------------
Orchestrates a full calibration run over all prompt versions and writes a versioned,
auditable record of exactly what produced each result.

For each prompt version it writes results/runs/<dataset>__<version>__<prompthash>/:
    manifest.json     model, prompt file + sha256, dataset + sha256, mode, timestamp, git commit
    metrics.json      agreement, kappa, macro/weighted F1, per-theme P/R/F1
    disagreements.csv  every response the model got 'wrong' vs the reference
    confusion.csv     manual x pred confusion matrix

Then, across versions, it writes:
    results/summary.md     the headline comparison table (feeds the CHANGELOG)
    results/flips.csv      responses whose classification changed across versions
    results/figures/*.png  agreement bar chart + confusion heatmap of the best version

Usage:
    python src/run_experiment.py                      # real set (git-ignored)
    python src/run_experiment.py --demo               # synthetic set (committed)
"""
from __future__ import annotations
import sys, json, hashlib, subprocess, datetime
from pathlib import Path
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

sys.path.insert(0, str(Path(__file__).resolve().parent))
from code_with_llm import code_responses, prompt_hash, DEFAULT_MODEL
from evaluate import evaluate_version, confusion, flip_report

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results"
RUNS = RESULTS / "runs"
FIGS = RESULTS / "figures"
for d in (RUNS, FIGS):
    d.mkdir(parents=True, exist_ok=True)

PROMPTS = [
    ("v1_theme", ROOT / "prompts" / "v1_zero_shot.txt"),
    ("v2_theme", ROOT / "prompts" / "v2_definitions.txt"),
    ("v3_theme", ROOT / "prompts" / "v3_few_shot.txt"),
]


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()[:12]


def git_commit() -> str:
    try:
        return subprocess.check_output(["git", "rev-parse", "--short", "HEAD"],
                                       cwd=ROOT, stderr=subprocess.DEVNULL).decode().strip()
    except Exception:
        return "not-a-git-repo"


def timestamp() -> str:
    return datetime.datetime.now().isoformat(timespec="seconds")


def run(dataset_path: Path, model: str = DEFAULT_MODEL):
    df = pd.read_csv(dataset_path)
    dataset_name = dataset_path.stem
    ds_hash = sha256(dataset_path)
    commit = git_commit()
    rows = []

    for version_col, prompt_path in PROMPTS:
        labels, mode = code_responses(df, prompt_path, model=model, version_col=version_col)
        scored = df.copy()
        scored[version_col] = labels
        metrics = evaluate_version(scored, version_col)

        run_dir = RUNS / f"{dataset_name}__{version_col}__{sha256(prompt_path)}"
        run_dir.mkdir(exist_ok=True)
        manifest = {
            "timestamp": timestamp(),
            "git_commit": commit,
            "model": model,
            "scoring_mode": mode,
            "prompt_file": str(prompt_path.relative_to(ROOT)),
            "prompt_sha256_12": prompt_hash(prompt_path),
            "dataset_file": str(dataset_path.relative_to(ROOT)) if dataset_path.is_relative_to(ROOT) else str(dataset_path),
            "dataset_sha256_12": ds_hash,
            "n_responses": int(len(df)),
        }
        (run_dir / "manifest.json").write_text(json.dumps(manifest, indent=2))
        (run_dir / "metrics.json").write_text(json.dumps(metrics, indent=2))
        pd.DataFrame(metrics["disagreements"]).to_csv(run_dir / "disagreements.csv", index=False)
        confusion(scored, version_col).to_csv(run_dir / "confusion.csv")

        rows.append({"version": version_col, "prompt": prompt_path.name,
                     "agreement": metrics["agreement"], "kappa": metrics["cohen_kappa"],
                     "macro_f1": metrics["macro_f1"], "mode": mode})
        print(f"[{version_col}] {mode}  agreement={metrics['agreement']*100:.1f}%  "
              f"kappa={metrics['cohen_kappa']:.3f}  macroF1={metrics['macro_f1']:.3f}")

    # cross-version artifacts (dataset-specific filenames so runs don't clobber each other)
    summary = pd.DataFrame(rows)
    _write_summary_md(summary, dataset_name, ds_hash, commit)
    version_cols = [v for v, _ in PROMPTS]
    flips = flip_report(df, version_cols)
    flips.to_csv(RESULTS / f"flips_{dataset_name}.csv", index=False)
    print(f"\n{len(flips)} classification flips across versions -> results/flips_{dataset_name}.csv")

    _make_figures(summary, df, version_cols[-1], dataset_name)
    return summary


def _write_summary_md(summary: pd.DataFrame, dataset_name, ds_hash, commit):
    lines = [f"# Calibration summary — `{dataset_name}` (sha256 {ds_hash}, commit {commit})",
             f"_Generated {timestamp()}_\n",
             "| version | prompt | agreement | Cohen's kappa | macro F1 | mode |",
             "|---------|--------|-----------|---------------|----------|------|"]
    for _, r in summary.iterrows():
        lines.append(f"| {r['version']} | {r['prompt']} | {r['agreement']*100:.1f}% | "
                     f"{r['kappa']:.3f} | {r['macro_f1']:.3f} | {r['mode']} |")
    (RESULTS / f"summary_{dataset_name}.md").write_text("\n".join(lines) + "\n")
    print(f"+ wrote results/summary_{dataset_name}.md")


def _make_figures(summary: pd.DataFrame, df, best_col, dataset_name):
    # agreement bar
    fig, ax = plt.subplots(figsize=(5, 3.2))
    ax.bar(summary["version"], summary["agreement"] * 100, color=["#c44", "#e9a", "#4a7"])
    for i, v in enumerate(summary["agreement"] * 100):
        ax.text(i, v + 1, f"{v:.0f}%", ha="center", fontsize=9)
    ax.set_ylim(0, 100); ax.set_ylabel("Agreement with manual (%)")
    ax.set_title(f"Prompt calibration — {dataset_name}")
    fig.tight_layout(); fig.savefig(FIGS / f"agreement_{dataset_name}.png", dpi=140); plt.close(fig)

    # confusion heatmap (best version)
    cm = confusion(df.assign(**{best_col: df[best_col]}), best_col)
    fig, ax = plt.subplots(figsize=(6, 5))
    im = ax.imshow(cm.values, cmap="Blues")
    ax.set_xticks(range(len(cm.columns))); ax.set_xticklabels([c.split(":")[1] for c in cm.columns], rotation=45, ha="right", fontsize=8)
    ax.set_yticks(range(len(cm.index))); ax.set_yticklabels([c.split(":")[1] for c in cm.index], fontsize=8)
    for i in range(cm.shape[0]):
        for j in range(cm.shape[1]):
            if cm.values[i, j]:
                ax.text(j, i, cm.values[i, j], ha="center", va="center", fontsize=8,
                        color="white" if cm.values[i, j] > cm.values.max() / 2 else "black")
    ax.set_title(f"Confusion — {best_col} ({dataset_name})"); ax.set_xlabel("model"); ax.set_ylabel("manual")
    fig.colorbar(im, fraction=0.046, pad=0.04); fig.tight_layout()
    fig.savefig(FIGS / f"confusion_{dataset_name}.png", dpi=140); plt.close(fig)
    print(f"+ wrote results/figures/agreement_{dataset_name}.png, confusion_{dataset_name}.png")


if __name__ == "__main__":
    demo = "--demo" in sys.argv
    ds = ROOT / "data" / "reference" / ("reference_set_demo.csv" if demo else "reference_set_real.csv")
    if not ds.exists():
        raise SystemExit(f"{ds} not found. Run: python src/build_reference_sets.py")
    print(f"Running calibration on {ds.relative_to(ROOT)}\n")
    run(ds)
