from __future__ import annotations

import re
import unicodedata

_TONE_MARK_TO_TONE: dict[str, int] = {
    "\u0301": 2,  # acute
    "\u0300": 3,  # grave
    "\u0302": 5,  # circumflex
    "\u030C": 6,  # caron
    "\u0304": 7,  # macron
    "\u030D": 8,  # vertical line above (tailo tone 8)
}

_TONE_SUPERSCRIPT: dict[int, str] = {
    1: "¹",
    2: "²",
    3: "³",
    4: "⁴",
    5: "⁵",
    6: "⁶",
    7: "⁷",
    8: "⁸",
}

_IPA_SYLLABIC = "\u0329"  # combining vertical line below
_IPA_NASAL = "\u0303"  # combining tilde

_ONSET_TO_IPA: dict[str, str] = {
    "tsh": "t͡sʰ",
    "ts": "t͡s",
    "chh": "t͡sʰ",  # POJ-ish alias
    "ch": "t͡s",  # POJ-ish alias
    "ph": "pʰ",
    "th": "tʰ",
    "kh": "kʰ",
    "ng": "ŋ",
    "p": "p",
    "b": "b",
    "m": "m",
    "t": "t",
    "n": "n",
    "l": "l",
    "k": "k",
    "g": "ɡ",
    "h": "h",
    "s": "s",
    "j": "d͡z",
    "": "",
}

_ONSET_CANDIDATES = sorted(_ONSET_TO_IPA.keys(), key=len, reverse=True)

_CODA_TO_IPA: dict[str, str] = {
    "p": "p̚",
    "t": "t̚",
    "k": "k̚",
    "h": "ʔ",
    "m": "m",
    "n": "n",
    "ng": "ŋ",
    "": "",
}

_TAILO_TOKEN_RE = re.compile(r"[A-Za-z\u00C0-\u024F\u1E00-\u1EFF\u0300-\u036F\u207Fⁿ]+")

# Base letters commonly seen in Tâi-lô/POJ-ish syllables. Keep intentionally small so we
# don't accidentally convert arbitrary English words too aggressively.
_ALLOWED_BASE_LETTERS = set("abceghijklmnops tu")  # space removed below
_ALLOWED_BASE_LETTERS.discard(" ")

_IPA_VOWELS = set("aeiouɔo")


def _strip_tone_and_normalize(token: str) -> tuple[str, int]:
    nfd = unicodedata.normalize("NFD", token)
    tone: int | None = None
    out: list[str] = []
    for ch in nfd:
        t = _TONE_MARK_TO_TONE.get(ch)
        if t is not None:
            tone = t
            continue
        out.append(ch)

    base = unicodedata.normalize("NFC", "".join(out))
    base = base.replace("ⁿ", "nn").lower()

    if tone is None:
        if base.endswith(("p", "t", "k", "h")):
            tone = 4
        else:
            tone = 1
    return base, tone


def _looks_like_tailo_token(token: str) -> bool:
    if not token:
        return False

    base, _tone = _strip_tone_and_normalize(token)
    if base in ("m", "ng"):
        return True

    has_vowel = any(ch in "aeiouo" for ch in base)
    if not has_vowel:
        # Allow syllabic consonant rimes like "hm", "sng", "hng".
        if base.endswith("ng") and base[:-2] in _ONSET_TO_IPA:
            return True
        if base.endswith("m") and base[:-1] in _ONSET_TO_IPA:
            return True
        return False

    # Check the decomposed base letters are within our conservative allowlist.
    for ch in unicodedata.normalize("NFD", base):
        if unicodedata.combining(ch):
            continue
        if ch not in _ALLOWED_BASE_LETTERS:
            return False
    return True


def tailo_syllable_to_ipa(token: str) -> str:
    """
    Convert one tailo-ish syllable into IPA, keeping tones as superscript digits.
    If the token doesn't look like a valid syllable, returns it unchanged.
    """
    if not _looks_like_tailo_token(token):
        return token

    base, tone = _strip_tone_and_normalize(token)

    if base == "m":
        return "m" + _IPA_SYLLABIC + _TONE_SUPERSCRIPT[tone]
    if base == "ng":
        return "ŋ" + _IPA_SYLLABIC + _TONE_SUPERSCRIPT[tone]

    onset = ""
    rime = base
    for cand in _ONSET_CANDIDATES:
        if cand and base.startswith(cand):
            onset = cand
            rime = base[len(cand) :]
            break

    nasal = False
    if rime.endswith("nn") and len(rime) > 2:
        nasal = True
        rime = rime[:-2]

    coda = ""
    rime_body = rime
    for cand in ("ng", "m", "n", "p", "t", "k", "h"):
        if rime.endswith(cand):
            coda = cand
            rime_body = rime[: -len(cand)]
            break

    if rime_body.endswith("nn") and len(rime_body) > 2:
        nasal = True
        rime_body = rime_body[:-2]

    ipa_onset = _ONSET_TO_IPA.get(onset, "")

    # If we ended up with a syllabic consonant rime (e.g., sng/hm), mark it.
    if not rime_body and coda in ("m", "n", "ng"):
        nucleus = _CODA_TO_IPA[coda] + _IPA_SYLLABIC
        ipa = ipa_onset + nucleus
        return ipa + _TONE_SUPERSCRIPT[tone]

    if not rime_body:
        return token

    ipa_rime = rime_body.replace("oo", "O")
    ipa_rime = ipa_rime.replace("o", "ɔ")
    ipa_rime = ipa_rime.replace("O", "o")

    if nasal:
        for i in range(len(ipa_rime) - 1, -1, -1):
            if ipa_rime[i] in _IPA_VOWELS:
                ipa_rime = ipa_rime[: i + 1] + _IPA_NASAL + ipa_rime[i + 1 :]
                break

    ipa_coda = _CODA_TO_IPA.get(coda, "")
    ipa = ipa_onset + ipa_rime + ipa_coda
    return ipa + _TONE_SUPERSCRIPT[tone]


def tailo_to_ipa(text: str) -> str:
    """
    Convert tailo-ish syllables found in free text into IPA (with tone superscripts).
    Non-tailo segments are left unchanged.
    """

    def repl(match: re.Match[str]) -> str:
        token = match.group(0)
        return tailo_syllable_to_ipa(token)

    return _TAILO_TOKEN_RE.sub(repl, text)
