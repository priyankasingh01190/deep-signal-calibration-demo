"""
nlp_analysis.py
---------------
The unsupervised, hypothesis-blind half of the project: VADER sentiment + word/bigram
frequency on the four open-ended questions, plus the paired convergent-validity tests.

This regenerates (and verifies) the artifacts the earlier NLP session produced, and adds
the paired t-tests that mirror the dissertation's within-subjects design:
  * emotional connection: AI (Q38) vs human (Q39)
  * expectations/concerns:  AI (Q40) vs human (Q41)

Outputs:
  results/nlp_summary.json          (per-question freq + sentiment)
  results/convergent_validity.json  (paired t-tests, Cohen's dz)

Reads the raw survey from data/raw/survey_raw.csv (git-ignored). Aggregates only —
no raw response text is written to results/.

Usage:  python src/nlp_analysis.py
"""
from __future__ import annotations
import json
import re
from collections import Counter
from pathlib import Path
import numpy as np
import pandas as pd
from scipy import stats
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw" / "survey_raw.csv"
OUT = ROOT / "results"
OUT.mkdir(exist_ok=True)

# column index -> short question key
QCOLS = {40: "Q38_connected_AI", 41: "Q39_connected_human",
         42: "Q40_concerns_AI", 43: "Q41_concerns_human"}

STOP = set("""a an and are as at be been but by for from had has have i if in into is it its
me my no not of on or our so that the their them then there these they this to too us was we
were what when which who will with would you your can could do does dont don't im it's you're""".split())


def tokens(text: str) -> list[str]:
    return [w for w in re.findall(r"[a-z']+", str(text).lower()) if w not in STOP and len(w) > 2]


def question_summary(series: pd.Series, sia: SentimentIntensityAnalyzer) -> dict:
    resp = series.dropna().astype(str)
    resp = resp = resp[resp.str.strip() != ""]
    all_tokens, bigrams, compounds = [], Counter(), []
    pos = neg = neu = 0
    for txt in resp:
        toks = tokens(txt)
        all_tokens += toks
        bigrams.update(zip(toks, toks[1:]))
        c = sia.polarity_scores(txt)["compound"]
        compounds.append(c)
        pos += c >= 0.05
        neg += c <= -0.05
        neu += -0.05 < c < 0.05
    n = len(resp)
    wc = Counter(all_tokens)
    return {
        "n_responses": n,
        "total_words": len(all_tokens),
        "unique_words": len(wc),
        "top_words": wc.most_common(15),
        "top_bigrams": [(" ".join(bg), c) for bg, c in bigrams.most_common(10)],
        "mean_compound": round(float(np.mean(compounds)), 4),
        "pct_positive": round(100 * pos / n, 1),
        "pct_negative": round(100 * neg / n, 1),
        "pct_neutral": round(100 * neu / n, 1),
    }


def paired_test(df, sia, id_col, col_ai, col_hu, label):
    """Paired t-test on VADER compound: AI vs human, same participants."""
    sub = df[[id_col, df.columns[col_ai], df.columns[col_hu]]].dropna()
    ai = sub[df.columns[col_ai]].apply(lambda t: sia.polarity_scores(str(t))["compound"])
    hu = sub[df.columns[col_hu]].apply(lambda t: sia.polarity_scores(str(t))["compound"])
    diff = hu - ai
    t, p = stats.ttest_rel(hu, ai)
    dz = float(diff.mean() / diff.std(ddof=1))
    return {
        "comparison": label,
        "n_pairs": int(len(sub)),
        "mean_AI": round(float(ai.mean()), 4),
        "mean_human": round(float(hu.mean()), 4),
        "t": round(float(t), 3),
        "df": int(len(sub) - 1),
        "p": float(f"{p:.2e}"),
        "cohen_dz": round(dz, 3),
    }


def main():
    if not RAW.exists():
        raise SystemExit(f"Raw survey not found at {RAW} (git-ignored). Place it there to run.")
    df = pd.read_csv(RAW, encoding="utf-8-sig")
    sia = SentimentIntensityAnalyzer()
    id_col = df.columns[0]

    summary = {key: question_summary(df[df.columns[idx]], sia) for idx, key in QCOLS.items()}
    (OUT / "nlp_summary.json").write_text(json.dumps(summary, indent=2))
    print("+ wrote results/nlp_summary.json")

    cv = {
        "emotional_connection_AI_vs_human": paired_test(df, sia, id_col, 40, 41, "connection: human - AI"),
        "concerns_AI_vs_human": paired_test(df, sia, id_col, 42, 43, "concerns: human - AI"),
    }
    (OUT / "convergent_validity.json").write_text(json.dumps(cv, indent=2))
    print("+ wrote results/convergent_validity.json")

    for k, v in cv.items():
        print(f"  {k}: t({v['df']})={v['t']}, p={v['p']}, dz={v['cohen_dz']} "
              f"(AI {v['mean_AI']} vs human {v['mean_human']}, n={v['n_pairs']})")


if __name__ == "__main__":
    main()
