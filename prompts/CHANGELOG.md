# Prompt CHANGELOG

Every change to a scoring prompt is a version bump with a stated hypothesis and a measured
result on the fixed reference set (`data/reference/reference_set_real.csv`, n=30). Accuracy =
agreement with the reference `manual_theme`. See `results/runs/` for the full manifests.

| Version | File | Change | Hypothesis | Result (agreement vs manual) |
|--------|------|--------|-----------|------------------------------|
| v1 | `v1_zero_shot.txt` | Baseline. Theme **names only**, no definitions, single label. | Establish a floor. | **60.0%** |
| v2 | `v2_definitions.txt` | Added theme **definitions**, an explicit **dominant-theme** rule, and an `OTHER` option. | Definitions will resolve surface-word confusions (e.g. "advice" → ACCURACY). | **86.7%** (+26.7pp) |
| v3 | `v3_few_shot.txt` | Added **ordered tie-break rules**, **3 worked examples**, and a "list markers first" step. | Tie-breaks will fix the benefit-vs-concern and training-vs-privacy confusions v2 still makes. | **93.3%** (+6.6pp) |

## Rationale per bump

### v1 → v2
v1's errors were dominated by **surface-word capture**: any mention of "advice/information"
pulled the label to ACCURACY, and any positive aside ("cheaper", "quick") pulled it to
ACCESS_BENEFIT, regardless of the response's actual emphasis. Adding definitions plus a
dominant-theme instruction was expected to fix most of these. It fixed 8 of 12 v1 errors.

### v2 → v3
v2 still made two *classes* of error:
1. **Benefit-vs-concern** on responses that open with expectations before stating a concern.
2. **Training-vs-privacy** on responses where distrust of data is *caused by* lack of
   professional training (should be ACCOUNTABILITY).
The ordered tie-break rules + worked examples target exactly these. Net: two more errors
resolved, and — importantly — **no regressions except one** (see below), which is the kind
of thing the harness exists to catch.

## Watch items (unexpected shifts flagged by the flip detector)
- **`cmhaix3np...`** flipped PRIVACY (v1) → ACCURACY (v2) → PRIVACY (v3). The v2 definition
  of ACCURACY ("wrong advice") over-captured a response whose *main* concern is a database
  leak. v3's rule 1 ("code the stated main concern") recovered it. A "minor" wording change
  changed a classification — logged, traced, resolved.
- **`cmh4td2r...`** stayed SAFETY through v2 and only corrected to PRIVACY at v3 (respondent
  explicitly says "my main concern … is that personal information may not be confidential").
- **`cmlds5z85...`** (triple-theme: privacy + accuracy + empathy) never resolved to the
  reference label under any version — an honest ceiling case, kept visible rather than hidden.
