from __future__ import annotations

import re

TONE_COMBINING_MARK = {
    2: "\u0301",  # acute
    3: "\u0300",  # grave
    5: "\u0302",  # circumflex
    6: "\u030C",  # caron
    7: "\u0304",  # macron
    8: "\u030D",  # vertical line above (POJ/Tâi-lô tone 8)
}

VOWEL_TONE = {
    "a": {2: "á", 3: "à", 5: "â", 6: "ǎ", 7: "ā"},
    "e": {2: "é", 3: "è", 5: "ê", 6: "ě", 7: "ē"},
    "i": {2: "í", 3: "ì", 5: "î", 6: "ǐ", 7: "ī"},
    "o": {2: "ó", 3: "ò", 5: "ô", 6: "ǒ", 7: "ō"},
    "u": {2: "ú", 3: "ù", 5: "û", 6: "ǔ", 7: "ū"},
}

_ROMAN_SYLLABLE_RE = re.compile(r"[A-Za-z]+[1-9]?")
_ROMAN_NUMERIC_RE = re.compile(r"[A-Za-z]+[1-9]")


def _to_tailo_orthography(syllable: str) -> str:
    # Convert POJ-ish orthography found in dict.csv to MOE Tâi-lô-ish.
    # Keep conservative and local (syllable-level).
    syllable = syllable.replace("ⁿ", "nn").replace("N", "nn")
    syllable = syllable.lower()

    if syllable.startswith("chh"):
        syllable = "tsh" + syllable[3:]
    elif syllable.startswith("ch"):
        syllable = "ts" + syllable[2:]

    syllable = syllable.replace("oe", "ue")
    syllable = syllable.replace("oa", "ua")
    return syllable


def _pick_mark_index(body: str) -> int | None:
    if not body:
        return None

    # Vowels first.
    for vowel in ("a", "e", "o"):
        idx = body.find(vowel)
        if idx != -1:
            return idx

    vowel_indices = [i for i, ch in enumerate(body) if ch in ("i", "u")]
    if vowel_indices:
        return vowel_indices[-1]

    # Syllabic consonants.
    if body.startswith("ng"):
        return 0  # mark 'n'
    if body.startswith("m"):
        return 0  # mark 'm'
    return None


def _apply_tone_mark(body: str, tone: int) -> str:
    if tone in (1, 4):
        return body

    mark_index = _pick_mark_index(body)
    if mark_index is None:
        return body

    base_char = body[mark_index]
    if tone in VOWEL_TONE.get(base_char, {}):
        return body[:mark_index] + VOWEL_TONE[base_char][tone] + body[mark_index + 1 :]

    combining = TONE_COMBINING_MARK.get(tone)
    if not combining:
        return body
    return body[: mark_index + 1] + combining + body[mark_index + 1 :]


def convert_poj_word_to_tailo(text: str, *, orthography: bool = True) -> str:
    """
    Convert a POJ-ish word (e.g. dict.csv `word`) into Tâi-lô-ish output.
    - Converts orthography (ch/chh/oe/oa/N) and tone numbers to tone marks.
    - Safe to run on strings that include punctuation/parentheses; only roman
      syllables are converted.
    """

    def repl(match: re.Match[str]) -> str:
        token = match.group(0)
        tone = None
        if token and token[-1].isdigit() and token[-1] != "0":
            tone = int(token[-1])
            body = token[:-1]
        else:
            body = token

        if orthography:
            body = _to_tailo_orthography(body)
        else:
            body = body.replace("ⁿ", "nn").replace("N", "nn").lower()

        if tone is None:
            return body
        return _apply_tone_mark(body, tone)

    return _ROMAN_SYLLABLE_RE.sub(repl, text.strip())


def convert_numeric_poj_in_text(text: str, *, orthography: bool = True) -> str:
    """
    Convert only tone-number syllables (A-Za-z + [1-9]) inside free text.
    Useful for `--mode auto` so we don't mutate unrelated English words.
    """

    def repl(match: re.Match[str]) -> str:
        token = match.group(0)
        tone = int(token[-1])
        body = token[:-1]
        body = _to_tailo_orthography(body) if orthography else body.replace("N", "nn").lower()
        return _apply_tone_mark(body, tone)

    return _ROMAN_NUMERIC_RE.sub(repl, text)

