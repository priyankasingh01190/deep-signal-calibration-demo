# Data governance

## Position
The raw open-ended responses were collected under GDPR for a specific MSc dissertation, with
participants identified only by anonymous reference IDs. Using that text to build a public,
shareable portfolio project is a **new purpose**, distinct from the research it was consented
for. This note records how that is handled — precisely because judgement about data
governance is central to a psychological-risk screening product.

## Controls in this repository
1. **No raw participant text is committed.** The following are git-ignored:
   - `data/raw/` (the survey export)
   - `data/processed/` (cleaned long-form responses)
   - `data/reference/reference_set_real.csv` (the 30 real responses used for the real run)
   - the loose NLP-session artifacts at the repo root that contain response text or IDs
2. **The committed reference set is synthetic.** `reference_set_demo.csv` contains short
   responses written by hand to exercise the six themes. It carries no participant data, so
   the pipeline runs and every metric reproduces for a reviewer who has never seen the study.
3. **Only aggregate / de-identified outputs are committed.** Metrics, confusion matrices,
   word-frequency lists and effect sizes describe the corpus in aggregate; no committed file
   lets you reconstruct an individual's response.
4. **A PII screen runs at prep time.** `prepare_data.py` flags email addresses, URLs, long
   numbers, and named institutions for manual review before any external use. (Current
   corpus: no hits.)
5. **AI-interface exposure is minimised.** When scoring live, only the individual free-text
   response is sent — never the Likert data, demographics, or IDs — and the real run is not
   required to reproduce the committed results.

## What a reviewer sees vs what stays local
| Artifact | Committed? | Contains participant text? |
|----------|-----------|-----------------------------|
| Code, prompts, coding frame, docs | yes | no |
| `reference_set_demo.csv` (synthetic) | yes | no |
| Metrics, confusion, flips, figures, `nlp_summary.json` | yes | no (aggregate) |
| `reference_set_real.csv`, `data/raw`, `data/processed` | **no** | yes → local only |

## If this were productionised
The same principles scale: a data-processing agreement covering the calibration purpose,
access-controlled storage for transcripts, pseudonymisation before any model call, retention
limits, and an audit trail linking every score to its input version (already implemented here
via run manifests).
