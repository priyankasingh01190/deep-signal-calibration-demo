"""
code_with_llm.py
----------------
Run a versioned prompt over a set of responses and return one theme label per response.

Two modes:
  * API mode   — if ANTHROPIC_API_KEY is set and `anthropic` is installed, each response is
                 sent through the chosen prompt to a Claude model. This is the real scorer.
  * offline    — otherwise, labels are read from the reference set's stored fixture columns
                 (v1_theme/v2_theme/v3_theme). This lets the pipeline run with no key so a
                 reviewer can reproduce every metric offline.

The point of the harness is that the SAME prompt files drive both modes, and every run is
stamped with model + prompt file + prompt hash (see run_experiment.py).

Usage:
  from code_with_llm import code_responses
  labels = code_responses(df, prompt_path, model="claude-sonnet-5", version_col="v2_theme")
"""
from __future__ import annotations
import os
import re
import hashlib
from pathlib import Path
import pandas as pd

VALID = {"PRIVACY", "ACCURACY", "EMPATHY", "SAFETY", "ACCOUNTABILITY", "ACCESS_BENEFIT", "OTHER"}
DEFAULT_MODEL = "claude-sonnet-5"


def prompt_hash(prompt_path: str | Path) -> str:
    return hashlib.sha256(Path(prompt_path).read_bytes()).hexdigest()[:12]


def _parse_label(text: str) -> str:
    """Pull a valid theme name out of a model reply (handles the v3 'Theme: X' format)."""
    up = text.upper()
    m = re.search(r"THEME:\s*([A-Z_]+)", up)
    if m and m.group(1) in VALID:
        return m.group(1)
    # else take the last valid theme token that appears
    hits = [t for t in re.findall(r"[A-Z_]+", up) if t in VALID]
    return hits[-1] if hits else "OTHER"


def _api_available() -> bool:
    if not os.environ.get("ANTHROPIC_API_KEY"):
        return False
    try:
        import anthropic  # noqa: F401
        return True
    except ImportError:
        return False


def code_responses(
    df: pd.DataFrame,
    prompt_path: str | Path,
    model: str = DEFAULT_MODEL,
    version_col: str | None = None,
) -> tuple[list[str], str]:
    """Return (labels, mode). mode is 'api:<model>' or 'offline:fixture'."""
    if _api_available():
        import anthropic
        client = anthropic.Anthropic()
        template = Path(prompt_path).read_text()
        labels = []
        for _, row in df.iterrows():
            msg = client.messages.create(
                model=model,
                max_tokens=64,
                messages=[{"role": "user",
                           "content": template.replace("{response}", str(row["response"]))}],
            )
            labels.append(_parse_label(msg.content[0].text))
        return labels, f"api:{model}"

    # offline fixture mode
    if version_col and version_col in df.columns:
        return df[version_col].astype(str).tolist(), "offline:fixture"
    raise RuntimeError(
        "No ANTHROPIC_API_KEY and no fixture column to fall back on. "
        "Set the key to score live, or pass version_col for offline reproduction."
    )


if __name__ == "__main__":
    print("API available:", _api_available())
    for p in ["prompts/v1_zero_shot.txt", "prompts/v2_definitions.txt", "prompts/v3_few_shot.txt"]:
        print(f"{p}  sha256[:12]={prompt_hash(p)}")
