"""
prepare_data.py
---------------
Turns the raw survey export into a clean, minimal, de-identified set of open-ended
responses. This is the documented, re-runnable version of the manual clean-up that would
otherwise live in someone's head.

Steps:
  1. Read data/raw/survey_raw.csv (git-ignored).
  2. Keep only the 4 open-ended questions (cols 40-43) + the anonymous response id.
  3. Melt to long form: one row per (response_id, question, response).
  4. Drop blanks; flag any response that trips a light PII regex for manual review.
  5. Write data/processed/responses_long.csv (git-ignored).

Outputs a short console report so the cleaning decisions are visible, not implicit.

Usage:  python src/prepare_data.py
"""
from __future__ import annotations
import re
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw" / "survey_raw.csv"
OUT = ROOT / "data" / "processed"
OUT.mkdir(parents=True, exist_ok=True)

QCOLS = {40: "Q38_connected_AI", 41: "Q39_connected_human",
         42: "Q40_concerns_AI", 43: "Q41_concerns_human"}

PII = {
    "email": r"[\w.\-]+@[\w.\-]+",
    "url": r"https?://\S+",
    "long_number": r"\b\d{7,}\b",
    "named_institution": r"\b(university|imperial|ucl|kcl|oxford|cambridge)\b",
}


def main():
    if not RAW.exists():
        raise SystemExit(f"Raw survey not found at {RAW} (git-ignored). Place it there to run.")
    df = pd.read_csv(RAW, encoding="utf-8-sig")
    id_col = df.columns[0]

    long_rows = []
    flags = []
    for idx, key in QCOLS.items():
        col = df.columns[idx]
        for _, r in df[[id_col, col]].dropna().iterrows():
            text = str(r[col]).strip()
            if not text:
                continue
            long_rows.append({"response_id": r[id_col], "question": key, "response": text})
            for name, pat in PII.items():
                if re.search(pat, text, flags=re.I):
                    flags.append({"response_id": r[id_col], "question": key, "pii_type": name})

    long = pd.DataFrame(long_rows)
    long.to_csv(OUT / "responses_long.csv", index=False)
    print(f"+ wrote data/processed/responses_long.csv  ({len(long)} responses)")
    print("  per question:")
    print(long.groupby("question")["response"].count().to_string())
    wc = long["response"].str.split().str.len()
    print(f"  words per response: median={int(wc.median())}, max={int(wc.max())}")
    if flags:
        print(f"\n! {len(flags)} responses tripped the PII screen — review before any external use:")
        print(pd.DataFrame(flags).to_string(index=False))
    else:
        print("\n  PII screen: no hits across email / url / long-number / named-institution.")


if __name__ == "__main__":
    main()
