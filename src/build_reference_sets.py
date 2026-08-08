"""
build_reference_sets.py
-----------------------
Builds the coded reference sets used by the calibration harness.

Outputs
  data/reference/reference_set_real.csv   (30 real Q40 responses)      -- GIT-IGNORED
  data/reference/reference_set_demo.csv   (8 synthetic responses)      -- committed

Columns: response_id, response, manual_theme, v1_theme, v2_theme, v3_theme

`manual_theme` is the illustrative reference standard (see docs/coding_frame.md).
`v1/v2/v3_theme` are the labels produced by running prompts/v1..v3 over each response.
For the committed repo these model labels are stored as fixtures so `evaluate.py` runs
with no API key; regenerate them from scratch with `src/code_with_llm.py` + an API key.

Run:  python src/build_reference_sets.py
"""
from pathlib import Path
import csv
import json
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
REAL_SRC = ROOT / "reference_set_30.csv"          # real responses handed over from the NLP chat
OUT_DIR = ROOT / "data" / "reference"
OUT_DIR.mkdir(parents=True, exist_ok=True)

# The real coding (response_id -> [manual, v1, v2, v3]) lives in a GIT-IGNORED sidecar so no
# participant identifiers are committed. Absent it, only the synthetic demo set is built.
REAL_CODES_PATH = OUT_DIR / "real_codes.json"
REAL_CODES = json.loads(REAL_CODES_PATH.read_text()) if REAL_CODES_PATH.exists() else {}

# --- Synthetic demo set (safe to publish; no participant text) -------------------------
# (response_id, response, manual, v1, v2, v3)
DEMO_ROWS = [
    ("demo01", "I just worry my private messages could be leaked or sold on to advertisers.",
     "PRIVACY", "PRIVACY", "PRIVACY", "PRIVACY"),
    ("demo02", "It often gives confident answers that turn out to be wrong or completely made up.",
     "ACCURACY", "ACCURACY", "ACCURACY", "ACCURACY"),
    ("demo03", "A bot can't actually feel anything, so it never truly understands what I'm going through.",
     "EMPATHY", "EMPATHY", "EMPATHY", "EMPATHY"),
    ("demo04", "If someone is in a crisis it might just agree with them and make things worse.",
     "SAFETY", "ACCURACY", "SAFETY", "SAFETY"),
    ("demo05", "These tools have no clinical training and no regulator holding them to account.",
     "ACCOUNTABILITY", "PRIVACY", "ACCOUNTABILITY", "ACCOUNTABILITY"),
    ("demo06", "It's free and available at 3am, which beats a six-month NHS waiting list.",
     "ACCESS_BENEFIT", "ACCESS_BENEFIT", "ACCESS_BENEFIT", "ACCESS_BENEFIT"),
    ("demo07", "It's cheap and always on, but I'd fear it reinforcing a vulnerable person's worst thoughts.",
     "SAFETY", "ACCESS_BENEFIT", "SAFETY", "SAFETY"),
    ("demo08", "My main concern is confidentiality, though I do like that it feels less judgemental.",
     "PRIVACY", "ACCESS_BENEFIT", "PRIVACY", "PRIVACY"),
]

COLUMNS = ["response_id", "response", "manual_theme", "v1_theme", "v2_theme", "v3_theme"]


def build_real():
    if not REAL_SRC.exists():
        print(f"! {REAL_SRC.name} not found — skipping real set (only the demo set will be built).")
        return
    df = pd.read_csv(REAL_SRC)
    rows = []
    missing = []
    for _, r in df.iterrows():
        rid = r["response_id"]
        if rid not in REAL_CODES:
            missing.append(rid)
            continue
        manual, v1, v2, v3 = REAL_CODES[rid]
        rows.append([rid, r["response"], manual, v1, v2, v3])
    out = OUT_DIR / "reference_set_real.csv"
    pd.DataFrame(rows, columns=COLUMNS).to_csv(out, index=False, quoting=csv.QUOTE_MINIMAL)
    print(f"+ wrote {out.relative_to(ROOT)}  ({len(rows)} rows)")
    if missing:
        print(f"  ! {len(missing)} responses had no code and were skipped: {missing}")


def build_demo():
    out = OUT_DIR / "reference_set_demo.csv"
    pd.DataFrame(DEMO_ROWS, columns=COLUMNS).to_csv(out, index=False, quoting=csv.QUOTE_MINIMAL)
    print(f"+ wrote {out.relative_to(ROOT)}  ({len(DEMO_ROWS)} rows)")


if __name__ == "__main__":
    build_real()
    build_demo()
