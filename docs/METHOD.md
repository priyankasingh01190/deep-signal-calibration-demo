# Method

## 1. Data
UK university students (n≈110) answered a survey on attitudes to AI vs human mental-health
support: ~30 Likert items plus four open-ended questions —

- **Q38** what would make you feel emotionally connected to an AI chatbot
- **Q39** what would make you feel emotionally connected to a human therapist
- **Q40** expectations/concerns about an AI mental-health chatbot
- **Q41** expectations/concerns about a human therapist

Median response length 26–37 words. `prepare_data.py` extracts the four open questions to
long form, drops blanks, and runs a light PII screen (email / URL / long numbers / named
institutions) — no hits.

## 2. The calibration task (main deliverable)
**Goal:** measure whether a change to a coding prompt actually improves agreement with a
human coding frame, on a *fixed* reference set, so improvement is demonstrated rather than
asserted.

- **Reference set:** 30 Q40 responses (the richest/most multi-theme question), `n=30`.
- **Coding frame:** six themes + OTHER (`docs/coding_frame.md`), derived inductively.
- **Gold standard:** each response assigned a single dominant `manual_theme`.
- **Prompt versions:** three files (`prompts/v1..v3`), each a documented step-up in rigour.
- **Scoring:** each prompt is run over every response; the label is compared to `manual_theme`.
- **Metrics:** overall agreement, **Cohen's κ** (chance-corrected), per-theme
  precision/recall/F1, a manual×model confusion matrix, and a **flip report** (responses
  whose label changed across versions).

Why κ *and* agreement: with six unequal classes, raw agreement flatters. κ corrects for
chance and is the honest headline. Macro-F1 is reported too because it exposes rare-class
failures that agreement hides (see the v3 macro-F1 dip).

### Scoring modes
The same prompt files drive two modes. With `ANTHROPIC_API_KEY` set, each response is sent
through the prompt to a Claude model (the real scorer). Without a key, labels are read from
fixture columns stored in the reference set, so every metric reproduces offline. The mode is
recorded in each run manifest (`scoring_mode`).

## 3. The NLP / convergent-validity half
An unsupervised check that knows nothing about the hypotheses:

- **VADER** compound sentiment per response; word and bigram frequencies per question.
- **Paired t-tests** on sentiment, same participants rating AI vs human, for the connection
  pair (Q38 vs Q39) and the concerns pair (Q40 vs Q41). Effect size = Cohen's dz.

This mirrors the dissertation's within-subjects design and tests whether a purely lexical
method independently recovers the same direction of effect. It does (both p<.01), but at a
much smaller magnitude than the validated Likert scales — a documented illustration of a
computational method under-reading a construct.

## 4. Reproducibility / record-keeping
Each `(dataset, prompt)` run writes `results/runs/<dataset>__<version>__<prompthash>/`
containing a manifest that pins: timestamp, git commit, model, scoring mode, prompt file +
sha256, dataset file + sha256, n. Given the same inputs the outputs are identical; given a
different result, the manifest says exactly which input moved.

## 5. Limitations (stated, not hidden)
- The `manual_theme` codes are an **illustrative** reference standard by a single rater, not
  the dissertation's final Framework Analysis codes, and there is no second-rater reliability
  here. The harness is the deliverable; the codes are swappable.
- n=30 for calibration is small; per-theme F1 for rare classes (ACCOUNTABILITY, OTHER) rests
  on ≤3 items and should be read as indicative.
- VADER is lexicon-based and misses negation-in-context, sarcasm, and non-lexical signals
  (e.g. "body language"). It is used as a deliberately blunt convergent check, not a measure.
- Fixture labels in the committed repo were produced by running these prompts through Claude;
  re-run with a key to regenerate from scratch.
