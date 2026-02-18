from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .converter import contains_hanzi, hanzi_to_tailo
from .dict_loader import load_dict_csv
from .ipa import tailo_to_ipa
from .opencc_util import to_traditional
from .romanize import convert_numeric_poj_in_text, convert_poj_word_to_tailo


def _read_input_text(args: argparse.Namespace) -> str:
    if args.text:
        return " ".join(args.text)
    return sys.stdin.read()


def _default_dict_path() -> Path:
    cwd_dict = Path.cwd() / "dict.csv"
    if cwd_dict.exists():
        return cwd_dict
    return Path(__file__).resolve().parent.parent / "dict.csv"


def cmd_lookup(args: argparse.Namespace) -> int:
    dict_path = Path(args.dict or _default_dict_path())
    word = args.word
    if not args.no_opencc:
        word = to_traditional(word, config=args.opencc)
    try:
        mapping, _max_len = load_dict_csv(dict_path, orthography=not args.no_orthography)
    except FileNotFoundError:
        print(f"dict.csv not found: {dict_path} (use --dict PATH)", file=sys.stderr)
        return 2
    except ValueError as e:
        print(str(e), file=sys.stderr)
        return 2
    vals = mapping.get(word)
    if not vals:
        print(f"(not found) {word}", file=sys.stderr)
        return 2
    for v in vals:
        print(tailo_to_ipa(v) if args.output == "ipa" else v)
    return 0


def cmd_convert(args: argparse.Namespace) -> int:
    text = _read_input_text(args)

    if args.mode == "poj":
        out = convert_poj_word_to_tailo(text, orthography=not args.no_orthography)
        if args.output == "ipa":
            out = tailo_to_ipa(out)
        print(out)
        return 0

    if args.mode == "hanzi":
        dict_path = Path(args.dict or _default_dict_path())
        if not args.no_opencc:
            text = to_traditional(text, config=args.opencc)
        try:
            mapping, max_len = load_dict_csv(dict_path, orthography=not args.no_orthography)
        except FileNotFoundError:
            print(f"dict.csv not found: {dict_path} (use --dict PATH)", file=sys.stderr)
            return 2
        except ValueError as e:
            print(str(e), file=sys.stderr)
            return 2
        out = hanzi_to_tailo(
            text,
            mapping,
            max_key_len=max_len,
            ambiguous=args.ambiguous,
            unknown=args.unknown,
        )
        if args.output == "ipa":
            out = tailo_to_ipa(out)
        print(out)
        return 0

    # auto
    if contains_hanzi(text):
        dict_path = Path(args.dict or _default_dict_path())
        if not args.no_opencc:
            text = to_traditional(text, config=args.opencc)
        try:
            mapping, max_len = load_dict_csv(dict_path, orthography=not args.no_orthography)
        except FileNotFoundError:
            print(f"dict.csv not found: {dict_path} (use --dict PATH)", file=sys.stderr)
            return 2
        except ValueError as e:
            print(str(e), file=sys.stderr)
            return 2
        text = hanzi_to_tailo(
            text,
            mapping,
            max_key_len=max_len,
            ambiguous=args.ambiguous,
            unknown=args.unknown,
        )
    text = convert_numeric_poj_in_text(text, orthography=not args.no_orthography)
    if args.output == "ipa":
        text = tailo_to_ipa(text)
    print(text)
    return 0


def _add_common_args(p: argparse.ArgumentParser) -> None:
    p.add_argument(
        "--dict",
        help="Path to dict.csv (default: ./dict.csv if exists).",
    )
    p.add_argument(
        "--opencc",
        default="s2tw",
        help="OpenCC config for Simplified→Traditional (default: s2tw).",
    )
    p.add_argument(
        "--no-opencc",
        action="store_true",
        help="Disable Simplified→Traditional conversion.",
    )
    p.add_argument(
        "--no-orthography",
        action="store_true",
        help="Skip POJ→台羅 orthography (still converts tone numbers).",
    )
    p.add_argument(
        "--output",
        choices=("tailo", "ipa"),
        default="tailo",
        help="Output format (default: tailo).",
    )


def build_convert_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="tailo",
        description="Convert text into Tâi-lô (台羅).",
        epilog="Subcommands: `tailo lookup <漢字>`",
    )
    _add_common_args(p)
    p.add_argument(
        "--mode",
        choices=("auto", "hanzi", "poj"),
        default="auto",
        help="Conversion mode.",
    )
    p.add_argument(
        "--ambiguous",
        choices=("first", "all"),
        default="first",
        help="When multiple pronunciations exist for a Hanzi entry.",
    )
    p.add_argument(
        "--unknown",
        choices=("keep", "mark"),
        default="keep",
        help="How to handle unknown Hanzi.",
    )
    p.add_argument("text", nargs="*", help="Text to convert (or use stdin).")
    return p


def build_lookup_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="tailo lookup",
        description="Lookup a Hanzi headword in dict.csv and print possible 台羅.",
    )
    _add_common_args(p)
    p.add_argument("word", help="Hanzi headword to lookup, e.g. 一")
    return p


def main(argv: list[str] | None = None) -> int:
    try:
        argv = list(sys.argv[1:] if argv is None else argv)

        if argv and argv[0] == "lookup":
            parser = build_lookup_parser()
            args = parser.parse_args(argv[1:])
            return cmd_lookup(args)

        if argv and argv[0] == "convert":
            argv = argv[1:]

        parser = build_convert_parser()
        args = parser.parse_args(argv)
        return cmd_convert(args)
    except BrokenPipeError:
        return 0


if __name__ == "__main__":
    raise SystemExit(main())
