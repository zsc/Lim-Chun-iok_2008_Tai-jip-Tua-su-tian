# SPEC: `tailo-cli`（text → 台羅）

## Summary
Build a small Python CLI that converts:
- 漢字/台文句子 → 台羅（Tâi-lô）拼音（利用本 repo 的 `dict.csv`）
- 或 POJ/台語數字調（如 `chit8 e5`）→ 台羅調號（如 `tsi̍t ê`）

Target users: in-repo usage (default `./dict.csv`) and command-line piping.

## Inputs
- Text from CLI positional args or `stdin`.
- Dictionary CSV: `dict.csv` in this repo (generated from SQLite via `sql2csv.sh`).

## Outputs
- UTF-8 text to `stdout`.
- 台羅 tone marks (diacritics + tone-8 combining mark).
- For 漢字轉換: insert a single space between adjacent romanized segments when the original text had no separator.

## CLI Contract

### Convert (default)
```
tailo [--dict PATH] [--opencc CONFIG] [--no-opencc] [--mode auto|hanzi|poj] [--ambiguous first|all] [--unknown keep|mark] [--no-orthography] [TEXT...]
```

Examples:
```
tailo chit8 e5
# -> tsi̍t ê

tailo --mode hanzi 一大囝
# -> tsi̍t-tuā kiánn   (longest-match from dict)

echo "chit8 e5" | tailo
# -> tsi̍t ê
```

Modes:
- `auto` (default): if text contains Hanzi, convert via dictionary; then convert any remaining tone-number POJ tokens.
- `hanzi`: only dictionary-based conversion (non-Hanzi passthrough).
- `poj`: treat input as POJ-ish romanization; convert syllables and tone numbers.

Options:
- `--dict PATH`: path to `dict.csv` (default: `./dict.csv` if exists).
- `--opencc CONFIG`: OpenCC config for 簡→繁（default: `s2tw`).
- `--no-opencc`: disable 簡→繁 conversion.
- `--ambiguous first|all`: when dictionary has multiple pronunciations for a headword.
  - `first`: pick the first loaded pronunciation.
  - `all`: output `{a/b/c}`.
- `--unknown keep|mark`:
  - `keep`: keep unknown Hanzi as-is.
  - `mark`: output `<?>`.
- `--no-orthography`: skip POJ→台羅 orthography conversion (still converts tone numbers).

### Lookup
```
tailo lookup [--dict PATH] [--opencc CONFIG] [--no-opencc] [--no-orthography] 漢字
```

Example:
```
tailo lookup 一
# -> tsi̍t
# -> it
```

## Dictionary (`dict.csv`) Requirements
- CSV header must contain at least: `word`, `chinese`.
- `chinese` cells are usually bracketed like `[鴉]` (with padding spaces).
- Build a mapping:
  - key: bracket inner text (strip spaces)
  - value: `word` converted to 台羅 (see rules below)
- Only include keys that contain Hanzi codepoints (skip keys like `[a3 -a3 ]`).

## Hanzi Segmentation
- Pre-step (default): convert Simplified→Traditional via OpenCC (`s2tw`), so simplified input can match traditional dictionary keys.
- Use longest-match scanning:
  - Precompute `max_key_len` from dictionary keys.
  - At each Hanzi position `i`, try candidates `text[i:i+L]` from `L=max_key_len` down to `1`.
  - If matched, emit pronunciation and advance by `len(match)`.
  - If not matched, apply `--unknown` policy.
- Spacing rule:
  - If output currently ends with a “word-ish” character (Unicode category `L/M/N`)
  - and next emitted segment starts with a “word-ish” character,
  - insert one ASCII space.

## POJ-ish → 台羅 Conversion Rules

### Orthography (can be disabled via `--no-orthography`)
Applied per syllable:
- `N` or `ⁿ` → `nn` (nasal marker)
- lowercase
- initial `chh` → `tsh`
- initial `ch` → `ts`
- `oe` → `ue`
- `oa` → `ua`

### Tone marks
Input uses trailing tone digits `1-8` (e.g., `kiaN2`, `chit8`, `boe7`).

- Tone 1, 4: no mark
- Tone 2: acute (á)
- Tone 3: grave (à)
- Tone 5: circumflex (â)
- Tone 6: caron (ǎ) (rare in this dataset; included for completeness)
- Tone 7: macron (ā)
- Tone 8: combining vertical line above (a̍, i̍, …)

### Mark placement
Pick the nucleus position in this priority:
1. first `a`
2. else first `e`
3. else first `o`
4. else the last vowel among `i`/`u`
5. else syllabic `ng` → mark `n`
6. else syllabic `m` → mark `m`

## Non-goals
- Tone sandhi / context-aware tone changes.
- Word-sense disambiguation (dictionary ambiguities remain ambiguities).
- Full Taiwanese NLP tokenization beyond longest-match dictionary lookup.

## Repo Layout
- `tailo_cli/romanize.py`: POJ-ish → 台羅 conversion.
- `tailo_cli/dict_loader.py`: load `dict.csv` into a Hanzi→台羅 mapping.
- `tailo_cli/converter.py`: longest-match Hanzi conversion + spacing.
- `tailo_cli/__main__.py`: CLI entrypoint (`tailo`).
- `tests/test_tailo_cli.py`: unit tests (small, no large file I/O).

## Dev / Validation
Install (editable):
```
python -m pip install -e .
```

Run tests:
```
python -m unittest discover -s tests
```

## Licensing note
- Code in this repo is MIT (see `LICENSE`).
- Dictionary data has its own license statement in `README.md` (CC BY-NC-SA 3.0 TW); keep usage compliant.
