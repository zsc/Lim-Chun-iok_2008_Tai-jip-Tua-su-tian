from __future__ import annotations

from functools import lru_cache

try:
    from opencc import OpenCC
except ImportError:  # pragma: no cover
    OpenCC = None  # type: ignore[assignment]


@lru_cache(maxsize=8)
def _get_converter(config: str):
    if OpenCC is None:  # pragma: no cover
        raise RuntimeError(
            "OpenCC not available. Install `opencc-python-reimplemented` or pass --no-opencc."
        )
    return OpenCC(config)


def to_traditional(text: str, *, config: str = "s2tw") -> str:
    if not text:
        return text
    return _get_converter(config).convert(text)

