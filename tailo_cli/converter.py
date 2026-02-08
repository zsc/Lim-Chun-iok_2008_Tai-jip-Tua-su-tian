from __future__ import annotations

import unicodedata


def is_hanzi(ch: str) -> bool:
    code = ord(ch)
    return (
        0x4E00 <= code <= 0x9FFF
        or 0x3400 <= code <= 0x4DBF
        or 0xF900 <= code <= 0xFAFF
        or 0x20000 <= code <= 0x2A6DF
    )


def contains_hanzi(text: str) -> bool:
    return any(is_hanzi(ch) for ch in text)


def _is_wordish(ch: str) -> bool:
    if not ch:
        return False
    cat = unicodedata.category(ch)
    return cat[0] in ("L", "M", "N")


def hanzi_to_tailo(
    text: str,
    mapping: dict[str, list[str]],
    *,
    max_key_len: int,
    ambiguous: str = "first",
    unknown: str = "keep",
) -> str:
    if ambiguous not in ("first", "all"):
        raise ValueError("ambiguous must be 'first' or 'all'")
    if unknown not in ("keep", "mark"):
        raise ValueError("unknown must be 'keep' or 'mark'")

    out = ""
    i = 0
    while i < len(text):
        ch = text[i]
        if is_hanzi(ch):
            match = None
            match_vals: list[str] | None = None
            max_len = min(max_key_len, len(text) - i)
            for length in range(max_len, 0, -1):
                cand = text[i : i + length]
                vals = mapping.get(cand)
                if vals:
                    match = cand
                    match_vals = vals
                    break

            if match and match_vals:
                if ambiguous == "first":
                    seg = match_vals[0]
                else:
                    seg = "{" + "/".join(match_vals) + "}"

                if out and seg and _is_wordish(out[-1]) and _is_wordish(seg[0]):
                    out += " "
                out += seg
                i += len(match)
                continue

            if unknown == "mark":
                if out and _is_wordish(out[-1]):
                    out += " "
                out += "<?>"
            else:
                out += ch
            i += 1
            continue

        # Non-hanzi: pass through as-is.
        out += ch
        i += 1

    return out
