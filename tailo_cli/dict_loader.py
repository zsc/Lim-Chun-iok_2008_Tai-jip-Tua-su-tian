from __future__ import annotations

import csv
import re
from pathlib import Path

from .romanize import convert_poj_word_to_tailo

_BRACKETED_RE = re.compile(r"^\[(.*)\]$")
_HAS_HANZI_RE = re.compile("[\u3400-\u4DBF\u4E00-\u9FFF\uF900-\uFAFF]")


def load_dict_csv(
    path: Path,
    *,
    orthography: bool = True,
) -> tuple[dict[str, list[str]], int]:
    """
    Load dict.csv and build a mapping:
      漢字詞條 -> [台羅, 台羅, ...]
    Returns (mapping, max_key_len).
    """
    mapping: dict[str, list[str]] = {}
    max_key_len = 0

    with path.open("r", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            chinese = (row.get("chinese") or "").strip()
            m = _BRACKETED_RE.match(chinese)
            if not m:
                continue
            key = m.group(1).strip()
            if not key or not _HAS_HANZI_RE.search(key):
                continue

            word = (row.get("word") or "").strip()
            if not word:
                continue

            tailo = convert_poj_word_to_tailo(word, orthography=orthography)
            if not tailo:
                continue

            mapping.setdefault(key, [])
            if tailo not in mapping[key]:
                mapping[key].append(tailo)

            if len(key) > max_key_len:
                max_key_len = len(key)

    if not mapping:
        raise ValueError(f"No entries loaded from {path}")
    return mapping, max_key_len
