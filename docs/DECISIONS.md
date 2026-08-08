# Decision log

Decisions recorded as they were made, not reconstructed afterwards. Newest first.

### D-008 — Report macro-F1 alongside agreement, even though it makes v3 look worse
v3 improves agreement (86.7→93.3%) and κ (0.83→0.92) but its macro-F1 *drops* (0.866→0.796)
because one ACCURACY response flips to OTHER and rare classes are tiny. Kept all three
metrics visible rather than reporting only the flattering one — the divergence is itself the
finding a calibration role should catch.

### D-007 — Dataset-specific result filenames
`summary.md`/`flips.csv` were being overwritten when the demo run followed the real run.
Switched to `summary_<dataset>.md` / `flips_<dataset>.csv` so real and demo runs coexist.

### D-006 — Manifest pins sha256 of prompt AND dataset
"Which model+prompt+protocol produced this output" is the core record-keeping requirement.
Every run writes a manifest with sha256 of both the prompt file and the dataset, plus the git
commit, so any historical result is fully attributable.

### D-005 — Flip detector as a first-class output
The JD calls out tracing "a change we thought was minor that ends up changing someone's
classification." Implemented `flip_report()` to list every response whose label changed
across versions and whether the final version landed on the reference label. 14 flips on the
real set; two never resolved (logged in the CHANGELOG watch-items).

### D-004 — Three prompt versions designed to isolate causes, not just "get better"
v1→v2 tests *definitions*; v2→v3 tests *tie-break rules + few-shot*. Each bump changes one
class of thing so the metric delta is attributable to a cause, mirroring "say what changed
and why."

### D-003 — Single dominant-theme coding, not multi-label
Responses are frequently multi-theme. Multi-label would dilute the signal and make agreement
ill-defined. Chose single dominant theme with an explicit decision rule; the residual
ambiguity is what makes the prompt versions separable.

### D-002 — Public repo uses synthetic exemplars; real data stays local
Participant free text was collected under GDPR for the dissertation. Committing it to a
public repo is a new purpose. Decision: synthetic committed reference set + git-ignored real
data + aggregate-only committed outputs. See DATA_GOVERNANCE.md. (This constraint is treated
as a feature to demonstrate, not an obstacle.)

### D-001 — Reuse the completed NLP artifacts rather than redo them
The earlier session had already produced sentiment + frequency output. Rebuilt it as a
re-runnable script (`nlp_analysis.py`) that regenerates and *verifies* those numbers (they
matched to 3dp), then extended it with the paired convergent-validity tests that were missing.
