# How this project maps to the Research Operations Partner role

The JD describes a role that sits between data science and clinical psychology, owning the
*rigour* behind a transcript-based scoring pipeline while the clinical calls stay with Mark.
This project is a scaled-down, end-to-end instance of exactly that.

| What the role asks for | Where it is in this repo |
|------------------------|--------------------------|
| "Design and run structured tests every time we change a scoring prompt, marker or protocol — using a fixed reference set" | `data/reference/` (fixed set) + `prompts/v1..v3` + `src/run_experiment.py` |
| "Keep a clean, versioned record linking every output to the exact model, prompt, and protocol version" | `results/runs/*/manifest.json` — sha256 of prompt + dataset, model, git commit, timestamp |
| "Analyse which markers and signals are actually driving classifications" | per-theme precision/recall/F1 + confusion matrices in `evaluate.py`; **`marker_importance.py`** surfaces the distinctive lexical markers per theme (weighted log-odds + logistic-regression feature importance) → `results/marker_importance_*.md` |
| "Support the statistical and regression work… feature importance" | `marker_importance.py` (multinomial logistic regression, weighted log-odds) + Cohen's κ + paired t-tests |
| "Track and investigate unexpected shifts… a change we thought minor ends up changing someone's classification" | `flip_report()` → `results/flips_*.csv` + the watch-items in `prompts/CHANGELOG.md` |
| "Support the statistical and regression work… move from expert-judgement-calibrated to data-calibrated" | Cohen's κ against manual codes + paired t-tests / effect sizes in `nlp_analysis.py` |
| "Document reasoning and decisions as they're made, not reconstructed later" | `docs/DECISIONS.md` (dated log) + `prompts/CHANGELOG.md` |
| "Turn working scripts and informal knowledge into something a new team member could pick up" | `README.md` reproduce section; each script has a docstring + `--help`-style header |
| "Flag, not decide — surface with evidence, clinical interpretation stays with the psychologist" | the coding frame is *illustrative* and swappable; the harness measures, it does not adjudicate what a theme *means* |
| Comfort in an early-stage, process-doesn't-exist-yet environment | the whole repo is process built from scratch around a bare set of scripts |

## The one honest gap, stated plainly
The `manual_theme` codes are my own single-rater illustrative frame, not the dissertation's
final Framework Analysis codes, and there's no inter-rater reliability figure. In the real
Deep Signal setting the gold standard would be the clinician's codes and I'd be measuring the
pipeline against *those* — which is the point of the "flag, don't decide" design. Swapping in
real codes is a one-column edit (`manual_theme`) and a re-run.

## Two-line pitch for the application
> I built a versioned prompt-calibration harness on my own dissertation transcripts: a fixed
> reference set, three documented prompt versions (60% → 87% → 93% agreement, κ 0.50 → 0.92),
> confusion-matrix diagnostics, a detector for classifications that silently flip between
> versions, and an aggregate-only data-governance model — plus an unsupervised NLP check that
> independently reproduces the study's quantitative direction. It's the Research Operations
> Partner job in miniature.
